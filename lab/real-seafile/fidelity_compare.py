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
import hashlib
import json
import posixpath
import re
import sys
import unicodedata
import zipfile
from io import BytesIO
from pathlib import Path
from xml.etree import ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
PKG = "{http://schemas.openxmlformats.org/package/2006/relationships}"
WP = "{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}"
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
_VOLATILE_W_ATTRS = {"rsidR", "rsidRPr", "rsidP", "rsidDel", "rsidTr", "rsidSect"}


def _docx_xml(node):
    """Canonical semantic XML, independent of namespace prefixes and attr order."""
    if node is None:
        return None
    tag = node.tag.rsplit("}", 1)[-1]
    attrs = []
    for key, value in node.attrib.items():
        name = key.rsplit("}", 1)[-1]
        if name in _VOLATILE_W_ATTRS:
            continue
        if (tag in {"top", "left", "bottom", "right", "insideH", "insideV"}
                and (name, value) in (("color", "auto"), ("space", "0"))):
            continue
        if tag == "shd" and name == "color" and value == "auto":
            continue
        attrs.append((name, value))
    return {"tag": tag, "attrs": sorted(attrs),
            "text": (node.text or "").strip(), "children": [_docx_xml(child) for child in node]}


def _docx_relationships(parts: dict[str, bytes], rels_part: str,
                        source_part: str) -> tuple[dict[str, dict], list[str]]:
    root = _xml(parts, rels_part)
    if root is None:
        return {}, [f"unreadable or missing {rels_part}"]
    result, errors = {}, []
    base = posixpath.dirname(source_part)
    for rel in root.findall(f"{PKG}Relationship"):
        rel_id, target = rel.get("Id"), rel.get("Target")
        if not rel_id or not target:
            errors.append(f"incomplete relationship in {rels_part}")
            continue
        external = rel.get("TargetMode") == "External"
        path = target if external else posixpath.normpath(posixpath.join(base, target))
        result[rel_id] = {"type": rel.get("Type", "").rsplit("/", 1)[-1],
                          "target": path, "external": external}
    return result, errors


def _docx_style_name(style_id: str | None, styles: dict[str, dict]) -> str | None:
    if style_id is None:
        return None
    style = styles.get(style_id)
    if style is None:
        return f"unresolved:{style_id}"
    name = " ".join(style["name"].split()).casefold()
    known = {"heading1": "heading 1", "heading2": "heading 2"}
    name = known.get(style_id.casefold(), name)
    return f"{style['type'].casefold()}:{name}"


def _docx_onoff(parent, name: str) -> bool:
    element = parent.find(f"{W}{name}") if parent is not None else None
    return bool(element is not None and element.get(W + "val", "1").lower()
                not in ("0", "false", "off", "no"))


def _docx_paragraph(node, styles: dict[str, dict], numbering: dict[str, dict]) -> dict:
    ppr = node.find(f"{W}pPr")
    style = ppr.find(f"{W}pStyle") if ppr is not None else None
    style_name = _docx_style_name(style.get(W + "val") if style is not None else None, styles)
    numpr = ppr.find(f"{W}numPr") if ppr is not None else None
    num_id = numpr.find(f"{W}numId") if numpr is not None else None
    level = numpr.find(f"{W}ilvl") if numpr is not None else None
    num_value = num_id.get(W + "val") if num_id is not None else None
    level_value = level.get(W + "val", "0") if level is not None else "0"
    list_style = numbering.get(num_value, {}).get(level_value) if num_value is not None else None
    if num_value is not None and list_style is None:
        list_style = {"unresolved_num_id": num_value, "level": level_value}

    significant_ppr = {"jc", "spacing", "ind", "keepNext", "keepLines", "pageBreakBefore",
                       "widowControl", "outlineLvl", "tabs", "contextualSpacing"}
    ppr_props = [_docx_xml(child) for child in (ppr if ppr is not None else [])
                 if child.tag.rsplit("}", 1)[-1] in significant_ppr]
    runs = []
    for run in node.findall(f".//{W}r"):
        rpr = run.find(f"{W}rPr")
        color = rpr.find(f"{W}color") if rpr is not None else None
        color_value = None
        if color is not None and color.get(W + "val", "auto").lower() != "auto":
            color_value = sorted((key.rsplit("}", 1)[-1], value)
                                 for key, value in color.attrib.items())
        rstyle = rpr.find(f"{W}rStyle") if rpr is not None else None
        formatting = {"bold": _docx_onoff(rpr, "b"), "italic": _docx_onoff(rpr, "i"),
                      "color": color_value,
                      "style": _docx_style_name(rstyle.get(W + "val") if rstyle is not None else None, styles)}
        text_parts = []
        for item in run.iter():
            if item.tag in (W + "t", W + "delText"):
                text_parts.append(item.text or "")
            elif item.tag == W + "tab":
                text_parts.append("\t")
            elif item.tag == W + "br" and item.get(W + "type") != "page":
                text_parts.append("\n")
        run_text = "".join(text_parts)
        if runs and runs[-1]["format"] == formatting:
            runs[-1]["text"] += run_text
        else:
            runs.append({"text": run_text, "format": formatting})

    text, breaks = [], []
    for item in node.iter():
        if item.tag in (W + "t", W + "delText"):
            text.append(item.text or "")
        elif item.tag == W + "tab":
            text.append("\t")
        elif item.tag == W + "br":
            kind = item.get(W + "type", "textWrapping")
            breaks.append(kind)
            if kind != "page":
                text.append("\n")
    if ppr is not None and ppr.find(f"{W}pageBreakBefore") is not None:
        breaks.insert(0, "pageBreakBefore")
    return {"text": "".join(text), "style": style_name, "numbering": list_style,
            "properties": ppr_props, "runs": runs, "breaks": breaks}


