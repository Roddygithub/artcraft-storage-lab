#!/usr/bin/env python3
"""Offline checks for the deterministic legacy/OpenDocument viewing fixtures.

Run: python3 tests/test_legacy_fixtures.py

Scope: fixture integrity (bytes, marker, checksums), the bridge name-to-bytes
signature guard, and the opt-in viewing routing map. This proves *routing and
fixture* evidence only. It does not open anything in Seafile, run a browser,
import a document in an editor, or replace any ONLYOFFICE format.
"""
from __future__ import annotations

import hashlib
import io
from pathlib import Path
import sys
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "bridge"))

from bridge.app import Config, content_matches_extension, load_editors  # noqa: E402

MARKER = b"GR-LEGACY-MARKER-20261108"
FIXTURES = ROOT / "lab/real-seafile/fixtures/legacy"
VIEWING_MAP = ROOT / "lab/real-seafile/editors.viewing.json"

# matrix format -> (fixture file, expected editor or None when no documented Craft import exists)
LEGACY = {
    "doc":   ("doc.doc",     "wordcraft"),
    "odt":   ("doc.odt",     "wordcraft"),
    "fodt":  ("doc.fodt",    None),
    "xls":   ("sheet.xls",   "gridcraft"),
    "ods":   ("sheet.ods",   "gridcraft"),
    "fods":  ("sheet.fods",  None),
    "csv":   ("sheet.csv",   "gridcraft"),
    "ppt":   ("slide.ppt",   None),
    "odp":   ("slide.odp",   None),
    "fodp":  ("slide.fodp",  None),
    "pps":   ("slide.pps",   None),
    "ppsx":  ("slide.ppsx",  None),
}


def marker_present(data: bytes) -> bool:
    if MARKER in data or MARKER.decode().encode("utf-16-le") in data:
        return True
    if data[:2] == b"PK":
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            return any(MARKER in zf.read(name) for name in zf.namelist())
    return False


class LegacyFixtureTests(unittest.TestCase):
    def test_every_required_viewing_format_has_a_fixture(self):
        for ext, (name, _) in LEGACY.items():
            path = FIXTURES / name
            self.assertTrue(path.is_file(), f"{ext}: {name} is missing")
            self.assertFalse(path.is_symlink(), ext)

    def test_checksums_match_the_committed_bytes(self):
        lines = (FIXTURES / "SHA256SUMS").read_text().splitlines()
        listed = {}
        for line in lines:
            digest, name = line.split()
            listed[name] = digest
        self.assertEqual(set(listed), {name for name, _ in LEGACY.values()},
                         "SHA256SUMS must list exactly the fixture set")
        for name, digest in listed.items():
            actual = hashlib.sha256((FIXTURES / name).read_bytes()).hexdigest()
            self.assertEqual(actual, digest, name)

    def test_every_fixture_carries_the_marker(self):
        for ext, (name, _) in LEGACY.items():
            self.assertTrue(marker_present((FIXTURES / name).read_bytes()), ext)

    def test_bridge_signature_guard_accepts_every_fixture(self):
        for ext, (name, _) in LEGACY.items():
            data = (FIXTURES / name).read_bytes()
            self.assertTrue(content_matches_extension(ext, data), ext)

    def test_viewing_map_is_loadable_and_routes_only_documented_imports(self):
        editors = load_editors(str(VIEWING_MAP))
        cfg = Config(public_url="https://bridge.example",
                     seahub_origin="https://seafile.example", editors=editors)
        routed = {ext: LEGACY[ext][1] for ext in LEGACY if LEGACY[ext][1]}
        for ext, editor in routed.items():
            self.assertEqual(cfg.extension_editor.get(ext), editor, ext)
        for ext, (_, editor) in LEGACY.items():
            if editor is None:
                self.assertNotIn(ext, cfg.extension_editor,
                                 f"{ext} has no documented Craft import; it must stay unrouted")

    def test_viewing_map_keeps_the_base_routes(self):
        cfg = Config(public_url="https://bridge.example", seahub_origin="https://seafile.example",
                     editors=load_editors(str(VIEWING_MAP)))
        for ext, editor in (("docx", "wordcraft"), ("xlsx", "gridcraft"), ("pdf", "pdfcraft"),
                            ("dxf", "cadcraft"), ("svg", "vectorcraft"), ("figcraft", "figcraft")):
            self.assertEqual(cfg.extension_editor.get(ext), editor, ext)


if __name__ == "__main__":
    unittest.main(verbosity=2)
