"""Synthetic PPTX bytes and a bounded semantic text reader (stdlib only).

Adapted from docs/reviews/GR-044/runtime/make_fixture.py. No editor patches.
Intended for official DeckCraft 0.16.0 same-format Save tests; schema validation,
rendering and app runtime compatibility are NOT VERIFIED here.
Title box: x=914400, y=1885950, w=7315200, h=1371600 EMU on a
9144000 x 5143500 EMU slide; horizontally and vertically centered, 28pt.
"""
from io import BytesIO
import posixpath
import xml.etree.ElementTree as ET
from zipfile import BadZipFile, ZIP_DEFLATED, ZipFile, ZipInfo

TITLE = "ArtCraft synthetic PPTX"
MIME = "application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"
P = "http://schemas.openxmlformats.org/presentationml/2006/main"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG = "http://schemas.openxmlformats.org/package/2006/relationships"
CT = "http://schemas.openxmlformats.org/package/2006/content-types"
NS = {"p": P, "a": A}
MAX_XML_BYTES = 2 * 1024 * 1024
MAX_TOTAL_BYTES = 16 * 1024 * 1024

PARTS = {
    "[Content_Types].xml": '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
  <Override PartName="/ppt/slides/slide1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>
  <Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>
  <Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>
  <Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>
</Types>''',
    "_rels/.rels": '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
</Relationships>''',
    "ppt/presentation.xml": '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst>
  <p:sldIdLst><p:sldId id="256" r:id="rId2"/></p:sldIdLst>
  <p:sldSz cx="9144000" cy="5143500" type="screen16x9"/><p:notesSz cx="6858000" cy="9144000"/>
</p:presentation>''',
    "ppt/_rels/presentation.xml.rels": '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide1.xml"/>
</Relationships>''',
    "ppt/slides/slide1.xml": '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld><p:spTree>
    <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
    <p:sp><p:nvSpPr><p:cNvPr id="2" name="Synthetic editable title"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="914400" y="1885950"/><a:ext cx="7315200" cy="1371600"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:solidFill><a:srgbClr val="F2F6FF"/></a:solidFill><a:ln><a:solidFill><a:srgbClr val="38598A"/></a:solidFill></a:ln></p:spPr><p:txBody><a:bodyPr anchor="ctr"/><a:lstStyle/><a:p><a:pPr algn="ctr"/><a:r><a:rPr lang="en-US" sz="2800" b="1"><a:solidFill><a:srgbClr val="183153"/></a:solidFill></a:rPr><a:t>ArtCraft synthetic PPTX</a:t></a:r><a:endParaRPr lang="en-US"/></a:p></p:txBody></p:sp>
  </p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sld>''',
    "ppt/slides/_rels/slide1.xml.rels": '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
</Relationships>''',
    "ppt/slideLayouts/slideLayout1.xml": '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" type="blank" preserve="1">
  <p:cSld name="Blank"><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr></p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sldLayout>''',
    "ppt/slideLayouts/_rels/slideLayout1.xml.rels": '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/>
</Relationships>''',
    "ppt/slideMasters/slideMaster1.xml": '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld name="Master"><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr></p:spTree></p:cSld>
  <p:clrMap accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" bg1="lt1" bg2="lt2" folHlink="folHlink" hlink="hlink" tx1="dk1" tx2="dk2"/><p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst><p:txStyles><p:titleStyle/><p:bodyStyle/><p:otherStyle/></p:txStyles>
</p:sldMaster>''',
    "ppt/slideMasters/_rels/slideMaster1.xml.rels": '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/>
</Relationships>''',
    "ppt/theme/theme1.xml": '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="Synthetic"><a:themeElements><a:clrScheme name="Synthetic"><a:dk1><a:srgbClr val="000000"/></a:dk1><a:lt1><a:srgbClr val="FFFFFF"/></a:lt1><a:dk2><a:srgbClr val="183153"/></a:dk2><a:lt2><a:srgbClr val="F2F6FF"/></a:lt2><a:accent1><a:srgbClr val="4F81BD"/></a:accent1><a:accent2><a:srgbClr val="C0504D"/></a:accent2><a:accent3><a:srgbClr val="9BBB59"/></a:accent3><a:accent4><a:srgbClr val="8064A2"/></a:accent4><a:accent5><a:srgbClr val="4BACC6"/></a:accent5><a:accent6><a:srgbClr val="F79646"/></a:accent6><a:hlink><a:srgbClr val="0000FF"/></a:hlink><a:folHlink><a:srgbClr val="800080"/></a:folHlink></a:clrScheme><a:fontScheme name="Synthetic"><a:majorFont><a:latin typeface="Arial"/><a:ea typeface=""/><a:cs typeface=""/></a:majorFont><a:minorFont><a:latin typeface="Arial"/><a:ea typeface=""/><a:cs typeface=""/></a:minorFont></a:fontScheme><a:fmtScheme name="Synthetic"><a:fillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:fillStyleLst><a:lnStyleLst><a:ln w="9525"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln><a:ln w="9525"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln><a:ln w="9525"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln></a:lnStyleLst><a:effectStyleLst><a:effectStyle><a:effectLst/></a:effectStyle><a:effectStyle><a:effectLst/></a:effectStyle><a:effectStyle><a:effectLst/></a:effectStyle></a:effectStyleLst><a:bgFillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:bgFillStyleLst></a:fmtScheme></a:themeElements></a:theme>''',
}



