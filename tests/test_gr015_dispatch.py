"""Run in the pinned Seahub runtime to guard ArtCraft/ONLYOFFICE dispatch."""

from types import SimpleNamespace
from unittest.mock import patch

import django
from django.test import RequestFactory

django.setup()

import seahub.base.decorators as decorators
import seahub.views.file as file_views


def main():
    view = file_views.view_lib_file
    while hasattr(view, "__wrapped__"):
        view = view.__wrapped__

    repo = SimpleNamespace(
        head_cmmt_id="head", encrypted=False, store_id="store", version=1,
        origin_path="", is_virtual=False, repo_id="synthetic-repo",
    )
    permission = SimpleNamespace(
        can_edit_on_web=True, can_download=True, can_preview=True,
    )
    api = SimpleNamespace(
        get_repo=lambda _: repo,
        get_file_id_by_path=lambda *_: "file-id",
        get_fileserver_access_token=lambda *_args, **_kwargs: "synthetic-view-token",
        get_dirent_by_path=lambda *_: None,
        get_file_size=lambda *_: 100,
    )

    def request():
        value = RequestFactory().get("/lib/synthetic-repo/file/report.docx")
        value.user = SimpleNamespace(username="synthetic-user", org=None)
        value.session = {}
        value.LANGUAGE_CODE = "en"
        return value

    patches = {
        "seafile_api": api,
        "get_office_feature_by_repo": lambda _: (True, False),
        "check_folder_permission": lambda *_: "rw",
        "parse_repo_perm": lambda _: permission,
        "get_file_type_and_ext": lambda _: (file_views.DOCUMENT, "docx"),
        "is_org_context": lambda _: False,
        "is_pro_version": lambda: False,
        "is_repo_owner": lambda *_: False,
        "is_repo_admin": lambda *_: False,
        "gen_file_get_url_new": lambda *_: "/download/report.docx",
        "gen_file_get_url": lambda *_: "/raw/report.docx",
        "gen_inner_file_get_url": lambda *_: "/raw/report.docx",
        "is_file_starred": lambda *_: False,
        "check_file_lock": lambda *_: (False, False),
        "if_locked_by_online_office": lambda *_: False,
        "send_file_access_msg": lambda *_: None,
        "get_onlyoffice_dict": lambda *_args, **_kwargs: {"onlyoffice_marker": True},
        "render": lambda _request, template, context:
            SimpleNamespace(template=template, context=context),
    }

    with (
        patch.object(file_views.settings, "ARTCRAFT_REPO_IDS", ("synthetic-repo",), create=True),
        patch.object(file_views.settings, "ARTCRAFT_ACTION_URL", "http://gateway/open/", create=True),
        patch.object(file_views.settings, "ARTCRAFT_FILE_EXTENSIONS", ("docx",), create=True),
        patch.object(decorators, "get_repo", lambda _: repo),
        patch.multiple(file_views, **patches),
        patch.object(file_views, "ONLYOFFICE_FILE_EXTENSION", ("docx",)),
        patch.object(file_views, "ONLYOFFICE_EDIT_FILE_EXTENSION", ("docx",)),
    ):
        artcraft = view(request(), repo_id="synthetic-repo", path="report.docx")
        assert artcraft.template == "view_file_thirdparty_editor.html"
        assert artcraft.context["action_url"] == "http://gateway/open/"

        with patch.object(file_views.settings, "ARTCRAFT_REPO_IDS", ()):
            onlyoffice = view(request(), repo_id="synthetic-repo", path="report.docx")
        assert onlyoffice.template == "onlyoffice_file_view_react.html"
        assert onlyoffice.context["onlyoffice_marker"] is True

    print("PASS: allowlisted DOCX dispatches to ArtCraft")
    print("PASS: non-allowlisted DOCX falls through to ONLYOFFICE")
    print("NOTE: this is a Seahub routing test; Document Server edit/save is not exercised")


if __name__ == "__main__":
    main()
