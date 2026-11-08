#!/usr/bin/env python3
"""Offline check: python3 tests/test_pptx_roundtrip_fixture.py."""
from io import BytesIO
from pathlib import Path
import sys
import unittest
from zipfile import ZipFile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lab/real-seafile"))
import pptx_roundtrip_fixture as fixture


def package(changes=None, remove=()):
    parts = dict(fixture.PARTS)
    parts.update(changes or {})
    out = BytesIO()
    with ZipFile(out, "w") as archive:
        for name, value in parts.items():
            if name not in remove:
                archive.writestr(name, value)
    return out.getvalue()


class FixtureTests(unittest.TestCase):
    def test_positive_and_deterministic(self):
        data = fixture.synthetic_pptx()
        self.assertEqual(data, fixture.synthetic_pptx())
        self.assertEqual(fixture.slide_texts(data), [[fixture.TITLE]])
        slide = fixture.PARTS["ppt/slides/slide1.xml"]
        split = slide.replace(fixture.TITLE, "ArtCraft</a:t></a:r><a:r><a:t> synthetic PPTX")
        self.assertEqual(fixture.slide_texts(package({"ppt/slides/slide1.xml": split})), [[fixture.TITLE]])

    def test_metadata_notes_and_unreferenced_slide_do_not_count(self):
        path = "ppt/slides/slide1.xml"
        blank = fixture.PARTS[path].replace(fixture.TITLE, "Other title")
        data = package({path: blank, "docProps/core.xml": f"<metadata>{fixture.TITLE}</metadata>",
                        "ppt/notesSlides/notesSlide1.xml": fixture.PARTS[path],
                        "ppt/slides/slide99.xml": fixture.PARTS[path]})
        self.assertEqual(fixture.slide_texts(data), [["Other title"]])

    def test_slide_relationship_target_and_order_are_authoritative(self):
        relpath = "ppt/_rels/presentation.xml.rels"
        moved = fixture.PARTS["ppt/slides/slide1.xml"].replace(fixture.TITLE, "Edited title")
        data = package({relpath: fixture.PARTS[relpath].replace("slides/slide1.xml", "slides/slide7.xml"),
                        "ppt/slides/slide7.xml": moved})
        self.assertEqual(fixture.slide_texts(data), [["Edited title"]])

    def test_malformed_missing_wrong_mime_and_unsafe(self):
        relpath = "ppt/_rels/presentation.xml.rels"
        rels = fixture.PARTS[relpath]
        invalid = [b"not a zip", package({"ppt/presentation.xml": "<broken"}),
                   package(remove=("ppt/slides/slide1.xml",)),
                   package({"[Content_Types].xml": fixture.PARTS["[Content_Types].xml"].replace(fixture.MIME, "application/xml")}),
                   package({relpath: rels.replace('Target="slides/slide1.xml"', 'Target="https://example.invalid/slide.xml" TargetMode="External"')}),
                   package({relpath: rels.replace('Target="slides/slide1.xml"', 'Target="../../escape.xml"')}),
                   package({"ppt/presentation.xml": "x" * (fixture.MAX_XML_BYTES + 1)}),
                   package({"docProps/core.xml": '<!DOCTYPE x [<!ENTITY x "marker">]><x>&x;</x>'})]
        for data in invalid:
            with self.subTest(size=len(data)), self.assertRaises(ValueError):
                fixture.slide_texts(data)


if __name__ == "__main__":
    unittest.main()
