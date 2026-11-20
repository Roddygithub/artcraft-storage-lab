#!/usr/bin/env python3
"""Exercise complete XLSX reports through the API, CLI, and probe path."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock

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


class XlsxReportJsonTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fidelity_corpus.corpus()["fidelity-workbook.xlsx"]

    def assert_complete_report_json(self, result):
        decoded = json.loads(json.dumps(result, ensure_ascii=False))
        cells = decoded["before"]["cells"]
        self.assertTrue(cells)
        self.assertIn('["Data","A1"]', cells)
        self.assertEqual(json.loads('["Data","A1"]'), ["Data", "A1"])
        self.assertEqual(decoded["verdicts"]["formulas"], "PRESERVED")

    def test_compare_result_is_json_serializable(self):
        self.assert_complete_report_json(fidelity_compare.compare(self.fixture, self.fixture))

    def test_cli_writes_valid_complete_json_report(self):
        with tempfile.TemporaryDirectory() as temp:
            original = Path(temp) / "original.xlsx"
            saved = Path(temp) / "saved.xlsx"
            report = Path(temp) / "report.json"
            original.write_bytes(self.fixture)
            saved.write_bytes(self.fixture)
            completed = subprocess.run(
                [sys.executable, str(ROOT / "lab/real-seafile/fidelity_compare.py"),
                 str(original), str(saved), "--json", str(report)],
                cwd=ROOT, capture_output=True, text=True, check=False)
            self.assertEqual(completed.returncode, 0, completed.stderr + completed.stdout)
            self.assertEqual(json.loads(completed.stdout)["kind"], "xlsx")
            self.assert_complete_report_json(json.loads(report.read_text(encoding="utf-8")))

    def test_probe_save_comparison_is_json_serializable(self):
        mark = Mock()
        result = fidelity_probe.compare_saved_file(
            True, "xlsx", self.fixture, self.fixture, "marker", mark)
        self.assert_complete_report_json(result)
        with tempfile.TemporaryDirectory() as temp:
            report = Path(temp) / "xlsx-comparison.json"
            fidelity_probe.write_json(report, result)
            self.assert_complete_report_json(json.loads(report.read_text(encoding="utf-8")))
        mark.assert_not_called()


if __name__ == "__main__":
    unittest.main(verbosity=2)
