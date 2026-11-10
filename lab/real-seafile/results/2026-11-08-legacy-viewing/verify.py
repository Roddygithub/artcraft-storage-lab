"""Integrity checks for the retained legacy/OpenDocument viewing-route evidence.

Route evidence only: it re-asserts the sanitized slice summary, not any editor
import, rendering or format replacement.
"""
import hashlib
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent

sums = {}
for line in (HERE / 'SHA256SUMS').read_text().splitlines():
    digest, name = line.split('  ')
    assert Path(name).name == name and name not in sums
    sums[name] = digest
    assert hashlib.sha256((HERE / name).read_bytes()).hexdigest() == digest, name
assert set(sums) == {p.name for p in HERE.iterdir() if p.is_file()} - {'SHA256SUMS'}

d = json.loads((HERE / 'slice.json').read_text())
assert d['passed'] == 57 and d['failed'] == 0 and d['seafile_version'] == '13.0.28'
assert len(d['checks']) == len({c['name'] for c in d['checks']}) == 57
assert all(c['ok'] is True for c in d['checks'])

ROUTED = {'doc': 'wordcraft', 'odt': 'wordcraft', 'xls': 'gridcraft',
          'ods': 'gridcraft', 'csv': 'gridcraft'}
UNROUTED = ('fodt', 'fods', 'fodp', 'ppt', 'odp', 'pps', 'ppsx')
names = {c['name'] for c in d['checks']}
for ext, editor in ROUTED.items():
    assert f'seahub_{ext}_routes_to_wopi_{editor}' in names, ext
    assert f'bridge_open_{ext}_{editor}' in names, ext
for ext in UNROUTED:
    assert f'seahub_{ext}_has_no_wopi_route' in names, ext
blob = json.dumps(d)
# `reader@lab.test` is a static fixture name that also appears verbatim in
# lab/real-seafile/run_slice.py, and `wopi/files/<id>` keeps only the redacted
# placeholder. The random per-run synthetic admin account, tokens, WOPISrc
# values and repo id must not be retained.
for secret in ('synthetic-', 'access_token', 'WOPISrc=http', 'repo_id'):
    assert secret not in blob, secret
assert not re.search(r'wopi/files/[0-9a-f]{8,}', blob), 'an unredacted WOPI file id is retained'
assert '@auth.local' not in blob, 'a per-run auth account is retained'
print('PASS: integrity, HTTP 57/57, 5 routed legacy viewing formats, 7 unrouted, no secrets retained')
