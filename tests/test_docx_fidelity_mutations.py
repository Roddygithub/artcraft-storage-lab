#!/usr/bin/env python3
"""Semantic DOCX fidelity regressions and deterministic mutation checks."""
from io import BytesIO
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile
from xml.etree import ElementTree as ET
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
for name, value in {"SEAFILE_URL": "http://127.0.0.1",
                    "BRIDGE_URL": "http://127.0.0.1:8778",
                    "ADMIN_EMAIL": "test@example.invalid",
                    "ADMIN_PASSWORD": "unused"}.items():
    os.environ.setdefault(name, value)
sys.path.insert(0, str(ROOT / "lab/real-seafile"))
import docx_fidelity_corpus  # noqa: E402
import fidelity_compare  # noqa: E402
import fidelity_corpus  # noqa: E402
import fidelity_probe  # noqa: E402

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
FIXTURE = fidelity_corpus.corpus()["fidelity-report.docx"]


def mutate(part, change):
    output = BytesIO()
    with zipfile.ZipFile(BytesIO(FIXTURE)) as source, zipfile.ZipFile(
            output, "w", zipfile.ZIP_DEFLATED) as target:
        for info in source.infolist():
            body = source.read(info.filename)
            if info.filename == part:
                body = change(body)
            target.writestr(info, body)
    return output.getvalue()


def remove_part(part):
    output = BytesIO()
    with zipfile.ZipFile(BytesIO(FIXTURE)) as source, zipfile.ZipFile(
            output, "w", zipfile.ZIP_DEFLATED) as target:
        for info in source.infolist():
            if info.filename != part:
                target.writestr(info, source.read(info.filename))
    return output.getvalue()


def xml_change(part, callback):
    def update(body):
        root = ET.fromstring(body)
        callback(root)
        return ET.tostring(root, encoding="utf-8", xml_declaration=True)
    return mutate(part, update)


def find_paragraph(root, text):
    return next(p for p in root.findall(f".//{W}p") if text in "".join(p.itertext()))


