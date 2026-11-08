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

import base64
import hashlib
import html
import http.client
import stat
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
# Seahub's WOPI file endpoints: /api2/wopi/files/<id> (13.x) or /api/v2.1/wopi/files/<id>.
_WOPI_PATH_RE = re.compile(r"^/api(?:2|/v2\.1)/wopi/files/[0-9a-f]{32,64}$")
# Trunk/wasm-bindgen content-hashed asset names: app-<16 hex>.js, app-<16 hex>_bg.wasm, fonts/<hex>/...
_HASHED_ASSET_RE = re.compile(r"(?:[-_][0-9a-f]{16}(?:_bg)?\.(?:js|wasm|ico)|/[0-9a-f]{16}/)")
_INLINE_SCRIPT_RE = re.compile(r"<script(?![^>]*\bsrc\s*=)[^>]*>(.*?)</script>", re.S | re.I)


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Never follow a redirect: urllib would turn PutFile into a GET and report success."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise urllib.error.HTTPError(req.full_url, code, f"redirect to {newurl} refused", headers, fp)


_OPENER = urllib.request.build_opener(_NoRedirect())


def _urlopen_no_redirect(req, timeout=None):
    return _OPENER.open(req, timeout=timeout)



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
    urlopen: Callable = _urlopen_no_redirect
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
            spec["extensions"] = [str(e).lower() for e in spec["extensions"]]
            for ext in spec["extensions"]:
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
        if not _WOPI_PATH_RE.match(parts.path):
            raise ValueError("WOPISrc is not a Seahub WOPI file endpoint")
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
        except (urllib.error.URLError, ConnectionError, TimeoutError, OSError, http.client.HTTPException) as exc:
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
        status, _, body = self._request(
            src,
            token,
            method="POST",
            suffix="/contents",
            headers={"X-WOPI-Override": "PUT"},
            body=data,
        )
        if status != 200:
            # 2xx other than 200 is not a WOPI PutFile success; the stored state is verified anyway.
            raise UpstreamError(status, body)
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


SIGNATURE_KNOWN = frozenset({"docx", "xlsx", "pptx", "ppsx", "odt", "ods", "odp", "pdf", "svg", "png", "jpg", "jpeg", "webp", "dxf", "drawio",
                             "doc", "xls", "ppt", "pps", "fodt", "fods", "fodp"})
_OOXML_PART = {"docx": "word/", "xlsx": "xl/", "pptx": "ppt/", "ppsx": "ppt/"}
_OLECF_MAGIC = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"
_FLAT_ODF_EXT = ("fodt", "fods", "fodp")


def _text_head(data: bytes, n: int = 65536) -> bytes:
    head = data[:n]
    for bom in (b"\xef\xbb\xbf", b"\xff\xfe", b"\xfe\xff"):
        if head.startswith(bom):
            head = head[len(bom):]
            break
    return head.lstrip()


