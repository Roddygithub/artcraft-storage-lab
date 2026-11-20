#!/usr/bin/env python3
"""XLSX fidelity comparator must reject same-count content/style mutations."""
from io import BytesIO
from pathlib import Path
import sys
import zipfile
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lab/real-seafile"))
import fidelity_compare  # noqa: E402
import fidelity_corpus  # noqa: E402

S = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
FIXTURE = fidelity_corpus.corpus()["fidelity-workbook.xlsx"]


def mutate(part, change):
    source = zipfile.ZipFile(BytesIO(FIXTURE))
    output = BytesIO()
    with source, zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as target:
        for info in source.infolist():
            data = source.read(info.filename)
            if info.filename == part:
                root = ET.fromstring(data)
                change(root)
                data = ET.tostring(root, encoding="utf-8", xml_declaration=True)
            target.writestr(info, data)
    return output.getvalue()


def set_formula(cell, text):
    cell.find(f"{S}f").text = text


def assert_regression(body, feature):
    result = fidelity_compare.compare(FIXTURE, body)
    assert result["verdicts"][feature] in ("ALTERED", "LOST"), result["verdicts"]
    assert feature in result["regressions"], result["regressions"]
    return result


assert not fidelity_compare.compare(FIXTURE, FIXTURE)["regressions"]

formula_mutation = mutate("xl/worksheets/sheet1.xml", lambda root: set_formula(
    root.find(f".//{S}c[@r='B5']"), "SUM(B2:B3)"))
formula_result = assert_regression(formula_mutation, "formulas")
assert formula_result["before"]["formula_count"] == formula_result["after"]["formula_count"]

reference_mutation = mutate("xl/worksheets/sheet1.xml", lambda root: set_formula(
    root.find(f".//{S}c[@r='C2']"), "Sheet2!B2"))
assert_regression(reference_mutation, "formulas")

value_mutation = mutate("xl/worksheets/sheet1.xml", lambda root: root.find(
    f".//{S}c[@r='B2']/{S}v").__setattr__("text", "11"))
assert_regression(value_mutation, "cell_values")
intentional = fidelity_compare.compare(FIXTURE, value_mutation, marker="11")
assert intentional["verdicts"]["cell_values"] == "PRESERVED"

def extra_value_mutation(root):
    root.find(f".//{S}c[@r='B2']/{S}v").text = "11"
    root.find(f".//{S}c[@r='B3']/{S}v").text = "99"

assert_regression(mutate("xl/worksheets/sheet1.xml", extra_value_mutation), "cell_values")

def date_format(root):
    root.find(f"{S}cellXfs/{S}xf[@numFmtId='14']").set("numFmtId", "0")

assert_regression(mutate("xl/styles.xml", date_format), "number_formats")


def fill(root):
    root.find(f".//{S}fill/{S}patternFill/{S}fgColor").set("rgb", "FFFF0000")

assert_regression(mutate("xl/styles.xml", fill), "fills")


def border(root):
    root.find(f"{S}borders/{S}border[2]/{S}left").set("style", "medium")

assert_regression(mutate("xl/styles.xml", border), "borders")

print("PASS: intact workbook preserved; 6 XLSX mutations detected")
