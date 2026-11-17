"""Verify the isolated Proxmox deployment evidence: assertion counts, retained
proof in detail fields (version growth+creator, fresh browser context), and
byte equality of relayed vs read-back artifacts."""
import hashlib, json, re
from pathlib import Path

root = Path(__file__).resolve().parent
expected = {"wordcraft": 24, "gridcraft": 27, "deckcraft": 15}
VERSION = re.compile(r"history \d+->\d+ grew=True creator_is_opener=True")
FRESH = re.compile(r"new_browser_context=True url_has_login_redirect=False")
PAIRS = {
    "wordcraft": ("wordcraft-original.docx", "wordcraft-first-relay.docx", "wordcraft-first-readback.docx"),
    "gridcraft": ("gridcraft-original.xlsx", "gridcraft-first-relay.xlsx", "gridcraft-first-readback.xlsx"),
    "deckcraft": ("pptx-original.pptx", "pptx-first-relay.pptx", "pptx-readback.pptx"),
}
def sha(p): return hashlib.sha256((root / p).read_bytes()).hexdigest()

total = 0
for editor, n in expected.items():
    d = json.loads((root / f"{editor}-browser.json").read_text())
    assert d["passed"] == d["assertion_count"] == n and d["failed"] == 0, (editor, d["passed"], d["failed"])
    # Version-proof checks are identified by their detail carrying the history
    # proof, not by the check name (several version-named checks have no history
    # detail, e.g. download-substitution checks).
    versioned = [c for c in d["checks"] if "grew=" in c["detail"]]
    # DeckCraft is the single-save PPTX round-trip fixture; the other two
    # editors run the two-save (open->save, reopen->save) flow.
    min_versions = 1 if editor == "deckcraft" else 2
    assert len(versioned) >= min_versions and all(VERSION.search(c["detail"]) for c in versioned), (editor, "version proof")
    fresh = [c for c in d["checks"] if FRESH.search(c["detail"])]
    assert fresh and all(FRESH.search(c["detail"]) for c in fresh), (editor, "fresh proof")
    downloads = [c for c in d["checks"] if "did_not_download" in c["name"]]
    assert downloads and all(c["ok"] for c in downloads), (editor, "downloads")
    o, r, b = PAIRS[editor]
    assert sha(r) == sha(b), (editor, "relay != readback")
    assert sha(o) != sha(b), (editor, "original == readback")
    total += n
print(f"PASS: {total}/{sum(expected.values())} assertions with retained proof; "
      f"DOCX/XLSX/PPTX relay==readback; originals differ; no downloads substituted saves")
