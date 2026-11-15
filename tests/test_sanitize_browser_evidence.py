"""Unit tests for scripts/sanitize-browser-evidence.py.

The sanitizer exists so retained evidence keeps the observed `detail` (version
growth, creator attribution, navigation outcome) while dropping identifiers.
These tests pin both halves of that contract, including the fail-closed path.
"""
import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "sanitize_browser_evidence", ROOT / "scripts" / "sanitize-browser-evidence.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

RAW = {
    "repo_id": "15c1fcf4-ddbc-469f-ba5e-0c30ef809d3c",
    "ran_at": "2026-11-15T10:00:00Z",
    "checks": [
        {"name": "wordcraft_save_creates_seafile_version_by_user", "ok": True,
         "detail": "history 1->2 grew=True creator_is_opener=True status='saved to Seafile'"},
        {"name": "frames", "ok": True,
         "detail": "frames=[('', 'http://seafile.lab/lib/15c1fcf4-ddbc-469f-ba5e-0c30ef809d3c/file/test.docx', None), "
                   "('office_frame', 'http://bridge:8778/edit/wordcraft?WOPISrc=http%3A%2F%2Fseafile.lab%2Fa', '')]"},
        {"name": "leaky", "ok": True,
         "detail": "top={'creator': 'synthetic-abc@lab.test', 'id': 'ffffffffffffffffffffffffffffffffffffffff'} "
                   "https://x.test/api2/wopi/files/abc?access_token=SECRET"},
    ],
}


class SanitizeBrowserEvidenceTest(unittest.TestCase):
    def test_detail_is_kept_and_proof_survives(self):
        out = mod.sanitize(RAW, "wordcraft")
        self.assertEqual(out["editor"], "wordcraft")
        self.assertEqual(out["assertion_count"], 3)
        self.assertEqual(out["passed"], 3)
        self.assertIn("grew=True creator_is_opener=True", out["checks"][0]["detail"])

    def test_identifiers_are_redacted(self):
        text = json.dumps(mod.sanitize(RAW, "wordcraft"))
        for leak in ("15c1fcf4", "synthetic-abc@lab.test", "ffffffffffffffffffffffffffffffffffffffff",
                     "SECRET", "WOPISrc=http"):
            self.assertNotIn(leak, text)

    def test_reformatted_proofs_still_present(self):
        out = mod.sanitize(RAW, "wordcraft")
        self.assertIn("lib/<id>/file/test.docx", out["checks"][1]["detail"])
        self.assertIn("?<query>", out["checks"][1]["detail"])
        self.assertIn("<synthetic-account>", out["checks"][2]["detail"])

    def test_leak_detector_flags_raw_and_clears_sanitized(self):
        self.assertEqual(mod.leaks(mod.sanitize(RAW, "wordcraft")), [])
        leaked = mod.sanitize(RAW, "wordcraft")
        leaked["checks"][0]["detail"] += " repo 15c1fcf4-ddbc-469f-ba5e-0c30ef809d3c untouched"
        self.assertTrue(mod.leaks(leaked))

    def test_redact_is_idempotent(self):
        once = mod.redact(RAW["checks"][2]["detail"])
        self.assertEqual(mod.redact(once), once)


if __name__ == "__main__":
    sys.exit(unittest.main())
