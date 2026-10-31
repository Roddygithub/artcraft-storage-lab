"""A fake of Seahub's WOPI host (``seahub/wopi/views.py``), faithful to what matters.

Reproduced semantics (verified against Seahub master / 12.0 / 13.0 source):

* token = opaque id looked up in a cache; unknown token -> 404 (Seahub logs
  "Get wopi cache value failed" and returns 404); missing token -> 401.
* CheckFileInfo returns ``Version`` = object id of the current content,
  ``UserCanWrite``/``SupportsUpdate``/``ReadOnly`` from the cached ``can_edit``,
  ``SupportsLocks``/``SupportsGetLock`` = True, ``LastModifiedTime``.
* LOCK / UNLOCK / REFRESH_LOCK / GET_LOCK with ``X-WOPI-Lock``; mismatch -> 409
  with ``X-WOPI-Lock`` = current lock.
* GetFile returns the bytes.
* **PutFile never checks ``can_edit`` nor the lock nor any version header** —
  this is Seahub's actual behaviour and the reason the bridge must enforce
  these itself.  Identical content produces no new version (fileserver
  ``update-api`` behaviour).  Writes are attributed to the token's user.
"""

from __future__ import annotations

import hashlib
import json
import threading
import time
from wsgiref.simple_server import WSGIRequestHandler, make_server


class _QuietHandler(WSGIRequestHandler):
    def log_message(self, *args):  # noqa: D401 - silence
        pass


