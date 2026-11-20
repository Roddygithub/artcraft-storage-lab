#!/usr/bin/env python3
"""Fresh-editor reopen checks cannot be satisfied by a successful Seafile download."""
from pathlib import Path
import os
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
for name, value in {"SEAFILE_URL": "http://127.0.0.1",
                    "BRIDGE_URL": "http://127.0.0.1:8778",
                    "ADMIN_EMAIL": "test@example.invalid",
                    "ADMIN_PASSWORD": "unused"}.items():
    os.environ.setdefault(name, value)
sys.path.insert(0, str(ROOT / "lab/real-seafile"))
import fidelity_probe  # noqa: E402


class ReopenGateTests(unittest.TestCase):
    def test_fresh_editor_and_visible_marker_are_required(self):
        self.assertTrue(fidelity_probe.reopen_verified(
            login_ok=True, ready=True, relay_body=b"saved", saved_body=b"saved",
            marker_visible=True))

    def test_successful_api_readback_cannot_hide_failed_editor_reopen(self):
        api_readback = b"saved"
        self.assertEqual(api_readback, b"saved")
        self.assertFalse(fidelity_probe.reopen_verified(
            login_ok=False, ready=False, relay_body=None, saved_body=b"saved",
            marker_visible=None))

    def test_editor_must_receive_exact_saved_bytes_and_render_marker(self):
        self.assertFalse(fidelity_probe.reopen_verified(
            login_ok=True, ready=True, relay_body=b"other", saved_body=b"saved",
            marker_visible=True))
        self.assertFalse(fidelity_probe.reopen_verified(
            login_ok=True, ready=True, relay_body=b"saved", saved_body=b"saved",
            marker_visible=None))

    def test_new_seafile_version_requires_distinct_version_id(self):
        self.assertFalse(fidelity_probe._new_version([], [{"id": "v1"}]))
        self.assertFalse(fidelity_probe._new_version([{"id": "v1"}], [{"id": "v1"}]))
        self.assertTrue(fidelity_probe._new_version([{"id": "v1"}], [{"id": "v2"}]))

    def test_ocr_helper_reports_unavailable_and_detects_visible_marker(self):
        with patch.object(fidelity_probe.shutil, "which", return_value=None):
            self.assertIsNone(fidelity_probe.visible_marker(b"png", "typedmarker"))
        completed = type("Completed", (), {"stdout": b"typedmarker", "stderr": b""})()
        with patch.object(fidelity_probe.shutil, "which", return_value="/usr/bin/tesseract"), \
                patch.object(fidelity_probe.subprocess, "run", return_value=completed):
            self.assertTrue(fidelity_probe.visible_marker(b"png", "typedmarker"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