def synthetic_pptx() -> bytes:
    """Return deterministic one-slide synthetic presentation bytes."""
    output = BytesIO()
    with ZipFile(output, "w", ZIP_DEFLATED) as archive:
        for name, content in PARTS.items():
            info = ZipInfo(name, date_time=(2020, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, content.encode("utf-8"))
    return output.getvalue()


def slide_texts(data: bytes) -> list[list[str]]:
    """Read paragraphs in actual slide shapes, in presentation order.

    Return one list of paragraph strings per referenced slide. Runs are joined,
    preserving split markers. Notes, metadata and unreferenced slides never count.
    Reject unsafe/broken packages with ValueError. This is not an XSD validator.
    Bounds deliberately suit small lab documents, not arbitrary presentations.
    """
    try:
        with ZipFile(BytesIO(data)) as archive:
            infos = archive.infolist()
            names = {item.filename for item in infos}
            if len(infos) > 512 or len(names) != len(infos):
                raise ValueError("too many or duplicate ZIP members")
            if sum(item.file_size for item in infos) > MAX_TOTAL_BYTES:
                raise ValueError("package too large")
            for name in names:
                if (name.startswith("/") or "\\" in name or
                        posixpath.normpath(name) != name or name.startswith("../")):
                    raise ValueError("unsafe part name")
            roots = {}
            for item in infos:
                if item.filename.endswith((".xml", ".rels")):
                    if item.file_size > MAX_XML_BYTES:
                        raise ValueError("XML part too large")
                    raw = archive.read(item)
                    # Reject DTDs/entities, including UTF-16/32 encoded declarations.
                    flat = raw.replace(b"\x00", b"").upper()
                    if b"<!DOCTYPE" in flat or b"<!ENTITY" in flat:
                        raise ValueError("DTD/entity forbidden")
                    roots[item.filename] = ET.fromstring(raw)

            def root(name, tag):
                value = roots.get(name)
                if value is None or value.tag != tag:
                    raise ValueError(f"missing or invalid part: {name}")
                return value

            relationships = {}
            for name in roots:
                if not name.endswith(".rels"):
                    continue
                if name == "_rels/.rels":
                    source = ""
                else:
                    directory, filename = posixpath.split(name)
                    if posixpath.basename(directory) != "_rels":
                        raise ValueError("invalid relationship part")
                    source = posixpath.join(posixpath.dirname(directory), filename[:-5])
                    if source not in names:
                        raise ValueError("missing relationship source")
                rels = {}
                for rel in root(name, f"{{{PKG}}}Relationships"):
                    target = rel.get("Target", "")
                    rid = rel.get("Id")
                    if (rel.tag != f"{{{PKG}}}Relationship" or not rid or rid in rels
                            or rel.get("TargetMode", "Internal") != "Internal"
                            or not target or any(c in target for c in "\\:%?#")
                            or target.startswith("//")):
                        raise ValueError("unsafe relationship")
                    resolved = posixpath.normpath(posixpath.join(
                        posixpath.dirname(source), target)) if not target.startswith("/") else target[1:]
                    if resolved.startswith("../") or resolved not in names:
                        raise ValueError("missing or escaping relationship target")
                    rels[rid] = (rel.get("Type"), resolved)
                relationships[source] = rels

            office = [target for kind, target in relationships.get("", {}).values()
                      if kind == R + "/officeDocument"]
            if len(office) != 1:
                raise ValueError("expected one presentation")
            presentation = office[0]
            types = root("[Content_Types].xml", f"{{{CT}}}Types")
            matches = [e.get("ContentType") for e in types
                       if e.tag == f"{{{CT}}}Override" and e.get("PartName") == "/" + presentation]
            if matches != [MIME]:
                raise ValueError("wrong presentation MIME")
            document = root(presentation, f"{{{P}}}presentation")
            result = []
            for slide_id in document.findall("p:sldIdLst/p:sldId", NS):
                relation = relationships.get(presentation, {}).get(slide_id.get(f"{{{R}}}id"))
                if relation is None or relation[0] != R + "/slide":
                    raise ValueError("missing slide relationship")
                slide = root(relation[1], f"{{{P}}}sld")
                tree = slide.find("p:cSld/p:spTree", NS)
                if tree is None:
                    raise ValueError("missing slide shape tree")
                paragraphs = []
                for shape in tree.iter(f"{{{P}}}sp"):
                    for paragraph in shape.findall("p:txBody/a:p", NS):
                        paragraphs.append("".join(
                            node.text or "" for run in paragraph
                            if run.tag in (f"{{{A}}}r", f"{{{A}}}fld")
                            for node in run.findall("a:t", NS)))
                result.append(paragraphs)
            return result
    except (BadZipFile, ET.ParseError, KeyError, RuntimeError, NotImplementedError,
            OSError, EOFError) as exc:
        raise ValueError("invalid PPTX package") from exc
