"""The ArtCraft gateway: a Seafile host page for the Craft web editors.

It is the piece between Seafile and a Craft web app:

    Seafile  --(form POST, access_token)-->  this service
    this service  --(file-info / file-content)-->  Seafile
    this service  --(static files)-->  the Craft web app (same origin)
    browser  <--(postMessage)-->  the Craft web app (in an iframe)

The service holds the Seafile credential. The browser never does.
"""

import base64
import hashlib
import io
import ipaddress
import json
import mimetypes
import os
import posixpath
import re
import secrets
import struct
import urllib.parse
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from . import hostpage
from .sessions import SessionStore
from .seafile import Seafile, SeafileError

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
STATIC_ROOT = os.path.join(ROOT, "static")
CONFIG_PATH = os.path.join(ROOT, "config", "dispatch.json")

# Permissions that allow writing a file back.
EDITABLE_PERMISSIONS = ("rw", "cloud-edit", "preview-edit")
MAX_CONTENT_TYPES_XML_BYTES = 1024 * 1024

# The Craft app names, as the protocol uses them: "wordcraft:open".
APP_ALIASES = {
    "wordcraft": "wordcraft",
    "gridcraft": "gridcraft",
    "deckcraft": "deckcraft",
    "pdfcraft": "pdfcraft",
    "vectorcraft": "vectorcraft",
}


def payload_matches_name(name, data):
    """Reject a known export format before it can replace the original."""
    ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
    if ext == "pdf":
        return data.startswith(b"%PDF-")
    if ext == "svg":
        text = data[:4096].decode("utf-8", "ignore").lower()
        return "<svg" in text
    if ext == "scraftz":
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as archive:
                sessions = [item for item in archive.infolist()
                            if item.filename.endswith(".scraft")
                            and "/" not in item.filename
                            and "\\" not in item.filename]
            return len(sessions) == 1 and sessions[0].file_size > 0
        except (OSError, RuntimeError, zipfile.BadZipFile):
            return False
    if ext == "pcraft":
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as archive:
                manifests = [item for item in archive.infolist()
                             if item.filename == "manifest.json"]
            # ponytail: metadata-only ceiling; semantic manifest validation
            # stays in PhotoCraft so the gateway never decompresses payloads.
            return len(manifests) == 1 and manifests[0].file_size > 0
        except (OSError, RuntimeError, ValueError, EOFError,
                zipfile.BadZipFile, struct.error):
            return False
    if ext in {"docx", "xlsx", "pptx"}:
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as archive:
                entry = archive.getinfo("[Content_Types].xml")
                if entry.file_size > MAX_CONTENT_TYPES_XML_BYTES:
                    return False
                with archive.open(entry) as stream:
                    raw_types = stream.read(MAX_CONTENT_TYPES_XML_BYTES + 1)
                if len(raw_types) > MAX_CONTENT_TYPES_XML_BYTES:
                    return False
                types = raw_types.decode("utf-8", "ignore")
        except (KeyError, OSError, RuntimeError, zipfile.BadZipFile):
            return False
        expected = {
            "docx": "wordprocessingml.document",
            "xlsx": "spreadsheetml.sheet",
            "pptx": "presentationml.presentation",
        }[ext]
        return expected in types
    return True


def load_dispatch(path=CONFIG_PATH):
    """extension -> {app, url}. The extension keys carry no dot."""
    with open(path, encoding="utf-8") as handle:
        raw = json.load(handle)
    return {k.lower().lstrip("."): v for k, v in raw.items()}


