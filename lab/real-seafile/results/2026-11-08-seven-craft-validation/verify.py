"""Check retained evidence integrity; not an independent browser replay."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
sums = {}
for line in (HERE / 'SHA256SUMS').read_text().splitlines():
    digest, name = line.split('  ')
    assert Path(name).name == name and name not in sums
    sums[name] = digest
    assert hashlib.sha256((HERE / name).read_bytes()).hexdigest() == digest, name
assert set(sums) == {p.name for p in HERE.iterdir() if p.is_file()} - {'SHA256SUMS'}
for filename, total in [('slice.json', 40), ('browser.json', 132)]:
    d = json.loads((HERE / filename).read_text())
    assert d['passed'] == total and d['failed'] == 0
    assert len(d['checks']) == len({c['name'] for c in d['checks']}) == total
    assert all(c['ok'] is True for c in d['checks'])
d = json.loads((HERE / 'offline.json').read_text())
assert d['passed'] == len(d['checks']) == 19 and d['failed'] == 0
assert all(c['exit'] == 0 for c in d['checks'])
for relay, saved in [('wordcraft-first-relay.docx', 'wordcraft-first-readback.docx'),
                     ('pdfcraft-relay-save.pdf', 'pdfcraft-saved.pdf'),
                     ('vectorcraft-relay-save.svg', 'vectorcraft-saved.svg'),
                     ('figcraft-relay-save.figcraft', 'figcraft-saved.figcraft'),
                     ('pptx-first-relay.pptx', 'pptx-readback.pptx')]:
    assert (HERE / relay).read_bytes() == (HERE / saved).read_bytes(), relay
assert json.loads((HERE / 'cleanup.json').read_text())['project_containers_absent'] is True
import sys, re
sys.path.insert(0, str(HERE.parents[1]))
from pptx_roundtrip_fixture import slide_texts, TITLE
text = '\n'.join(p for slide in slide_texts((HERE / 'pptx-readback.pptx').read_bytes()) for p in slide)
assert TITLE in text and re.search(r'pptxtyped[0-9a-f]{10}', text)
print('PASS: integrity, HTTP 40/40, browser 132/132, offline 19/19, five relay/readback pairs')
