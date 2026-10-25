#!/usr/bin/env python3
"""Focused size-bound checks for the GR-041 staged asset helper."""

import importlib.util
import io
import stat
import struct
import tempfile
import unittest
import warnings
import zipfile
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location(
    "craft_web_zip", Path(__file__).parents[1] / "scripts/craft_web_zip.py"
)
craft_web_zip = importlib.util.module_from_spec(spec)
spec.loader.exec_module(craft_web_zip)


def make_zip(entries):
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as archive:
        for name, data in entries:
            archive.writestr(name, data)
    return output.getvalue()


class CraftZipLimitsTest(unittest.TestCase):
    def test_download_exact_limit_and_over_limit(self):
        data = b"12345"
        url = "https://example.invalid/asset.zip"
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "asset.zip"
            with patch.object(craft_web_zip.urllib.request, "urlopen", return_value=io.BytesIO(data)) as open_url:
                craft_web_zip.download(url, destination, len(data))
            open_url.assert_called_once_with(url, timeout=craft_web_zip.DOWNLOAD_TIMEOUT_SECONDS)
            self.assertEqual(destination.read_bytes(), data)
            with patch.object(craft_web_zip.urllib.request, "urlopen", return_value=io.BytesIO(data)):
                with self.assertRaisesRegex(ValueError, "exceeds"):
                    craft_web_zip.download("https://example.invalid/asset.zip", destination, len(data) - 1)

    def test_download_total_deadline(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "asset.zip"
            with patch.object(craft_web_zip.urllib.request, "urlopen", return_value=io.BytesIO(b"x")):
                with patch.object(craft_web_zip.time, "monotonic", side_effect=[0.0, 0.0, 2.0]):
                    with self.assertRaisesRegex(TimeoutError, "exceeds 1 seconds"):
                        craft_web_zip.download("https://example.invalid/asset.zip",
                                               destination, max_seconds=1)
            self.assertEqual(destination.read_bytes(), b"")

    def test_extraction_exact_limit_and_over_limit(self):
        archive = make_zip([("web/index.html", b"abc"), ("web/app.wasm", b"def")])
        with tempfile.TemporaryDirectory() as directory:
            zip_path = Path(directory) / "asset.zip"
            zip_path.write_bytes(archive)
            self.assertEqual(craft_web_zip.extract(zip_path, Path(directory) / "ok", 6), "web")
            with self.assertRaisesRegex(ValueError, "contents exceed"):
                craft_web_zip.extract(zip_path, Path(directory) / "over", 5)

    def test_entry_count_limit_is_checked_before_zipinfo_loading(self):
        archive = make_zip([("web/index.html", b"a"), ("web/app.wasm", b"b")])
        with tempfile.TemporaryDirectory() as directory:
            zip_path = Path(directory) / "asset.zip"
            zip_path.write_bytes(archive)
            with patch.object(craft_web_zip.zipfile, "ZipFile", side_effect=AssertionError("too late")):
                with self.assertRaisesRegex(ValueError, "more than 1 entries"):
                    craft_web_zip.extract(zip_path, Path(directory) / "out", max_entries=1)

    def test_duplicate_and_unsafe_paths_are_rejected(self):
        duplicate = io.BytesIO()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            with zipfile.ZipFile(duplicate, "w") as archive:
                archive.writestr("web/index.html", b"one")
                archive.writestr("web//index.html", b"two")
                archive.writestr("web/app.wasm", b"wasm")
        unsafe_archives = {
            "traversal": make_zip([("../escape", b"x"), ("web/index.html", b"a"),
                                   ("web/app.wasm", b"b")]),
            "absolute": make_zip([("/escape", b"x"), ("web/index.html", b"a"),
                                  ("web/app.wasm", b"b")]),
            "backslash": make_zip([("web\\escape", b"x"), ("web/index.html", b"a"),
                                   ("web/app.wasm", b"b")]),
            "multi-root": make_zip([("web/index.html", b"a"), ("other/app.wasm", b"b")]),
            "missing-index": make_zip([("web/app.wasm", b"b")]),
            "missing-wasm": make_zip([("web/index.html", b"a")]),
        }
        with tempfile.TemporaryDirectory() as directory:
            duplicate_path = Path(directory) / "duplicate.zip"
            duplicate_path.write_bytes(duplicate.getvalue())
            with self.assertRaisesRegex(ValueError, "duplicate ZIP entry"):
                craft_web_zip.extract(duplicate_path, Path(directory) / "duplicate-out")
            for label, data in unsafe_archives.items():
                path = Path(directory) / f"{label}.zip"
                path.write_bytes(data)
                with self.subTest(kind=label):
                    with self.assertRaises((ValueError, zipfile.BadZipFile)):
                        craft_web_zip.extract(path, Path(directory) / f"{label}-out")

    def test_zip64_and_multi_disk_records_are_rejected(self):
        original = make_zip([("web/index.html", b"a"), ("web/app.wasm", b"b")])
        eocd = original.rfind(b"PK\x05\x06")
        zip64 = bytearray(original)
        struct.pack_into("<HH", zip64, eocd + 8, 0xFFFF, 0xFFFF)
        zip64_locator = (original[:eocd] + b"PK\x06\x07" + b"\x00" * 16
                         + original[eocd:])
        multi_disk = bytearray(original)
        struct.pack_into("<H", multi_disk, eocd + 4, 1)
        with tempfile.TemporaryDirectory() as directory:
            for label, data, message in (
                    ("zip64", zip64, "ZIP64"),
                    ("zip64-locator", zip64_locator, "ZIP64"),
                    ("multi-disk", multi_disk, "multi-disk")):
                path = Path(directory) / f"{label}.zip"
                path.write_bytes(data)
                with self.subTest(kind=label):
                    with self.assertRaisesRegex((ValueError, zipfile.BadZipFile), message):
                        craft_web_zip.extract(path, Path(directory) / f"{label}-out")

    def test_symlink_entries_are_rejected(self):
        archive_data = io.BytesIO()
        with zipfile.ZipFile(archive_data, "w") as archive:
            archive.writestr("web/index.html", b"html")
            archive.writestr("web/app.wasm", b"wasm")
            link = zipfile.ZipInfo("web/link")
            link.create_system = 3
            link.external_attr = (stat.S_IFLNK | 0o777) << 16
            archive.writestr(link, "target")
        with tempfile.TemporaryDirectory() as directory:
            zip_path = Path(directory) / "symlink.zip"
            zip_path.write_bytes(archive_data.getvalue())
            with self.assertRaisesRegex(ValueError, "unsafe ZIP entry"):
                craft_web_zip.extract(zip_path, Path(directory) / "out")

    def test_malformed_archive_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            zip_path = Path(directory) / "broken.zip"
            zip_path.write_bytes(b"not a zip")
            with self.assertRaises(zipfile.BadZipFile):
                craft_web_zip.extract(zip_path, Path(directory) / "out")


if __name__ == "__main__":
    unittest.main()
