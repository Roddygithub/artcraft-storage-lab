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

NS = {"w": corpus.W}


class FidelityCorpusTests(unittest.TestCase):
    def test_three_deterministic_cases_are_well_formed_docx_packages(self):
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

    def test_used_wordprocessingml_property_elements_follow_schema_order(self):
        for data in corpus.corpus().values():
            with zipfile.ZipFile(io.BytesIO(data)) as docx:
                styles = ET.fromstring(docx.read("word/styles.xml"))
                for style_id in ("Title", "Heading1", "Heading2"):
                    style = styles.find(f"w:style[@w:styleId='{style_id}']", NS)
                    self.assertIsNotNone(style)
                    children = [child.tag.rsplit("}", 1)[-1] for child in style]
                    self.assertLess(children.index("pPr"), children.index("rPr"))

                document = ET.fromstring(docx.read("word/document.xml"))
                table = document.find(".//w:tbl", NS)
                if table is None:
                    continue
                table_properties = table.find("w:tblPr", NS)
                self.assertIsNotNone(table_properties)
                table_children = [child.tag.rsplit("}", 1)[-1]
                                  for child in table_properties]
                self.assertLess(table_children.index("tblW"),
                                table_children.index("tblBorders"))

                header_cell_properties = table.find("w:tr/w:tc/w:tcPr", NS)
                self.assertIsNotNone(header_cell_properties)
                cell_children = [child.tag.rsplit("}", 1)[-1]
                                 for child in header_cell_properties]
                self.assertLess(cell_children.index("tcW"), cell_children.index("shd"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