def _docx_table(table, styles: dict[str, dict], numbering: dict[str, dict]) -> dict:
    tblpr = table.find(f"{W}tblPr")
    tbl_tags = {"tblStyle", "tblW", "tblInd", "jc", "tblBorders", "tblLayout", "tblCellMar",
                "tblCaption", "tblDescription", "shd"}
    tbl_props = []
    for child in (tblpr if tblpr is not None else []):
        tag = child.tag.rsplit("}", 1)[-1]
        if tag not in tbl_tags:
            continue
        if tag == "tblStyle":
            tbl_props.append({"tag": tag, "style": _docx_style_name(child.get(W + "val"), styles)})
        else:
            tbl_props.append(_docx_xml(child))
    grid = table.find(f"{W}tblGrid")
    grid_widths = [col.get(W + "w") for col in grid.findall(f"{W}gridCol")] if grid is not None else []
    rows = []
    for row in table.findall(f"{W}tr"):
        trpr = row.find(f"{W}trPr")
        row_tags = {"cantSplit", "tblHeader", "trHeight", "jc", "gridBefore", "gridAfter"}
        row_props = [_docx_xml(child) for child in (trpr if trpr is not None else [])
                     if child.tag.rsplit("}", 1)[-1] in row_tags]
        cells = []
        for cell in row.findall(f"{W}tc"):
            tcpr = cell.find(f"{W}tcPr")
            cell_tags = {"tcW", "gridSpan", "vMerge", "shd", "vAlign", "tcBorders", "tcMar", "noWrap"}
            cell_props = [_docx_xml(child) for child in (tcpr if tcpr is not None else [])
                          if child.tag.rsplit("}", 1)[-1] in cell_tags]
            cells.append({"properties": cell_props,
                          "paragraphs": [_docx_paragraph(p, styles, numbering)
                                         for p in cell.findall(f"{W}p")],
                          "nested_tables": [_docx_table(t, styles, numbering)
                                            for t in cell.findall(f"{W}tbl")]})
        rows.append({"properties": row_props, "cells": cells})
    return {"properties": tbl_props, "grid": grid_widths, "rows": rows}


def _docx_header_footer(root, styles: dict[str, dict], numbering: dict[str, dict]) -> dict:
    if root is None:
        return {"error": "part is not valid XML"}
    codes = [" ".join((field.get(W + "instr") or "").split()).upper()
             for field in root.findall(f".//{W}fldSimple")]
    codes.extend(" ".join((instr.text or "").split()).upper()
                 for instr in root.findall(f".//{W}instrText"))
    return {"paragraphs": [_docx_paragraph(paragraph, styles, numbering)
                           for paragraph in root.findall(f".//{W}p")], "fields": codes}


