"""WSGI application for the Seafile WOPI editor bridge (prototype).

Design (docs/REFOUNDATION-REPORT.md §5):

* Seahub is configured with ``ENABLE_OFFICE_WEB_APP`` and
  ``OFFICE_WEB_APP_BASE_URL`` pointing at ``/wopi/discovery.xml`` here.
* On a file click Seahub POSTs ``access_token`` + ``access_token_ttl`` to the
  ``urlsrc`` we advertised, with ``WOPISrc=<Seahub WOPI files URL>`` in the
  query string.  We answer with a host page embedding the editor iframe.
* The host page keeps the token in memory and calls the ``/relay/*``
  endpoints; the relay forwards CheckFileInfo / GetFile / PutFile / lock
  operations to Seahub.  Nothing is stored server-side.

Everything Seahub does not enforce on PutFile (``UserCanWrite``, version
precondition, content signature) is enforced here before forwarding.
"""

from __future__ import annotations

import hashlib
import html
import json
import os
import re
import secrets
import urllib.error
import urllib.parse
import urllib.request
import zipfile
import io
from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List, Optional, Tuple

__all__ = ["Config", "Bridge", "UpstreamError", "TransportError", "load_editors"]

_ALLOWED_LOCK_OPS = ("LOCK", "UNLOCK", "REFRESH_LOCK", "GET_LOCK")
_EXT_RE = re.compile(r"^[a-z0-9]{1,16}$")
_EDITOR_ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,31}$")


# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #


@dataclass
class Config:
    public_url: str
    """Origin of this bridge as seen by the browser, e.g. ``https://craft.example``."""

    seahub_origin: str
    """Origin of Seahub; ``WOPISrc`` must live under it and may frame us."""

    editors: Dict[str, dict]
    """editor id -> {"url": str, "app": str, "extensions": [str], "label": str}.

    ``url`` is the same-origin iframe URL of the editor bundle (e.g.
    ``/editors/wordcraft/index.html?host=parent``); ``app`` is the
    ``postMessage`` type prefix the editor uses (``wordcraft`` for
    ``wordcraft:ready``...).
    """

    static_dir: Optional[str] = None
    """Directory served under ``/editors/``; ``None`` disables static serving."""

    max_bytes: int = 256 * 1024 * 1024
    timeout: float = 30.0
    lock_refresh_seconds: int = 600
    urlopen: Callable = urllib.request.urlopen
    """Injectable for tests (lost-response simulation)."""

    extension_editor: Dict[str, str] = field(init=False)

    def __post_init__(self) -> None:
        self.public_url = self.public_url.rstrip("/")
        self.seahub_origin = _origin_of(self.seahub_origin)
        self.extension_editor = {}
        for editor_id, spec in self.editors.items():
            if not _EDITOR_ID_RE.match(editor_id):
                raise ValueError(f"invalid editor id {editor_id!r}")
            for key in ("url", "app", "extensions"):
                if key not in spec:
                    raise ValueError(f"editor {editor_id}: missing {key!r}")
            if not spec["url"].startswith("/"):
                raise ValueError(f"editor {editor_id}: url must be same-origin (start with '/')")
            for ext in spec["extensions"]:
                ext = ext.lower()
                if not _EXT_RE.match(ext):
                    raise ValueError(f"editor {editor_id}: bad extension {ext!r}")
                if ext in self.extension_editor:
                    raise ValueError(f"extension {ext!r} mapped twice")
                self.extension_editor[ext] = editor_id


def load_editors(path: str) -> Dict[str, dict]:
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("editors.json must be an object")
    return data


def _origin_of(url: str) -> str:
    parts = urllib.parse.urlsplit(url)
    if parts.scheme not in ("http", "https") or not parts.netloc:
        raise ValueError(f"not an http(s) origin: {url!r}")
    return f"{parts.scheme}://{parts.netloc}".lower()


# --------------------------------------------------------------------------- #
# Upstream (Seahub WOPI host) client
# --------------------------------------------------------------------------- #


class UpstreamError(Exception):
    """Seahub answered with a non-2xx status."""

    def __init__(self, status: int, body: bytes = b"", headers: Optional[dict] = None):
        super().__init__(f"upstream status {status}")
        self.status = status
        self.body = body
        self.headers = headers or {}


