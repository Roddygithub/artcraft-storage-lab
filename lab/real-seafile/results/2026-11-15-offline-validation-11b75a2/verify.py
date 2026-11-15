import json
from pathlib import Path

root = Path(__file__).resolve().parent
summary = json.loads((root / 'summary.json').read_text())
assert summary['source'] == '11b75a23be5e263f9bb7b4b9cb332caa2158bd6d'
assert summary['passed'] == 20 and summary['failed'] == 0
assert all(check['exit'] == 0 for check in summary['checks'])
print('PASS: offline validation 20/20 at 11b75a2')