def docx_features(body: bytes) -> dict:
    p = _parts(body)
    f: dict = {"kind": "docx", "parts": sorted(p), "part_count": len(p), "errors": []}
    doc = _xml(p, "word/document.xml")
    if doc is None or doc.tag != W + "document":
        f["error"] = "missing or invalid word/document.xml"
        return f
    if _xml(p, "[Content_Types].xml") is None or _xml(p, "_rels/.rels") is None:
        f["errors"].append("package content types or root relationships are missing or invalid")
    if doc.find(f"{W}body") is None:
        f["errors"].append("word/document.xml has no document body")

    styles_root = _xml(p, "word/styles.xml") if "word/styles.xml" in p else None
    styles = {}
    if "word/styles.xml" in p and styles_root is None:
        f["errors"].append("word/styles.xml is invalid XML")
    if styles_root is not None:
        for style in styles_root.findall(f"{W}style"):
            style_id, name = style.get(W + "styleId"), style.find(f"{W}name")
            if style_id:
                styles[style_id] = {"type": style.get(W + "type", "paragraph"),
                                    "name": name.get(W + "val") if name is not None else style_id}
    style_data = {}
    if styles_root is not None:
        # Heading outline levels are implied by the named heading style and
        # are often materialized by editors when they save the same document.
        ppr_tags = {"jc", "spacing", "ind", "keepNext", "keepLines", "pageBreakBefore"}
        rpr_tags = {"b", "i", "color", "rFonts", "sz", "szCs", "u", "highlight", "strike", "vertAlign"}
        for style in styles_root.findall(f"{W}style"):
            style_id = style.get(W + "styleId")
            if not style_id:
                continue
            style_key = _docx_style_name(style_id, styles)
            based = style.find(f"{W}basedOn")
            ppr, rpr = style.find(f"{W}pPr"), style.find(f"{W}rPr")
            style_data[style_key] = {
                "based_on": _docx_style_name(based.get(W + "val"), styles) if based is not None else None,
                "paragraph": [_docx_xml(item) for item in (ppr if ppr is not None else [])
                              if item.tag.rsplit("}", 1)[-1] in ppr_tags],
                "run": [_docx_xml(item) for item in (rpr if rpr is not None else [])
                        if item.tag.rsplit("}", 1)[-1] in rpr_tags],
            }

    rels_part = "word/_rels/document.xml.rels"
    rels, rel_errors = _docx_relationships(p, rels_part, "word/document.xml")
    has_refs = any(node.get(R + "id") for node in doc.iter())
    if rels_part in p:
        f["errors"].extend(rel_errors)
    elif has_refs:
        f["errors"].append("document relationships are missing")

    numbering_root = _xml(p, "word/numbering.xml") if "word/numbering.xml" in p else None
    if "word/numbering.xml" in p and numbering_root is None:
        f["errors"].append("word/numbering.xml is invalid XML")
    numbering = {}
    if numbering_root is not None:
        abstract = {}
        for item in numbering_root.findall(f"{W}abstractNum"):
            aid, levels = item.get(W + "abstractNumId"), {}
            for level in item.findall(f"{W}lvl"):
                ilvl = level.get(W + "ilvl", "0")
                fmt, marker = level.find(f"{W}numFmt"), level.find(f"{W}lvlText")
                start = level.find(f"{W}start")
                levels[ilvl] = {"format": fmt.get(W + "val") if fmt is not None else None,
                                "text": marker.get(W + "val") if marker is not None else None,
                                "start": start.get(W + "val") if start is not None else "1"}
            abstract[aid] = levels
        for item in numbering_root.findall(f"{W}num"):
            num_id, aid = item.get(W + "numId"), item.find(f"{W}abstractNumId")
            if num_id and aid is not None:
                numbering[num_id] = abstract.get(aid.get(W + "val"), {})

    paragraphs = [_docx_paragraph(item, styles, numbering) for item in doc.findall(f".//{W}p")]
    for paragraph in paragraphs:
        numbering_ref = paragraph["numbering"]
        if isinstance(numbering_ref, dict) and "unresolved_num_id" in numbering_ref:
            f["errors"].append(f"unresolved numbering reference {numbering_ref['unresolved_num_id']}")
        if paragraph["style"] and paragraph["style"].startswith("unresolved:"):
            f["errors"].append(f"unresolved paragraph style {paragraph['style']}")
        for run in paragraph["runs"]:
            if run["format"]["style"] and run["format"]["style"].startswith("unresolved:"):
                f["errors"].append(f"unresolved run style {run['format']['style']}")
    table_elements = doc.findall(f".//{W}tbl")
    tables = [_docx_table(table, styles, numbering) for table in table_elements]

    related_parts = {"header": [], "footer": []}
    related_by_target = {}
    for relation in rels.values():
        if relation["type"] not in related_parts:
            continue
        target = relation["target"]
        root = None if relation["external"] else _xml(p, target)
        if root is None:
            f["errors"].append(f"referenced {relation['type']} {target!r} is missing or invalid")
            content = {"error": "missing or invalid part"}
        else:
            content = _docx_header_footer(root, styles, numbering)
        related_by_target[target] = content
        related_parts[relation["type"]].append(content)
    for values in related_parts.values():
        values.sort(key=lambda value: json.dumps(value, ensure_ascii=False, sort_keys=True))

    images = []
    for blip in doc.findall(f".//{A}blip"):
        rel_id = blip.get(R + "embed") or blip.get(R + "link")
        relation = rels.get(rel_id)
        if relation is None:
            f["errors"].append(f"image relationship {rel_id!r} is missing")
            images.append({"error": "missing relationship", "relationship": rel_id})
            continue
        target = relation["target"]
        if relation["external"] or target not in p:
            f["errors"].append(f"image target {target!r} is missing or external")
            images.append({"error": "missing or external media", "target": target})
            continue
        drawing_ancestor = blip
        while drawing_ancestor is not None and drawing_ancestor.tag != W + "drawing":
            drawing_ancestor = next((parent for parent in doc.iter()
                                     if drawing_ancestor in list(parent)), None)
        extents = ([dict(sorted(node.attrib.items()))
                    for node in drawing_ancestor.findall(f".//{WP}extent")]
                   if drawing_ancestor is not None else [])
        images.append({"sha256": hashlib.sha256(p[target]).hexdigest(),
                       "extent": extents, "relationship_type": relation["type"]})

    sections = []
    for section in doc.findall(f".//{W}sectPr"):
        def section_prop(tag):
            element = section.find(f"{W}{tag}")
            if tag not in ("cols", "type"):
                return _docx_xml(element)
            defaults = {"cols": {"num": "1", "space": "720"},
                        "type": {"val": "nextPage"}}[tag]
            value = _docx_xml(element) if element is not None else {
                "tag": tag, "attrs": [], "text": "", "children": []}
            attrs = dict(value["attrs"])
            for key, default in defaults.items():
                attrs.setdefault(key, default)
            value["attrs"] = sorted(attrs.items())
            return value

        refs = []
        for tag in ("headerReference", "footerReference"):
            for ref in section.findall(f"{W}{tag}"):
                rel_id, relation = ref.get(R + "id"), rels.get(ref.get(R + "id"))
                if relation is None or relation["external"] or relation["target"] not in p:
                    f["errors"].append(f"section {tag} relationship {rel_id!r} is unresolved")
                    refs.append({"kind": tag, "type": ref.get(W + "type"), "error": "unresolved"})
                else:
                    ref_content = related_by_target[relation["target"]]
                    refs.append({"kind": tag, "type": ref.get(W + "type"), "content": ref_content})
        sections.append({"page_size": section_prop("pgSz"),
                         "page_margins": section_prop("pgMar"),
                         "columns": section_prop("cols"),
                         "type": section_prop("type"),
                         "page_numbering": section_prop("pgNumType"),
                         "references": refs})

    headers, footers = related_parts["header"], related_parts["footer"]

    text = "".join(para["text"] for para in paragraphs)
    latin_extended = lambda value: ord(value) > 127 and unicodedata.name(value, "").startswith("LATIN")
    east_asian = lambda value: any(part in unicodedata.name(value, "")
                                   for part in ("CJK", "IDEOGRAPH", "HIRAGANA", "KATAKANA", "HANGUL"))
    list_items = [{"index": i, "text": para["text"], "numbering": para["numbering"]}
                  for i, para in enumerate(paragraphs) if para["numbering"] is not None]
    run_formats = [{"index": i, "runs": [run["format"] for run in para["runs"]]}
                   for i, para in enumerate(paragraphs)]
    page_breaks = [{"index": i, "breaks": para["breaks"]}
                   for i, para in enumerate(paragraphs) if para["breaks"]]
    style_indices = {name: [i for i, para in enumerate(paragraphs)
                            if para["style"] == f"paragraph:{normalized}"]
                     for name, normalized in (("Title", "title"), ("Heading1", "heading 1"),
                                              ("Heading2", "heading 2"))}
    f.update({"paragraph_data": paragraphs, "style_data": style_data,
              "table_data": tables, "image_data": images,
              "section_data": sections, "headers": headers, "footers": footers,
              "list_data": list_items, "run_formats": run_formats, "page_break_data": page_breaks,
              "style_indices": style_indices, "text": text,
              "accent_text": "".join(char for char in text if latin_extended(char)),
              "cjk_text": "".join(char for char in text if east_asian(char)),
              "paragraphs": len(paragraphs), "tables": len(tables),
              "table_rows": sum(len(table["rows"]) for table in tables),
              "table_cells": sum(len(row["cells"]) for table in tables for row in table["rows"]),
              "images": len(images), "page_breaks": sum(len(item["breaks"]) for item in page_breaks),
              "list_paragraphs": len(list_items), "heading1": bool(style_indices["Heading1"]),
              "title_style": bool(style_indices["Title"]),
              "bold_runs": sum(run["format"]["bold"] for para in paragraphs for run in para["runs"]),
              "italic_runs": sum(run["format"]["italic"] for para in paragraphs for run in para["runs"]),
              "colour_runs": sum(run["format"]["color"] is not None for para in paragraphs for run in para["runs"]),
              "sectPr": bool(sections), "header_parts": list(range(len(headers))),
              "footer_parts": list(range(len(footers))),
              "footer_page_field": any("PAGE" in field for item in footers
                                        for field in item.get("fields", [])),
              "accents_expected": ACCENTS,
              "accents_found": "".join(sorted(set(char for char in ACCENTS if char in text))),
              "cjk_found": "".join(sorted(set(char for char in CJK if char in text))),
              "text_len": len(text), "errors": f["errors"]})
    if f["errors"]:
        f["error"] = "; ".join(sorted(set(f["errors"])))
    return f


