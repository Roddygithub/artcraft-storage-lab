#!/usr/bin/env python3
"""Check the retained sanitized result structure; does not replay the lab."""
import json
from pathlib import Path
root = Path(__file__).resolve().parent
for name, expected in [("slice", 48), ("browser", 23)]:
    d = json.loads((root / (name + ".json")).read_text())
    assert d["failed"] == 0 and d["passed"] == expected
    assert len(d["checks"]) == expected and all(c["ok"] is True for c in d["checks"])
    assert len({c["name"] for c in d["checks"]}) == expected
browser = {c["name"] for c in json.loads((root / "browser.json").read_text())["checks"]}
assert {"wordcraft_opened_from_seafile_file_list", "wordcraft_reopened_from_seafile_file_list",
        "wordcraft_saves_did_not_download", "wordcraft_reopen_editor_holds_the_original_marker",
        "wordcraft_reopen_editor_holds_the_second_typed_marker"} <= browser
print("PASS: retained HTTP 48/48 and WordCraft browser 23/23; runtime not replayed")
