"""Bounded semantic structure checks for the retained synthetic DOCX corpus."""
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('layout_features', HERE.parent / '2026-11-08-wordcraft-structure-recovery/verify.py')
layout = importlib.util.module_from_spec(spec)
spec.loader.exec_module(layout)
W = layout.W

def formatting(data):
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        doc = ET.fromstring(z.read('word/document.xml'))
        numbering = ET.fromstring(z.read('word/numbering.xml'))
        abstract = {e.get(W + 'abstractNumId'): e for e in numbering.findall(W + 'abstractNum')}
        nums = {e.get(W + 'numId'): abstract[e.find(W + 'abstractNumId').get(W + 'val')]
                for e in numbering.findall(W + 'num')}
        lists = []
        for p in doc.iter(W + 'p'):
            props = p.find(W + 'pPr/' + W + 'numPr')
            if props is None:
                continue
            num = props.find(W + 'numId').get(W + 'val')
            level = props.find(W + 'ilvl')
            level = level.get(W + 'val') if level is not None else '0'
            lvl = next(e for e in nums[num].findall(W + 'lvl') if e.get(W + 'ilvl') == level)
            lists.append((''.join(e.text or '' for e in p.iter(W + 't')),
                          lvl.find(W + 'numFmt').get(W + 'val'), lvl.find(W + 'lvlText').get(W + 'val')))
        runs = []
        for run in doc.iter(W + 'r'):
            props = run.find(W + 'rPr')
            if props is not None and len(props):
                runs.append((''.join(e.text or '' for e in run.iter(W + 't')),
                             [(e.tag, sorted(e.attrib.items())) for e in props]))
        return {'lists': lists, 'direct_formatted_runs': runs}

def main():
    sums = {}
    for line in (HERE / 'SHA256SUMS').read_text().splitlines():
        digest, name = line.split('  ')
        assert name not in sums and not Path(name).is_absolute() and '..' not in Path(name).parts
        sums[name] = digest
        assert hashlib.sha256((HERE / name).read_bytes()).hexdigest() == digest, name
    assert set(sums) == {p.relative_to(HERE).as_posix() for p in HERE.rglob('*') if p.is_file()} - {'SHA256SUMS'}
    for case in ('prose', 'structure'):
        root = HERE / case
        original = (root / 'wordcraft-original.docx').read_bytes()
        for name in ('wordcraft-first-readback.docx', 'wordcraft-second-readback.docx'):
            data = (root / name).read_bytes()
            assert layout.features(data) == layout.features(original), (case, name, 'structure')
            assert formatting(data) == formatting(original), (case, name, 'formatting')
        assert (root / 'wordcraft-first-relay.docx').read_bytes() == (root / 'wordcraft-first-readback.docx').read_bytes()
        result = json.loads((root / 'browser.json').read_text())
        assert len({c['name'] for c in result['checks']}) == len(result['checks']) == 28
        assert all(c['ok'] is True for c in result['checks'])
    print('PASS: hashes, two 28-check runs, relay equality, fixture structure, direct formatting and list semantics')

if __name__ == '__main__':
    main()