# ------------------------------------------------------------------------ XLSX
def _xlsx_shared(parts: dict[str, bytes]) -> list[str]:
    root = _xml(parts, "xl/sharedStrings.xml")
    if root is None:
        return []
    return [_text_of(si) for si in root.findall("%ssi" % S)]


def _style_value(node):
    """Return XML style properties without depending on prefixes/serialization."""
    if node is None:
        return None
    return (node.tag.rsplit("}", 1)[-1], tuple(sorted(node.attrib.items())),
            tuple(_style_value(child) for child in node))


def _style_has(node, tag, attr=None):
    if not node:
        return False
    if node[0] == tag and (attr is None or any(key == attr for key, _ in node[1])):
        return True
    return any(_style_has(child, tag, attr) for child in node[2])


def xlsx_features(body: bytes) -> dict:
    p = _parts(body)
    wb = _xml(p, "xl/workbook.xml")
    f: dict = {"kind": "xlsx", "parts": sorted(p), "part_count": len(p)}
    if wb is None:
        f["error"] = "no xl/workbook.xml"
        return f
    names = [s.get("name") for s in wb.findall(".//%ssheet" % S)]
    shared = _xlsx_shared(p)
    styles = _xml(p, "xl/styles.xml")
    numfmts = {}
    if styles is not None:
        numfmts = {int(x.get("numFmtId")): x.get("formatCode")
                   for x in styles.findall(".//%snumFmt" % S)}
    xfs = styles.findall(".//%scellXfs/%sxf" % (S, S)) if styles is not None else []
    fills = styles.findall(".//%sfills/%sfill" % (S, S)) if styles is not None else []
    borders = styles.findall(".//%sborders/%sborder" % (S, S)) if styles is not None else []
    cell_map = {}
    formulas = {}
    for name in sorted(n for n in p if re.match(r"xl/worksheets/sheet\d+\.xml", n)):
        sh = _xml(p, name)
        if sh is None:
            continue
        sheet_name = names[int(re.search(r"sheet(\d+)\.xml$", name).group(1)) - 1]
        for c in sh.findall(".//%sc" % S):
            coord = c.get("r")
            v = c.find("%sv" % S)
            formula = c.find("%sf" % S)
            if c.get("t") == "inlineStr":
                value = _text_of(c)
            elif c.get("t") == "s" and v is not None and v.text and v.text.isdigit():
                idx = int(v.text)
                value = shared[idx] if idx < len(shared) else None
            else:
                value = v.text if v is not None else None
            style_id = int(c.get("s", "0"))
            xf = xfs[style_id] if style_id < len(xfs) else None
            def component(items, key):
                idx = int(xf.get(key, "0")) if xf is not None else 0
                return _style_value(items[idx]) if idx < len(items) else None
            numfmt_id = int(xf.get("numFmtId", "0")) if xf is not None else 0
            # JSON-encode the coordinate pair so worksheet names containing
            # punctuation remain unambiguous in complete comparison reports.
            key = json.dumps([sheet_name, coord], ensure_ascii=False, separators=(",", ":"))
            cell_map[key] = {
                "value": value,
                "type": c.get("t"),
                "value_type": "string" if c.get("t") in ("s", "inlineStr", "str") else c.get("t", "number"),
                "formula": _text_of(formula) if formula is not None else None,
                "number_format": numfmts.get(numfmt_id, f"builtin:{numfmt_id}"),
                "fill": component(fills, "fillId"),
                "border": component(borders, "borderId"),
                "font": component(styles.findall(".//%sfonts/%sfont" % (S, S)), "fontId") if styles is not None else None,
            }
            if formula is not None:
                formulas[f"{sheet_name}!{coord}"] = _text_of(formula)
    texts = [x["value"] for x in cell_map.values() if isinstance(x["value"], str)]
    f.update({
        "sheet_names": names,
        "sheet_count": len(names),
        "formulas": formulas,
        "formula_count": len(formulas),
        "cross_sheet_formula": any("!" in x for x in formulas.values()),
        "sum_formula": any("SUM(" in x.upper() for x in formulas.values()),
        "cells": cell_map,
        "inline_strings": sum(1 for x in cell_map.values() if x["type"] == "inlineStr"),
        "numeric_cells": sum(1 for x in cell_map.values() if x["value"] is not None and x["type"] not in ("s", "inlineStr")),
        "date_cells": sum(1 for x in cell_map.values() if x["number_format"] == "builtin:14" or "yyyy" in x["number_format"].lower() or "dd" in x["number_format"].lower()),
        "header_filled_cells": sum(1 for x in cell_map.values() if _style_has(x["fill"], "patternFill", "patternType") and _style_has(x["fill"], "fgColor")),
        "bordered_cells": sum(1 for x in cell_map.values() if _style_has(x["border"], "left", "style") or _style_has(x["border"], "right", "style") or _style_has(x["border"], "top", "style") or _style_has(x["border"], "bottom", "style")),
        "shared_strings": len(shared),
        "texts": texts[:40],
    })
    return f


# ------------------------------------------------------------------------ PPTX
_PPTX_SHAPE_TAGS = {P + name for name in ("sp", "pic", "graphicFrame", "cxnSp")}
_PPTX_FILL_TAGS = {A + name for name in ("solidFill", "gradFill", "blipFill", "pattFill",
                                         "noFill", "grpFill")}


