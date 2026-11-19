#!/usr/bin/env python3
"""Representative DOCX/XLSX/PPTX fixtures for round-trip fidelity checks.

Stdlib only. These are deliberately *richer* than the minimal fixtures used by
the 66/66 browser replay: they contain the features a real document carries and
that a canvas editor can silently drop on save.

  DOCX  title, headings, bold/italic/colored runs, accents and CJK, bullets,
        numbered list, 3x3 table, inline PNG image, page break, header,
        footer with a PAGE field.
  XLSX  two sheets, inline strings, numbers, a real date with a number format,
        a SUM formula, a cross-sheet formula, a header row with fill+borders.
  PPTX  three slides, text boxes, a rectangle shape, an inline image, and
        precisely positioned EMU geometry.

A valid ZIP is not evidence of fidelity: `fidelity_compare.py` reads the actual
parts and classifies each feature. Nothing here is written to look good -- the
fixtures are fixed and the comparison is computed from the bytes.

Usage:
    python3 lab/real-seafile/fidelity_corpus.py <output-dir>
"""
from __future__ import annotations

import hashlib
import json
import struct
import sys
import zipfile
import zlib
from io import BytesIO
from pathlib import Path

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG = "http://schemas.openxmlformats.org/package/2006/relationships"
CT = "http://schemas.openxmlformats.org/package/2006/content-types"
S = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
P = "http://schemas.openxmlformats.org/presentationml/2006/main"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
PIC = "http://schemas.openxmlformats.org/drawingml/2006/picture"


# --------------------------------------------------------------------- assets
def png_bytes(size: int = 8, rgb: tuple[int, int, int] = (200, 40, 40)) -> bytes:
    """A deterministic solid-colour PNG, built without Pillow."""
    raw = b"".join(b"\x00" + bytes(rgb) * size for _ in range(size))

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))

    ihdr = struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