def content_matches_extension(ext: str, data: bytes) -> bool:
    """A cheap check that the bytes are the kind of file the name says. Unknown extensions pass:
    the table is in SIGNATURE_KNOWN so a deployment can see which mappings are unguarded."""
    ext = ext.lower()
    if ext in ("docx", "xlsx", "pptx", "ppsx", "odt", "ods", "odp"):
        if not data.startswith(b"PK\x03\x04"):
            return False
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as zf:
                names = set(zf.namelist())
        except zipfile.BadZipFile:
            return False
        if ext in _OOXML_PART:
            return "[Content_Types].xml" in names and any(n.startswith(_OOXML_PART[ext]) for n in names)
        return "mimetype" in names
    if ext == "pdf":
        return b"%PDF-" in data[:1024]
    if ext == "svg":
        head = _text_head(data)
        return head.startswith(b"<") and b"<svg" in head
    if ext == "png":
        return data.startswith(b"\x89PNG\r\n\x1a\n")
    if ext in ("jpg", "jpeg"):
        return data.startswith(b"\xff\xd8\xff")
    if ext == "webp":
        return data[:4] == b"RIFF" and data[8:12] == b"WEBP"
    if ext == "dxf":
        head = _text_head(data, 256)
        return head.startswith(b"AutoCAD Binary DXF") or bool(re.match(rb"0\s*\r?\n\s*SECTION", head))
    if ext == "drawio":
        return _text_head(data).startswith(b"<")
    if ext in ("doc", "xls", "ppt", "pps"):
        # Legacy binary Office: an OLE compound file.
        return data.startswith(_OLECF_MAGIC)
    if ext in _FLAT_ODF_EXT:
        # Flat OpenDocument: a single XML stream whose root is office:document.
        head = _text_head(data)
        return head.startswith(b"<") and b"office:document" in head
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
    304: "Not Modified",
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
        headers = list(headers)
        names = {k.lower() for k, _ in headers}
        if "cache-control" not in names:
            headers.append(("Cache-Control", "no-store"))   # pages and relay answers carry a token or a document
        headers += [("X-Content-Type-Options", "nosniff"), ("Referrer-Policy", "no-referrer")]
        head_only = environ.get("REQUEST_METHOD", "GET").upper() == "HEAD"
        if hasattr(body, "read"):
            # A static file streamed from disk (editor bundles are tens of MB; never load them whole).
            size = os.fstat(body.fileno()).st_size
            headers.append(("Content-Length", str(size)))
            start_response(f"{status} {_STATUS_TEXT.get(status, 'Status')}", headers)
            if head_only:
                body.close()
                return [b""]
            wrapper = environ.get("wsgi.file_wrapper")
            return wrapper(body, 64 * 1024) if wrapper else _FileIter(body)
        headers.append(("Content-Length", str(len(body))))
        start_response(f"{status} {_STATUS_TEXT.get(status, 'Status')}", headers)
        return [b"" if head_only else body]

    @staticmethod
    def _map_upstream(exc: UpstreamError):
        if exc.status in (401, 404):
            return 401, [("Content-Type", "application/json")], b'{"error":"access token rejected by seafile (expired or revoked)"}'
        if exc.status == 409:
            return 409, [("Content-Type", "application/json")], b'{"error":"seafile reported a conflict"}'
        if 300 <= exc.status < 400:
            return 502, [("Content-Type", "application/json")], b'{"error":"seafile answered with a redirect; check BRIDGE_SEAHUB_ORIGIN (scheme and host must be the final ones)"}'
        # No upstream status in the body: it would be an oracle for whatever path the caller named.
        return 502, [("Content-Type", "application/json")], b'{"error":"seafile did not accept the request"}'

    # -- routing ------------------------------------------------------------

    def _dispatch(self, environ):
        method = environ["REQUEST_METHOD"].upper()
        path = environ.get("PATH_INFO", "/") or "/"

        if path == "/healthz" and method == "GET":
            return 200, [("Content-Type", "text/plain")], b"ok\n"
        if path == "/wopi/discovery.xml" and method == "GET":
            return 200, [("Content-Type", "application/xml; charset=utf-8")], self.discovery_xml().encode()
        if path == "/host.js" and method in ("GET", "HEAD"):
            if _etag_matches(environ, self._host_js_etag):
                return 304, [("ETag", self._host_js_etag), ("Cache-Control", "no-cache")], b""
            return 200, [("Content-Type", "application/javascript; charset=utf-8"), ("ETag", self._host_js_etag), ("Cache-Control", "no-cache")], self._host_js
        if path.startswith("/edit/"):
            if method != "POST":
                raise _HTTPError(405, "the editor entry point expects Seahub's form POST")
            return self._handle_edit(environ, path[len("/edit/"):])
        if path.startswith("/relay/"):
            if method != "POST":
                raise _HTTPError(405, "relay endpoints are POST only")
            return self._handle_relay(environ, path[len("/relay/"):])
        if path.startswith("/editors/") and method in ("GET", "HEAD"):
            return self._handle_static(environ, path[len("/editors/"):])
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
        # Seahub posts the token from its own origin into an <iframe>. A top-level POST from
        # another site (editor-CSRF: the victim typing into the attacker's file) is refused when
        # the browser says where the request came from.
        origin = environ.get("HTTP_ORIGIN", "")
        if origin and origin.rstrip("/").lower() != self.cfg.seahub_origin.lower():
            raise _HTTPError(403, "the editor entry point only accepts Seahub's form POST")
        dest = environ.get("HTTP_SEC_FETCH_DEST", "")
        if dest and dest != "iframe":
            raise _HTTPError(403, "the editor entry point only accepts an iframe form POST")

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
        fills = {"{{NONCE}}": nonce, "{{TITLE}}": html.escape(name), "{{CONFIG_JSON}}": json.dumps(config).replace("<", "\\u003c")}
        page = re.sub(r"\{\{(NONCE|TITLE|CONFIG_JSON)\}\}", lambda m: fills[m.group(0)], self._host_html)
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
        if not expected:
            raise _HTTPError(400, "X-Expected-Version is required (the version the document was opened at)")
        data = self._read_body(environ)
        if not data:
            raise _HTTPError(400, "empty document body refused")

        info = self.wopi.check_file_info(src, token)
        name = str(info.get("BaseFileName", ""))
        ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""

        # 1. Seahub's PutFile does not enforce this on the bridge path; we do. (It stays writable
        #    to anyone holding the token directly -- see README.)
        if not info.get("UserCanWrite", False):
            raise _HTTPError(403, "you do not have write permission on this file")
        # 2. No Save-As / rename through the save channel.
        if claimed_name and claimed_name != name:
            raise _HTTPError(400, "save under a different name is not allowed", {"expectedName": name})
        # 3. Content signature must match the extension (no PDF bytes into a .docx).
        if not content_matches_extension(ext, data):
            raise _HTTPError(415, f"document bytes are not a valid .{ext}")
        # 4. Optimistic concurrency: the version we opened must still be current -- unless what is
        #    stored already *is* this document (a retry after a lost answer): then the save is done.
        current = str(info.get("Version", ""))
        if current != expected:
            if self.wopi.get_file(src, token) == data:
                return self._json(200, {"version": current, "reconciled": True, "verified": True, "lastModified": info.get("LastModifiedTime", "")})
            raise _HTTPError(409, "the file changed in Seafile since it was opened", {"current": current, "expected": expected})

        try:
            self.wopi.put_file(src, token, data)
        except (TransportError, UpstreamError) as exc:
            if isinstance(exc, UpstreamError) and exc.status in (401, 403, 404):
                raise  # the token is bad; nothing to reconcile
            # Lost or failed answer (timeout, proxy 5xx, redirect): the write may still have landed.
            after = self.wopi.check_file_info(src, token)
            if self.wopi.get_file(src, token) == data:
                return self._json(200, {"version": str(after.get("Version", "")), "reconciled": True, "verified": True, "lastModified": after.get("LastModifiedTime", "")})
            if str(after.get("Version", "")) == current:
                raise  # nothing landed; the client may retry with the same expected version
            raise _HTTPError(409, "a different version landed while saving", {"current": str(after.get("Version", ""))})

        # 5. Trust nothing about the answer: read back what Seafile holds now.
        after = self.wopi.check_file_info(src, token)
        after_version = str(after.get("Version", ""))
        if self.wopi.get_file(src, token) != data:
            if after_version == current:
                raise _HTTPError(502, "seafile acknowledged the save but did not store it")
            raise _HTTPError(409, "another version landed right after the save; reopen the file", {"current": after_version})
        return self._json(200, {"version": after_version, "reconciled": False, "verified": True, "lastModified": after.get("LastModifiedTime", "")})

    # -- static editor bundles ---------------------------------------------

    def _handle_static(self, environ, rel: str):
        if not self.cfg.static_dir:
            raise _HTTPError(404, "static serving disabled")
        if "\x00" in rel:
            raise _HTTPError(404, "not found")
        root = os.path.realpath(self.cfg.static_dir)
        target = os.path.realpath(os.path.join(root, rel))
        if not (target == root or target.startswith(root + os.sep)):
            raise _HTTPError(404, "not found")
        if os.path.isdir(target):
            target = os.path.join(target, "index.html")
        try:
            st = os.stat(target)
        except OSError:
            raise _HTTPError(404, "not found")
        if not stat.S_ISREG(st.st_mode):
            raise _HTTPError(404, "not found")
        ctype = _guess_type(target)
        if ctype.startswith("text/html"):
            with open(target, "rb") as fh:
                body = fh.read()
            etag = '"' + hashlib.sha256(body).hexdigest()[:32] + '"'
            headers = [("ETag", etag), ("Cache-Control", "no-cache"), ("Content-Type", ctype), ("Content-Security-Policy", self._editor_csp(body))]
            if _etag_matches(environ, etag):
                return 304, headers, b""
            return 200, headers, body
        # Hashed assets (app-<hash>.js, app-<hash>_bg.wasm, fonts/<hash>/) never change under their
        # name; everything else (host-shim.js, manifests) is revalidated.
        etag = '"%x-%x"' % (st.st_size, int(st.st_mtime))
        if _HASHED_ASSET_RE.search("/" + rel):
            cache = "public, max-age=31536000, immutable"
        else:
            cache = "no-cache"
        headers = [("ETag", etag), ("Cache-Control", cache), ("Content-Type", ctype)]
        if _etag_matches(environ, etag):
            return 304, headers, b""
        return 200, headers, open(target, "rb")

    def _editor_csp(self, page: bytes) -> str:
        """The editor page is a same-origin iframe of the host page: it can read the host DOM, so the
        real control is what it may load and where it may send. Inline module scripts (Trunk's
        bootstrap) are allowed by hash, everything else must be same-origin; no network beyond it."""
        hashes = " ".join(
            "'sha256-" + base64.b64encode(hashlib.sha256(m.group(1).encode("utf-8")).digest()).decode() + "'"
            for m in _INLINE_SCRIPT_RE.finditer(page.decode("utf-8", "replace"))
        )
        return (
            "default-src 'none'; "
            f"script-src 'self' 'wasm-unsafe-eval'{(' ' + hashes) if hashes else ''}; "
            + "connect-src 'self'; img-src 'self' data: blob:; style-src 'self' 'unsafe-inline'; "
            "font-src 'self' data:; worker-src 'self' blob:; media-src 'self' blob: data:; "
            f"frame-ancestors 'self' {self.cfg.seahub_origin}; base-uri 'none'; form-action 'none'"
        )

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


def _etag_matches(environ, etag: str) -> bool:
    inm = environ.get("HTTP_IF_NONE_MATCH", "")
    return bool(inm) and etag in [t.strip() for t in inm.split(",")]


class _FileIter:
    def __init__(self, fh, chunk=64 * 1024):
        self.fh, self.chunk = fh, chunk

    def __iter__(self):
        return self

    def __next__(self):
        data = self.fh.read(self.chunk)
        if not data:
            self.fh.close()
            raise StopIteration
        return data

    def close(self):
        self.fh.close()


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