def _pptx_xml(node):
    """Return a JSON-safe, prefix-independent signature for meaningful DrawingML."""
    if node is None:
        return None
    return {"tag": node.tag.rsplit("}", 1)[-1],
            "attrs": sorted((key.rsplit("}", 1)[-1], value) for key, value in node.attrib.items()),
            "text": (node.text or "").strip(), "children": [_pptx_xml(child) for child in node]}


def _pptx_transform(shape):
    xfrm = shape.find(f"{P}spPr/{A}xfrm")
    if xfrm is None:
        xfrm = shape.find(f"{P}grpSpPr/{A}xfrm")
    if xfrm is None:
        xfrm = shape.find(f"{P}xfrm")
    if xfrm is None:
        return None
    off, ext = xfrm.find(f"{A}off"), xfrm.find(f"{A}ext")
    child_off, child_ext = xfrm.find(f"{A}chOff"), xfrm.find(f"{A}chExt")
    def pair(node, xkey, ykey):
        if node is None:
            return None
        try:
            return {"x": int(node.get(xkey)), "y": int(node.get(ykey))}
        except (TypeError, ValueError):
            return {"x": node.get(xkey), "y": node.get(ykey)}
    geometry = {"position": pair(off, "x", "y"), "size": pair(ext, "cx", "cy"),
                "rotation": int(xfrm.get("rot", "0")),
                "flip_h": xfrm.get("flipH", "0") == "1",
                "flip_v": xfrm.get("flipV", "0") == "1"}
    if child_off is not None or child_ext is not None:
        geometry["child_position"] = pair(child_off, "x", "y")
        geometry["child_size"] = pair(child_ext, "cx", "cy")
    return geometry


def _pptx_shape_properties(shape):
    props = shape.find(f"{P}spPr")
    if props is None:
        props = shape.find(f"{P}grpSpPr")
    if props is None:
        props = shape
    fill = next((child for child in props if child.tag in _PPTX_FILL_TAGS), None)
    line = props.find(f"{A}ln")
    geom = props.find(f"{A}prstGeom")
    if geom is None:
        geom = props.find(f"{A}custGeom")
    return {"fill": _pptx_xml(fill), "line": _pptx_xml(line), "geometry": _pptx_xml(geom)}


def _pptx_shape_identity(shape):
    nonvisual = next((child for child in shape if child.tag in
                      (P + "nvSpPr", P + "nvPicPr", P + "nvGraphicFramePr", P + "nvCxnSpPr")), None)
    props = nonvisual.find(f"{P}cNvPr") if nonvisual is not None else None
    if props is None:
        return {"id": None, "name": None}
    return {"id": props.get("id"), "name": props.get("name")}


def _pptx_shape_text(shape):
    paragraphs = []
    for paragraph in shape.findall(f".//{A}p"):
        runs = []
        for item in paragraph:
            if item.tag in (A + "r", A + "fld"):
                runs.append("".join(t.text or "" for t in item.findall(f".//{A}t")))
            elif item.tag == A + "br":
                runs.append("\n")
        if not runs:
            runs = ["".join(t.text or "" for t in paragraph.findall(f".//{A}t"))]
        paragraphs.append("".join(runs))
    return paragraphs


def _pptx_slide_shape_data(root, parts, rels, errors, slide_name):
    tree = root.find(f".//{P}spTree")
    if tree is None:
        errors.append(f"{slide_name} has no shape tree")
        return []
    result = []

    def visit(container, groups=()):
        for shape in container:
            if shape.tag == P + "grpSp":
                group_identity = _pptx_shape_identity(shape)
                group_tree = shape.find(f"{P}spTree")
                visit(group_tree if group_tree is not None else shape,
                      groups + ((group_identity, _pptx_transform(shape)),))
                continue
            if shape.tag not in _PPTX_SHAPE_TAGS:
                continue
            identity = _pptx_shape_identity(shape)
            if identity["id"] is None or identity["name"] is None:
                errors.append(f"{slide_name} contains a shape without a complete nonvisual identity")
            key = (identity["id"], identity["name"])
            image = None
            for blip in shape.findall(f".//{A}blip"):
                rel_id = blip.get(R + "embed") or blip.get(R + "link")
                relation = rels.get(rel_id)
                if relation is None:
                    errors.append(f"{slide_name} image relation {rel_id!r} is unresolved")
                    image = {"error": "unresolved relationship", "relationship": rel_id}
                    continue
                target = relation["target"]
                if relation["external"] or target not in parts:
                    errors.append(f"{slide_name} image target {target!r} is missing or external")
                    image = {"error": "missing or external media", "target": target}
                    continue
                image = {"relationship_type": relation["type"],
                         "sha256": hashlib.sha256(parts[target]).hexdigest()}
            result.append({"kind": shape.tag.rsplit("}", 1)[-1], "identity": identity,
                           "group_path": list(groups), "geometry": _pptx_transform(shape),
                           "properties": _pptx_shape_properties(shape),
                           "text": _pptx_shape_text(shape), "image": image})
    visit(tree)
    keys = [(item["identity"]["id"], item["identity"]["name"]) for item in result]
    if len(keys) != len(set(keys)):
        errors.append(f"{slide_name} contains duplicate shape identities")
    return result