def _zip(parts: dict[str, bytes | str]) -> bytes:
    out = BytesIO()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for name, content in parts.items():
            info = zipfile.ZipInfo(name, date_time=(2020, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            z.writestr(info, content.encode("utf-8") if isinstance(content, str) else content)
    return out.getvalue()


# ------------------------------------------------------------------------ DOCX
def _w_run(text: str, *, bold=False, italic=False, color=None, size=None) -> str:
    props = []
    if bold:
        props.append("<w:b/>")
    if italic:
        props.append("<w:i/>")
    if color:
        props.append('<w:color w:val="%s"/>' % color)
    if size:
        props.append('<w:sz w:val="%d"/>' % size)
    rpr = "<w:rPr>%s</w:rPr>" % "".join(props) if props else ""
    text = (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
    return '<w:r>%s<w:t xml:space="preserve">%s</w:t></w:r>' % (rpr, text)


def _w_para(*runs: str, style=None, num_id=None, page_break=False, keep=False) -> str:
    props = []
    if style:
        props.append('<w:pStyle w:val="%s"/>' % style)
    if num_id:
        props.append('<w:numPr><w:ilvl w:val="0"/><w:numId w:val="%d"/></w:numPr>' % num_id)
    if keep:
        props.append("<w:keepNext/>")
    ppr = "<w:pPr>%s</w:pPr>" % "".join(props) if props else ""
    body = '<w:r><w:br w:type="page"/></w:r>' if page_break else "".join(runs)
    return "<w:p>%s%s</w:p>" % (ppr, body)


def _w_cell(text: str, *, header=False, width=2400) -> str:
    shade = '<w:shd w:val="clear" w:fill="D9EAF7"/>' if header else ""
    return ('<w:tc><w:tcPr><w:tcW w:w="%d" w:type="dxa"/>%s</w:tcPr>%s</w:tc>'
            % (width, shade, _w_para(_w_run(text, bold=header))))


def _w_table(rows: list[list[str]]) -> str:
    border = ("<w:tblBorders>"
              '<w:top w:val="single" w:sz="6"/><w:left w:val="single" w:sz="6"/>'
              '<w:bottom w:val="single" w:sz="6"/><w:right w:val="single" w:sz="6"/>'
              '<w:insideH w:val="single" w:sz="4"/><w:insideV w:val="single" w:sz="4"/>'
              "</w:tblBorders>")
    trs = "".join("<w:tr>%s</w:tr>" % "".join(_w_cell(c, header=(i == 0)) for c in row)
                  for i, row in enumerate(rows))
    grid = "".join('<w:gridCol w:w="2400"/>' for _ in rows[0])
    return ('<w:tbl><w:tblPr><w:tblW w:w="4800" w:type="dxa"/>%s</w:tblPr>'
            "<w:tblGrid>%s</w:tblGrid>%s</w:tbl>" % (border, grid, trs))


def _w_image(rel_id: str, cx=914400, cy=914400, name="image1.png") -> str:
    return (
        '<w:p><w:r><w:drawing>'
        '<wp:inline distT="0" distB="0" distL="0" distR="0">'
        '<wp:extent cx="%d" cy="%d"/><wp:docPr id="1" name="Picture 1"/>'
        '<wp:cNvGraphicFramePr><a:graphicFrameLocks noChangeAspect="1"/></wp:cNvGraphicFramePr>'
        '<a:graphic><a:graphicData uri="%s">'
        '<pic:pic><pic:nvPicPr><pic:cNvPr id="1" name="%s"/><pic:cNvPicPr/></pic:nvPicPr>'
        '<pic:blipFill><a:blip r:embed="%s"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
        '<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="%d" cy="%d"/></a:xfrm>'
        '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr>'
        "</pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>"
        % (cx, cy, PIC, name, rel_id, cx, cy)
    )


DOCX_STYLES = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<w:styles xmlns:w="%s">'
    "<w:docDefaults><w:rPrDefault><w:rPr>"
    '<w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:sz w:val="22"/>'
    "</w:rPr></w:rPrDefault><w:pPrDefault><w:pPr>"
    '<w:spacing w:after="160"/></w:pPr></w:pPrDefault></w:docDefaults>'
    '<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/></w:style>'
    '<w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/>'
    '<w:basedOn w:val="Normal"/><w:pPr><w:keepNext/></w:pPr>'
    '<w:rPr><w:b/><w:color w:val="1F4E79"/><w:sz w:val="36"/></w:rPr></w:style>'
    '<w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/>'
    '<w:basedOn w:val="Normal"/><w:next w:val="Normal"/>'
    '<w:pPr><w:keepNext/><w:spacing w:before="240" w:after="120"/></w:pPr>'
    '<w:rPr><w:b/><w:color w:val="2F5597"/><w:sz w:val="28"/></w:rPr></w:style>'
    '<w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/>'
    '<w:basedOn w:val="Normal"/><w:rPr><w:b/><w:sz w:val="24"/></w:rPr></w:style>'
    "</w:styles>" % W
)

DOCX_NUMBERING = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<w:numbering xmlns:w="%s">'
    '<w:abstractNum w:abstractNumId="0"><w:multiLevelType w:val="singleLevel"/>'
    '<w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="bullet"/>'
    '<w:lvlText w:val="\u2022"/><w:lvlJc w:val="left"/>'
    '<w:pPr><w:ind w:left="720" w:hanging="360"/></w:pPr></w:lvl></w:abstractNum>'
    '<w:abstractNum w:abstractNumId="1"><w:multiLevelType w:val="singleLevel"/>'
    '<w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="decimal"/>'
    '<w:lvlText w:val="%%1."/><w:lvlJc w:val="left"/>'
    '<w:pPr><w:ind w:left="720" w:hanging="360"/></w:pPr></w:lvl></w:abstractNum>'
    '<w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num>'
    '<w:num w:numId="2"><w:abstractNumId w:val="1"/></w:num>'
    "</w:numbering>" % W
)


def docx() -> bytes:
    body = "".join([
        _w_para(_w_run("Fidelity report — synthetic"), style="Title"),
        _w_para(_w_run("Heading one", bold=True), style="Heading1"),
        _w_para(_w_run("Plain paragraph, then "),
                _w_run("bold", bold=True), _w_run(", "),
                _w_run("italic", italic=True), _w_run(", and "),
                _w_run("coloured", color="C00000"), _w_run(" runs.")),
        # accents + CJK: an encoding loss is a real fidelity regression
        _w_para(_w_run("Accents: Caf\u00e9 na\u00efve r\u00e9sum\u00e9 \u00c5ngstr\u00f6m \u00f1 \u00fc")),
        _w_para(_w_run("CJK: \u65e5\u672c\u8a9e \u4e2d\u6587 \ud55c\uad6d\uc5b4")),
        _w_para(_w_run("Structure", bold=True), style="Heading2"),
        _w_para(_w_run("First bullet"), num_id=1),
        _w_para(_w_run("Second bullet"), num_id=1),
        _w_para(_w_run("First numbered item"), num_id=2),
        _w_para(_w_run("Second numbered item"), num_id=2),
        _w_para(_w_run("Table", bold=True), style="Heading2"),
        _w_table([["Item", "Value", "Note"], ["Alpha", "1", "one"],
                  ["Beta", "2", "two"], ["Gamma", "3", "three"]]),
        _w_para(_w_run("Image below", bold=True), style="Heading2"),
        _w_image("rId5"),
        _w_para(page_break=True),
        _w_para(_w_run("Second page", bold=True), style="Heading1"),
        _w_para(_w_run("Text after the page break.")),
    ])

    document = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="%s" xmlns:r="%s" xmlns:wp="%s" xmlns:a="%s" xmlns:pic="%s">'
        "<w:body>%s"
        '<w:sectPr><w:headerReference w:type="default" r:id="rId3"/>'
        '<w:footerReference w:type="default" r:id="rId4"/>'
        '<w:pgSz w:w="12240" w:h="15840"/>'
        '<w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"'
        ' w:header="720" w:footer="720" w:gutter="0"/></w:sectPr>'
        "</w:body></w:document>" % (W, R, WP, A, PIC, body)
    )

    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="%s">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Default Extension="png" ContentType="image/png"/>'
        '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
        '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
        '<Override PartName="/word/numbering.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/>'
        '<Override PartName="/word/header1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.header+xml"/>'
        '<Override PartName="/word/footer1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/>'
        "</Types>" % CT
    )

    root_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="%s">'
        '<Relationship Id="rId1" Type="%s/officeDocument" Target="word/document.xml"/>'
        "</Relationships>" % (PKG, R)
    )

    doc_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="%s">'
        '<Relationship Id="rId1" Type="%s/styles" Target="styles.xml"/>'
        '<Relationship Id="rId2" Type="%s/numbering" Target="numbering.xml"/>'
        '<Relationship Id="rId3" Type="%s/header" Target="header1.xml"/>'
        '<Relationship Id="rId4" Type="%s/footer" Target="footer1.xml"/>'
        '<Relationship Id="rId5" Type="%s/image" Target="media/image1.png"/>'
        "</Relationships>" % (PKG, R, R, R, R, R)
    )

    header = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
              '<w:hdr xmlns:w="%s">%s</w:hdr>'
              % (W, _w_para(_w_run("ARTCRAFT FIDELITY HEADER", color="666666"))))
    footer = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
              '<w:ftr xmlns:w="%s"><w:p><w:r><w:t>Page </w:t></w:r>'
              '<w:fldSimple w:instr="PAGE"><w:r><w:t>1</w:t></w:r></w:fldSimple></w:p></w:ftr>'
              % W)

    return _zip({
        "[Content_Types].xml": content_types,
        "_rels/.rels": root_rels,
        "word/document.xml": document,
        "word/_rels/document.xml.rels": doc_rels,
        "word/styles.xml": DOCX_STYLES,
        "word/numbering.xml": DOCX_NUMBERING,
        "word/header1.xml": header,
        "word/footer1.xml": footer,
        "word/media/image1.png": png_bytes(),
    })


