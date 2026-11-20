#!/usr/bin/env python3
"""Regression tests for the fidelity probe's save-confirmation gate."""
from pathlib import Path
import os
import sys
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
for name, value in {"SEAFILE_URL": "http://127.0.0.1",
                    "BRIDGE_URL": "http://127.0.0.1:8778",
                    "ADMIN_EMAIL": "test@example.invalid",
                    "ADMIN_PASSWORD": "unused"}.items():
    os.environ.setdefault(name, value)
sys.path.insert(0, str(ROOT / "lab/real-seafile"))
import fidelity_compare  # noqa: E402
import fidelity_corpus  # noqa: E402
import fidelity_probe  # noqa: E402


class SavedFileGateTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fidelity_corpus.corpus()["fidelity-report.docx"]
        self.mark = Mock(return_value=False)

    def test_confirmed_save_runs_real_comparison(self):
        result = fidelity_probe.compare_saved_file(
            True, "docx", self.fixture, self.fixture, "marker", self.mark)
        self.assertEqual(result["kind"], "docx")
        self.assertNotIn("error", result)
        self.assertEqual(result["regressions"], [])
        self.mark.assert_not_called()

    def test_unconfirmed_save_fails_and_skips_comparison(self):
        with patch.object(fidelity_probe.fidelity_compare, "compare",
                          side_effect=AssertionError("comparison must not run")) as compare:
            result = fidelity_probe.compare_saved_file(
                False, "docx", self.fixture, self.fixture, "marker", self.mark)
        self.assertIsNone(result)
        compare.assert_not_called()
        self.mark.assert_called_once()
        name, passed, detail = self.mark.call_args.args
        self.assertEqual(name, "docx_fidelity")
        self.assertFalse(passed)
        self.assertIn("NOT_VERIFIED", detail)


if __name__ == "__main__":
    unittest.main(verbosity=2)
