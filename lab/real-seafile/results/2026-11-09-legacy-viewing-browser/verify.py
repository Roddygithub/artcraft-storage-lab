"""Integrity checks for the retained legacy/OpenDocument browser routing evidence.

Route and safety evidence only: it re-asserts the sanitized slice and browser
summaries, not any editor import, rendering or format replacement.
"""
import hashlib
import json
from pathlib import Path
import re

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

b = json.loads((HERE / 'browser.json').read_text())
assert b['passed'] == 140 and b['failed'] == 0
assert len(b['checks']) == len({c['name'] for c in b['checks']}) == 140
assert all(c['ok'] is True for c in b['checks'])
viewing = [c['name'] for c in b['checks'] if c['name'].startswith('viewing_')]
assert len(viewing) == 21, len(viewing)
assert 'viewing_probe_authenticated_session' in viewing
for fixture, editor in (('doc_doc', 'wordcraft'), ('doc_odt', 'wordcraft'),
                        ('sheet_xls', 'gridcraft'), ('sheet_ods', 'gridcraft'),
                        ('sheet_csv', 'gridcraft')):
    for suffix in ('opened_from_seafile_file_list', 'routes_to_', 'open_did_not_download',
                   'open_wrote_no_version'):
        expected = f'viewing_{fixture}_{suffix}'
        if suffix == 'routes_to_':
            expected = f'viewing_{fixture}_routes_to_{editor}'
        assert expected in viewing, expected

blob = (HERE / 'slice.json').read_text() + (HERE / 'browser.json').read_text()
# `reader@lab.test` is the static read-only fixture account defined verbatim in
# lab/real-seafile/run_slice.py, and `wopi/files/<id>` keeps only the redacted
# placeholder. The random per-run synthetic accounts, tokens, WOPISrc values and
# repo id must not be retained.
for secret in ('synthetic-', '@auth.local', 'access_token', 'WOPISrc=http', 'repo_id'):
    assert secret not in blob, secret
assert not re.search(r'wopi/files/[0-9a-f]{8,}', blob), 'an unredacted WOPI file id is retained'
emails = set(re.findall(r'[\w.+-]+@[\w.-]+', blob))
assert emails <= {'reader@lab.test'}, emails
print('PASS: integrity, HTTP 57/57, browser 140/140 (21 viewing checks), '
      '5 routed legacy formats, 7 unrouted, no secrets retained')