# ------------------------------------------------------------------------ XLSX
XLSX_STYLES = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<styleSheet xmlns="%s">'
    '<fonts count="2"><font><sz val="11"/><name val="Calibri"/></font>'
    '<font><b/><sz val="11"/><name val="Calibri"/></font></fonts>'
    '<fills count="3"><fill><patternFill patternType="none"/></fill>'
    '<fill><patternFill patternType="gray125"/></fill>'
    '<fill><patternFill patternType="solid"><fgColor rgb="FFD9EAF7"/><bgColor indexed="64"/></patternFill></fill></fills>'
    '<borders count="2"><border><left/><right/><top/><bottom/><diagonal/></border>'
    '<border><left style="thin"/><right style="thin"/><top style="thin"/><bottom style="thin"/><diagonal/></border></borders>'
    '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
    '<cellXfs count="4">'
    '<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>'
    '<xf numFmtId="0" fontId="1" fillId="2" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1"/>'
    '<xf numFmtId="14" fontId="0" fillId="0" borderId="1" xfId="0" applyNumberFormat="1" applyBorder="1"/>'
    '<xf numFmtId="0" fontId="0" fillId="0" borderId="1" xfId="0" applyBorder="1"/>'
    "</cellXfs>"
    '<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>'
    "</styleSheet>" % S
)


