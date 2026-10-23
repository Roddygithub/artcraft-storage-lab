"""Exercise the patched save view through Django's real URL resolver.

Run inside the pinned, isolated Seahub container with the environment used by
test_gr015_dispatch.py. Seafile RPC and the fileserver transport are synthetic;
the patched Django route, DRF view, permission parser, and middleware are real.
"""

from types import SimpleNamespace
from unittest.mock import patch

import django
from django.test import Client, override_settings

django.setup()

from seahub.thirdparty_editor import views


TOKEN = "synthetic-permission-test"
CAPABILITY = {
    "audience": "artcraft",
    "repo_id": "synthetic-repo",
    "file_path": "/synthetic.docx",
    "request_user": "synthetic-user@example.test",
    "permission": {"can_edit": True},
}


class FakeCache:
    def __init__(self, capability):
        self.capability = capability

    def get(self, key):
        assert key == "thirdparty_editor_access_token_" + TOKEN
        return self.capability


class FakeUser:
    objects = SimpleNamespace(get=lambda **_kwargs: object())

    class DoesNotExist(Exception):
        pass


class FakeSeafile:
    def __init__(self, permission):
        self.permission = permission
        self.repo = SimpleNamespace(head_cmmt_id="head-before")
        self.update_token_calls = 0
        self.permission_checks = 0

    def get_repo(self, _repo_id):
        return self.repo

    def check_permission_by_path(self, _repo_id, _path, _user):
        self.permission_checks += 1
        return self.permission

    def get_file_id_by_path(self, _repo_id, _path):
        return "file-before"

    def get_fileserver_access_token(self, *_args, **_kwargs):
        self.update_token_calls += 1
        return "must-not-be-requested-for-denied-save"


def main():
    docx = "/tmp/synthetic.docx"
    with open(docx, "rb") as source:
        content = source.read()

    client = Client()
    for label, opened_permission, current_permission in (
            ("read-only", "r", "r"), ("revoked after open", "rw", "r")):
        seafile = FakeSeafile(opened_permission)
        capability = {**CAPABILITY, "permission": {
            "can_edit": opened_permission in ("rw", "admin", "preview-edit")}}
        # The cached grant records permission at open time; RPC reports the
        # current permission at save time, after any revocation.
        seafile.permission = current_permission
        fileserver_posts = []
        with (
            override_settings(ARTCRAFT_REPO_IDS=("synthetic-repo",),
                              ARTCRAFT_FILE_EXTENSIONS=("docx",),
                              ARTCRAFT_MAX_FILE_SIZE=50 * 1024 * 1024),
            patch.object(views, "cache", FakeCache(capability)),
            patch.object(views, "User", FakeUser),
            patch.object(views, "seafile_api", seafile),
            patch.object(views.requests, "post", lambda *args, **kwargs:
                         fileserver_posts.append((args, kwargs))),
        ):
            response = client.post(
                "/thirdparty-editor/file-save/?access_token=" + TOKEN,
                data=content,
                content_type="application/octet-stream",
                HTTP_X_SEAFILE_FILE_ID="file-before",
                HTTP_X_SEAFILE_HEAD_ID="head-before",
                HTTP_X_ARTCRAFT_FILENAME="synthetic.docx",
            )

        assert response.status_code == 403, (label, response.status_code, response.content)
        assert seafile.update_token_calls == 0, (label, seafile.update_token_calls)
        assert fileserver_posts == [], (label, fileserver_posts)
        assert seafile.permission_checks == (0 if opened_permission == "r" else 1)
        print(f"PASS: {label} capability is refused by Django save route (403), before update token/fileserver")

    print("LIMIT: Seafile RPC and file persistence are synthetic; this does not test live revocation propagation")


if __name__ == "__main__":
    main()