class Gateway:
    def __init__(self, seafile, dispatch, static_root=STATIC_ROOT, max_bytes=None):
        self.seafile = seafile
        self.dispatch = dispatch
        self.static_root = static_root
        self.max_bytes = max_bytes or int(
            os.environ.get("ARTCRAFT_MAX_BYTES", 50 * 1024 * 1024))
        self.sessions = SessionStore()

    def app_for(self, filename):
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        return self.dispatch.get(ext)

    def open_session(self, access_token):
        """Called when Seafile posts the access token to our host page.

        Returns (session, None) or (None, error_message).
        """
        try:
            info = self.seafile.thirdparty_file_info(access_token)
        except SeafileError as exc:
            return None, f"Seafile refused the access token: {exc}"

        repo_id = info.get("repo_id")
        path = info.get("file_path")
        name = info.get("file_name") or (path or "").rsplit("/", 1)[-1]
        if not repo_id or not path:
            return None, "Seafile did not say which file to open"

        return self._make_session(repo_id, path, name, info.get("username", ""),
                                  access_token, detail=info)

    def open_session_direct(self, repo_id, path, user=None):
        """Disabled: a repo/path request has no editing-user identity."""
        return None, "direct repo/path opening is disabled; use Seafile's access_token"

    def _make_session(self, repo_id, path, name, user, access_token, detail=None):
        target = self.app_for(name)
        if not target:
            return None, f"no Craft editor is registered for '{name}'"
        app = target["app"]

        if detail is None:
            try:
                detail = self.seafile.user_file_detail(repo_id, path, user, access_token)
            except (AttributeError, SeafileError):
                detail = {}
        can_edit = detail.get("can_edit")
        if not isinstance(can_edit, bool):
            can_edit = detail.get("permission") in EDITABLE_PERMISSIONS

        file_id = detail.get("file_id") or detail.get("id") or ""
        head_commit_id = detail.get("head_commit_id") or ""
        session = self.sessions.create(
            repo_id=repo_id, path=path, name=name, file_id=file_id,
            user=user, can_edit=can_edit,
            user_authorized=can_edit,
            access_token=access_token, app=app,
            head_commit_id=head_commit_id,
        )
        return session, None

    def document(self, session):
        """The bytes of the document being edited."""
        with session.lock:
            return self._document_locked(session)

    def _document_locked(self, session):
        if session.access_token:
            data = self.seafile.thirdparty_file_content(
                session.access_token, session.file_id, max_bytes=self.max_bytes)
        else:
            data = self.seafile.download(session.repo_id, session.path)
        if len(data) > self.max_bytes:
            raise SeafileError(f"the document is larger than the {self.max_bytes} byte limit")
        return data

    def save(self, session, data, name=None):
        """Write the bytes back. Returns (result_dict, http_status).

        Writes require user-bound authorization and an upstream atomic
        compare-and-swap primitive. Stock Seafile has neither, so this gateway
        fails closed until an upstream endpoint supplies both; a gateway lock
        cannot protect against external writers.
        """
        with session.lock:
            return self._save_locked(session, data, name)

    def _save_locked(self, session, data, name):
        if not session.can_edit or not session.user_authorized:
            return {"ok": False, "error": "you do not have permission to edit this file"}, 403
        if name is not None and name != session.name:
            return {"ok": False, "error": "Save As and exports cannot replace the original file"}, 400
        if len(data) > self.max_bytes:
            return {"ok": False, "error": "the document is larger than the limit"}, 413
        if not payload_matches_name(session.name, data):
            return {"ok": False, "error": "saved content does not match the original document type"}, 400

        digest = hashlib.sha256(data).digest()
        receipt = session.last_save

        # Seahub re-authorizes the user and the fileserver atomically checks the
        # opened file id and repository head before committing the new version.
        try:
            if receipt is not None and receipt[:2] == (digest, len(data)):
                # A receipt acknowledges an already committed save, but never
                # substitutes for current user-bound authorization or freshness.
                detail = self.seafile.user_file_detail(
                    session.repo_id, session.path, session.user, session.access_token)
                can_edit = detail.get("can_edit")
                if not isinstance(can_edit, bool):
                    can_edit = detail.get("permission") in EDITABLE_PERMISSIONS
                if not can_edit:
                    raise SeafileError("permission revoked", status=403)
                if (detail.get("id") != receipt[2]["file_id"]
                        or detail.get("head_commit_id") != receipt[2]["version"]):
                    raise SeafileError("conflict", status=409)
                return dict(receipt[2]), 200
            saved = self.seafile.thirdparty_file_save(
                session.access_token, session.file_id, session.head_commit_id,
                session.name, data)
        except AttributeError:
            return {"ok": False, "error": "user-bound Seafile save is unavailable"}, 503
        except SeafileError as exc:
            if exc.status == 404:
                return {"ok": False, "error": "the file no longer exists"}, 404
            if exc.status in (401, 403):
                return {"ok": False, "error": "you no longer have permission to edit this file"}, 403
            if exc.status == 409:
                return {
                    "ok": False,
                    "error": "this file or library changed while you were editing it; "
                             "your changes were not saved",
                    "conflict": True,
                }, 409
            # Upstream errors can echo capability-bearing URLs or document
            # content. Keep details server-side; the browser gets no response
            # body from Seafile.
            return {"ok": False, "error": "Seafile could not confirm the save"}, 502
        session.file_id = saved["file_id"]
        session.head_commit_id = saved["head_commit_id"]
        session.unsaved = False
        result = {
            "ok": True,
            "file_id": session.file_id,
            "version": session.head_commit_id,
            "message": "saved",
        }
        session.last_save = (digest, len(data), result)
        return dict(result), 200


