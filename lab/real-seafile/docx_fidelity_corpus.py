#!/usr/bin/env python3
"""Generate a tiny, deterministic DOCX corpus for the WordCraft/ONLYOFFICE lab comparison.

Only the Python standard library is used. The documents contain synthetic text and exercise
paragraph/run formatting, lists, tables, headers/footers, and a page break.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import zipfile
from pathlib import Path

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG = "http://schemas.openxmlformats.org/package/2006/relationships"
CT = "http://schemas.openxmlformats.org/package/2006/content-types"


def _r(text: str, *, bold: bool = False, italic: bool = False, color: str | None = None) -> str:
    props = []
    if bold:
        props.append("<w:b/>")
    if italic:
        props.append("<w:i/>")
    if color:
        props.append(f'<w:color w:val="{color}"/>')
    rpr = f"<w:rPr>{''.join(props)}</w:rPr>" if props else ""
    return f"<w:r>{rpr}<w:t xml:space=\"preserve\">{html.escape(text)}</w:t></w:r>"


def _p(*runs: str, style: str | None = None, num_id: int | None = None,
       page_break: bool = False) -> str:
    props = []
    if style:
        props.append(f'<w:pStyle w:val="{style}"/>')
    if num_id:
        props.append(f"<w:numPr><w:ilvl w:val=\"0\"/><w:numId w:val=\"{num_id}\"/></w:numPr>")
    ppr = f"<w:pPr>{''.join(props)}</w:pPr>" if props else ""
    content = '<w:r><w:br w:type="page"/></w:r>' if page_break else "".join(runs)
    return f"<w:p>{ppr}{content}</w:p>"


def _cell(text: str, *, header: bool = False) -> str:
    shade = '<w:shd w:fill="D9EAF7"/>' if header else ""
    val = _r(text, bold=header)
    return f"<w:tc><w:tcPr>{shade}<w:tcW w:w=\"2400\" w:type=\"dxa\"/></w:tcPr>{_p(val)}</w:tc>"


def _table(rows: list[list[str]]) -> str:
    border = '<w:tblBorders><w:top w:val="single" w:sz="6"/><w:left w:val="single" w:sz="6"/><w:bottom w:val="single" w:sz="6"/><w:right w:val="single" w:sz="6"/><w:insideH w:val="single" w:sz="4"/><w:insideV w:val="single" w:sz="4"/></w:tblBorders>'
    trs = []
    for i, row in enumerate(rows):
        trs.append("<w:tr>" + "".join(_cell(text, header=(i == 0)) for text in row) + "</w:tr>")
    return f"<w:tbl><w:tblPr>{border}<w:tblW w:w=\"4800\" w:type=\"dxa\"/></w:tblPr><w:tblGrid><w:gridCol w:w=\"2400\"/><w:gridCol w:w=\"2400\"/></w:tblGrid>{''.join(trs)}</w:tbl>"


def _package(body: str) -> bytes:
    document = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="{W}" xmlns:r="{R}"><w:body>{body}
<w:sectPr><w:headerReference w:type="default" r:id="rId3"/><w:footerReference w:type="default" r:id="rId4"/>
<w:pgSz w:w="12240" w:h="15840"/><w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="720" w:footer="720" w:gutter="0"/></w:sectPr></w:body></w:document>'''
    content_types = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="{CT}"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/><Override PartName="/word/numbering.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/><Override PartName="/word/header1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.header+xml"/><Override PartName="/word/footer1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/></Types>'''
    rels = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="{PKG}"><Relationship Id="rId1" Type="{R}/officeDocument" Target="word/document.xml"/></Relationships>'''
    doc_rels = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="{PKG}"><Relationship Id="rId1" Type="{R}/styles" Target="styles.xml"/><Relationship Id="rId2" Type="{R}/numbering" Target="numbering.xml"/><Relationship Id="rId3" Type="{R}/header" Target="header1.xml"/><Relationship Id="rId4" Type="{R}/footer" Target="footer1.xml"/></Relationships>'''
    styles = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="{W}"><w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:sz w:val="22"/></w:rPr></w:rPrDefault><w:pPrDefault><w:pPr><w:spacing w:after="160"/></w:pPr></w:pPrDefault></w:docDefaults>
<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/></w:style>
<w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:basedOn w:val="Normal"/><w:rPr><w:b/><w:color w:val="1F4E79"/><w:sz w:val="36"/></w:rPr><w:pPr><w:keepNext/></w:pPr></w:style>
<w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:rPr><w:b/><w:color w:val="2F5597"/><w:sz w:val="28"/></w:rPr><w:pPr><w:keepNext/><w:spacing w:before="240" w:after="120"/></w:pPr></w:style>
<w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/><w:basedOn w:val="Normal"/><w:rPr><w:b/><w:sz w:val="24"/></w:rPr><w:pPr><w:keepNext/></w:pPr></w:style></w:styles>'''
    numbering = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:numbering xmlns:w="{W}"><w:abstractNum w:abstractNumId="0"><w:multiLevelType w:val="singleLevel"/><w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="bullet"/><w:lvlText w:val="•"/><w:lvlJc w:val="left"/><w:pPr><w:ind w:left="720" w:hanging="360"/></w:pPr></w:lvl></w:abstractNum>
<w:abstractNum w:abstractNumId="1"><w:multiLevelType w:val="singleLevel"/><w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="decimal"/><w:lvlText w:val="%1."/><w:lvlJc w:val="left"/><w:pPr><w:ind w:left="720" w:hanging="360"/></w:pPr></w:lvl></w:abstractNum>
<w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num><w:num w:numId="2"><w:abstractNumId w:val="1"/></w:num></w:numbering>'''
    header = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:hdr xmlns:w="{W}">{_p(_r("ARTCRAFT SYNTHETIC FIDELITY CORPUS", color="666666"))}</w:hdr>'''
    footer = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:ftr xmlns:w="{W}"><w:p><w:r><w:t>Page </w:t></w:r><w:fldSimple w:instr="PAGE"><w:r><w:t>1</w:t></w:r></w:fldSimple></w:p></w:ftr>'''
    props = {
        "[Content_Types].xml": content_types,
        "_rels/.rels": rels,
        "word/document.xml": document,
        "word/_rels/document.xml.rels": doc_rels,
        "word/styles.xml": styles,
        "word/numbering.xml": numbering,
        "word/header1.xml": header,
        "word/footer1.xml": footer,
    }
    import io
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for name, value in props.items():
            info = zipfile.ZipInfo(name, date_time=(2020, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, value)
    return out.getvalue()


def corpus() -> dict[str, bytes]:
    prose = "".join([
        _p(_r("Fidelity Case 1 — Prose and runs"), style="Title"),
        _p(_r("This synthetic paragraph checks a normal text run, ") + _r("bold text", bold=True) + _r(", ") + _r("italic text", italic=True) + _r(", and an accent-colored phrase.") + _r(" Accent", color="C00000")),
        _p(_r("Second paragraph: the quick brown fox jumps over the lazy dog.")),
    ])
    structure = "".join([
        _p(_r("Fidelity Case 2 — Lists and table"), style="Title"),
        _p(_r("Section heading"), style="Heading1"),
        _p(_r("A paragraph before a short list.")),
        _p(_r("First bullet"), num_id=1), _p(_r("Second bullet"), num_id=1),
        _p(_r("First numbered item"), num_id=2), _p(_r("Second numbered item"), num_id=2),
        _p(_r("Two-column table"), style="Heading2"),
        _table([["Item", "Value"], ["Alpha", "One"], ["Beta", "Two"]]),
    ])
    layout = "".join([
        _p(_r("Fidelity Case 3 — Page layout"), style="Title"),
        _p(_r("First page text: this file has a repeated header and a page-number footer.")),
        _p(page_break=True),
        _p(_r("Second page heading"), style="Heading1"),
        _p(_r("Second page paragraph. The fixed title and page break make the page boundary observable.")),
        _table([["Column A", "Column B"], ["Page two", "Visible"]]),
    ])
    return {
        "fidelity-prose.docx": _package(prose),
        "fidelity-structure.docx": _package(structure),
        "fidelity-layout.docx": _package(layout),
    }


def write_corpus(directory: Path) -> dict[str, str]:
    directory.mkdir(parents=True, exist_ok=True)
    hashes = {}
    for name, data in corpus().items():
        target = directory / name
        target.write_bytes(data)
        hashes[name] = hashlib.sha256(data).hexdigest()
    (directory / "SHA256SUMS.json").write_text(json.dumps(hashes, indent=2) + "\n")
    return hashes


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    for name, digest in write_corpus(args.output).items():
        print(f"{name} {digest}")


if __name__ == "__main__":
    main()
