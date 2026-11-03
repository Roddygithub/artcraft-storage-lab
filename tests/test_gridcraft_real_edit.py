#!/usr/bin/env python3
"""Regression for the GridCraft XLSX slice's semantic assertions: the stdlib cell reader
(run_slice.xlsx_cells) used by lab/real-seafile/run_browser.py must parse the real lab
fixture (A1=1) and the string/numeric encodings the editors emit, and must reject
malformed input instead of ever letting a positive cell assertion pass on it. Pure
stdlib, no browser, no live services; the synthetic workbook bytes are parser fixtures
only and are never uploaded or injected anywhere."""
import io
import os
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lab", "real-seafile"))

# run_slice reads these at import; supply synthetic values, restore afterwards.
_REAL: dict = {}
for _k, _v in (("SEAFILE_URL", "http://127.0.0.1:1/seahub"),
               ("BRIDGE_URL", "http://127.0.0.1:1/bridge"),
               ("ONLYOFFICE_URL", "http://127.0.0.1:1/onlyoffice"),
               ("ADMIN_EMAIL", "synthetic@example.invalid"),
               ("ADMIN_PASSWORD", "synthetic-not-a-real-password")):
    _REAL[_k] = os.environ.get(_k)
    os.environ.setdefault(_k, _v)
import run_slice as rs  # noqa: E402

failures: list[str] = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (f"  -- {detail}" if detail else ""), flush=True)
    if not ok:
        failures.append(name)


def workbook(sheet1: str, shared: str | None = None) -> bytes:
    """A minimal-but-legal XLSX wrapper around a hand-written sheet1.xml (+ sharedStrings)."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("xl/workbook.xml",
                   '<?xml version="1.0"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
                   'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
                   '<sheets><sheet name="Sheet1" sheetId="1" r:id="rId1"/></sheets></workbook>')
        z.writestr("xl/_rels/workbook.xml.rels",
                   '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/></Relationships>')
        if shared is not None:
            z.writestr("xl/sharedStrings.xml", shared)
        z.writestr("xl/worksheets/sheet1.xml", sheet1)
    return buf.getvalue()


def raises_value_error(data, tag):
    try:
        rs.xlsx_cells(data)
    except ValueError:
        return True
    except Exception as e:  # noqa: BLE001
        print(f"  ({tag}: raised {type(e).__name__} instead of ValueError)", flush=True)
        return False
    return False


def main():
    NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    fixture = rs.minimal_xlsx()

    # the real lab fixture: numeric A1
    cells = rs.xlsx_cells(fixture)
    check("lab_fixture_a1_is_numeric_one", cells.get("A1") == "1", f"cells={cells}")

    # plain numeric and cached-formula-string cells
    data = workbook(f'<worksheet xmlns="{NS}"><sheetData>'
                    f'<row r="1"><c r="A1"><v>3.14</v></c><c r="A2"><v>-7</v></c>'
                    f'<c r="B1" t="str"><f>CONCAT("a","b")</f><v>ab</v></c>'
                    f'</row></sheetData></worksheet>')
    cells = rs.xlsx_cells(data)
    check("numeric_and_formula_string_cells_parsed",
          cells == {"A1": "3.14", "A2": "-7", "B1": "ab"}, f"cells={cells}")

    # inline string cell (the common editor-emitted encoding for typed text)
    data = workbook(f'<worksheet xmlns="{NS}"><sheetData>'
                    f'<row r="2"><c r="B2" t="inlineStr"><is><t>gridtypedx</t></is></c>'
                    f'</row></sheetData></worksheet>')
    cells = rs.xlsx_cells(data)
    check("inline_string_cell_parsed", cells.get("B2") == "gridtypedx", f"cells={cells}")

    # shared strings, including a multi-run <si> (rich text) joining
    data = workbook(
        f'<worksheet xmlns="{NS}"><sheetData>'
        f'<row r="1"><c r="C3" t="s"><v>1</v></c><c r="D4" t="s"><v>0</v></c></row>'
        f'</sheetData></worksheet>',
        f'<sst xmlns="{NS}" count="2" uniqueCount="2">'
        f'<si><t>hello</t></si>'
        f'<si><r><t>rich</t></r><r><t>text</t></r></si>'
        f'</sst>')
    cells = rs.xlsx_cells(data)
    check("shared_string_cells_parsed", cells == {"C3": "richtext", "D4": "hello"}, f"cells={cells}")

    # malformed input must be rejected, never raise or return a partial map
    check("not_a_zip_rejected", raises_value_error(b"this is not a zip file at all", "non-zip"))
    check("zip_without_sheet_rejected",
          raises_value_error(b"PK\x03\x04garbage", "broken zip"))
    broken = workbook(f'<worksheet xmlns="{NS}"><sheetData><row>')
    check("broken_sheet_xml_rejected", raises_value_error(broken, "broken xml"))
    bad_ref = workbook(
        f'<worksheet xmlns="{NS}"><sheetData><row r="1"><c r="A1" t="s"><v>5</v></c></row></sheetData></worksheet>',
        f'<sst xmlns="{NS}"><si><t>only</t></si></sst>')
    check("shared_string_index_out_of_range_rejected", raises_value_error(bad_ref, "bad index"))
    bad_idx = workbook(
        f'<worksheet xmlns="{NS}"><sheetData><row r="1"><c r="A1" t="s"><v>notanumber</v></c></row></sheetData></worksheet>',
        f'<sst xmlns="{NS}"><si><t>only</t></si></sst>')
    check("non_numeric_shared_string_index_rejected", raises_value_error(bad_idx, "bad idx"))
    missing_v = workbook(
        f'<worksheet xmlns="{NS}"><sheetData><row r="1"><c r="A1" t="s"></c></row></sheetData></worksheet>',
        f'<sst xmlns="{NS}"><si><t>only</t></si></sst>')
    check("missing_shared_string_index_rejected", raises_value_error(missing_v, "missing v"))
    empty_v = workbook(
        f'<worksheet xmlns="{NS}"><sheetData><row r="1"><c r="B2" t="s"><v/></c></row></sheetData></worksheet>',
        f'<sst xmlns="{NS}"><si><t>only</t></si></sst>')
    check("empty_shared_string_index_rejected", raises_value_error(empty_v, "empty v"))

    print(f"\n{len(failures)} failed", flush=True)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
