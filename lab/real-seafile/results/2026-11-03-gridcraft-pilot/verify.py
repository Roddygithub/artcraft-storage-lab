#!/usr/bin/env python3
"""Verify retained results and source hashes, without replaying any service."""
import hashlib
import json
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parent
for name in ("slice", "browser"):
    result = json.loads((root / (name + ".json")).read_text())
    assert result["passed"] == 48 and result["failed"] == 0
    assert len(result["checks"]) == 48 and all(c["ok"] is True for c in result["checks"])
    assert len({c["name"] for c in result["checks"]}) == 48
    assert len(result["raw_result_sha256"]) == 64
    assert all(set(c) == {"name", "ok"} for c in result["checks"])
names = {c["name"] for c in result["checks"]}
assert {
    "wordcraft_reopen_editor_holds_the_original_marker",
    "wordcraft_reopen_editor_holds_the_second_typed_marker",
    "wordcraft_saves_did_not_download",
    "gridcraft_opened_from_seafile_file_list",
    "gridcraft_reopened_from_seafile_file_list",
    "gridcraft_reopen_editor_holds_the_original_value",
    "gridcraft_reopen_editor_holds_the_second_typed_value",
    "gridcraft_reopen_second_save_creates_seafile_version_by_user",
    "gridcraft_saves_did_not_download",
} <= names
source = json.loads((root / "runtime-source-hashes.json").read_text())
assert source["source_commit"] == json.loads((root / "SOURCE.json").read_text())["source_commit"]
for path, expected in source["files"].items():
    data = subprocess.check_output(["git", "show", source["source_commit"] + ":" + path], cwd=root.parents[3])
    assert hashlib.sha256(data).hexdigest() == expected, path
print(f"PASS: retained HTTP 48/48, browser 48/48, {len(source['files'])} candidate source hashes; no runtime replay")
