"""Verify the retained synthetic DOCX structure; not full rendering fidelity."""
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import xml.etree.ElementTree as ET
import zipfile

HERE = Path(__file__).resolve().parent
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
R = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'

def features(data):
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        def xml(name):
            info = z.getinfo(name)
            assert info.file_size <= 8 * 1024 * 1024, 'oversized XML'
            return ET.fromstring(z.read(name))
        doc = xml('word/document.xml')
        rels = {e.get('Id'): e for e in xml('word/_rels/document.xml.rels')}
        result = {}
        for kind in ('header', 'footer'):
            texts, fields = [], []
            for ref in doc.iter(W + kind + 'Reference'):
                rel = rels[ref.get(R + 'id')]
                assert rel.get('Type', '').endswith('/' + kind)
                assert rel.get('TargetMode') != 'External'
                target = PurePosixPath('word') / rel.get('Target', '')
                assert not target.is_absolute() and '..' not in target.parts
                part = xml(str(target))
                texts.append(''.join(e.text or '' for e in part.iter(W + 't')))
                fields.extend((e.get(W + 'instr') or e.text or '').strip()
                              for e in part.iter() if e.tag in (W + 'fldSimple', W + 'instrText'))
            result[kind + '_text'] = texts
            result[kind + '_fields'] = fields
        result.update(
            tables=[[''.join(e.text or '' for e in cell.iter(W + 't'))
                     for cell in table.iter(W + 'tc')] for table in doc.iter(W + 'tbl')],
            page_breaks=sum(e.get(W + 'type') == 'page' for e in doc.iter(W + 'br')),
            page_geometry=[dict(e.attrib) for e in doc.iter() if e.tag in (W + 'pgSz', W + 'pgMar')],
            paragraph_styles=[e.get(W + 'val') for e in doc.iter(W + 'pStyle')])
        return result

def main():
    sums = {}
    for line in (HERE / 'SHA256SUMS').read_text().splitlines():
        digest, name = line.split('  ')
        assert name not in sums and Path(name).name == name
        sums[name] = digest
        assert hashlib.sha256((HERE / name).read_bytes()).hexdigest() == digest, name
    assert set(sums) == {p.name for p in HERE.iterdir() if p.is_file()} - {'SHA256SUMS'}
    original = features((HERE / 'wordcraft-original.docx').read_bytes())
    for name in ('wordcraft-first-readback.docx', 'wordcraft-second-readback.docx'):
        assert features((HERE / name).read_bytes()) == original, name
    assert (HERE / 'wordcraft-first-readback.docx').read_bytes() == (HERE / 'wordcraft-first-relay.docx').read_bytes()
    result = json.loads((HERE / 'browser.json').read_text())
    assert len(result['checks']) == len({c['name'] for c in result['checks']}) == 28
    assert all(c['ok'] is True for c in result['checks'])
    print('PASS: hashes, 28 browser assertions, relay equality and bounded DOCX structural preservation')

if __name__ == '__main__':
    main()