def pptx_features(body: bytes) -> dict:
    p = _parts(body)
    pres = _xml(p, "ppt/presentation.xml")
    f: dict = {"kind": "pptx", "parts": sorted(p), "part_count": len(p), "errors": []}
    if pres is None or pres.tag != P + "presentation":
        f["error"] = "missing or invalid ppt/presentation.xml"
        return f
    if _xml(p, "[Content_Types].xml") is None or _xml(p, "_rels/.rels") is None:
        f["errors"].append("package content types or root relationships are missing or invalid")
    slide_ids = pres.find(f"{P}sldIdLst")
    if slide_ids is None or not list(slide_ids):
        f["errors"].append("presentation has no slide list")
    elif len({node.get("id") for node in slide_ids}) != len(list(slide_ids)):
        f["errors"].append("presentation contains duplicate slide identities")
    rels, rel_errors = _docx_relationships(p, "ppt/_rels/presentation.xml.rels", "ppt/presentation.xml")
    f["errors"].extend(rel_errors)
    ordered_slides = []
    seen_targets = set()
    for slide_id in list(slide_ids) if slide_ids is not None else []:
        rel_id = slide_id.get(R + "id")
        relation = rels.get(rel_id)
        if relation is None or relation["type"] != "slide" or relation["external"]:
            f["errors"].append(f"slide relationship {rel_id!r} is unresolved or not a slide")
            ordered_slides.append({"relationship": rel_id, "error": "unresolved slide relationship",
                                   "shapes": []})
            continue
        target = relation["target"]
        if target in seen_targets:
            f["errors"].append(f"slide target {target!r} is referenced more than once")
        seen_targets.add(target)
        root = _xml(p, target)
        if root is None or root.tag != P + "sld":
            f["errors"].append(f"referenced slide {target!r} is missing or invalid")
            ordered_slides.append({"relationship": rel_id, "target": target,
                                   "error": "missing or invalid slide", "shapes": []})
            continue
        slide_rels_name = posixpath.join(posixpath.dirname(target), "_rels",
                                         posixpath.basename(target) + ".rels")
        slide_rels, slide_rel_errors = _docx_relationships(p, slide_rels_name, target)
        if slide_rel_errors:
            f["errors"].extend(slide_rel_errors)
        shapes = _pptx_slide_shape_data(root, p, slide_rels, f["errors"], target)
        common = root.find(f"{P}cSld")
        ordered_slides.append({"target": target,
                               "name": common.get("name") if common is not None else None,
                               "show_master_shapes": common.get("showMasterSp", "1") if common is not None else None,
                               "visible": root.get("show", "1") != "0",
                               "shapes": shapes})
    fills = [{"slide": index, "identity": shape["identity"], "fill": shape["properties"]["fill"]}
             for index, slide in enumerate(ordered_slides) for shape in slide["shapes"]]
    images = [{"slide": index, "identity": shape["identity"], "image": shape["image"]}
              for index, slide in enumerate(ordered_slides) for shape in slide["shapes"]
              if shape["kind"] == "pic"]
    presentation_size = pres.find(f"{P}sldSz")
    dimensions = _pptx_xml(presentation_size)
    if dimensions is None:
        f["errors"].append("presentation slide dimensions are missing")
    f.update({
        "slide_ids": len(slide_ids) if slide_ids is not None else 0,
        "slide_parts": len(ordered_slides),
        "slide_order": [{"name": slide.get("name"),
                         "shapes": [(shape["kind"], shape["identity"]) for shape in slide["shapes"]],
                         "error": slide.get("error")}
                        for slide in ordered_slides],
        "slide_structure": [{"name": slide.get("name"),
                             "show_master_shapes": slide.get("show_master_shapes"),
                             "visible": slide.get("visible"), "error": slide.get("error")}
                            for slide in ordered_slides],
        "presentation_size": dimensions,
        "slide_data": ordered_slides,
        "media_parts": sorted(n for n in p if n.startswith("ppt/media/")),
        "shape_count": sum(len(slide["shapes"]) for slide in ordered_slides),
        "image_data": images,
        "fill_data": fills,
        "errors": f["errors"],
    })
    if f["errors"]:
        f["error"] = "; ".join(sorted(set(f["errors"])))
    return f


# ------------------------------------------------------------------ comparison
def _paragraph_structure(paragraph: dict) -> dict:
    return {"style": paragraph["style"], "numbering": paragraph["numbering"],
            "properties": paragraph["properties"],
            "run_formats": [run["format"] for run in paragraph["runs"]],
            "breaks": paragraph["breaks"]}


def _paragraphs_match(before: list[dict], after: list[dict], marker: str | None = None) -> tuple[bool, int | None]:
    if len(before) != len(after):
        return False, None
    changed = [index for index, (left, right) in enumerate(zip(before, after)) if left != right]
    if not changed:
        return True, None
    if marker is None or len(changed) != 1:
        return False, None
    if (sum(p["text"].count(marker) for p in after) != 1
            or sum(p["text"].count(marker) for p in before) != 0):
        return False, None
    index = changed[0]
    if marker not in after[index]["text"] or marker in before[index]["text"]:
        return False, None
    if _paragraph_structure(before[index]) != _paragraph_structure(after[index]):
        return False, None
    return True, index


def _tables_match(before: list[dict], after: list[dict], marker: str | None = None) -> bool:
    if len(before) != len(after):
        return False
    for left, right in zip(before, after):
        if left["properties"] != right["properties"] or left["grid"] != right["grid"]:
            return False
        if len(left["rows"]) != len(right["rows"]):
            return False
        for lrow, rrow in zip(left["rows"], right["rows"]):
            if lrow["properties"] != rrow["properties"] or len(lrow["cells"]) != len(rrow["cells"]):
                return False
            for lcell, rcell in zip(lrow["cells"], rrow["cells"]):
                if lcell["properties"] != rcell["properties"]:
                    return False
                equal, _ = _paragraphs_match(lcell["paragraphs"], rcell["paragraphs"], marker)
                if not equal or not _tables_match(lcell["nested_tables"], rcell["nested_tables"], marker):
                    return False
    return True


def _feature_status(before, after) -> str:
    if before == after:
        return "PRESERVED" if before not in (None, [], {}, "", 0, False) else "NOT_SUPPORTED"
    if before and not after:
        return "LOST"
    return "ALTERED"


def _pptx_text_match(before: list[dict], after: list[dict], marker: str | None) -> bool:
    if len(before) != len(after):
        return False
    changed = []
    marker_count = 0
    old_marker_count = 0
    for slide_index, (left_slide, right_slide) in enumerate(zip(before, after)):
        left_shapes, right_shapes = left_slide["shapes"], right_slide["shapes"]
        if len(left_shapes) != len(right_shapes):
            return False
        for shape_index, (left, right) in enumerate(zip(left_shapes, right_shapes)):
            if (left["kind"], left["identity"]) != (right["kind"], right["identity"]):
                return False
            left_text, right_text = left["text"], right["text"]
            marker_count += sum(text.count(marker) for text in right_text) if marker else 0
            old_marker_count += sum(text.count(marker) for text in left_text) if marker else 0
            if left_text != right_text:
                changed.append((slide_index, shape_index, left_text, right_text))
    if not changed:
        return True
    if marker is None or len(changed) != 1 or marker_count != 1 or old_marker_count:
        return False
    _slide, _shape, left_text, right_text = changed[0]
    old_value, new_value = "\n".join(left_text), "\n".join(right_text)
    return new_value == marker or new_value.replace(marker, "", 1) == old_value