class TransportError(Exception):
    """No HTTP response was obtained (connection reset, timeout, ...)."""


class WopiClient:
    def __init__(self, cfg: Config):
        self.cfg = cfg

    # -- validation ---------------------------------------------------------

    def validate_src(self, src: str) -> str:
        if not src:
            raise ValueError("missing WOPISrc")
        if _origin_of(src) != self.cfg.seahub_origin:
            raise ValueError("WOPISrc is not on the configured Seahub origin")
        parts = urllib.parse.urlsplit(src)
        if parts.query or parts.fragment:
            raise ValueError("WOPISrc must not carry a query string")
        return src

    @staticmethod
    def validate_token(token: str) -> str:
        if not token or len(token) > 256 or not re.match(r"^[A-Za-z0-9._~-]+$", token):
            raise ValueError("malformed access token")
        return token

    # -- low level ----------------------------------------------------------

    def _request(
        self,
        src: str,
        token: str,
        *,
        method: str = "GET",
        suffix: str = "",
        headers: Optional[dict] = None,
        body: Optional[bytes] = None,
    ) -> Tuple[int, dict, bytes]:
        url = f"{src}{suffix}?access_token={urllib.parse.quote(token, safe='')}"
        req = urllib.request.Request(url, data=body, method=method)
        for key, value in (headers or {}).items():
            req.add_header(key, value)
        if body is not None and "Content-Type" not in (headers or {}):
            req.add_header("Content-Type", "application/octet-stream")
        try:
            with self.cfg.urlopen(req, timeout=self.cfg.timeout) as resp:
                return resp.status, dict(resp.headers), resp.read()
        except urllib.error.HTTPError as exc:
            raise UpstreamError(exc.code, exc.read() or b"", dict(exc.headers or {})) from exc
        except (urllib.error.URLError, ConnectionError, TimeoutError, OSError) as exc:
            raise TransportError(str(exc)) from exc

    # -- WOPI operations ----------------------------------------------------

    def check_file_info(self, src: str, token: str) -> dict:
        status, _, body = self._request(src, token)
        try:
            info = json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise UpstreamError(502, b"CheckFileInfo is not JSON") from exc
        if not isinstance(info, dict) or "Version" not in info or "BaseFileName" not in info:
            raise UpstreamError(502, b"CheckFileInfo lacks Version/BaseFileName")
        return info

    def get_file(self, src: str, token: str) -> bytes:
        _, _, body = self._request(src, token, suffix="/contents")
        return body

    def put_file(self, src: str, token: str, data: bytes) -> dict:
        _, _, body = self._request(
            src,
            token,
            method="POST",
            suffix="/contents",
            headers={"X-WOPI-Override": "PUT"},
            body=data,
        )
        try:
            return json.loads(body.decode("utf-8")) if body else {}
        except (UnicodeDecodeError, json.JSONDecodeError):
            return {}

    def lock(self, src: str, token: str, op: str, lock_id: str, old_lock: str = "") -> Tuple[int, str]:
        if op not in _ALLOWED_LOCK_OPS:
            raise ValueError("unsupported lock operation")
        headers = {"X-WOPI-Override": op}
        if op != "GET_LOCK":
            headers["X-WOPI-Lock"] = lock_id
        if old_lock:
            headers["X-WOPI-OldLock"] = old_lock
        try:
            status, resp_headers, _ = self._request(src, token, method="POST", headers=headers, body=b"")
        except UpstreamError as exc:
            if exc.status == 409:
                return 409, _header(exc.headers, "X-WOPI-Lock")
            raise
        return status, _header(resp_headers, "X-WOPI-Lock")


def _header(headers: dict, name: str) -> str:
    for key, value in headers.items():
        if key.lower() == name.lower():
            return value
    return ""


# --------------------------------------------------------------------------- #
# Content signature guard (what the gateway used to do, now in the bridge)
# --------------------------------------------------------------------------- #


