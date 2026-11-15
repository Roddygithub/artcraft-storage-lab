import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent
summary = json.loads((root / 'summary.json').read_text())
assert summary['source'] == '11b75a23be5e263f9bb7b4b9cb332caa2158bd6d'
assert summary['passed'] == 20 and summary['failed'] == 0
assert len(summary['checks']) == 20 and all(check['exit'] == 0 for check in summary['checks'])
assert {check['log'] for check in summary['checks']} == {path.name for path in root.glob('*.log')}
entries = {}
for line in (root / 'SHA256SUMS').read_text().splitlines():
    digest, name = line.split('  ', 1)
    path = Path(name)
    assert not path.is_absolute() and '..' not in path.parts and name not in entries
    target = root / path
    assert target.is_file(), f'missing evidence file: {name}'
    assert hashlib.sha256(target.read_bytes()).hexdigest() == digest, f'hash mismatch: {name}'
    entries[name] = digest
actual = {path.relative_to(root).as_posix() for path in root.rglob('*')
          if path.is_file() and path.name != 'SHA256SUMS'}
assert set(entries) == actual, f'manifest coverage mismatch: {set(entries) ^ actual}'
print('PASS: offline validation 20/20, all logs present, manifest complete')
