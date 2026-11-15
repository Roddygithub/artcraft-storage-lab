import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent
expected = {"wordcraft": 24, "gridcraft": 27, "deckcraft": 15}
for editor, count in expected.items():
    data = json.loads((root / f"{editor}-browser.json").read_text())
    assert data["editor"] == editor
    assert data["assertion_count"] == data["passed"] == count
    assert data["failed"] == 0 and len(data["checks"]) == count
    assert all(check["ok"] is True for check in data["checks"])
assert (root / "wordcraft-first-relay.docx").read_bytes() == (root / "wordcraft-first-readback.docx").read_bytes()
assert (root / "pptx-first-relay.pptx").read_bytes() == (root / "pptx-readback.pptx").read_bytes()
for line in (root / "SHA256SUMS").read_text().splitlines():
    digest, name = line.split("  ", 1)
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == digest, name
print("PASS: 66/66 browser assertions, DOCX/PPTX relay readback equality, and artifact hashes")
