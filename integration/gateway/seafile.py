"""Minimal Seafile client for the ArtCraft gateway.

Only the calls the gateway needs. No dependency beyond the standard library.

Credentials come from the environment, never from a file in the repository:

    ARTCRAFT_SEAFILE_URL     e.g. https://seafile.example.org
    ARTCRAFT_SEAFILE_TOKEN   an account token (Authorization: Token <t>)
    ARTCRAFT_SEAFILE_USER    the user the token belongs to (for attribution)
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
    def __init__(self, base_url, token, timeout=30):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout

    # -- plumbing ---------------------------------------------------------

    def _request(self, url, method="GET", headers=None, data=None, raw=False):
        headers = dict(headers or {})
        if self.token and "Authorization" not in headers:
            headers["Authorization"] = "Token " + self.token
        req = urllib.request.Request(url, method=method, data=data, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                body = resp.read()
                return resp.status, body if raw else body
        except urllib.error.HTTPError as exc:
            body = exc.read()
            if raw:
                raise SeafileError(f"HTTP {exc.code} for {url}", exc.code, body) from exc
            raise SeafileError(self._describe(exc.code, body), exc.code, body) from exc
        except urllib.error.URLError as exc:
            raise SeafileError(f"cannot reach {url}: {exc.reason}") from exc

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
            raise SeafileError(f"invalid JSON from {url}: {body[:200]!r}", status, body) from exc

    # -- the third-party editor hook -------------------------------------

    def thirdparty_file_info(self, access_token):
        """GET /thirdparty-editor/file-info/ - who and what the host is editing."""
        url = (f"{self.base_url}/thirdparty-editor/file-info/"
               f"?access_token={urllib.parse.quote(access_token)}")
        return self._json(url)

    def thirdparty_file_content(self, access_token):
        """GET /thirdparty-editor/file-content/ - the document bytes."""
        url = (f"{self.base_url}/thirdparty-editor/file-content/"
               f"?access_token={urllib.parse.quote(access_token)}")
        status, body = self._request(url, raw=True)
        return body

    # -- the ordinary API -------------------------------------------------

    def file_detail(self, repo_id, path):
        """GET /api2/repos/<id>/file/detail/ - the current content id and permission."""
        url = (f"{self.base_url}/api2/repos/{repo_id}/file/detail/"
               f"?p={urllib.parse.quote(path)}")
        return self._json(url)

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
        status, body = self._request(link, raw=True)
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
        status, resp = self._request(link, method="POST", headers=headers, data=body, raw=True)
        return resp.decode(errors="replace").strip()

    def upload_file(self, repo_id, parent_dir, name, data, replace=True):
        """Upload a new file. Returns the new content id."""
        url = (f"{self.base_url}/api2/repos/{repo_id}/upload-link/"
               f"?p={urllib.parse.quote(parent_dir)}&replace={1 if replace else 0}")
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
            f"\r\n--{boundary}--\r\n".encode(),
        ])
        headers = {
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Content-Length": str(len(body)),
        }
        status, resp = self._request(link, method="POST", headers=headers, data=body, raw=True)
        return resp.decode(errors="replace").strip()


    @staticmethod
    def from_env():
        url = os.environ.get("ARTCRAFT_SEAFILE_URL")
        token = os.environ.get("ARTCRAFT_SEAFILE_TOKEN")
        if not url or not token:
            raise SystemExit(
                "ARTCRAFT_SEAFILE_URL and ARTCRAFT_SEAFILE_TOKEN must be set "
                "(the token is an account token; keep it out of the repository)"
            )
        return Seafile(url, token)
