"""Check retained GR-048 evidence (does not replace browser execution/visual QA)."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent
record = json.loads((root / 'runtime/browser-evidence.json').read_text())
pre, post, run = record['preAck'], record['postAck'], record['runtime']
assert pre['dirty'] is True and pre['size'] == 3464
assert post['dirty'] is False and post['ackTicket'] == pre['ticket'] == 'figcraft:1'
assert run['verification']['result'] == 'bounded synthetic transport PASS'
assert run['state']['reopened'] is True and run['state']['dirty'] is False
assert run['state']['dirtyBeforeAck'] is True
assert run['state']['saveSha256'] == pre['sha256']
assert any(e['generation'] == 2 and e['type'] == 'figcraft:ready' for e in run['state']['events'])
for response in record['responseHashes']:
    assert response['status'] == 200
    if response['path'] in ['/host.html', '/synthetic.figcraft']:
        data = (root / 'runtime' / response['path'][1:]).read_bytes()
        assert len(data) == response['size']
        assert hashlib.sha256(data).hexdigest() == response['sha256']
patch = root.parent / 'GR-019/figcraft-shared-host-save.patch'
assert hashlib.sha256(patch.read_bytes()).hexdigest() == '954850ba5aff7362e776b2331a5a5ff54bf9d71374d7b29bc856c2b7a47c4798'
print('PASS: retained positive-flow evidence, host/fixture response hashes, accepted patch hash')