class FakeSeahub:
    WOPI_PREFIX = "/api/v2.1/wopi/files/"

    def __init__(self):
        self.files = {}      # file_id -> dict(name, content, version, mtime, commits, last_modifier)
        self.tokens = {}     # token -> dict(file_id, user, can_edit, expires)
        self.locks = {}      # file_id -> lock id
        self.put_log = []    # (file_id, user, len)
        self.lock = threading.Lock()
        self._server = None
        self._thread = None
        self.origin = None

    # -- test helpers --------------------------------------------------------

    def add_file(self, file_id: str, name: str, content: bytes) -> None:
        with self.lock:
            self.files[file_id] = {
                "name": name,
                "content": content,
                "version": _obj_id(content),
                "mtime": time.time(),
                "commits": 1,
                "last_modifier": "seed",
            }

    def mint_token(self, file_id: str, user: str, can_edit: bool, ttl: float = 3600) -> str:
        token = hashlib.sha256(f"{file_id}{user}{can_edit}{time.time_ns()}".encode()).hexdigest()
        with self.lock:
            self.tokens[token] = {"file_id": file_id, "user": user, "can_edit": can_edit, "expires": time.time() + ttl}
        return token

    def revoke(self, token: str) -> None:
        with self.lock:
            self.tokens.pop(token, None)

    def external_write(self, file_id: str, content: bytes, user: str = "someone-else") -> str:
        """Simulate another writer (sync client, WebDAV, another editor)."""
        return self._write(file_id, content, user)

    def wopi_src(self, file_id: str) -> str:
        return f"{self.origin}{self.WOPI_PREFIX}{file_id}"

    def start(self) -> str:
        self._server = make_server("127.0.0.1", 0, self, handler_class=_QuietHandler)
        self.origin = f"http://127.0.0.1:{self._server.server_port}"
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()
        return self.origin

    def stop(self) -> None:
        if self._server:
            self._server.shutdown()
            self._server.server_close()

    # -- internals -----------------------------------------------------------

    def _write(self, file_id: str, content: bytes, user: str) -> str:
        with self.lock:
            f = self.files[file_id]
            new_id = _obj_id(content)
            if new_id == f["version"]:
                return new_id  # fileserver: identical content -> no new commit
            f["content"] = content
            f["version"] = new_id
            f["mtime"] = time.time()
            f["commits"] += 1
            f["last_modifier"] = user
            return new_id

    def _auth(self, environ):
        qs = dict(p.split("=", 1) for p in environ.get("QUERY_STRING", "").split("&") if "=" in p)
        token = qs.get("access_token")
        if not token:
            return None, 401
        with self.lock:
            rec = self.tokens.get(token)
            if rec and rec["expires"] < time.time():
                rec = None
        if not rec:
            return None, 404
        return rec, 200

    def __call__(self, environ, start_response):
        path = environ.get("PATH_INFO", "")
        method = environ["REQUEST_METHOD"]
        if not path.startswith(self.WOPI_PREFIX):
            return _respond(start_response, 404, b"not found")
        rest = path[len(self.WOPI_PREFIX):]
        contents = rest.endswith("/contents")
        file_id = rest[:-len("/contents")] if contents else rest

        rec, status = self._auth(environ)
        if status != 200:
            return _respond(start_response, status, b"")
        if rec["file_id"] != file_id:
            return _respond(start_response, 404, b"")
        with self.lock:
            f = dict(self.files.get(file_id) or {})
        if not f:
            return _respond(start_response, 404, b"")

        if not contents and method == "GET":
            info = {
                "BaseFileName": f["name"],
                "Size": len(f["content"]),
                "OwnerId": "owner",
                "UserId": rec["user"],
                "UserFriendlyName": rec["user"],
                "Version": f["version"],
                "LastModifiedTime": time.strftime("%Y-%m-%dT%H:%M:%S.000000Z", time.gmtime(f["mtime"])),
                "UserCanWrite": rec["can_edit"],
                "SupportsUpdate": rec["can_edit"],
                "ReadOnly": not rec["can_edit"],
                "SupportsLocks": True,
                "SupportsGetLock": True,
                "UserCanNotWriteRelative": True,
                "PostMessageOrigin": self.origin,
            }
            return _respond(start_response, 200, json.dumps(info).encode(), "application/json")

        if not contents and method == "POST":
            op = environ.get("HTTP_X_WOPI_OVERRIDE", "")
            lock_id = environ.get("HTTP_X_WOPI_LOCK", "")
            with self.lock:
                current = self.locks.get(file_id, "")
                if op == "LOCK":
                    if current and current != lock_id:
                        return _respond(start_response, 409, b"", extra=[("X-WOPI-Lock", current)])
                    self.locks[file_id] = lock_id
                    return _respond(start_response, 200, b"")
                if op in ("REFRESH_LOCK", "UNLOCK"):
                    if current != lock_id:
                        return _respond(start_response, 409, b"", extra=[("X-WOPI-Lock", current)])
                    if op == "UNLOCK":
                        self.locks.pop(file_id, None)
                    return _respond(start_response, 200, b"")
                if op == "GET_LOCK":
                    return _respond(start_response, 200, b"", extra=[("X-WOPI-Lock", current)])
            return _respond(start_response, 501, b"")

        if contents and method == "GET":
            return _respond(start_response, 200, f["content"], "application/octet-stream")

        if contents and method == "POST":
            # Seahub: no can_edit check, no lock check, no version check.
            n = int(environ.get("CONTENT_LENGTH") or 0)
            data = environ["wsgi.input"].read(n)
            self._write(file_id, data, rec["user"])
            with self.lock:
                self.put_log.append((file_id, rec["user"], len(data)))
                mtime = self.files[file_id]["mtime"]
            body = json.dumps({"LastModifiedTime": time.strftime("%Y-%m-%dT%H:%M:%S.000000Z", time.gmtime(mtime))}).encode()
            return _respond(start_response, 200, body, "application/json")

        return _respond(start_response, 405, b"")


def _obj_id(content: bytes) -> str:
    return hashlib.sha1(content).hexdigest()


def _respond(start_response, status, body, ctype="text/plain", extra=None):
    reason = {200: "OK", 401: "Unauthorized", 404: "Not Found", 405: "Method Not Allowed", 409: "Conflict", 501: "Not Implemented"}.get(status, "Status")
    headers = [("Content-Type", ctype), ("Content-Length", str(len(body)))] + list(extra or [])
    start_response(f"{status} {reason}", headers)
    return [body]