def content_matches_extension(ext: str, data: bytes) -> bool:
    ext = ext.lower()
    if ext in ("docx", "xlsx", "pptx", "odt", "ods", "odp"):
        if not data.startswith(b"PK\x03\x04"):
            return False
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as zf:
                names = set(zf.namelist())
        except zipfile.BadZipFile:
            return False
        if ext in ("docx", "xlsx", "pptx"):
            return "[Content_Types].xml" in names
        return "mimetype" in names
    if ext == "pdf":
        return data.lstrip()[:5] == b"%PDF-"
    if ext == "svg":
        head = data[:4096].lstrip()
        return head.startswith(b"<") and b"<svg" in head
    if ext == "png":
        return data.startswith(b"\x89PNG\r\n\x1a\n")
    if ext in ("jpg", "jpeg"):
        return data.startswith(b"\xff\xd8\xff")
    if ext == "drawio":
        head = data[:4096].lstrip()
        return head.startswith(b"<")
    # Unknown extension: no signature knowledge, accept.
    return True


# --------------------------------------------------------------------------- #
# WSGI application
# --------------------------------------------------------------------------- #


class _HTTPError(Exception):
    def __init__(self, status: int, message: str, extra: Optional[dict] = None):
        super().__init__(message)
        self.status = status
        self.message = message
        self.extra = extra or {}


_STATUS_TEXT = {
    200: "OK",
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    409: "Conflict",
    411: "Length Required",
    413: "Payload Too Large",
    415: "Unsupported Media Type",
    500: "Internal Server Error",
    502: "Bad Gateway",
    504: "Gateway Timeout",
}


