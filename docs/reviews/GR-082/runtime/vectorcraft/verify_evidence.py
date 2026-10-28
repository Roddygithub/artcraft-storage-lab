#!/usr/bin/env python3
"""Verify retained smoke evidence, input hashes, and the external release bundle."""
import base64, hashlib, json, re
from run_qualification import ROOT, CHECKS, BUNDLE
EVIDENCE = ROOT/'docs/reviews/GR-082/runtime/vectorcraft'
if __name__ == '__main__':
    manifest = json.loads((CHECKS/'vectorcraft-bundle-manifest.json').read_text())
    evidence = json.loads((EVIDENCE/'browser-evidence.json').read_text())
    expected = {p:e['sha256'] for p,e in manifest['files'].items()}
    actual = {str(p.relative_to(BUNDLE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in BUNDLE.rglob('*') if p.is_file() and p.name != '.trunk-lock'}
    assert expected == actual == evidence['assets_before'] == evidence['assets_after']
    for p, sha in json.loads((CHECKS/'vectorcraft-test-inputs.json').read_text()).items():
        assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest() == sha, p
    for asset in evidence['served_assets']:
        assert expected[asset['path']] == asset['sha256']
        assert manifest['files'][asset['path']]['size'] == asset['size']
    assert sum(a['path'].endswith('.wasm') for a in evidence['served_assets']) == 2
    assert evidence['save_count'] == 1 and evidence['downloads'] == []
    assert evidence['host_state'] == 'Saved — new version synthetic-v1'
    assert hashlib.sha256((EVIDENCE/'saved.svg').read_bytes()).hexdigest() == evidence['saved_sha256']
    for tag in re.findall(r'<(?:link|script)\b[^>]*>', (BUNDLE/'index.html').read_text()):
        target = re.search(r'(?:href|src)="([^"]+)"', tag)
        sri = re.search(r'integrity="([^"]+)"', tag)
        if target and sri:
            assert sri.group(1) == 'sha384-'+base64.b64encode(hashlib.sha384((BUNDLE/target.group(1).removeprefix('./')).read_bytes()).digest()).decode()
    print('PASS: all 9 release assets, test inputs, served before/after hashes, two WASM transfers, SVG hash, one save, no downloads and index SRI agree')
    print('PROVISIONAL: synthetic memory host only; no Seafile, identity binding or native host-ACK qualification')