def _c(ref: str, *, s=None, text=None, number=None, formula=None) -> str:
    style = ' s="%d"' % s if s is not None else ""
    if text is not None:
        escaped = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        return '<c r="%s"%s t="inlineStr"><is><t>%s</t></is></c>' % (ref, style, escaped)
    if formula is not None:
        cached = number if number is not None else 0
        return '<c r="%s"%s><f>%s</f><v>%s</v></c>' % (ref, style, formula, cached)
    return '<c r="%s"%s><v>%s</v></c>' % (ref, style, number)


def xlsx() -> bytes:
    sheet1_rows = [
        '<row r="1">%s%s%s</row>' % (_c("A1", s=1, text="Item"), _c("B1", s=1, text="Value"),
                                     _c("C1", s=1, text="Link")),
        '<row r="2">%s%s%s</row>' % (_c("A2", s=3, text="Alpha"), _c("B2", s=3, number=10),
                                     _c("C2", s=3, formula="Sheet2!B1", number=42)),
        '<row r="3">%s%s</row>' % (_c("A3", s=3, text="Beta"), _c("B3", s=3, number=20)),
        '<row r="4">%s%s</row>' % (_c("A4", s=3, text="Gamma"), _c("B4", s=3, number=30)),
        '<row r="5">%s%s</row>' % (_c("A5", s=3, text="Total"),
                                   _c("B5", s=3, formula="SUM(B2:B4)", number=60)),
        '<row r="7">%s%s</row>' % (_c("A7", s=3, text="Date"),
                                   _c("B7", s=2, number=45292)),  # 2024-01-15
    ]
    sheet2_rows = [
        '<row r="1">%s%s</row>' % (_c("A1", s=1, text="Source"), _c("B1", s=1, text="Number")),
        '<row r="2">%s%s</row>' % (_c("A2", s=3, text="Constant"), _c("B2", s=3, number=42)),
    ]

    def sheet(rows: list[str], cols: str) -> str:
        return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<worksheet xmlns="%s"><sheetPr/><dimension ref="A1:C7"/>'
                '<sheetViews><sheetView workbookViewId="0"/></sheetViews>'
                '<sheetFormatPr defaultRowHeight="15"/>'
                '<cols>%s</cols><sheetData>%s</sheetData>'
                "</worksheet>" % (S, cols, "".join(rows)))

    cols1 = ('<col min="1" max="1" width="16" customWidth="1"/>'
             '<col min="2" max="3" width="12" customWidth="1"/>')
    cols2 = '<col min="1" max="2" width="16" customWidth="1"/>'

    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="%s">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        '<Override PartName="/xl/worksheets/sheet2.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
        "</Types>" % CT
    )

    return _zip({
        "[Content_Types].xml": content_types,
        "_rels/.rels": ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                        '<Relationships xmlns="%s">'
                        '<Relationship Id="rId1" Type="%s/officeDocument" Target="xl/workbook.xml"/>'
                        "</Relationships>" % (PKG, R)),
        "xl/workbook.xml": ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                            '<workbook xmlns="%s" xmlns:r="%s">'
                            "<sheets>"
                            '<sheet name="Data" sheetId="1" r:id="rId1"/>'
                            '<sheet name="Source" sheetId="2" r:id="rId2"/>'
                            "</sheets></workbook>" % (S, R)),
        "xl/_rels/workbook.xml.rels": ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                                       '<Relationships xmlns="%s">'
                                       '<Relationship Id="rId1" Type="%s/worksheet" Target="worksheets/sheet1.xml"/>'
                                       '<Relationship Id="rId2" Type="%s/worksheet" Target="worksheets/sheet2.xml"/>'
                                       '<Relationship Id="rId3" Type="%s/styles" Target="styles.xml"/>'
                                       "</Relationships>" % (PKG, R, R, R)),
        "xl/styles.xml": XLSX_STYLES,
        "xl/worksheets/sheet1.xml": sheet(sheet1_rows, cols1),
        "xl/worksheets/sheet2.xml": sheet(sheet2_rows, cols2),
    })


