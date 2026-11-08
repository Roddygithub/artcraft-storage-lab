#!/usr/bin/env python3
"""Offline semantic checks for PdfCraft's synthetic AcroForm save assertions."""
import os
import re
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


def append_pdf_revision(data, object_number, body, size):
    previous = int(re.findall(rb"(?m)^startxref\s+(\d+)\s*$", data)[-1])
    prefix = b"" if data.endswith(b"\n") else b"\n"
    object_offset = len(data) + len(prefix)
    serialized = (f"{object_number} 0 obj\n".encode() + body +
                  b"\nendobj\n")
    xref_offset = object_offset + len(serialized)
    xref = (f"xref\n{object_number} 1\n{object_offset:010d} 00000 n \n"
            f"trailer\n<< /Size {size} /Root 1 0 R /Prev {previous} >>\n"
            f"startxref\n{xref_offset}\n%%EOF\n").encode()
    return data + prefix + serialized + xref


def field_body(field_name=b"name", value_token=None):
    data = open(os.path.join(HERE, "..", "lab", "real-seafile", "fixtures", "form.pdf"), "rb").read()
    match = re.search(rb"(?ms)^4\s+0\s+obj\b(.*?)\bendobj\b", data)
    body = match.group(1).strip().replace(b"/T (name)", b"/T (" + field_name + b")")
    if value_token is not None:
        body = body[:-2] + b" /V " + value_token + b" >>"
    return body


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
    literal = append_pdf_revision(fixture, 4, field_body(value_token=b"(" + marker + b")"), 13)
    assert run_browser.pdf_text_field_has_value(literal, "name", marker.decode())

    hex_value = marker.hex().upper().encode()
    hexadecimal = append_pdf_revision(fixture, 4, field_body(value_token=b"<" + hex_value + b">"), 13)
    assert run_browser.pdf_text_field_has_value(hexadecimal, "name", marker.decode())

    escaped = append_pdf_revision(fixture, 4, field_body(value_token=b"(pdfedited\\(123\\))"), 13)
    assert run_browser.pdf_text_field_has_value(escaped, "name", "pdfedited(123)")

    other_field = append_pdf_revision(fixture, 4, field_body(b"city", b"(" + marker + b")"), 13)
    assert not run_browser.pdf_text_field_has_value(other_field, "name", marker.decode())
    unrelated_page_text = append_pdf_revision(
        fixture, 14, b"<< /Contents (" + marker + b") >>", 15
    )
    assert not run_browser.pdf_text_field_has_value(unrelated_page_text, "name", marker.decode())

    superseded = append_pdf_revision(fixture, 4, field_body(value_token=b"(" + marker + b")"), 13)
    superseded = append_pdf_revision(
        superseded, 4, field_body(value_token=b"(different-current-value)"), 13
    )
    assert not run_browser.pdf_text_field_has_value(superseded, "name", marker.decode())
    assert run_browser.pdf_text_field_has_value(superseded, "name", "different-current-value")

    truncated_xref = b"%PDF-1.7\nstartxref\n0000000040\n%%EOF\n".ljust(40, b" ") + b"xref\n"
    assert run_browser._current_pdf_object_bodies(truncated_xref) is None
    assert not run_browser.pdf_text_field_has_value(truncated_xref, "name", marker.decode())
    print("PASS: PdfCraft AcroForm field-value assertions")


if __name__ == "__main__":
    main()
