#!/usr/bin/env python3
"""Offline fixture-selection checks for WordCraft's corrected DOCX fidelity corpus."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.join(HERE, "..", "lab", "real-seafile")
sys.path.insert(0, LAB)
for key, value in (("SEAFILE_URL", "http://127.0.0.1:1/seahub"),
                   ("BRIDGE_URL", "http://127.0.0.1:1/bridge"),
                   ("ONLYOFFICE_URL", "http://127.0.0.1:1/onlyoffice"),
                   ("ADMIN_EMAIL", "synthetic@example.invalid"),
                   ("ADMIN_PASSWORD", "synthetic-not-a-real-password")):
    os.environ.setdefault(key, value)

try:
    import playwright.sync_api  # noqa: F401
except ModuleNotFoundError:
    import types
    playwright = types.ModuleType("playwright")
    sync_api = types.ModuleType("playwright.sync_api")
    sync_api.sync_playwright = None
    playwright.sync_api = sync_api
    sys.modules["playwright"] = playwright
    sys.modules["playwright.sync_api"] = sync_api

import docx_fidelity_corpus  # noqa: E402
import run_browser  # noqa: E402
from io import BytesIO  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402


def main():
    base = {"test.docx": ("wordcraft", b"minimal", ""),
            "test.xlsx": ("gridcraft", b"xlsx", "")}
    assert run_browser.select_wordcraft_fidelity_fixture(base, "") is base
    assert base["test.docx"] == ("wordcraft", b"minimal", "")

    selected = dict(base)
    assert run_browser.select_wordcraft_fidelity_fixture(
        selected, "fidelity-layout.docx"
    ) is selected
    assert "test.docx" not in selected
    assert selected["test.xlsx"] == base["test.xlsx"]
    assert selected["fidelity-layout.docx"] == (
        "wordcraft", docx_fidelity_corpus.corpus()["fidelity-layout.docx"], ""
    )

    for invalid, mapping in (("missing.docx", dict(base)),
                             ("fidelity-layout.docx", {"fidelity-layout.docx": base["test.docx"]}),
                             ("fidelity-layout.docx", {"test.xlsx": base["test.xlsx"]})):
        original = dict(mapping)
        try:
            run_browser.select_wordcraft_fidelity_fixture(mapping, invalid)
        except ValueError:
            pass
        else:
            raise AssertionError(f"invalid fixture selection did not fail closed: {invalid}")
        assert mapping == original

    blank = Image.new("RGB", (1400, 900), "white")
    page = ImageDraw.Draw(blank)
    page.rectangle((295, 291, 1112, 875), outline=(220, 220, 220))
    cursor = ImageDraw.Draw(blank)
    cursor.line((392, 386, 392, 408), fill=(25, 25, 25), width=2)
    blank_bytes = BytesIO()
    blank.save(blank_bytes, format="PNG")
    assert not run_browser.wordcraft_canvas_shows_document(blank_bytes.getvalue())

    rendered = Image.new("RGB", (1400, 900), "white")
    draw = ImageDraw.Draw(rendered)
    for y in (397, 426, 455, 484, 513, 542):
        draw.line((392, y, 825, y), fill=(20, 20, 20), width=3)
    rendered_bytes = BytesIO()
    rendered.save(rendered_bytes, format="PNG")
    assert run_browser.wordcraft_canvas_shows_document(rendered_bytes.getvalue())

    class FakePage:
        def __init__(self):
            self.captures = iter((blank_bytes.getvalue(), rendered_bytes.getvalue(),
                                  rendered_bytes.getvalue()))

        def screenshot(self):
            return next(self.captures)

        def wait_for_timeout(self, _milliseconds):
            pass

    assert run_browser.wait_for_wordcraft_document(FakePage(), timeout=5)

    print("PASS: WordCraft fidelity fixture selection")


if __name__ == "__main__":
    main()