# ------------------------------------------------------------------------ PPTX
def _sp(shape_id: int, name: str, x: int, y: int, cx: int, cy: int,
        text: str, *, size=1800, bold=False, fill=None, align="l") -> str:
    solid = ('<a:solidFill><a:srgbClr val="%s"/></a:solidFill>' % fill) if fill else ""
    return (
        '<p:sp><p:nvSpPr><p:cNvPr id="%d" name="%s"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
        '<p:spPr><a:xfrm><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></a:xfrm>'
        '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>%s</p:spPr>'
        '<p:txBody><a:bodyPr wrap="square" anchor="t"/><a:lstStyle/>'
        '<a:p><a:pPr algn="%s"/><a:r><a:rPr lang="en-US" sz="%d"%s/><a:t>%s</a:t></a:r></a:p>'
        "</p:txBody></p:sp>"
        % (shape_id, name, x, y, cx, cy, solid, align, size,
           ' b="1"' if bold else "", text)
    )


def _pic(shape_id: int, name: str, rel_id: str, x: int, y: int, cx: int, cy: int) -> str:
    return (
        '<p:pic><p:nvPicPr><p:cNvPr id="%d" name="%s"/><p:cNvPicPr/><p:nvPr/></p:nvPicPr>'
        '<p:blipFill><a:blip r:embed="%s"/><a:stretch><a:fillRect/></a:stretch></p:blipFill>'
        '<p:spPr><a:xfrm><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></a:xfrm>'
        '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr></p:pic>'
        % (shape_id, name, rel_id, x, y, cx, cy)
    )


def _slide(shapes: str) -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<p:sld xmlns:a="%s" xmlns:r="%s" xmlns:p="%s">'
        "<p:cSld><p:spTree>"
        '<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
        '<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/>'
        '<a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
        "%s</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>"
        % (A, R, P, shapes)
    )


def _slide_rels(extra: str = "") -> str:
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="%s">'
            '<Relationship Id="rId1" Type="%s/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>'
            "%s</Relationships>" % (PKG, R, extra))


PPTX_LAYOUT = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<p:sldLayout xmlns:a="%s" xmlns:r="%s" xmlns:p="%s" type="blank" preserve="1">'
    '<p:cSld name="Blank"><p:spTree>'
    '<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
    '<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/>'
    '<a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
    "</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sldLayout>"
    % (A, R, P)
)