class Handler(BaseHTTPRequestHandler):
    server_version = "artcraft-gateway/0.1"
    protocol_version = "HTTP/1.1"

    # -- helpers ----------------------------------------------------------

    def log_message(self, fmt, *args):
        if os.environ.get("ARTCRAFT_GATEWAY_VERBOSE"):
            super().log_message(fmt, *args)

    def _send(self, status, body=b"", content_type="text/plain; charset=utf-8", headers=None):
        if isinstance(body, str):
            body = body.encode()
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        for key, value in (headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _json(self, status, payload):
        self._send(status, json.dumps(payload), "application/json; charset=utf-8")

    def _read_body(self, limit=None):
        length = int(self.headers.get("Content-Length") or 0)
        if limit and length > limit:
            return None
        return self.rfile.read(length) if length else b""

    # -- routes -----------------------------------------------------------

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        gateway = self.server.gateway

        if path == "/healthz":
            return self._json(200, {"ok": True})

        if path.startswith("/session/") and path.endswith("/document"):
            sid = path.split("/")[2]
            session = gateway.sessions.get(sid)
            if session is None:
                return self._json(404, {"ok": False, "error": "unknown or expired session"})
            try:
                data = gateway.document(session)
            except SeafileError as exc:
                status = exc.status if exc.status in (403, 404, 409) else 502
                return self._json(status, {"ok": False, "error": str(exc),
                                          "conflict": status == 409})
            return self._send(200, data, "application/octet-stream",
                              {"Cache-Control": "no-store"})

        if path.startswith("/artcraft/"):
            return self._serve_static(path)

        return self._json(404, {"ok": False, "error": "not found"})

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path
        gateway = self.server.gateway
        same_origin = self._same_origin()
        # Seafile's hidden form navigates to /open/ across origins. Allow only
        # that one capability-bearing handoff from the configured Seafile
        # origin; every browser API POST remains same-origin with the gateway.
        if not same_origin and not (path == "/open/" and self._from_seafile_origin()):
            return self._json(403, {"ok": False, "error": "same-origin request required"})

        if path == "/open/":
            return self._open(gateway)

        if path.startswith("/session/") and path.endswith("/save"):
            sid = path.split("/")[2]
            session = gateway.sessions.get(sid)
            if session is None:
                return self._json(404, {
                    "ok": False,
                    "error": "the editing session expired or is unavailable; "
                             "return to Seafile and reopen the file",
                })
            data = self._read_body(limit=gateway.max_bytes)
            if data is None:
                return self._json(413, {"ok": False, "error": "the document is larger than the limit"})
            name = self.headers.get("X-ArtCraft-Filename")
            result, status = gateway.save(session, data, name=name)
            return self._json(status, result)

        if path.startswith("/session/") and path.endswith("/dirty"):
            sid = path.split("/")[2]
            session = gateway.sessions.get(sid)
            if session is None:
                return self._json(404, {"ok": False, "error": "unknown or expired session"})
            body = self._read_body(limit=64) or b""
            with session.lock:
                session.unsaved = body.strip().lower() in (b"true", b"1")
                result = {"ok": True, "unsaved": session.unsaved}
            return self._json(200, result)

        return self._json(404, {"ok": False, "error": "not found"})

    def _open(self, gateway):
        parsed = urllib.parse.urlparse(self.path)
        body = self._read_body(limit=64 * 1024)
        fields = urllib.parse.parse_qs(body.decode("utf-8", "replace"))
        access_token = (fields.get("access_token") or [""])[0]
        repo_id = (fields.get("repo_id") or [""])[0]
        path = (fields.get("path") or [""])[0]
        # A caller that wants the session as data rather than as a page.
        as_json = "format=json" in parsed.query or \
            "application/json" in (self.headers.get("Accept") or "")

        if access_token:
            session, error = gateway.open_session(access_token)
        else:
            return self._json(401, {"ok": False, "error": "a Seafile access_token is required"})

        if session is None:
            return self._json(400, {"ok": False, "error": error})

        if as_json:
            return self._json(200, {"ok": True, **session.as_dict()})

        target = gateway.dispatch[session.name.rsplit(".", 1)[-1].lower()]
        csp_nonce = base64.b64encode(secrets.token_bytes(18)).decode("ascii")
        page = hostpage.render(
            sid=session.sid,
            app=APP_ALIASES.get(target["app"], target["app"]),
            app_url=target["url"],
            file_name=session.name,
            can_edit=session.can_edit,
            csp_nonce=csp_nonce,
        )
        frame_ancestors = self._configured_seafile_origin() or "'none'"
        csp = "; ".join((
            "default-src 'none'",
            "base-uri 'none'",
            "object-src 'none'",
            "frame-ancestors " + frame_ancestors,
            "form-action 'none'",
            "frame-src 'self'",
            "connect-src 'self'",
            "img-src 'self' data: blob:",
            "script-src 'nonce-" + csp_nonce + "'",
            "style-src 'nonce-" + csp_nonce + "'",
        ))
        return self._send(200, page, "text/html; charset=utf-8", {
            "Cache-Control": "no-store",
            "Content-Security-Policy": csp,
        })

    def _same_origin(self):
        origin = urllib.parse.urlsplit(self.headers.get("Origin") or "")
        request_host = self.headers.get("Host", "").lower()
        forwarded_proto = self.headers.get("X-Forwarded-Proto", "")
        request_scheme = forwarded_proto.split(",", 1)[0].strip().lower() or origin.scheme.lower()
        return bool(
            origin.scheme.lower() == request_scheme
            and origin.netloc.lower() == request_host
            and request_host
        )

    @staticmethod
    def _normalize_origin(value):
        if (
            not value or "?" in value or "#" in value
            or any(ord(char) <= 0x20 or ord(char) == 0x7f for char in value)
        ):
            return None
        try:
            parsed = urllib.parse.urlsplit(value)
            port = parsed.port
        except ValueError:
            return None
        if not (
            parsed.scheme.lower() in ("http", "https") and parsed.hostname
            and parsed.netloc and not parsed.netloc.endswith(":")
            and "@" not in parsed.netloc
            and not parsed.path and not parsed.query and not parsed.fragment
            and not parsed.username and not parsed.password
        ):
            return None
        try:
            host = parsed.hostname.encode("idna").decode("ascii").lower()
        except UnicodeError:
            return None
        if "%" in host:  # no percent-encoded or scoped host syntax
            return None
        if ":" in host:  # urlsplit removes IPv6 brackets from .hostname
            try:
                host = f"[{ipaddress.IPv6Address(host).compressed}]"
            except ValueError:
                return None
        elif re.fullmatch(r"[0-9.]+", host):
            try:
                host = str(ipaddress.IPv4Address(host))
            except ValueError:
                return None
        elif not re.fullmatch(
                r"(?=.{1,253}\.?$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)"
                r"(?:\.(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?))*\.?", host):
            return None

        scheme = parsed.scheme.lower()
        if port == (443 if scheme == "https" else 80):
            port = None
        return f"{scheme}://{host}" + (f":{port}" if port is not None else "")

    def _configured_seafile_origin(self):
        return self._normalize_origin(os.environ.get("ARTCRAFT_SEAFILE_ORIGIN", ""))

    def _from_seafile_origin(self):
        allowed = self._configured_seafile_origin()
        origin = self._normalize_origin(self.headers.get("Origin") or "")
        return bool(allowed and origin == allowed)

    def _serve_static(self, path):
        gateway = self.server.gateway
        rel = posixpath.normpath(path[len("/artcraft/"):]).lstrip("/")
        if rel.startswith("..") or os.path.isabs(rel):
            return self._json(400, {"ok": False, "error": "bad path"})
        target = os.path.join(gateway.static_root, rel)
        # realpath, not abspath: a symlink inside the static root must not lead
        # out of it. Both the file we serve and the directory it is in are
        # checked against the real root.
        real_root = os.path.realpath(gateway.static_root)
        target = os.path.realpath(target)
        if target != real_root and not target.startswith(real_root + os.sep):
            return self._json(400, {"ok": False, "error": "bad path"})
        if os.path.isdir(target):
            # "/artcraft/<app>/" and "/artcraft/<app>" both serve the app's index.
            index = os.path.join(target, "index.html")
            target = index if os.path.isfile(index) else ""
        if not target or not os.path.isfile(target):
            return self._json(404, {"ok": False, "error": "not found"})

        ctype, _ = mimetypes.guess_type(target)
        if target.endswith(".wasm"):
            ctype = "application/wasm"
        elif target.endswith(".js"):
            ctype = "text/javascript"
        headers = {}
        if target.endswith(".html"):
            headers["Cache-Control"] = "no-cache"
        else:
            headers["Cache-Control"] = "public, max-age=31536000, immutable"
        with open(target, "rb") as handle:
            body = handle.read()
        return self._send(200, body, ctype or "application/octet-stream", headers)


def serve(host="127.0.0.1", port=8777, seafile=None, dispatch_path=CONFIG_PATH):
    seafile = seafile or Seafile.from_env()
    dispatch = load_dispatch(dispatch_path)
    gateway = Gateway(seafile, dispatch)
    httpd = ThreadingHTTPServer((host, port), Handler)
    httpd.gateway = gateway
    print(f"artcraft gateway on http://{host}:{port}/  "
          f"(seafile {seafile.base_url}, apps: {', '.join(sorted(dispatch))})")
    httpd.serve_forever()
