"""Verify the retained CE12 evidence: assertions, the proof inside their detail
fields, byte equality of relayed vs read-back artifacts, and artifact hashes.

This verifier does not accept a bare `"ok": true` for the central claims:
- every version assertion must carry `grew=True creator_is_opener=True`;
- every fresh-session assertion must carry `new_browser_context=True
  url_has_login_redirect=False` (the run creates a real new browser context
  and logs in again);
- every open/reopen-from-file-list assertion must carry
  `url_has_login_redirect=False`;
- DOCX, XLSX and PPTX relay artifacts must equal their Seafile readbacks, and
  the XLSX readback must differ from the original fixture bytes.
"""
import hashlib
import json
import re
from pathlib import Path

root = Path(__file__).resolve().parent
expected = {"wordcraft": 24, "gridcraft": 27, "deckcraft": 15}
VERSION = re.compile(r"history \d+->\d+ grew=True creator_is_opener=True")
FRESH = re.compile(r"new_browser_context=True url_has_login_redirect=False")
LIST = re.compile(r"url_has_login_redirect=False")

version_checks = {
    "wordcraft": ["wordcraft_save_creates_seafile_version_by_user",
                  "wordcraft_reopen_second_save_creates_seafile_version_by_user"],
    "gridcraft": ["gridcraft_save_creates_seafile_version_by_user",
                  "gridcraft_reopen_second_save_creates_seafile_version_by_user"],
    "deckcraft": ["pptx_new_version_attributed_to_user"],
}
fresh_checks = {
    "wordcraft": ["wordcraft_reopen_fresh_seafile_session"],
    "gridcraft": ["gridcraft_reopen_fresh_seafile_session"],
    "deckcraft": ["pptx_fresh_session_file_list_reopen"],
}
list_checks = {
    "wordcraft": ["wordcraft_opened_from_seafile_file_list",
                  "wordcraft_reopened_from_seafile_file_list"],
    "gridcraft": ["gridcraft_opened_from_seafile_file_list",
                  "gridcraft_reopened_from_seafile_file_list"],
    "deckcraft": ["pptx_opened_from_seafile_file_list"],
}

for editor, count in expected.items():
    data = json.loads((root / f"{editor}-browser.json").read_text())
    assert data["editor"] == editor
    assert data["assertion_count"] == data["passed"] == count, (editor, data["assertion_count"], data["passed"])
    assert data["failed"] == 0 and len(data["checks"]) == count
    assert all(check["ok"] is True for check in data["checks"])
    by_name = {c["name"]: c for c in data["checks"]}
    # The central claims must carry their proof, not a bare boolean.
    for name in version_checks[editor]:
        assert name in by_name, f"{editor}: missing {name}"
        detail = by_name[name]["detail"]
        assert VERSION.search(detail), f"{editor}/{name}: no version proof in {detail!r}"
    for name in fresh_checks[editor]:
        assert name in by_name, f"{editor}: missing {name}"
        detail = by_name[name]["detail"]
        assert FRESH.search(detail), f"{editor}/{name}: no fresh-context proof in {detail!r}"
    for name in list_checks[editor]:
        assert name in by_name, f"{editor}: missing {name}"
        detail = by_name[name]["detail"]
        assert LIST.search(detail), f"{editor}/{name}: no navigation proof in {detail!r}"
    # Nothing may look like an unredacted identifier.
    text = json.dumps(data)
    for pattern in (r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+",
                    r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b",
                    r"\b[0-9a-f]{32,64}\b"):
        assert not re.search(pattern, text), f"{editor}: leak matching {pattern}"

assert (root / "wordcraft-first-relay.docx").read_bytes() == (root / "wordcraft-first-readback.docx").read_bytes()
assert (root / "pptx-first-relay.pptx").read_bytes() == (root / "pptx-readback.pptx").read_bytes()
assert (root / "gridcraft-first-relay.xlsx").read_bytes() == (root / "gridcraft-first-readback.xlsx").read_bytes()
assert (root / "gridcraft-original.xlsx").read_bytes() != (root / "gridcraft-first-readback.xlsx").read_bytes()
for line in (root / "SHA256SUMS").read_text().splitlines():
    digest, name = line.split("  ", 1)
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == digest, name
print("PASS: 66/66 assertions with retained proof (version growth+creator, fresh "
      "browser context without login redirect), DOCX/XLSX/PPTX relay==readback, artifact hashes")