PPTX_MASTER = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<p:sldMaster xmlns:a="%s" xmlns:r="%s" xmlns:p="%s">'
    '<p:cSld name="Master"><p:spTree>'
    '<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
    '<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/>'
    '<a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
    "</p:spTree></p:cSld>"
    '<p:clrMap accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4"'
    ' accent5="accent5" accent6="accent6" bg1="lt1" bg2="lt2" folHlink="folHlink"'
    ' hlink="hlink" tx1="dk1" tx2="dk2"/>'
    '<p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst>'
    "<p:txStyles><p:titleStyle/><p:bodyStyle/><p:otherStyle/></p:txStyles></p:sldMaster>"
    % (A, R, P)
)

PPTX_THEME = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<a:theme xmlns:a="%s" name="Fidelity"><a:themeElements>'
    '<a:clrScheme name="Fidelity">'
    '<a:dk1><a:srgbClr val="000000"/></a:dk1><a:lt1><a:srgbClr val="FFFFFF"/></a:lt1>'
    '<a:dk2><a:srgbClr val="183153"/></a:dk2><a:lt2><a:srgbClr val="F2F6FF"/></a:lt2>'
    '<a:accent1><a:srgbClr val="4F81BD"/></a:accent1><a:accent2><a:srgbClr val="C0504D"/></a:accent2>'
    '<a:accent3><a:srgbClr val="9BBB59"/></a:accent3><a:accent4><a:srgbClr val="8064A2"/></a:accent4>'
    '<a:accent5><a:srgbClr val="4BACC6"/></a:accent5><a:accent6><a:srgbClr val="F79646"/></a:accent6>'
    '<a:hlink><a:srgbClr val="0000FF"/></a:hlink><a:folHlink><a:srgbClr val="800080"/></a:folHlink>'
    "</a:clrScheme>"
    '<a:fontScheme name="Fidelity"><a:majorFont><a:latin typeface="Arial"/>'
    '<a:ea typeface=""/><a:cs typeface=""/></a:majorFont>'
    '<a:minorFont><a:latin typeface="Arial"/><a:ea typeface=""/>'
    '<a:cs typeface=""/></a:minorFont></a:fontScheme>'
    '<a:fmtScheme name="Fidelity">'
    '<a:fillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill>'
    '<a:solidFill><a:schemeClr val="phClr"/></a:solidFill>'
    '<a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:fillStyleLst>'
    '<a:lnStyleLst><a:ln w="9525"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln>'
    '<a:ln w="9525"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln>'
    '<a:ln w="9525"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln></a:lnStyleLst>'
    '<a:effectStyleLst><a:effectStyle><a:effectLst/></a:effectStyle>'
    '<a:effectStyle><a:effectLst/></a:effectStyle>'
    '<a:effectStyle><a:effectLst/></a:effectStyle></a:effectStyleLst>'
    '<a:bgFillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill>'
    '<a:solidFill><a:schemeClr val="phClr"/></a:solidFill>'
    '<a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:bgFillStyleLst>'
    "</a:fmtScheme></a:themeElements></a:theme>" % A
)