def _pptx_geometry(slides: list[dict]) -> list[dict]:
    return [{"slide": slide_index, "identity": shape["identity"],
             "group_path": shape["group_path"], "geometry": shape["geometry"]}
            for slide_index, slide in enumerate(slides) for shape in slide["shapes"]]


def _pptx_geometry_status(before: list[dict], after: list[dict]) -> str:
    left, right = _pptx_geometry(before), _pptx_geometry(after)
    if left != right:
        return "LOST" if any(item["geometry"] is not None for item in left) and not any(
            item["geometry"] is not None for item in right) else "ALTERED"
    return "PRESERVED" if any(item["geometry"] is not None for item in left) else "NOT_SUPPORTED"


def _pptx_has_text(slides: list[dict]) -> bool:
    return any(any(paragraph for paragraph in shape["text"])
               for slide in slides for shape in slide["shapes"])


def _pptx_shape_structure(slides: list[dict]) -> list[dict]:
    return [{"slide": slide_index, "kind": shape["kind"], "identity": shape["identity"],
             "group_path": shape["group_path"],
             "properties": {key: shape["properties"][key] for key in ("line", "geometry")}}
            for slide_index, slide in enumerate(slides) for shape in slide["shapes"]]


def _pptx_fills_status(before: list[dict], after: list[dict]) -> str:
    if before != after:
        return "LOST" if any(item["fill"] is not None for item in before) and not any(
            item["fill"] is not None for item in after) else "ALTERED"
    return "PRESERVED" if any(item["fill"] is not None for item in before) else "NOT_SUPPORTED"


def _pptx_slide_size(value):
    if value is None:
        return None
    attrs = dict(value.get("attrs", []))
    return (attrs.get("cx"), attrs.get("cy"))


def _docx_run_projection(features: dict, key: str, allowed: int | None) -> list[dict]:
    result = []
    for pindex, paragraph in enumerate(features.get("paragraph_data", [])):
        for rindex, run in enumerate(paragraph["runs"]):
            value = run["format"][key]
            if value:
                result.append({"paragraph": pindex, "run": rindex,
                               "text": None if pindex == allowed else run["text"], "value": value})
    return result


def _docx_list_projection(features: dict, allowed: int | None) -> list[dict]:
    return [{"index": item["index"], "text": None if item["index"] == allowed else item["text"],
             "numbering": item["numbering"]} for item in features.get("list_data", [])]


def _docx_unicode_projection(features: dict, field: str, allowed: int | None) -> list[dict]:
    projection = []
    for index, paragraph in enumerate(features.get("paragraph_data", [])):
        text = "" if index == allowed else paragraph["text"]
        chars = []
        for char in text:
            name = unicodedata.name(char, "")
            if field == "accent_text" and ord(char) > 127 and name.startswith("LATIN"):
                chars.append(char)
            elif field == "cjk_text" and any(script in name for script in
                    ("CJK", "IDEOGRAPH", "HIRAGANA", "KATAKANA", "HANGUL")):
                chars.append(char)
        projection.append("".join(chars))
    return projection


def _docx_used_style_projection(features: dict) -> dict:
    used = {paragraph["style"] for paragraph in features.get("paragraph_data", [])
            if paragraph["style"]}
    used.update(run["format"]["style"] for paragraph in features.get("paragraph_data", [])
                for run in paragraph["runs"] if run["format"]["style"])
    def table_styles(tables):
        for table in tables:
            yield from (prop["style"] for prop in table["properties"]
                        if prop.get("tag") == "tblStyle" and prop.get("style"))
            for row in table["rows"]:
                for cell in row["cells"]:
                    yield from table_styles(cell["nested_tables"])
    used.update(table_styles(features.get("table_data", [])))
    return {name: features.get("style_data", {}).get(name) for name in sorted(used)}