class DocxFidelityMutationTests(unittest.TestCase):
    def assert_feature_regresses(self, body, feature):
        result = fidelity_compare.compare(FIXTURE, body)
        self.assertIn(result["verdicts"][feature], ("ALTERED", "LOST"), result["verdicts"])
        self.assertIn(feature, result["regressions"])
        return result

    def test_intact_main_and_legacy_fixtures_have_no_regressions(self):
        self.assertEqual(fidelity_compare.compare(FIXTURE, FIXTURE)["regressions"], [])
        for body in docx_fidelity_corpus.corpus().values():
            with self.subTest(case="legacy fixture"):
                self.assertEqual(fidelity_compare.compare(body, body)["regressions"], [])

    def test_real_archived_wordcraft_save_has_no_semantic_regressions(self):
        saved_path = ROOT / "lab/real-seafile/results/2026-11-18-clipboard-and-fidelity/fidelity/docx-after-save.docx"
        probe_path = ROOT / "lab/real-seafile/results/2026-11-18-clipboard-and-fidelity/fidelity/fidelity.json"
        marker = json.loads(probe_path.read_text(encoding="utf-8"))["cases"]["docx"]["marker"]
        result = fidelity_compare.compare(FIXTURE, saved_path.read_bytes(), marker=marker)
        self.assertEqual(result["regressions"], [], result["verdicts"])

    def test_table_cell_content_change_is_detected(self):
        body = xml_change("word/document.xml", lambda root:
                          setattr(find_paragraph(root, "Alpha").find(f".//{W}t"), "text", "Alphx"))
        self.assert_feature_regresses(body, "tables")

    def test_table_cell_structure_and_width_changes_are_detected(self):
        def remove_cell(root):
            table = root.find(f".//{W}tbl")
            table.find(f"{W}tr").remove(table.find(f"{W}tr/{W}tc"))
        self.assert_feature_regresses(xml_change("word/document.xml", remove_cell), "tables")

        def alter_width(root):
            root.find(f".//{W}tblW").set(W + "w", "5000")
        self.assert_feature_regresses(xml_change("word/document.xml", alter_width), "tables")

    def test_replacing_image_bytes_under_same_name_is_detected(self):
        body = mutate("word/media/image1.png", lambda data: data[:-1] + bytes([data[-1] ^ 1]))
        self.assert_feature_regresses(body, "images")

    def test_run_colour_change_is_detected(self):
        def change(root):
            color = root.find(f".//{W}color[@{W}val='C00000']")
            self.assertIsNotNone(color)
            color.set(W + "val", "0000FF")
        self.assert_feature_regresses(xml_change("word/document.xml", change), "colour_runs")

    def test_bold_italic_paragraph_style_and_style_definition_changes_are_detected(self):
        bold = xml_change("word/document.xml", lambda root: root.find(f".//{W}b").set(W + "val", "0"))
        self.assert_feature_regresses(bold, "bold_runs")
        italic = xml_change("word/document.xml", lambda root: root.find(f".//{W}i").set(W + "val", "0"))
        self.assert_feature_regresses(italic, "italic_runs")

        def paragraph_style(root):
            find_paragraph(root, "Heading one").find(f"{W}pPr/{W}pStyle").set(W + "val", "Normal")
        self.assert_feature_regresses(xml_change("word/document.xml", paragraph_style), "paragraph_styles")

        def style_color(root):
            root.find(f".//{W}style[@{W}styleId='Title']").find(f".//{W}color").set(W + "val", "FF0000")
        self.assert_feature_regresses(xml_change("word/styles.xml", style_color), "style_definitions")

    def test_deleting_a_list_paragraph_is_detected(self):
        def change(root):
            paragraph = find_paragraph(root, "First bullet")
            parent = next(item for item in root.iter() if paragraph in list(item))
            parent.remove(paragraph)
        self.assert_feature_regresses(xml_change("word/document.xml", change), "list_paragraphs")

    def test_accented_text_change_is_detected(self):
        def change(root):
            text = find_paragraph(root, "Café").find(f".//{W}t")
            text.text = text.text.replace("é", "e", 1)
        self.assert_feature_regresses(xml_change("word/document.xml", change), "accents")

    def test_cjk_text_change_is_detected(self):
        def change(root):
            text = find_paragraph(root, "日本語").find(f".//{W}t")
            text.text = text.text.replace("日", "中", 1)
        self.assert_feature_regresses(xml_change("word/document.xml", change), "cjk")

    def test_section_page_margin_change_is_detected(self):
        def change(root):
            root.find(f".//{W}pgMar").set(W + "top", "1450")
        self.assert_feature_regresses(xml_change("word/document.xml", change), "sectPr")

    def test_header_and_footer_content_changes_are_detected(self):
        header = xml_change("word/header1.xml", lambda root:
                            setattr(root.find(f".//{W}t"), "text", "ALTERED HEADER"))
        self.assert_feature_regresses(header, "header")
        footer = xml_change("word/footer1.xml", lambda root:
                            root.find(f".//{W}fldSimple").set(W + "instr", "NUMPAGES"))
        self.assert_feature_regresses(footer, "footer_page_field")

    def test_allowed_marker_does_not_hide_an_unrelated_change(self):
        marker = "intentional-edit-123"
        def intentional(root):
            para = find_paragraph(root, "Text after the page break")
            para.find(f".//{W}t").text += marker
        allowed = xml_change("word/document.xml", intentional)
        self.assertEqual(fidelity_compare.compare(FIXTURE, allowed, marker)["regressions"], [])

        def unauthorized(root):
            intentional(root)
            color = root.find(f".//{W}color[@{W}val='C00000']")
            color.set(W + "val", "0000FF")
        result = fidelity_compare.compare(FIXTURE, xml_change("word/document.xml", unauthorized), marker)
        self.assertIn("colour_runs", result["regressions"])
        self.assertIn("paragraphs", result["regressions"])

    def test_missing_media_and_invalid_document_fail_closed(self):
        missing_media = remove_part("word/media/image1.png")
        result = fidelity_compare.compare(FIXTURE, missing_media)
        self.assertEqual(result["verdicts"]["document"], "NOT_VERIFIED")
        self.assertIn("document", result["regressions"])
        invalid = mutate("word/document.xml", lambda _data: b"<w:document")
        result = fidelity_compare.compare(FIXTURE, invalid)
        self.assertEqual(result["verdicts"]["document"], "NOT_VERIFIED")
        self.assertIn("document", result["regressions"])

        incomplete = xml_change("word/document.xml", lambda root: root.remove(root.find(f"{W}body")))
        result = fidelity_compare.compare(FIXTURE, incomplete)
        self.assertEqual(result["verdicts"]["document"], "NOT_VERIFIED")
        self.assertIn("document", result["regressions"])

    def test_api_cli_and_probe_report_json_are_complete(self):
        result = fidelity_compare.compare(FIXTURE, FIXTURE)
        self.assertEqual(json.loads(json.dumps(result, ensure_ascii=False))["regressions"], [])
        with tempfile.TemporaryDirectory() as temp:
            original, saved, report = (Path(temp) / name for name in
                                       ("original.docx", "saved.docx", "comparison.json"))
            original.write_bytes(FIXTURE)
            saved.write_bytes(FIXTURE)
            completed = subprocess.run(
                [sys.executable, str(ROOT / "lab/real-seafile/fidelity_compare.py"),
                 str(original), str(saved), "--json", str(report)], cwd=ROOT,
                capture_output=True, text=True, check=False)
            self.assertEqual(completed.returncode, 0, completed.stderr + completed.stdout)
            self.assertEqual(json.loads(report.read_text(encoding="utf-8"))["regressions"], [])
            saved.write_bytes(b"not an OOXML package")
            completed = subprocess.run(
                [sys.executable, str(ROOT / "lab/real-seafile/fidelity_compare.py"),
                 str(original), str(saved), "--json", str(report)], cwd=ROOT,
                capture_output=True, text=True, check=False)
            self.assertEqual(completed.returncode, 1, completed.stderr + completed.stdout)
            failed_report = json.loads(report.read_text(encoding="utf-8"))
            self.assertEqual(failed_report["verdicts"]["document"], "NOT_VERIFIED")
            self.assertIn("document", failed_report["regressions"])
            probe_result = fidelity_probe.compare_saved_file(True, "docx", FIXTURE, FIXTURE,
                                                             "marker", Mock())
            probe_report = Path(temp) / "probe.json"
            fidelity_probe.write_json(probe_report, probe_result)
            self.assertEqual(json.loads(probe_report.read_text(encoding="utf-8"))["regressions"], [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