class Bridge:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.wopi = WopiClient(cfg)
        here = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(here, "static", "host.js"), "r", encoding="utf-8") as fh:
            self._host_js = fh.read().encode("utf-8")
        with open(os.path.join(here, "static", "host.html"), "r", encoding="utf-8") as fh:
            self._host_html = fh.read()
        self._host_js_etag = '"' + hashlib.sha256(self._host_js).hexdigest()[:32] + '"'

    # -- WSGI entry ---------------------------------------------------------

    def __call__(self, environ, start_response) -> Iterable[bytes]:
        try:
            status, headers, body = self._dispatch(environ)
        except _HTTPError as exc:
            payload = {"error": exc.message, **exc.extra}
            status, headers, body = exc.status, [("Content-Type", "application/json")], json.dumps(payload).encode()
        except UpstreamError as exc:
            status, headers, body = self._map_upstream(exc)
        except TransportError:
            status, headers, body = 504, [("Content-Type", "application/json")], b'{"error":"seafile unreachable"}'
        headers = list(headers) + [
            ("Content-Length", str(len(body))),
            ("X-Content-Type-Options", "nosniff"),
            ("Referrer-Policy", "no-referrer"),
            ("Cache-Control", "no-store"),
        ]
        start_response(f"{status} {_STATUS_TEXT.get(status, 'Status')}", headers)
        return [body]

    @staticmethod
    def _map_upstream(exc: UpstreamError):
        if exc.status in (401, 404):
            return 401, [("Content-Type", "application/json")], b'{"error":"access token rejected by seafile (expired or revoked)"}'
        if exc.status == 409:
            return 409, [("Content-Type", "application/json")], b'{"error":"seafile reported a conflict"}'
        return 502, [("Content-Type", "application/json")], json.dumps({"error": f"seafile returned {exc.status}"}).encode()

    # -- routing ------------------------------------------------------------

    def _dispatch(self, environ):
        method = environ["REQUEST_METHOD"].upper()
        path = environ.get("PATH_INFO", "/") or "/"

        if path == "/healthz" and method == "GET":
            return 200, [("Content-Type", "text/plain")], b"ok\n"
        if path == "/wopi/discovery.xml" and method == "GET":
            return 200, [("Content-Type", "application/xml; charset=utf-8")], self.discovery_xml().encode()
        if path == "/host.js" and method == "GET":
            return 200, [("Content-Type", "application/javascript; charset=utf-8"), ("ETag", self._host_js_etag)], self._host_js
        if path.startswith("/edit/"):
            if method != "POST":
                raise _HTTPError(405, "the editor entry point expects Seahub's form POST")
            return self._handle_edit(environ, path[len("/edit/"):])
        if path.startswith("/relay/"):
            if method != "POST":
                raise _HTTPError(405, "relay endpoints are POST only")
            return self._handle_relay(environ, path[len("/relay/"):])
        if path.startswith("/editors/") and method == "GET":
            return self._handle_static(path[len("/editors/"):])
        raise _HTTPError(404, "not found")

    # -- discovery ----------------------------------------------------------

    def discovery_xml(self) -> str:
        """WOPI discovery document in the shape Seahub's ``get_wopi_dict`` reads.

        Seahub iterates ``root.iter('action')`` and uses ``ext``, ``name`` and
        ``urlsrc`` only; with the default ``OFFICE_SERVER_TYPE`` it looks up
        both ``view`` and ``edit`` actions, so both are emitted per extension.
        """
        lines = ['<?xml version="1.0" encoding="UTF-8"?>', "<wopi-discovery>", '  <net-zone name="external-https">']
        for editor_id, spec in self.cfg.editors.items():
            label = html.escape(spec.get("label", editor_id), quote=True)
            lines.append(f'    <app name="{html.escape(editor_id, quote=True)}" favIconUrl="" checkLicense="false">')
            urlsrc = html.escape(f"{self.cfg.public_url}/edit/{editor_id}", quote=True)
            for ext in spec["extensions"]:
                for action in ("view", "edit"):
                    lines.append(f'      <action name="{action}" ext="{html.escape(ext.lower(), quote=True)}" default="true" urlsrc="{urlsrc}" title="{label}"/>')
            lines.append("    </app>")
        lines += ["  </net-zone>", "</wopi-discovery>", ""]
        return "\n".join(lines)

    # -- editor entry (Seahub form POST) ------------------------------------

    def _handle_edit(self, environ, editor_id: str):
        editor_id = editor_id.strip("/")
        spec = self.cfg.editors.get(editor_id)
        if spec is None:
            raise _HTTPError(404, "unknown editor")

        query = urllib.parse.parse_qs(environ.get("QUERY_STRING", ""), keep_blank_values=False)
        src = (query.get("WOPISrc") or [""])[0]
        try:
            src = self.wopi.validate_src(src)
        except ValueError as exc:
            raise _HTTPError(400, str(exc))

        form = self._read_form(environ)
        token = (form.get("access_token") or [""])[0]
        try:
            token = self.wopi.validate_token(token)
        except ValueError as exc:
            raise _HTTPError(400, str(exc))
        ttl = (form.get("access_token_ttl") or ["0"])[0]
        ttl = ttl if ttl.isdigit() else "0"

        # Resolve the file name now so the page can refuse wrong editors early
        # and show a title; this is also the first token validation.
        info = self.wopi.check_file_info(src, token)
        name = str(info.get("BaseFileName", ""))
        ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
        if ext not in spec["extensions"]:
            raise _HTTPError(400, f"{editor_id} does not handle .{ext} files")

        nonce = secrets.token_urlsafe(18)
        config = {
            "editorId": editor_id,
            "app": spec["app"],
            "editorUrl": spec["url"],
            "name": name,
            "ext": ext,
            "src": src,
            "token": token,
            "tokenTtl": int(ttl),
            "version": info.get("Version"),
            "userCanWrite": bool(info.get("UserCanWrite", False)),
            "userName": info.get("UserFriendlyName") or info.get("UserId") or "",
            "lockRefreshSeconds": self.cfg.lock_refresh_seconds,
            "maxBytes": self.cfg.max_bytes,
            "closeUrl": self.cfg.seahub_origin,
        }
        page = (
            self._host_html.replace("{{NONCE}}", nonce)
            .replace("{{TITLE}}", html.escape(name))
            .replace("{{CONFIG_JSON}}", json.dumps(config).replace("<", "\\u003c"))
        )
        csp = (
            "default-src 'none'; "
            f"script-src 'nonce-{nonce}'; "
            f"style-src 'nonce-{nonce}'; "
            "img-src 'self' data:; "
            "connect-src 'self'; "
            "frame-src 'self'; "
            f"frame-ancestors {self.cfg.seahub_origin}; "
            "base-uri 'none'; form-action 'none'"
        )
        headers = [("Content-Type", "text/html; charset=utf-8"), ("Content-Security-Policy", csp)]
        return 200, headers, page.encode("utf-8")

    # -- relay --------------------------------------------------------------

    def _handle_relay(self, environ, op: str):
        self._require_same_origin(environ)
        token = environ.get("HTTP_X_WOPI_TOKEN", "")
        src = environ.get("HTTP_X_WOPI_SRC", "")
        try:
            token = self.wopi.validate_token(token)
            src = self.wopi.validate_src(src)
        except ValueError as exc:
            raise _HTTPError(400, str(exc))

        if op == "info":
            info = self.wopi.check_file_info(src, token)
            return self._json(200, _public_info(info))

        if op == "file":
            info = self.wopi.check_file_info(src, token)
            data = self.wopi.get_file(src, token)
            headers = [
                ("Content-Type", "application/octet-stream"),
                ("X-Wopi-Version", str(info.get("Version", ""))),
                ("X-File-Name", urllib.parse.quote(str(info.get("BaseFileName", "")))),
            ]
            return 200, headers, data

        if op == "save":
            return self._relay_save(environ, src, token)

        if op == "lock":
            lock_op = environ.get("HTTP_X_WOPI_OVERRIDE", "")
            lock_id = environ.get("HTTP_X_WOPI_LOCK", "")
            old_lock = environ.get("HTTP_X_WOPI_OLDLOCK", "")
            if lock_op not in _ALLOWED_LOCK_OPS:
                raise _HTTPError(400, "unsupported lock operation")
            if lock_op != "GET_LOCK" and not re.match(r"^[A-Za-z0-9._~-]{1,128}$", lock_id):
                raise _HTTPError(400, "malformed lock id")
            status, current = self.wopi.lock(src, token, lock_op, lock_id, old_lock)
            return self._json(200 if status < 300 else status, {"status": status, "lock": current})

        raise _HTTPError(404, "unknown relay operation")

    def _relay_save(self, environ, src: str, token: str):
        expected = environ.get("HTTP_X_EXPECTED_VERSION", "")
        claimed_name = urllib.parse.unquote(environ.get("HTTP_X_FILE_NAME", ""))
        data = self._read_body(environ)
        if not data:
            raise _HTTPError(400, "empty document body refused")

        info = self.wopi.check_file_info(src, token)
        name = str(info.get("BaseFileName", ""))
        ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""

        # 1. Seahub's PutFile does not enforce this; we do.
        if not info.get("UserCanWrite", False):
            raise _HTTPError(403, "you do not have write permission on this file")
        # 2. No Save-As / rename through the save channel.
        if claimed_name and claimed_name != name:
            raise _HTTPError(400, "save under a different name is not allowed", {"expectedName": name})
        # 3. Content signature must match the extension (no PDF bytes into a .docx).
        if not content_matches_extension(ext, data):
            raise _HTTPError(415, f"document bytes are not a valid .{ext}")
        # 4. Optimistic concurrency: the version we opened must still be current.
        current = str(info.get("Version", ""))
        if expected and current != expected:
            raise _HTTPError(409, "the file changed in Seafile since it was opened", {"current": current, "expected": expected})

        try:
            self.wopi.put_file(src, token, data)
        except TransportError:
            # Lost response: the write may or may not have landed.
            after = self.wopi.check_file_info(src, token)
            if str(after.get("Version", "")) == current:
                raise  # nothing landed; the client may retry (identical bytes are idempotent)
            stored = self.wopi.get_file(src, token)
            if stored != data:
                raise _HTTPError(409, "a different version landed while saving", {"current": str(after.get("Version", ""))})
            return self._json(200, {"version": str(after.get("Version", "")), "reconciled": True, "lastModified": after.get("LastModifiedTime", "")})

        after = self.wopi.check_file_info(src, token)
        return self._json(200, {"version": str(after.get("Version", "")), "reconciled": False, "lastModified": after.get("LastModifiedTime", "")})

    # -- static editor bundles ---------------------------------------------

    def _handle_static(self, rel: str):
        if not self.cfg.static_dir:
            raise _HTTPError(404, "static serving disabled")
        root = os.path.realpath(self.cfg.static_dir)
        target = os.path.realpath(os.path.join(root, rel))
        if not (target == root or target.startswith(root + os.sep)):
            raise _HTTPError(404, "not found")
        if os.path.isdir(target):
            target = os.path.join(target, "index.html")
        if not os.path.isfile(target):
            raise _HTTPError(404, "not found")
        ctype = _guess_type(target)
        with open(target, "rb") as fh:
            body = fh.read()
        headers = [("Content-Type", ctype)]
        if ctype.startswith("text/html"):
            # Editor documents are framed by our host page, which is itself framed by Seahub:
            # frame-ancestors is checked against the whole ancestor chain, so both must be listed.
            # (Found by the real-browser slice; 'self' alone makes Chromium refuse the editor.)
            headers.append(("Content-Security-Policy", f"frame-ancestors 'self' {self.cfg.seahub_origin}"))
        return 200, headers, body

    # -- helpers ------------------------------------------------------------

    def _require_same_origin(self, environ) -> None:
        if environ.get("HTTP_X_BRIDGE_REQUEST") != "1":
            raise _HTTPError(403, "missing X-Bridge-Request header")
        origin = environ.get("HTTP_ORIGIN")
        if origin and origin.rstrip("/").lower() != self.cfg.public_url.lower():
            raise _HTTPError(403, "cross-origin relay call refused")
        fetch_site = environ.get("HTTP_SEC_FETCH_SITE")
        if fetch_site and fetch_site not in ("same-origin", "none"):
            raise _HTTPError(403, "cross-site relay call refused")

    def _read_body(self, environ) -> bytes:
        length = environ.get("CONTENT_LENGTH") or ""
        if not length.isdigit():
            raise _HTTPError(411, "Content-Length required")
        n = int(length)
        if n > self.cfg.max_bytes:
            # Drain moderately oversized bodies so the client receives the 413
            # instead of a connection reset; give up draining on absurd sizes.
            if n <= 4 * self.cfg.max_bytes:
                remaining = n
                stream = environ["wsgi.input"]
                while remaining > 0:
                    chunk = stream.read(min(65536, remaining))
                    if not chunk:
                        break
                    remaining -= len(chunk)
            raise _HTTPError(413, f"document larger than {self.cfg.max_bytes} bytes")
        data = environ["wsgi.input"].read(n) if n else b""
        if len(data) != n:
            raise _HTTPError(400, "truncated body")
        return data

    def _read_form(self, environ) -> Dict[str, List[str]]:
        ctype = environ.get("CONTENT_TYPE", "")
        if not ctype.startswith("application/x-www-form-urlencoded"):
            raise _HTTPError(415, "expected a form POST from Seahub")
        length = environ.get("CONTENT_LENGTH") or "0"
        if not length.isdigit() or int(length) > 16384:
            raise _HTTPError(400, "bad form length")
        raw = environ["wsgi.input"].read(int(length)).decode("utf-8", "replace")
        return urllib.parse.parse_qs(raw, keep_blank_values=False)

    @staticmethod
    def _json(status: int, payload: dict):
        return status, [("Content-Type", "application/json")], json.dumps(payload).encode()


def _public_info(info: dict) -> dict:
    """The subset of CheckFileInfo the host page needs (no user identifiers beyond display name)."""
    return {
        "name": info.get("BaseFileName"),
        "version": str(info.get("Version", "")),
        "size": info.get("Size"),
        "userCanWrite": bool(info.get("UserCanWrite", False)),
        "userName": info.get("UserFriendlyName") or "",
        "lastModified": info.get("LastModifiedTime", ""),
        "supportsLocks": bool(info.get("SupportsLocks", False)),
    }


def _guess_type(path: str) -> str:
    ext = path.rsplit(".", 1)[-1].lower() if "." in path else ""
    return {
        "html": "text/html; charset=utf-8",
        "js": "application/javascript; charset=utf-8",
        "mjs": "application/javascript; charset=utf-8",
        "wasm": "application/wasm",
        "css": "text/css; charset=utf-8",
        "json": "application/json",
        "svg": "image/svg+xml",
        "png": "image/png",
        "ico": "image/x-icon",
        "woff2": "font/woff2",
        "woff": "font/woff",
        "ttf": "font/ttf",
        "txt": "text/plain; charset=utf-8",
    }.get(ext, "application/octet-stream")