def pptx() -> bytes:
    slide1 = _slide(
        _sp(2, "Title", 914400, 1885950, 7315200, 1371600,
            "ArtCraft fidelity deck", size=2800, bold=True, fill="F2F6FF", align="ctr"))
    slide2 = _slide(
        _sp(2, "Heading", 609600, 457200, 4572000, 685800,
            "Second slide heading", size=2400, bold=True, fill="D9EAF7")
        + _sp(3, "Body", 609600, 1371600, 4572000, 1828800,
              "Body text on slide two, with a rectangle shape.", size=1600)
        + _pic(4, "Picture 1", "rId2", 5486400, 1371600, 1828800, 1828800))
    slide3 = _slide(
        _sp(2, "Precise", 1234440, 987552, 6400800, 1371600,
            "Precisely positioned text", size=2000, bold=True))

    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="%s">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Default Extension="png" ContentType="image/png"/>'
        '<Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>'
        '<Override PartName="/ppt/slides/slide1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
        '<Override PartName="/ppt/slides/slide2.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
        '<Override PartName="/ppt/slides/slide3.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
        '<Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>'
        '<Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>'
        '<Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>'
        "</Types>" % CT
    )

    return _zip({
        "[Content_Types].xml": content_types,
        "_rels/.rels": ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                        '<Relationships xmlns="%s">'
                        '<Relationship Id="rId1" Type="%s/officeDocument" Target="ppt/presentation.xml"/>'
                        "</Relationships>" % (PKG, R)),
        "ppt/presentation.xml": (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<p:presentation xmlns:a="%s" xmlns:r="%s" xmlns:p="%s">'
            '<p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst>'
            '<p:sldIdLst><p:sldId id="256" r:id="rId2"/><p:sldId id="257" r:id="rId3"/>'
            '<p:sldId id="258" r:id="rId4"/></p:sldIdLst>'
            '<p:sldSz cx="9144000" cy="5143500" type="screen16x9"/>'
            '<p:notesSz cx="6858000" cy="9144000"/></p:presentation>' % (A, R, P)),
        "ppt/_rels/presentation.xml.rels": (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="%s">'
            '<Relationship Id="rId1" Type="%s/slideMaster" Target="slideMasters/slideMaster1.xml"/>'
            '<Relationship Id="rId2" Type="%s/slide" Target="slides/slide1.xml"/>'
            '<Relationship Id="rId3" Type="%s/slide" Target="slides/slide2.xml"/>'
            '<Relationship Id="rId4" Type="%s/slide" Target="slides/slide3.xml"/>'
            "</Relationships>" % (PKG, R, R, R, R)),
        "ppt/slides/slide1.xml": slide1,
        "ppt/slides/slide2.xml": slide2,
        "ppt/slides/slide3.xml": slide3,
        "ppt/slides/_rels/slide1.xml.rels": _slide_rels(),
        "ppt/slides/_rels/slide2.xml.rels": _slide_rels(
            '<Relationship Id="rId2" Type="%s/image" Target="../media/image1.png"/>' % R),
        "ppt/slides/_rels/slide3.xml.rels": _slide_rels(),
        "ppt/slideLayouts/slideLayout1.xml": PPTX_LAYOUT,
        "ppt/slideLayouts/_rels/slideLayout1.xml.rels": (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="%s">'
            '<Relationship Id="rId1" Type="%s/slideMaster" Target="../slideMasters/slideMaster1.xml"/>'
            "</Relationships>" % (PKG, R)),
        "ppt/slideMasters/slideMaster1.xml": PPTX_MASTER,
        "ppt/slideMasters/_rels/slideMaster1.xml.rels": (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="%s">'
            '<Relationship Id="rId1" Type="%s/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>'
            '<Relationship Id="rId2" Type="%s/theme" Target="../theme/theme1.xml"/>'
            "</Relationships>" % (PKG, R, R)),
        "ppt/theme/theme1.xml": PPTX_THEME,
        "ppt/media/image1.png": png_bytes(),
    })


# ------------------------------------------------------------------------ API
def corpus() -> dict[str, bytes]:
    return {
        "fidelity-report.docx": docx(),
        "fidelity-workbook.xlsx": xlsx(),
        "fidelity-deck.pptx": pptx(),
    }


def write_corpus(directory: Path) -> dict[str, str]:
    directory.mkdir(parents=True, exist_ok=True)
    hashes = {}
    for name, data in corpus().items():
        (directory / name).write_bytes(data)
        hashes[name] = hashlib.sha256(data).hexdigest()
    (directory / "SHA256SUMS.json").write_text(json.dumps(hashes, indent=2) + "\n")
    return hashes


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    for name, digest in write_corpus(Path(sys.argv[1])).items():
        print("%s %s" % (name, digest))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
