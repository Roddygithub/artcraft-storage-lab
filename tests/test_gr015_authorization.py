#!/usr/bin/env python3
"""Execute GR-015's exact access-token decorator with synthetic Seafile state.

Set ARTCRAFT_SEAHUB_SOURCE to a clean checkout with the draft patch applied:
    ARTCRAFT_SEAHUB_SOURCE=/path/to/seahub \
      python3 tests/test_gr015_authorization.py

This isolates the decorator logic; it does not emulate Django or Seafile RPC.
"""

import ast
import io
import json
import os
from pathlib import Path
from types import SimpleNamespace
import zipfile
import xml.etree.ElementTree as ElementTree


source_root = os.environ.get("ARTCRAFT_SEAHUB_SOURCE")
if not source_root:
    raise SystemExit("ARTCRAFT_SEAHUB_SOURCE must point to patched Seahub source")
source_path = Path(source_root) / "seahub/thirdparty_editor/views.py"
module = ast.parse(source_path.read_text(encoding="utf-8"))
decorator_node = next(node for node in module.body
                      if isinstance(node, ast.FunctionDef)
                      and node.name == "access_token_check")
signature_node = next(node for node in module.body
                      if isinstance(node, ast.FunctionDef)
                      and node.name == "_matches_file_type")


class Response:
    def __init__(self, body, status=200, content_type=None):
        self.body = body
        self.status = status


class FakeSeafileAPI:
    permission = "rw"
    permission_checks = 0

    def get_repo(self, _repo_id):
        return object()

    def check_permission_by_path(self, _repo_id, _path, _user):
        self.permission_checks += 1
        return self.permission

    def get_file_id_by_path(self, _repo_id, _path):
        return "file-id"


class FakeCache:
    info = {"request_user": "alice@example.test", "repo_id": "repo-id",
            "file_path": "/folder/doc.docx"}

    def get(self, _key):
        return self.info


class FakeUser:
    class DoesNotExist(Exception):
        pass

    class objects:
        @staticmethod
        def get(**_kwargs):
            return object()


class Request:
    GET = {"access_token": "synthetic-capability"}


class Logger:
    messages = []

    def error(self, message):
        self.messages.append(str(message))


api = FakeSeafileAPI()
logger = Logger()
namespace = {
    "json": json,
    "io": io,
    "os": os,
    "zipfile": zipfile,
    "ElementTree": ElementTree,
    "HttpResponse": Response,
    "json_content_type": "application/json",
    "MAX_CONTENT_TYPES_XML_BYTES": 1024 * 1024,
    "logger": logger,
    "cache": FakeCache(),
    "ANONYMOUS_EMAIL": "anonymous@seafile.invalid",
    "User": FakeUser,
    "seafile_api": api,
    "parse_repo_perm": lambda permission: SimpleNamespace(
        can_preview=permission in {"r", "rw", "admin", "preview", "preview-edit"}),
}
exec(compile(ast.Module(body=[signature_node, decorator_node], type_ignores=[]),
             str(source_path), "exec"), namespace)

calls = []
wrapped = namespace["access_token_check"](
    lambda *_args, **_kwargs: calls.append("view-called") or Response("ok"))

assert wrapped(object(), Request()).status == 200
assert api.permission_checks == 1 and calls == ["view-called"]

api.permission = None
before = len(calls)
assert wrapped(object(), Request()).status == 403
assert len(calls) == before and api.permission_checks == 2

api.permission = "upload-only"
assert wrapped(object(), Request()).status == 403
assert api.permission_checks == 3

FakeCache.info = {"request_user": "anonymous@seafile.invalid", "repo_id": "repo-id",
                  "file_path": "/folder/doc.docx"}
before_checks = api.permission_checks
assert wrapped(object(), Request()).status == 403
assert api.permission_checks == before_checks

FakeCache.info = None
assert wrapped(object(), Request()).status == 404
assert all("synthetic-capability" not in message for message in logger.messages)

fixture = Path(__file__).parent / "fixtures/synthetic.xlsx"
assert namespace["_matches_file_type"]("synthetic.xlsx", fixture.read_bytes())
wrong_type = io.BytesIO()
with zipfile.ZipFile(wrong_type, "w") as archive:
    archive.writestr("[Content_Types].xml", "<Types>wordprocessingml.document</Types>")
assert not namespace["_matches_file_type"]("synthetic.xlsx", wrong_type.getvalue())
oversized_types = io.BytesIO()
with zipfile.ZipFile(oversized_types, "w", compression=zipfile.ZIP_DEFLATED) as archive:
    archive.writestr("[Content_Types].xml", b"<Types>" + b" " * (1024 * 1024) + b"</Types>")
assert not namespace["_matches_file_type"]("synthetic.xlsx", oversized_types.getvalue())

print("PASS: current read permission is checked on each request")
print("PASS: revoked/non-preview/anonymous capability reads are refused")
print("PASS: invalid capability is not written to the Seahub log")
print("PASS: patched Seahub accepts ordinary XLSX MIME and rejects DOCX content as XLSX")
print("PASS: patched Seahub rejects oversized expanded OOXML type metadata")
print("NOTE: exact decorator executed with synthetic dependencies; Django/Seafile integration unverified")
