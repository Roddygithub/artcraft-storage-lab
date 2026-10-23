#!/usr/bin/env python3
"""Check the synthetic workbook stores a real OOXML formula and cached value."""

from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

NS = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
fixture = Path(__file__).parent / "fixtures/synthetic.xlsx"
with zipfile.ZipFile(fixture) as archive:
    sheet = ET.fromstring(archive.read("xl/worksheets/sheet1.xml"))

formula_cell = sheet.find(".//x:c[@r='B3']", NS)
formula = formula_cell.find("x:f", NS)
cached = formula_cell.find("x:v", NS)
assert formula is not None and formula.text == "SUM(B2:B2)"
assert cached is not None and cached.text == "42"

print("PASS: B3 contains an OOXML formula element and cached result")
