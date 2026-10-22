"""Editing sessions for the ArtCraft gateway.

A session is what the browser holds: an opaque id that the server maps to
(repo, path, content id, user, permissions). It is deliberately *not* a bearer
token for Seafile: it authorises one document, for one user, for a short time.

In-memory on purpose. A restart drops the sessions, which is the safe default
for a prototype and matches the "short-lived session" requirement: the
browser's editing session dies with the service.
"""

import secrets
import threading
import time


class Session:
    __slots__ = ("sid", "repo_id", "path", "name", "file_id", "user", "can_edit",
                 "created", "last_seen", "access_token", "app", "unsaved")

    def __init__(self, sid, repo_id, path, name, file_id, user, can_edit,
                 access_token, app):
        self.sid = sid
        self.repo_id = repo_id
        self.path = path
        self.name = name
        self.file_id = file_id
        self.user = user
        self.can_edit = can_edit
        self.access_token = access_token
        self.app = app
        self.created = time.time()
        self.last_seen = self.created
        self.unsaved = False   # the Craft app holds bytes we have not persisted

    def touch(self):
        self.last_seen = time.time()

    def age(self):
        return time.time() - self.created

    def idle(self):
        return time.time() - self.last_seen

    def as_dict(self):
        return {
            "sid": self.sid,
            "repo_id": self.repo_id,
            "path": self.path,
            "name": self.name,
            "file_id": self.file_id,
            "user": self.user,
            "can_edit": self.can_edit,
            "app": self.app,
            "unsaved": self.unsaved,
        }


class SessionStore:
    def __init__(self, ttl=1800, idle_ttl=900, max_sessions=256):
        self.ttl = ttl
        self.idle_ttl = idle_ttl
        self.max_sessions = max_sessions
        self._sessions = {}
        self._lock = threading.Lock()

    def create(self, **kwargs):
        sid = secrets.token_urlsafe(24)
        session = Session(sid=sid, **kwargs)
        with self._lock:
            self._prune_locked()
            self._sessions[sid] = session
        return session

    def get(self, sid):
        with self._lock:
            session = self._sessions.get(sid)
            if session is None:
                return None
            if session.age() > self.ttl or session.idle() > self.idle_ttl:
                del self._sessions[sid]
                return None
            session.touch()
            return session

    def drop(self, sid):
        with self._lock:
            return self._sessions.pop(sid, None)

    def _prune_locked(self):
        now = time.time()
        for sid, session in list(self._sessions.items()):
            if now - session.created > self.ttl or now - session.last_seen > self.idle_ttl:
                del self._sessions[sid]
        while len(self._sessions) > self.max_sessions:
            oldest = min(self._sessions.values(), key=lambda s: s.last_seen)
            del self._sessions[oldest.sid]
