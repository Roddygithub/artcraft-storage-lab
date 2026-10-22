"""The ArtCraft gateway: a Seafile host page for the Craft web editors.

It is the piece between Seafile and a Craft web app:

    Seafile  --(form POST, access_token)-->  this service
    this service  --(file-info / file-content)-->  Seafile
    this service  --(static files)-->  the Craft web app (same origin)
    browser  <--(postMessage)-->  the Craft web app (in an iframe)

The service holds the Seafile credential. The browser never does.
"""

import json
import mimetypes
import os
import posixpath
import urllib.parse
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

# The Craft app names, as the protocol uses them: "wordcraft:open".
APP_ALIASES = {
    "wordcraft": "wordcraft",
    "gridcraft": "gridcraft",
    "deckcraft": "deckcraft",
    "pdfcraft": "pdfcraft",
    "vectorcraft": "vectorcraft",
}


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

        return self._make_session(repo_id, path, name, info.get("username", ""), access_token)

    def open_session_direct(self, repo_id, path, user=None):
        """Open a document using the gateway's own Seafile credential.

        This is the second entry point: it does not need Seafile's
        third-party-editor hook. It is what the integration tests drive, and it
        is the path a future "Open with Craft" entry would use.
        """
        try:
            detail = self.seafile.file_detail(repo_id, path)
        except SeafileError as exc:
            if exc.status == 404:
                return None, "the file does not exist"
            return None, f"cannot read the file: {exc}"
        name = path.rsplit("/", 1)[-1]
        return self._make_session(repo_id, path, name, user or "", None, detail=detail)

    def _make_session(self, repo_id, path, name, user, access_token, detail=None):
        target = self.app_for(name)
        if not target:
            return None, f"no Craft editor is registered for '{name}'"
        app = target["app"]

        # The real permission, not the hook's placeholder.
        can_edit = False
        if detail is None:
            try:
                detail = self.seafile.file_detail(repo_id, path)
            except SeafileError:
                detail = {}
        can_edit = detail.get("permission") in EDITABLE_PERMISSIONS

        file_id = detail.get("id") or ""
        session = self.sessions.create(
            repo_id=repo_id, path=path, name=name, file_id=file_id,
            user=user, can_edit=can_edit,
            access_token=access_token, app=app,
        )
        return session, None

    def document(self, session):
        """The bytes of the document being edited."""
        if session.access_token:
            data = self.seafile.thirdparty_file_content(session.access_token)
        else:
            data = self.seafile.download(session.repo_id, session.path)
        if len(data) > self.max_bytes:
            raise SeafileError(f"the document is larger than the {self.max_bytes} byte limit")
        return data

    def save(self, session, data):
        """Write the bytes back. Returns (result_dict, http_status).

        The conflict check below is a **read-then-write**, not an atomic
        compare-and-swap: Seafile's update API has no such primitive
        (`docs/reviews/GR-008/SEAFILE-CONCURRENCY-PRIMITIVES.md` §1.3-§1.4).
        A write that lands in the narrow window between the check and the
        update therefore wins over a concurrent one. The window is one API
        round trip; closing it would need a patch to the file server, which is
        upstream work (GR-014).
        """
        if not session.can_edit:
            return {"ok": False, "error": "you do not have permission to edit this file"}, 403
        if len(data) > self.max_bytes:
            return {"ok": False, "error": "the document is larger than the limit"}, 413

        # The conflict check: the content id must still be the one we opened.
        try:
            detail = self.seafile.file_detail(session.repo_id, session.path)
        except SeafileError as exc:
            if exc.status == 404:
                return {"ok": False, "error": "the file no longer exists"}, 404
            return {"ok": False, "error": f"cannot read the file: {exc}"}, 502

        current = detail.get("id") or ""
        if not current:
            return {"ok": False, "error": "the file no longer exists"}, 404
        if current != session.file_id:
            return {
                "ok": False,
                "error": "this file was modified by someone else while you were editing it; "
                         "your changes were not saved",
                "conflict": True,
                "expected": session.file_id,
                "current": current,
            }, 409
        permission = detail.get("permission")
        if permission not in EDITABLE_PERMISSIONS:
            return {"ok": False, "error": "you no longer have permission to edit this file"}, 403

        try:
            new_id = self.seafile.update_file(session.repo_id, session.path, data)
        except SeafileError as exc:
            return {"ok": False, "error": f"Seafile refused the write: {exc}"}, 502

        session.file_id = new_id or session.file_id
        session.unsaved = False
        return {
            "ok": True,
            "file_id": session.file_id,
            "version": detail.get("last_modified"),
            "message": "saved",
        }, 200


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
                return self._json(502, {"ok": False, "error": str(exc)})
            return self._send(200, data, "application/octet-stream",
                              {"Cache-Control": "no-store"})

        if path.startswith("/artcraft/"):
            return self._serve_static(path)

        return self._json(404, {"ok": False, "error": "not found"})

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path
        gateway = self.server.gateway

        if path == "/open/":
            return self._open(gateway)

        if path.startswith("/session/") and path.endswith("/save"):
            sid = path.split("/")[2]
            session = gateway.sessions.get(sid)
            if session is None:
                return self._json(404, {"ok": False, "error": "unknown or expired session"})
            data = self._read_body(limit=gateway.max_bytes)
            if data is None:
                return self._json(413, {"ok": False, "error": "the document is larger than the limit"})
            result, status = gateway.save(session, data)
            return self._json(status, result)

        if path.startswith("/session/") and path.endswith("/dirty"):
            sid = path.split("/")[2]
            session = gateway.sessions.get(sid)
            if session is None:
                return self._json(404, {"ok": False, "error": "unknown or expired session"})
            body = self._read_body(limit=64) or b""
            session.unsaved = body.strip().lower() in (b"true", b"1")
            return self._json(200, {"ok": True, "unsaved": session.unsaved})

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
        elif repo_id and path:
            session, error = gateway.open_session_direct(repo_id, path)
        else:
            return self._json(400, {"ok": False, "error": "no access_token and no repo_id/path"})

        if session is None:
            return self._json(400, {"ok": False, "error": error})

        if as_json:
            return self._json(200, {"ok": True, **session.as_dict()})

        target = gateway.dispatch[session.name.rsplit(".", 1)[-1].lower()]
        page = hostpage.render(
            sid=session.sid,
            app=APP_ALIASES.get(target["app"], target["app"]),
            app_url=target["url"],
            file_name=session.name,
            can_edit=session.can_edit,
        )
        return self._send(200, page, "text/html; charset=utf-8", {"Cache-Control": "no-store"})

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