def compare(original: bytes, saved: bytes, marker: str | None = None) -> dict:
    kind = "docx"
    if original[:2] == b"PK":
        try:
            with zipfile.ZipFile(BytesIO(original)) as z:
                names = z.namelist()
        except zipfile.BadZipFile as exc:
            return {"kind": kind, "error": f"original file is not a readable package: {exc}",
                    "verdicts": {"document": "NOT_VERIFIED"}, "counts": {"NOT_VERIFIED": 1},
                    "regressions": ["document"]}
        if any(n.startswith("xl/") for n in names):
            kind = "xlsx"
        elif any(n.startswith("ppt/") for n in names):
            kind = "pptx"
    fn = {"docx": docx_features, "xlsx": xlsx_features, "pptx": pptx_features}[kind]
    try:
        before = fn(original)
        after = fn(saved)
    except (zipfile.BadZipFile, KeyError, OSError, ValueError, ET.ParseError) as exc:
        message = "file is not a readable %s: %s" % (kind, exc)
        return {"kind": kind, "error": message, "verdicts": {"document": "NOT_VERIFIED"},
                "counts": {"NOT_VERIFIED": 1}, "regressions": ["document"]}

    if before.get("error") or after.get("error"):
        message = "; ".join(value for value in (before.get("error"), after.get("error")) if value)
        return {"kind": kind, "error": message, "verdicts": {"document": "NOT_VERIFIED"},
                "counts": {"NOT_VERIFIED": 1}, "regressions": ["document"],
                "before": before, "after": after}

    verdicts: dict[str, str] = {}

    def mark(feature: str, status: str) -> None:
        verdicts[feature] = status

    if kind == "docx":
        paragraphs_match, allowed = _paragraphs_match(
            before["paragraph_data"], after["paragraph_data"], marker)
        mark("paragraphs", "PRESERVED" if paragraphs_match else _feature_status(
            before["paragraph_data"], after["paragraph_data"]))
        mark("paragraph_count", "PRESERVED" if before["paragraphs"] == after["paragraphs"] else "ALTERED")
        effective_marker = marker if allowed is not None else None
        tables_match = _tables_match(before["table_data"], after["table_data"], effective_marker)
        mark("tables", "PRESERVED" if tables_match and before["table_data"] else
             ("NOT_SUPPORTED" if tables_match else _feature_status(before["table_data"], after["table_data"])))
        mark("images", _feature_status(before["image_data"], after["image_data"]))
        mark("page_breaks", _feature_status(before["page_break_data"], after["page_break_data"]))
        mark("list_paragraphs", "PRESERVED" if _docx_list_projection(before, allowed) ==
             _docx_list_projection(after, allowed) and before["list_data"] else
             ("NOT_SUPPORTED" if not before["list_data"] and not after["list_data"] else
              _feature_status(before["list_data"], after["list_data"])))
        for feature, format_key in (("bold_runs", "bold"), ("italic_runs", "italic"),
                                    ("colour_runs", "color")):
            left = _docx_run_projection(before, format_key, allowed)
            right = _docx_run_projection(after, format_key, allowed)
            mark(feature, _feature_status(left, right))
        mark("paragraph_styles", _feature_status(
            [p["style"] for p in before["paragraph_data"]],
            [p["style"] for p in after["paragraph_data"]]))
        mark("style_definitions", _feature_status(_docx_used_style_projection(before),
                                                   _docx_used_style_projection(after)))
        for feature, key in (("heading1", "Heading1"), ("title_style", "Title")):
            mark(feature, _feature_status(before["style_indices"][key], after["style_indices"][key]))
        mark("sectPr", _feature_status(before["section_data"], after["section_data"]))
        mark("header", _feature_status(before["headers"], after["headers"]))
        mark("footer_page_field", _feature_status(before["footers"], after["footers"]))
        for feature in ("accent_text", "cjk_text"):
            left, right = (_docx_unicode_projection(before, feature, allowed),
                           _docx_unicode_projection(after, feature, allowed))
            mark("accents" if feature == "accent_text" else "cjk", _feature_status(left, right))
    elif kind == "xlsx":
        mark("sheet_count",
             "PRESERVED" if after.get("sheet_count") == before.get("sheet_count") else "ALTERED")
        mark("sheet_names",
             "PRESERVED" if after.get("sheet_names") == before.get("sheet_names") else "ALTERED")
        mark("formulas", "PRESERVED" if before.get("formulas") == after.get("formulas") else "ALTERED")
        mark("cross_sheet_formula",
             "PRESERVED" if after.get("cross_sheet_formula") else "LOST")
        mark("sum_formula", "PRESERVED" if after.get("sum_formula") else "LOST")
        mark("date_format",
             "PRESERVED" if after.get("date_cells") else
             ("ALTERED" if before.get("date_cells") else "LOST"))
        mark("header_fill",
             "PRESERVED" if after.get("header_filled_cells") else "LOST")
        mark("borders", "PRESERVED" if after.get("bordered_cells") else "LOST")
        before_cells, after_cells = before.get("cells", {}), after.get("cells", {})
        allowed = set()
        if marker:
            allowed = {key for key, value in after_cells.items()
                       if marker in str(value.get("value"))
                       and marker not in str(before_cells.get(key, {}).get("value"))}
        keys = set(before_cells) | set(after_cells)
        def equal_cell(key, field):
            return before_cells.get(key, {}).get(field) == after_cells.get(key, {}).get(field)
        mark("cell_values", "PRESERVED" if all(key in allowed or
             (equal_cell(key, "value") and equal_cell(key, "value_type")) for key in keys) else "ALTERED")
        mark("number_formats", "PRESERVED" if all(equal_cell(key, "number_format") for key in keys) else "ALTERED")
        mark("fills", "PRESERVED" if all(equal_cell(key, "fill") for key in keys) else "ALTERED")
        mark("borders", "PRESERVED" if all(equal_cell(key, "border") for key in keys) else "ALTERED")
        mark("fonts", "PRESERVED" if all(equal_cell(key, "font") for key in keys) else "ALTERED")
        mark("charts", "NOT_SUPPORTED")  # no fixture chart; no editor chart claim
    else:
        before_slides, after_slides = before["slide_data"], after["slide_data"]
        mark("slide_count", "PRESERVED" if len(before_slides) == len(after_slides) else
             ("LOST" if len(after_slides) < len(before_slides) else "ALTERED"))
        mark("slide_order", "PRESERVED" if before.get("slide_order") == after.get("slide_order") else "ALTERED")
        mark("slide_structure", "PRESERVED" if before.get("slide_structure") == after.get("slide_structure")
             else "ALTERED")
        before_shapes = _pptx_shape_structure(before_slides)
        after_shapes = _pptx_shape_structure(after_slides)
        mark("shapes", "PRESERVED" if before_shapes == after_shapes and before_shapes else
             ("NOT_SUPPORTED" if not before_shapes and not after_shapes else
              ("LOST" if before_shapes and not after_shapes else "ALTERED")))
        mark("shape_count", "PRESERVED" if before.get("shape_count") == after.get("shape_count") else "ALTERED")
        mark("slide_dimensions", "PRESERVED" if _pptx_slide_size(before.get("presentation_size")) ==
             _pptx_slide_size(after.get("presentation_size")) else "ALTERED")
        mark("geometry", _pptx_geometry_status(before_slides, after_slides))
        mark("texts", "PRESERVED" if _pptx_has_text(before_slides) and
             _pptx_text_match(before_slides, after_slides, marker) else
             ("NOT_SUPPORTED" if not _pptx_has_text(before_slides) and not _pptx_has_text(after_slides)
              else ("LOST" if not _pptx_has_text(after_slides) else "ALTERED")))
        mark("images", _feature_status(before.get("image_data"), after.get("image_data")))
        mark("fills", _pptx_fills_status(before.get("fill_data", []), after.get("fill_data", [])))

    counts: dict[str, int] = {}
    for status in verdicts.values():
        counts[status] = counts.get(status, 0) + 1
    return {
        "kind": kind,
        "verdicts": verdicts,
        "counts": counts,
        "before": before,
        "after": after,
        "regressions": sorted(k for k, v in verdicts.items()
                               if v in ("LOST", "ALTERED", "NOT_VERIFIED")),
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
