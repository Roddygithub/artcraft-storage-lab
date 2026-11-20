#!/usr/bin/env python3
"""PPTX semantic comparison and deterministic negative mutation checks."""
from io import BytesIO
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
import zipfile
from unittest.mock import Mock
from xml.etree import ElementTree as ET

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
import pptx_roundtrip_fixture  # noqa: E402

P = "{http://schemas.openxmlformats.org/presentationml/2006/main}"
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
FIXTURE = fidelity_corpus.corpus()["fidelity-deck.pptx"]


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


def shape_by_text(root, text):
    return next(shape for shape in root.findall(f".//{P}sp")
                if text in "".join(node.text or "" for node in shape.findall(f".//{A}t")))


class PptxFidelityMutationTests(unittest.TestCase):
    def assert_feature_regresses(self, body, feature):
        result = fidelity_compare.compare(FIXTURE, body)
        self.assertIn(result["verdicts"][feature], ("ALTERED", "LOST", "NOT_VERIFIED"),
                      result["verdicts"])
        self.assertIn(feature, result["regressions"])
        return result

    def test_intact_fixtures_keep_semantic_verdicts(self):
        for body in (FIXTURE, pptx_roundtrip_fixture.synthetic_pptx()):
            with self.subTest(size=len(body)):
                result = fidelity_compare.compare(body, body)
                self.assertEqual(result["regressions"], [], result["verdicts"])
                self.assertEqual(result["verdicts"]["slide_order"], "PRESERVED")
                self.assertEqual(result["verdicts"]["geometry"], "PRESERVED")
                self.assertEqual(result["verdicts"]["fills"], "PRESERVED")

    def test_retained_deckcraft_save_has_no_unexpected_semantic_regressions(self):
        evidence = ROOT / "lab/real-seafile/results/2026-11-17-proxmox-isolated"
        original = (evidence / "pptx-original.pptx").read_bytes()
        saved = (evidence / "pptx-readback.pptx").read_bytes()
        saved_features = fidelity_compare.pptx_features(saved)
        saved_text = "\n".join(text for slide in saved_features["slide_data"]
                                for shape in slide["shapes"] for text in shape["text"])
        marker = re.search(r"pptxtyped[0-9a-f]{10}", saved_text)
        self.assertIsNotNone(marker)
        result = fidelity_compare.compare(original, saved, marker.group(0))
        self.assertEqual(result["regressions"], [], result["verdicts"])

    def test_non_target_text_change_is_detected_by_shape_identity(self):
        def change(root):
            title = shape_by_text(root, "ArtCraft fidelity deck")
            title.find(f".//{A}t").text = "Changed unrelated title"
        self.assert_feature_regresses(xml_change("ppt/slides/slide1.xml", change), "texts")

    def test_width_height_and_position_mutations_are_detected(self):
        def update_geometry(attribute, value):
            def change(root):
                shape_by_text(root, "ArtCraft fidelity deck").find(f"{P}spPr/{A}xfrm/{A}ext").set(
                    attribute, str(value))
            return change
        self.assert_feature_regresses(
            xml_change("ppt/slides/slide1.xml", update_geometry("cx", 7315201)), "geometry")
        self.assert_feature_regresses(
            xml_change("ppt/slides/slide1.xml", update_geometry("cy", 1371601)), "geometry")

        def move(root):
            shape_by_text(root, "ArtCraft fidelity deck").find(f"{P}spPr/{A}xfrm/{A}off").set("x", "914401")
        self.assert_feature_regresses(xml_change("ppt/slides/slide1.xml", move), "geometry")

    def test_shape_color_and_fill_type_mutations_are_detected(self):
        def change_color(root):
            title = shape_by_text(root, "ArtCraft fidelity deck")
            color = title.find(f"{P}spPr/{A}solidFill/{A}srgbClr")
            color.set("val", "0000FF")
        self.assert_feature_regresses(xml_change("ppt/slides/slide1.xml", change_color), "fills")

        def remove_fill(root):
            title = shape_by_text(root, "ArtCraft fidelity deck")
            properties = title.find(f"{P}spPr")
            properties.remove(properties.find(f"{A}solidFill"))
            ET.SubElement(properties, A + "noFill")
        self.assert_feature_regresses(xml_change("ppt/slides/slide1.xml", remove_fill), "fills")

    def test_image_replacement_under_same_name_is_detected(self):
        changed = mutate("ppt/media/image1.png", lambda data: data[:-1] + bytes([data[-1] ^ 1]))
        self.assert_feature_regresses(changed, "images")

    def test_shape_removal_is_detected(self):
        def remove(root):
            tree = root.find(f".//{P}spTree")
            shape = shape_by_text(root, "ArtCraft fidelity deck")
            tree.remove(shape)
        self.assert_feature_regresses(xml_change("ppt/slides/slide1.xml", remove), "shapes")

    def test_presentation_relationship_order_is_detected(self):
        def swap(root):
            listing = root.find(f"{P}sldIdLst")
            slides = list(listing)
            listing.remove(slides[0])
            listing.remove(slides[1])
            listing.insert(0, slides[1])
            listing.insert(1, slides[0])
        self.assert_feature_regresses(xml_change("ppt/presentation.xml", swap), "slide_order")

    def test_removing_a_referenced_slide_is_detected(self):
        def remove_slide(root):
            listing = root.find(f"{P}sldIdLst")
            listing.remove(listing[-1])
        self.assert_feature_regresses(xml_change("ppt/presentation.xml", remove_slide), "slide_count")

    def test_intentional_marker_is_narrow_and_does_not_hide_other_edits(self):
        marker = "intentional-deck-edit-123"

        def edit_target(root):
            title = shape_by_text(root, "ArtCraft fidelity deck")
            title.find(f".//{A}t").text += marker
        allowed = fidelity_compare.compare(FIXTURE,
                                           xml_change("ppt/slides/slide1.xml", edit_target), marker)
        self.assertEqual(allowed["verdicts"]["texts"], "PRESERVED", allowed["verdicts"])
        self.assertEqual(allowed["regressions"], [], allowed["verdicts"])

        # The unrelated change is on a different slide, so mutate that package part too.
        edited = xml_change("ppt/slides/slide1.xml", edit_target)
        output = BytesIO()
        with zipfile.ZipFile(BytesIO(edited)) as source, zipfile.ZipFile(
                output, "w", zipfile.ZIP_DEFLATED) as target:
            for info in source.infolist():
                body = source.read(info.filename)
                if info.filename == "ppt/slides/slide2.xml":
                    root = ET.fromstring(body)
                    shape_by_text(root, "Second slide heading").find(f".//{A}t").text = "Corrupted"
                    body = ET.tostring(root, encoding="utf-8", xml_declaration=True)
                target.writestr(info, body)
        result = fidelity_compare.compare(FIXTURE, output.getvalue(), marker)
        self.assertIn("texts", result["regressions"])

    def test_missing_required_slide_relationship_fails_closed(self):
        result = self.assert_feature_regresses(
            remove_part("ppt/_rels/presentation.xml.rels"), "document")
        self.assertEqual(result["verdicts"]["document"], "NOT_VERIFIED")
        invalid = fidelity_compare.compare(FIXTURE, b"not a zip package")
        self.assertEqual(invalid["verdicts"]["document"], "NOT_VERIFIED")
        self.assertIn("document", invalid["regressions"])

    def test_api_cli_probe_json_and_incomplete_package_exit_status(self):
        result = fidelity_compare.compare(FIXTURE, FIXTURE)
        self.assertEqual(json.loads(json.dumps(result))["regressions"], [])
        with tempfile.TemporaryDirectory() as temp:
            original, saved, report = (Path(temp) / name for name in
                                       ("original.pptx", "saved.pptx", "comparison.json"))
            original.write_bytes(FIXTURE)
            saved.write_bytes(FIXTURE)
            command = [sys.executable, str(ROOT / "lab/real-seafile/fidelity_compare.py"),
                       str(original), str(saved), "--json", str(report)]
            completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True,
                                       check=False)
            self.assertEqual(completed.returncode, 0, completed.stderr + completed.stdout)
            self.assertEqual(json.loads(report.read_text())["regressions"], [])

            saved.write_bytes(remove_part("ppt/_rels/presentation.xml.rels"))
            completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True,
                                       check=False)
            self.assertEqual(completed.returncode, 1, completed.stderr + completed.stdout)
            failed = json.loads(report.read_text())
            self.assertEqual(failed["verdicts"]["document"], "NOT_VERIFIED")

            probe = fidelity_probe.compare_saved_file(True, "pptx", FIXTURE, FIXTURE,
                                                      "marker", Mock())
            probe_path = Path(temp) / "probe.json"
            fidelity_probe.write_json(probe_path, probe)
            self.assertEqual(json.loads(probe_path.read_text())["regressions"], [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
