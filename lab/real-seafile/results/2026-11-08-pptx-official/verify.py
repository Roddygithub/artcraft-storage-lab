"""Integrity and semantic checks for retained synthetic PPTX evidence."""
import hashlib
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
from pptx_roundtrip_fixture import TITLE, slide_texts

sums = {}
for line in (HERE / 'SHA256SUMS').read_text().splitlines():
    digest, name = line.split('  ')
    assert Path(name).name == name and name not in sums
    sums[name] = digest
    assert hashlib.sha256((HERE / name).read_bytes()).hexdigest() == digest, name
assert set(sums) == {p.name for p in HERE.iterdir() if p.is_file()} - {'SHA256SUMS'}
for name, count in [('slice.json', 40), ('browser.json', 15)]:
    d = json.loads((HERE / name).read_text())
    assert d['passed'] == count and d['failed'] == 0
    assert len(d['checks']) == len({c['name'] for c in d['checks']}) == count
    assert all(c['ok'] is True for c in d['checks'])
relay = (HERE / 'pptx-first-relay.pptx').read_bytes()
saved = (HERE / 'pptx-readback.pptx').read_bytes()
assert relay == saved and saved != (HERE / 'pptx-original.pptx').read_bytes()
text = '\n'.join(p for slide in slide_texts(saved) for p in slide)
assert TITLE in text and re.search(r'pptxtyped[0-9a-f]{10}', text)
d = json.loads((HERE / 'offline.json').read_text())
assert d['passed'] == len(d['checks']) == 19 and d['failed'] == 0
assert all(c['exit'] == 0 for c in d['checks'])
print('PASS: integrity, HTTP 40/40, browser 15/15, offline 19/19 and real PPTX title/marker readback')
