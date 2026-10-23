"""Minimal Seafile client for the ArtCraft gateway.

Only the calls the gateway needs. No dependency beyond the standard library.

Credentials come from the environment, never from a file in the repository:

    ARTCRAFT_SEAFILE_URL     e.g. https://seafile.example.org
    ARTCRAFT_SEAFILE_TOKEN   optional account token for read-only diagnostics
"""

import json
import mimetypes
import os
import urllib.error
import urllib.parse
import urllib.request
import uuid


class SeafileError(Exception):
    """An error returned by Seafile, with the HTTP status when there is one."""

    def __init__(self, message, status=None, body=None):
        super().__init__(message)
        self.status = status
        self.body = body


class Seafile:
    _credential_query_keys = {"access_token", "token", "jwt", "signature", "password"}

    def __init__(self, base_url, token, timeout=30):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout

    # -- plumbing ---------------------------------------------------------

    def _request(self, url, method="GET", headers=None, data=None, raw=False, auth=True,
                 response_limit=None):
        """Perform a request.

        `auth=False` sends no credential. The file server's own URLs already carry
        a short-lived token in the query string, so the account token must not be
        sent to them: it would widen the blast radius of a leak for no gain.
        """
        headers = dict(headers or {})
        if auth and self.token and "Authorization" not in headers:
            headers["Authorization"] = "Token " + self.token
        req = urllib.request.Request(url, method=method, data=data, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                body = resp.read(response_limit + 1) if response_limit is not None else resp.read()
                if response_limit is not None and len(body) > response_limit:
                    raise SeafileError("Seafile response exceeds the document limit", 413)
                return resp.status, body if raw else body
        except urllib.error.HTTPError as exc:
            error_limit = min(response_limit + 1, 64 * 1024) if response_limit is not None else None
            body = exc.read(error_limit) if error_limit is not None else exc.read()
            if raw:
                raise SeafileError(
                    f"HTTP {exc.code} from {self._safe_url(url)}", exc.code, body) from exc
            raise SeafileError(self._redact_query_values(self._describe(exc.code, body), url),
                               exc.code, body) from exc
        except urllib.error.URLError as exc:
            raise SeafileError(
                f"cannot reach {self._safe_url(url)}: {exc.reason}") from exc

    @staticmethod
    def _safe_url(url):
        parts = urllib.parse.urlsplit(url)
        # Drop every query parameter and any userinfo; either can be a bearer
        # credential. Keep only enough context to identify the endpoint.
        netloc = parts.netloc.rsplit("@", 1)[-1]
        return urllib.parse.urlunsplit((parts.scheme, netloc, parts.path, "", ""))

    @classmethod
    def _redact_query_values(cls, message, url):
        for key, value in urllib.parse.parse_qsl(urllib.parse.urlsplit(url).query):
            if value and key.lower() in cls._credential_query_keys:
                message = message.replace(value, "[redacted]")
                message = message.replace(urllib.parse.quote(value), "[redacted]")
        return message

    @staticmethod
    def _describe(status, body):
        try:
            payload = json.loads(body)
        except Exception:
            return f"HTTP {status}: {body[:200]!r}"
        if isinstance(payload, dict):
            return f"HTTP {status}: {payload.get('error_msg') or payload}"
        return f"HTTP {status}: {payload}"

    def _json(self, url, **kwargs):
        status, body = self._request(url, **kwargs)
        try:
            return json.loads(body)
        except Exception as exc:
            raise SeafileError(
                f"invalid JSON from {self._safe_url(url)}", status, body) from exc

    # -- the third-party editor hook -------------------------------------

    def thirdparty_file_info(self, access_token):
        """GET /thirdparty-editor/file-info/ - who and what the host is editing."""
        url = (f"{self.base_url}/thirdparty-editor/file-info/"
               f"?access_token={urllib.parse.quote(access_token)}")
        return self._json(url)

    def thirdparty_file_content(self, access_token, expected_file_id, max_bytes=None):
        """GET the bytes, refusing a file that changed after the open."""
        url = (f"{self.base_url}/thirdparty-editor/file-content/"
               f"?access_token={urllib.parse.quote(access_token)}"
               f"&expected_file_id={urllib.parse.quote(expected_file_id)}")
        status, body = self._request(url, raw=True, response_limit=max_bytes)
        return body

    # -- the ordinary API -------------------------------------------------

    def file_detail(self, repo_id, path):
        """GET /api2/repos/<id>/file/detail/ - the current content id and permission."""
        url = (f"{self.base_url}/api2/repos/{repo_id}/file/detail/"
               f"?p={urllib.parse.quote(path)}")
        return self._json(url)

    def user_file_detail(self, repo_id, path, username, access_token):
        """Read current detail through the Seafile user-bound editor token."""
        info = self.thirdparty_file_info(access_token)
        if info.get("repo_id") != repo_id or info.get("file_path") != path:
            raise SeafileError("editor token is bound to a different document", status=403)
        if info.get("username") != username:
            raise SeafileError("editor token is bound to a different user", status=403)
        return {
            "id": info.get("file_id"),
            "permission": info.get("permission"),
            "can_edit": info.get("can_edit"),
            "head_commit_id": info.get("head_commit_id"),
            "last_modified": info.get("head_commit_id"),
        }

    def thirdparty_file_save(self, access_token, expected_id, expected_head, name, data):
        """Ask Seahub to re-authorize and atomically commit one editor save."""
        url = (f"{self.base_url}/thirdparty-editor/file-save/"
               f"?access_token={urllib.parse.quote(access_token)}")
        headers = {
            "Content-Type": "application/octet-stream",
            "X-Seafile-File-ID": expected_id,
            "X-Seafile-Head-ID": expected_head,
            "X-ArtCraft-Filename": urllib.parse.quote(name, safe=""),
        }
        status, body = self._request(url, method="POST", headers=headers, data=data, raw=True)
        try:
            result = json.loads(body)
        except Exception as exc:
            # Successful HTML/proxy error pages can echo the capability URL.
            # Never copy an upstream response body into an exception shown to
            # the browser; keep only the status for operator-side diagnosis.
            raise SeafileError("Seafile returned an invalid save response", status) from exc
        if status != 200:
            raise SeafileError(f"Seafile save failed with HTTP {status}", status)
        if not isinstance(result, dict) or not result.get("file_id") or not result.get("head_commit_id"):
            raise SeafileError("Seafile did not confirm a committed version", status=502)
        return result

    def atomic_update_file(self, repo_id, path, data, expected_id, username):
        """Replace only if `expected_id` is still current.

        The ordinary update link is unconditional.  This method is deliberately
        unavailable until the upstream Seafile endpoint supplies an atomic CAS.
        """
        raise SeafileError(
            "Seafile has no atomic compare-and-swap file update; writes are disabled",
            status=501,
        )

    def file_history(self, repo_id, path):
        """GET /api2/repos/<id>/file/history/ - the versions of a file."""
        url = (f"{self.base_url}/api2/repos/{repo_id}/file/history/"
               f"?p={urllib.parse.quote(path)}")
        return self._json(url)

    def download_link(self, repo_id, path):
        """GET /api2/repos/<id>/file/ - a URL that serves the file's bytes."""
        url = (f"{self.base_url}/api2/repos/{repo_id}/file/"
               f"?p={urllib.parse.quote(path)}")
        return self._json(url)

    def download(self, repo_id, path):
        """The bytes of a file, using the gateway's own credential."""
        link = self.download_link(repo_id, path)
        if not isinstance(link, str) or not link:
            raise SeafileError(f"no download link for {repo_id} {path}: {link!r}")
        # The link carries its own file-server token; the account token stays home.
        status, body = self._request(link, raw=True, auth=False)
        return body

    def update_link(self, repo_id, parent_dir):
        """GET /api2/repos/<id>/update-link/ - a one-shot URL that replaces a file."""
        url = (f"{self.base_url}/api2/repos/{repo_id}/update-link/"
               f"?p={urllib.parse.quote(parent_dir)}&from=api")
        return self._json(url)

    def update_file(self, repo_id, path, data):
        """Replace a file's content. Returns the new content id (obj id).

        The write is unconditional on the server side, so the caller must have
        checked the content id first (see docs/CONFLICTS.md).
        """
        parent = path.rsplit("/", 1)[0] or "/"
        link = self.update_link(repo_id, parent)
        if not isinstance(link, str) or not link:
            raise SeafileError(f"no update link for {repo_id} {parent}: {link!r}")

        boundary = uuid.uuid4().hex
        name = path.rsplit("/", 1)[-1]
        body = b"".join([
            f"--{boundary}\r\n".encode(),
            f'Content-Disposition: form-data; name="file"; filename="{name}"\r\n'.encode(),
            b"Content-Type: application/octet-stream\r\n\r\n",
            data,
            f"\r\n--{boundary}\r\n".encode(),
            f'Content-Disposition: form-data; name="target_file"\r\n\r\n'.encode(),
            path.encode(),
            f"\r\n--{boundary}--\r\n".encode(),
        ])
        headers = {
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Content-Length": str(len(body)),
        }
        status, resp = self._request(link, method="POST", headers=headers, data=body, raw=True,
                                     auth=False)
        return self._file_id(resp)

    def upload_file(self, repo_id, parent_dir, name, data, replace=True):
        """Upload a new file, or replace the one with that name. Returns the new content id.

        `replace` is a **form field** of the upload, not a parameter of the link
        (the file server reads it with `r.FormValue("replace")`). Without it the
        upload creates a second file with the name in brackets.
        """
        url = (f"{self.base_url}/api2/repos/{repo_id}/upload-link/"
               f"?p={urllib.parse.quote(parent_dir)}")
        link = self._json(url)
        if not isinstance(link, str) or not link:
            raise SeafileError(f"no upload link for {repo_id} {parent_dir}: {link!r}")

        boundary = uuid.uuid4().hex
        body = b"".join([
            f"--{boundary}\r\n".encode(),
            f'Content-Disposition: form-data; name="file"; filename="{name}"\r\n'.encode(),
            b"Content-Type: application/octet-stream\r\n\r\n",
            data,
            f"\r\n--{boundary}\r\n".encode(),
            f'Content-Disposition: form-data; name="parent_dir"\r\n\r\n'.encode(),
            parent_dir.encode(),
            f"\r\n--{boundary}\r\n".encode(),
            f'Content-Disposition: form-data; name="replace"\r\n\r\n'.encode(),
            (b"1" if replace else b"0"),
            f"\r\n--{boundary}--\r\n".encode(),
        ])
        headers = {
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Content-Length": str(len(body)),
        }
        status, resp = self._request(link, method="POST", headers=headers, data=body, raw=True,
                                     auth=False)
        return self._file_id(resp)

    @staticmethod
    def _file_id(body):
        """The content id the file server answers a write with.

        It is a hex id. Anything else means the answer is not what we expect, and
        treating it as an id would corrupt the session's conflict check.
        """
        text = body.decode(errors="replace").strip().strip('"')
        if not text or any(c not in "0123456789abcdef" for c in text.lower()):
            raise SeafileError(f"the file server did not answer with a file id: {text[:120]!r}")
        return text


    @staticmethod
    def from_env():
        url = os.environ.get("ARTCRAFT_SEAFILE_URL")
        token = os.environ.get("ARTCRAFT_SEAFILE_TOKEN")
        if not url:
            raise SystemExit(
                "ARTCRAFT_SEAFILE_URL must be set"
            )
        return Seafile(url, token)
