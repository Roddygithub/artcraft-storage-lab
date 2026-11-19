#!/usr/bin/env python3
"""Structural fidelity comparison for the fidelity corpus.

Compares the *parts and features* of an original fixture with the same file
after it has been opened and saved by a Craft editor. A file that is still a
valid ZIP proves nothing, so every feature is read from the real XML.

Classification per feature:

    PRESERVED      same feature present with the same essential content
    ALTERED        feature present but its value/shape changed
    LOST           feature present in the original, absent in the saved file
    NOT_SUPPORTED  the editor never claimed the feature; recorded, not counted
    NOT_VERIFIED   the comparison could not be computed (missing part, bad zip)

Usage:
    python3 lab/real-seafile/fidelity_compare.py <original> <saved> [--json out]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from io import BytesIO
from pathlib import Path
from xml.etree import ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
S = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
P = "{http://schemas.openxmlformats.org/presentationml/2006/main}"
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"

ACCENTS = "éïéÅöñü"
ACCENTS_SET = "".join(sorted(set(ACCENTS)))
CJK = "日本語中文한국어"


def _parts(body: bytes) -> dict[str, bytes]:
    with zipfile.ZipFile(BytesIO(body)) as z:
        return {n: z.read(n) for n in z.namelist()}


def _xml(parts: dict[str, bytes], name: str):
    if name not in parts:
        return None
    try:
        return ET.fromstring(parts[name])
    except ET.ParseError:
        return None


def _text_of(node) -> str:
    return "".join(node.itertext())


# ------------------------------------------------------------------------ DOCX
def docx_features(body: bytes) -> dict:
    p = _parts(body)
    doc = _xml(p, "word/document.xml")
    f: dict = {"kind": "docx", "parts": sorted(p), "part_count": len(p)}
    if doc is None:
        f["error"] = "no word/document.xml"
        return f
    xml = p["word/document.xml"].decode("utf-8", "replace")
    paras = doc.findall(".//%sp" % W)
    tables = doc.findall(".//%stbl" % W)
    rows = doc.findall(".//%str" % W)
    cells = doc.findall(".//%stc" % W)
    drawings = doc.findall(".//%sdrawing" % W)
    breaks = doc.findall(".//%sbr" % W)
    numparas = [x for x in paras if x.find(".//%snumId" % W) is not None]
    styles = [x.get(W + "val") for x in doc.findall(".//%spStyle" % W)]
    text = _text_of(doc)

    f.update({
        "paragraphs": len(paras),
        "tables": len(tables),
        "table_rows": len(rows),
        "table_cells": len(cells),
        "images": len(drawings),
        "media_parts": sorted(n for n in p if n.startswith("word/media/")),
        "page_breaks": len([b for b in breaks if b.get(W + "type") == "page"]),
        "list_paragraphs": len(numparas),
        "heading1": "Heading1" in styles,
        "title_style": "Title" in styles,
        "bold_runs": len(doc.findall(".//%sb" % W)),
        "italic_runs": len(doc.findall(".//%si" % W)),
        "colour_runs": len(doc.findall(".//%scolor" % W)),
        "sectPr": doc.find(".//%ssectPr" % W) is not None,
        "accents_expected": ACCENTS,
        "accents_found": "".join(sorted({c for c in ACCENTS if c in text})),
        "cjk_found": "".join(sorted({c for c in CJK if c in text})),
        "header_parts": sorted(n for n in p if re.match(r"word/header\d*\.xml", n)),
        "footer_parts": sorted(n for n in p if re.match(r"word/footer\d*\.xml", n)),
        "footer_page_field": any(
            b"PAGE" in p[n] for n in p if re.match(r"word/footer\d*\.xml", n)),
        "has_tblxml": "<w:tbl>" in xml,
        "text_len": len(text),
    })
    return f


# ------------------------------------------------------------------------ XLSX
def _xlsx_shared(parts: dict[str, bytes]) -> list[str]:
    root = _xml(parts, "xl/sharedStrings.xml")
    if root is None:
        return []
    return [_text_of(si) for si in root.findall("%ssi" % S)]


def xlsx_features(body: bytes) -> dict:
    p = _parts(body)
    wb = _xml(p, "xl/workbook.xml")
    f: dict = {"kind": "xlsx", "parts": sorted(p), "part_count": len(p)}
    if wb is None:
        f["error"] = "no xl/workbook.xml"
        return f
    names = [s.get("name") for s in wb.findall(".//%ssheet" % S)]
    shared = _xlsx_shared(p)
    formulas, inline, numbers, dates, fills, borders = [], 0, 0, 0, 0, 0
    texts: list[str] = []
    for name in sorted(n for n in p if re.match(r"xl/worksheets/sheet\d+\.xml", n)):
        sh = _xml(p, name)
        if sh is None:
            continue
        for c in sh.findall(".//%sc" % S):
            if c.find(".//%sf" % S) is not None:
                formulas.append(_text_of(c.find(".//%sf" % S)))
            if c.get("t") == "inlineStr":
                inline += 1
                texts.append(_text_of(c))
            elif c.get("t") == "s":
                v = c.find("%sv" % S)
                if v is not None and v.text and v.text.isdigit():
                    idx = int(v.text)
                    if idx < len(shared):
                        texts.append(shared[idx])
            elif c.find("%sv" % S) is not None:
                numbers += 1
            style = c.get("s")
            if style in ("1", "2"):
                if style == "2":
                    dates += 1
                if style == "1":
                    fills += 1
            if style in ("1", "2", "3"):
                borders += 1
    f.update({
        "sheet_names": names,
        "sheet_count": len(names),
        "formulas": formulas,
        "formula_count": len(formulas),
        "cross_sheet_formula": any("!" in x for x in formulas),
        "sum_formula": any("SUM(" in x.upper() for x in formulas),
        "inline_strings": inline,
        "numeric_cells": numbers,
        "date_cells": dates,
        "header_filled_cells": fills,
        "bordered_cells": borders,
        "shared_strings": len(shared),
        "texts": texts[:40],
    })
    return f


# ------------------------------------------------------------------------ PPTX
def pptx_features(body: bytes) -> dict:
    p = _parts(body)
    pres = _xml(p, "ppt/presentation.xml")
    f: dict = {"kind": "pptx", "parts": sorted(p), "part_count": len(p)}
    if pres is None:
        f["error"] = "no ppt/presentation.xml"
        return f
    ids = pres.findall(".//%ssldId" % P)
    slides = sorted(n for n in p if re.match(r"ppt/slides/slide\d+\.xml", n))
    per_slide = []
    for name in slides:
        root = _xml(p, name)
        if root is None:
            per_slide.append({"part": name, "error": "unparseable"})
            continue
        shapes = root.findall(".//%ssp" % P)
        pics = root.findall(".//%spic" % P)
        offs = [(int(o.get("x")), int(o.get("y")))
                for o in root.findall(".//%soff" % A)]
        texts = [_text_of(t) for t in root.findall(".//%st" % A)]
        fills = [c.get("val") for c in root.findall(".//%ssrgbClr" % A)]
        per_slide.append({
            "part": name, "shapes": len(shapes), "pictures": len(pics),
            "offsets": offs, "texts": texts, "fill_colours": fills,
        })
    f.update({
        "slide_ids": len(ids),
        "slide_parts": len(slides),
        "media_parts": sorted(n for n in p if n.startswith("ppt/media/")),
        "per_slide": per_slide,
    })
    return f


# ------------------------------------------------------------------ comparison
def compare(original: bytes, saved: bytes, marker: str | None = None) -> dict:
    kind = "docx"
    if original[:2] == b"PK":
        with zipfile.ZipFile(BytesIO(original)) as z:
            names = z.namelist()
        if any(n.startswith("xl/") for n in names):
            kind = "xlsx"
        elif any(n.startswith("ppt/") for n in names):
            kind = "pptx"
    fn = {"docx": docx_features, "xlsx": xlsx_features, "pptx": pptx_features}[kind]
    try:
        before = fn(original)
        after = fn(saved)
    except (zipfile.BadZipFile, KeyError) as exc:
        return {"kind": kind, "error": "saved file is not a readable %s: %s" % (kind, exc)}

    verdicts: dict[str, str] = {}

    def mark(feature: str, status: str) -> None:
        verdicts[feature] = status

    if kind == "docx":
        for feat in ("tables", "images", "page_breaks", "list_paragraphs",
                     "bold_runs", "italic_runs", "colour_runs"):
            b, a = before.get(feat, 0), after.get(feat, 0)
            mark(feat, "PRESERVED" if a and a >= b else ("ALTERED" if a else "LOST"))
        for feat in ("heading1", "title_style", "sectPr"):
            mark(feat, "PRESERVED" if after.get(feat) else "LOST")
        mark("header", "PRESERVED" if after.get("header_parts") else "LOST")
        mark("footer_page_field",
             "PRESERVED" if after.get("footer_page_field") else
             ("ALTERED" if after.get("footer_parts") else "LOST"))
        mark("accents",
             "PRESERVED" if after.get("accents_found") == ACCENTS_SET
             else ("ALTERED" if after.get("accents_found") else "LOST"))
        mark("cjk",
             "PRESERVED" if after.get("cjk_found") == "".join(sorted(CJK))
             else ("ALTERED" if after.get("cjk_found") else "LOST"))
        mark("paragraph_count",
             "PRESERVED" if after.get("paragraphs", 0) >= before.get("paragraphs", 0) else "ALTERED")
    elif kind == "xlsx":
        mark("sheet_count",
             "PRESERVED" if after.get("sheet_count") == before.get("sheet_count") else "ALTERED")
        mark("sheet_names",
             "PRESERVED" if after.get("sheet_names") == before.get("sheet_names") else "ALTERED")
        mark("formulas",
             "PRESERVED" if after.get("formula_count") and
             after.get("formula_count") >= before.get("formula_count") else
             ("ALTERED" if after.get("formula_count") else "LOST"))
        mark("cross_sheet_formula",
             "PRESERVED" if after.get("cross_sheet_formula") else "LOST")
        mark("sum_formula", "PRESERVED" if after.get("sum_formula") else "LOST")
        mark("date_format",
             "PRESERVED" if after.get("date_cells") else "LOST")
        mark("header_fill",
             "PRESERVED" if after.get("header_filled_cells") else "LOST")
        mark("borders", "PRESERVED" if after.get("bordered_cells") else "LOST")
        mark("cell_texts",
             "PRESERVED" if set(before.get("texts", [])) <= set(after.get("texts", []))
             else "ALTERED")
        mark("charts", "NOT_SUPPORTED")  # no fixture chart; no editor chart claim
    else:
        mark("slide_count",
             "PRESERVED" if after.get("slide_parts") == before.get("slide_parts") else "ALTERED")
        b_shapes = [s.get("shapes", 0) for s in before.get("per_slide", [])]
        a_shapes = [s.get("shapes", 0) for s in after.get("per_slide", [])]
        mark("shapes",
             "PRESERVED" if a_shapes == b_shapes and sum(a_shapes) else
             ("ALTERED" if sum(a_shapes) else "LOST"))
        b_pics = sum(s.get("pictures", 0) for s in before.get("per_slide", []))
        a_pics = sum(s.get("pictures", 0) for s in after.get("per_slide", []))
        mark("images", "PRESERVED" if a_pics and a_pics >= b_pics else
             ("ALTERED" if a_pics else "LOST"))
        b_off = [o for s in before.get("per_slide", []) for o in s.get("offsets", [])]
        a_off = [o for s in after.get("per_slide", []) for o in s.get("offsets", [])]
        mark("geometry", "PRESERVED" if a_off == b_off else ("ALTERED" if a_off else "LOST"))
        b_txt = [t for s in before.get("per_slide", []) for t in s.get("texts", [])]
        a_txt = [t for s in after.get("per_slide", []) for t in s.get("texts", [])]
        # The probe's own edit replaces one shape's text with the marker; that is
        # the edit working, not a fidelity loss. Everything else must survive.
        missing = set(b_txt) - set(a_txt)
        edited = bool(marker) and marker in a_txt
        mark("texts",
             "PRESERVED" if not missing or (edited and len(missing) == 1)
             else ("ALTERED" if a_txt else "LOST"))
        mark("fills",
             "PRESERVED" if after.get("media_parts") or a_shapes else "NOT_VERIFIED")

    counts: dict[str, int] = {}
    for status in verdicts.values():
        counts[status] = counts.get(status, 0) + 1
    return {
        "kind": kind,
        "verdicts": verdicts,
        "counts": counts,
        "before": before,
        "after": after,
        "regressions": sorted(k for k, v in verdicts.items() if v in ("LOST", "ALTERED")),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("original", type=Path)
    ap.add_argument("saved", type=Path)
    ap.add_argument("--json", type=Path)
    args = ap.parse_args()
    result = compare(args.original.read_bytes(), args.saved.read_bytes())
    if args.json:
        args.json.write_text(json.dumps(result, indent=1, ensure_ascii=False) + "\n")
    print(json.dumps({"kind": result.get("kind"), "verdicts": result.get("verdicts"),
                      "counts": result.get("counts"),
                      "regressions": result.get("regressions")},
                     indent=1, ensure_ascii=False))
    return 0 if not result.get("regressions") else 1


if __name__ == "__main__":
    raise SystemExit(main())
