#!/usr/bin/env python3
"""Verify marker rendering and the FODS raw-XML failure in retained screenshots."""
import json
from pathlib import Path
import re
import subprocess
import sys

from PIL import Image

HERE = Path(__file__).resolve().parent
MARKER = "grlegacymarker20261108"


def ocr(name, crop=None):
    image = Image.open(HERE / name)
    if crop:
        image = image.crop(crop).resize(((crop[2] - crop[0]) * 4,
                                        (crop[3] - crop[1]) * 4))
    result = subprocess.run(["tesseract", "stdin", "stdout", "--psm", "6"],
                            input=_png(image), capture_output=True, check=True)
    return result.stdout.decode("utf-8", "replace")


def _png(image):
    from io import BytesIO
    out = BytesIO()
    image.save(out, format="PNG")
    return out.getvalue()


def normalized(text):
    return re.sub(r"[^a-z0-9]", "", text.lower())


def main():
    summary = json.loads((HERE / "import-summary.json").read_text())
    cases = {case["fixture"]: case for case in summary["cases"]}
    assert summary["passed"] == 7 and summary["failed"] == 0
    assert all(cases[name]["ok"] for name in (
        "doc.doc", "doc.odt", "sheet.xls", "sheet.ods", "sheet.fods",
        "sheet.csv", "slide.ppsx"))

    rendered = {
        "doc_doc.png": None, "doc_odt.png": None,
        "sheet_xls.png": (20, 220, 440, 280),
        "sheet_ods.png": (20, 220, 440, 280),
        "sheet_csv.png": None,
        "slide_ppsx.png": (390, 240, 780, 290),
    }
    for name, crop in rendered.items():
        text = normalized(ocr(name, crop))
        assert MARKER in text, f"fixture marker not visible in {name}: {text[:180]}"
        print(f"PASS visible marker: {name}")

    fods = ocr("sheet_fods.png")
    assert "office:document" in fods.lower(), "expected the visible FODS XML leak"
    print("EXPECTED FINDING: FODS displays office:document XML; rendering is unsupported")


if __name__ == "__main__":
    main()
