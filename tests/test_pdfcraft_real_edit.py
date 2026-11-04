#!/usr/bin/env python3
"""Offline semantic checks for PdfCraft's synthetic AcroForm save assertions."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lab", "real-seafile"))
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

import run_browser  # noqa: E402


def main():
    fixtures = {"test.docx": ("wordcraft", b"docx", ""),
                "test.pdf": ("pdfcraft", b"pdf", "?edit_pdf=true")}
    assert run_browser.select_browser_fixtures(fixtures, "") is fixtures
    assert run_browser.select_browser_fixtures(fixtures, "pdfcraft") == {
        "test.pdf": fixtures["test.pdf"]
    }
    assert run_browser.select_browser_fixtures(fixtures, "deckcraft") == {}
    try:
        run_browser.select_browser_fixtures(fixtures, "missing")
    except ValueError:
        pass
    else:
        raise AssertionError("unknown editor filter should fail closed")

    fixture_path = os.path.join(HERE, "..", "lab", "real-seafile", "fixtures", "form.pdf")
    fixture = open(fixture_path, "rb").read()
    assert fixture.startswith(b"%PDF-1.7")
    assert b"/T (name)" in fixture
    assert not run_browser.pdf_text_field_has_value(fixture, "name", "pdfedited1234567890")

    marker = b"pdfedited1234567890"
    literal = fixture + b"\n14 0 obj\n<< /FT /Tx /T (name) /V (" + marker + b") >>\nendobj\n"
    assert run_browser.pdf_text_field_has_value(literal, "name", marker.decode())

    hex_value = marker.hex().upper().encode()
    hexadecimal = fixture + b"\n14 0 obj\n<< /FT /Tx /T (name) /V <" + hex_value + b"> >>\nendobj\n"
    assert run_browser.pdf_text_field_has_value(hexadecimal, "name", marker.decode())

    escaped = (fixture + b"\n14 0 obj\n<< /FT /Tx /T (name) /V (pdfedited\\(123\\)) >>\nendobj\n")
    assert run_browser.pdf_text_field_has_value(escaped, "name", "pdfedited(123)")

    other_field = fixture + b"\n14 0 obj\n<< /FT /Tx /T (city) /V (" + marker + b") >>\nendobj\n"
    assert not run_browser.pdf_text_field_has_value(other_field, "name", marker.decode())
    unrelated_page_text = fixture + b"\n14 0 obj\n<< /Contents (" + marker + b") >>\nendobj\n"
    assert not run_browser.pdf_text_field_has_value(unrelated_page_text, "name", marker.decode())
    print("PASS: PdfCraft AcroForm field-value assertions")


if __name__ == "__main__":
    main()
