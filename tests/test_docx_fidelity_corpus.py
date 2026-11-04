#!/usr/bin/env python3
"""Fast validation for the deterministic OOXML corpus used by the fidelity replay."""
from __future__ import annotations

import io
import sys
import unittest
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lab" / "real-seafile"))
import docx_fidelity_corpus as corpus  # noqa: E402


class FidelityCorpusTests(unittest.TestCase):
    def test_three_deterministic_cases_are_valid_ooxml_packages(self):
        first = corpus.corpus()
        second = corpus.corpus()
        self.assertEqual(first, second)
        self.assertEqual(set(first), {
            "fidelity-prose.docx",
            "fidelity-structure.docx",
            "fidelity-layout.docx",
        })
        required_parts = {
            "[Content_Types].xml", "_rels/.rels", "word/document.xml",
            "word/_rels/document.xml.rels", "word/styles.xml",
            "word/numbering.xml", "word/header1.xml", "word/footer1.xml",
        }
        for name, data in first.items():
            with self.subTest(name=name), zipfile.ZipFile(io.BytesIO(data)) as docx:
                self.assertEqual(docx.testzip(), None)
                self.assertTrue(required_parts.issubset(docx.namelist()))
                self.assertTrue(all(info.date_time == (2020, 1, 1, 0, 0, 0)
                                    for info in docx.infolist()))
                for part in required_parts:
                    ET.fromstring(docx.read(part))
        with zipfile.ZipFile(io.BytesIO(first["fidelity-prose.docx"])) as docx:
            self.assertIn("Fidelity Case 1", docx.read("word/document.xml").decode())

    def test_fidelity_cases_cover_the_intended_formatting_features(self):
        docs = {name: data for name, data in corpus.corpus().items()}
        xml = {name: zipfile.ZipFile(io.BytesIO(data)).read("word/document.xml").decode()
               for name, data in docs.items()}
        self.assertIn("<w:b/>", xml["fidelity-prose.docx"])
        self.assertIn("<w:i/>", xml["fidelity-prose.docx"])
        self.assertIn("<w:numId w:val=\"1\"/>", xml["fidelity-structure.docx"])
        self.assertIn("<w:tbl>", xml["fidelity-structure.docx"])
        self.assertIn("w:type=\"page\"", xml["fidelity-layout.docx"])
        self.assertIn("Second page heading", xml["fidelity-layout.docx"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
