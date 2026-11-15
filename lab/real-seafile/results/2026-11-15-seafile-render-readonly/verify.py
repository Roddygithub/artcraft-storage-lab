#!/usr/bin/env python3
"""Verify sanitized Seafile route/render evidence and screenshot markers."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
from difflib import SequenceMatcher

from PIL import Image

HERE = Path(__file__).resolve().parent
MARKER = "grlegacymarker20261108"


def verify_hashes():
    expected = {}
    for line in (HERE / "SHA256SUMS").read_text().splitlines():
        digest, name = line.split(maxsplit=1)
        expected[name.strip()] = digest
    actual = {p.relative_to(HERE).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in HERE.rglob("*") if p.is_file() and p.name != "SHA256SUMS"}
    assert actual == expected


def load(name, passed, checks):
    data = json.loads((HERE / name).read_text())
    assert data["passed"] == passed and data["failed"] == 0
    assert len(data["checks"]) == checks
    assert all(check["ok"] for check in data["checks"])
    return {check["name"]: check for check in data["checks"]}


def ocr(name, region):
    with Image.open(HERE / name) as source:
        width, height = source.size
        x1, y1, x2, y2 = region
        box = (int(width*x1), int(height*y1), int(width*x2), int(height*y2))
        crop = source.crop(box).resize(((box[2]-box[0])*3, (box[3]-box[1])*3))
        from io import BytesIO
        png = BytesIO()
        crop.save(png, format="PNG")
    result = subprocess.run(["tesseract", "stdin", "stdout", "--psm", "6"],
                            input=png.getvalue(), capture_output=True,
                            timeout=10, check=True)
    return re.sub(r"[^a-z0-9]", "", result.stdout.decode("utf-8", "replace").lower())


def visible_marker(text):
    return any(SequenceMatcher(None, MARKER, text[i:i+len(MARKER)]).ratio() >= .86
               for i in range(max(1, len(text)-len(MARKER)+1)))


def main():
    verify_hashes()
    http = load("slice.json", 56, 56)
    browser = load("browser.json", 58, 58)
    for ext in ("doc", "xls", "fods", "fodt", "fodp", "ppt", "odp", "pps"):
        assert http[f"seahub_{ext}_has_no_wopi_route"]["ok"], ext
    assert http["seahub_putfile_ignores_can_edit"]["ok"]

    cases = {
        "doc_odt": "wordcraft", "sheet_ods": "gridcraft",
        "sheet_csv": "gridcraft", "slide_ppsx": "deckcraft",
    }
    for fixture, editor in cases.items():
        for suffix in ("routes_to_" + editor, "host_reports_read_only",
                       "editor_received_the_fixture", "editor_payload_contains_the_marker",
                       "rendered_marker_and_expected_value", "open_did_not_download",
                       "open_wrote_no_version"):
            assert browser[f"viewing_{fixture}_{suffix}"]["ok"], suffix

    images = {
        "odt-wordcraft.png": (.22, .35, .65, .55),
        "ods-gridcraft.png": (.02, .29, .50, .42),
        "csv-gridcraft.png": (.02, .29, .50, .42),
        "ppsx-deckcraft.png": (.30, .34, .60, .43),
    }
    for name, region in images.items():
        text = ocr(name, region)
        assert visible_marker(text), f"marker missing from {name}: {text[:120]}"
        if name.startswith(("ods-", "csv-")):
            assert "42" in text, f"fixture value missing from {name}: {text[:120]}"
    assert "seahub_putfile_ignores_can_edit" in http
    for needle in ("repo_id", "synthetic-", "@auth.local", "access_token", "WOPISrc=http"):
        combined = (HERE / "slice.json").read_text() + (HERE / "browser.json").read_text()
        assert needle not in combined, needle
    print("PASS: HTTP 56/56, browser 58/58, 4 read-only rendered legacy formats, "
          "8 unrouted formats, checksums and sanitized summaries")
    print("LIMITATION: direct Seahub PutFile accepts a read-only WOPI token")


if __name__ == "__main__":
    main()
