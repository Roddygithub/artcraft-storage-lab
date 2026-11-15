import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent
expected = {'browser.json': 24, 'gridcraft-browser.json': 27, 'deckcraft-browser.json': 15}
for name, count in expected.items():
    data = json.loads((root / name).read_text())
    assert data['passed'] == count and data['failed'] == 0
    assert len(data['checks']) == count and all(check['ok'] for check in data['checks'])
for line in (root / 'SHA256SUMS').read_text().splitlines():
    digest, name = line.split('  ', 1)
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == digest, name
print('PASS: 66/66 browser assertions and retained SHA-256 files')
