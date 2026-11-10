"""Integrity checks for the retained 2026-11-10 relay-bytes viewing evidence.

This re-asserts the sanitized summaries: the seven routed legacy formats reached
their documented editor through the bridge, the editor received the fixture bytes
unchanged, and those bytes still carry the fixture marker. It does not assert
rendered pixels or any legacy save.
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

s = json.loads((HERE / 'slice.json').read_text())
assert s['passed'] == 59 and s['failed'] == 0 and s['seafile_version'] == '13.0.28'
assert len(s['checks']) == len({c['name'] for c in s['checks']}) == 59
assert all(c['ok'] is True for c in s['checks'])

ROUTED = {'doc': 'wordcraft', 'odt': 'wordcraft', 'xls': 'gridcraft',
          'ods': 'gridcraft', 'fods': 'gridcraft', 'csv': 'gridcraft',
          'ppsx': 'deckcraft'}
UNROUTED = ('fodt', 'fodp', 'ppt', 'odp', 'pps')
names = {c['name'] for c in s['checks']}
for ext, editor in ROUTED.items():
    assert f'seahub_{ext}_routes_to_wopi_{editor}' in names, ext
    assert f'bridge_open_{ext}_{editor}' in names, ext
for ext in UNROUTED:
    assert f'seahub_{ext}_has_no_wopi_route' in names, ext

b = json.loads((HERE / 'browser.json').read_text())
assert b['passed'] == 67 and b['failed'] == 0
assert len(b['checks']) == len({c['name'] for c in b['checks']}) == 67
assert all(c['ok'] is True for c in b['checks'])
viewing = {c['name']: c for c in b['checks'] if c['name'].startswith('viewing_')}
assert len(viewing) == 43, len(viewing)
assert 'viewing_probe_authenticated_session' in viewing

FIXTURES = {'doc_doc': ('wordcraft', 9216), 'doc_odt': ('wordcraft', 9325),
            'sheet_xls': ('gridcraft', 5632), 'sheet_ods': ('gridcraft', 8763),
            'sheet_fods': ('gridcraft', 15767), 'sheet_csv': ('gridcraft', 42),
            'slide_ppsx': ('deckcraft', 23994)}
for fixture, (editor, size) in FIXTURES.items():
    for suffix in ('opened_from_seafile_file_list', 'open_did_not_download',
                   'open_wrote_no_version'):
        assert f'viewing_{fixture}_{suffix}' in viewing, suffix
    assert f'viewing_{fixture}_routes_to_{editor}' in viewing
    received = viewing[f'viewing_{fixture}_editor_received_the_fixture']['detail']
    assert f'captured=True bytes={size} expected={size}' == received, received
    assert f'viewing_{fixture}_editor_payload_contains_the_marker' in viewing

blob = (HERE / 'slice.json').read_text() + (HERE / 'browser.json').read_text()
for secret in ('synthetic-', '@auth.local', 'access_token', 'WOPISrc=http', 'repo_id'):
    assert secret not in blob, secret
assert not re.search(r'wopi/files/[0-9a-f]{8,}', blob), 'an unredacted WOPI file id is retained'
emails = set(re.findall(r'[\w.+-]+@[\w.-]+', blob))
assert emails <= {'reader@lab.test'}, emails
print('PASS: integrity, HTTP 59/59, browser 67/67 (43 viewing checks), '
      '7 routed formats delivered the fixture bytes with the marker, no secrets retained')
