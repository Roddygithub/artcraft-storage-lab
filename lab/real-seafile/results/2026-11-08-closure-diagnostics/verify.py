#!/usr/bin/env python3
"""Offline inventory verification; optional private byte/source recheck."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
EXPECTED = {
    'wordcraft-final-20261108-run1': 28,
    'gridcraft-20261108-run1': 27,
    'pdfcraft-20261108-run1': 18,
    'cadcraft-20261108-run1': 20,
    'vector-20261108-run4': 20,
    'fig-20261108-run1': 21,
    'onlyoffice-final-20261108-run2': 11,
}
FILES = {'README.md', 'inventory.json', 'verify.py', 'SHA256SUMS'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def digest(value):
    require(isinstance(value, str) and re.fullmatch('[0-9a-f]{64}', value),
            'invalid SHA-256')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--private-root', type=Path,
                        help='parent directory containing the closure-* private runs')
    args = parser.parse_args()
    require({p.name for p in HERE.iterdir()} == FILES, 'included artifact inventory differs')
    require(all(p.is_file() and not p.is_symlink() for p in HERE.iterdir()),
            'unexpected artifact type')
    sums = {}
    for line in (HERE / 'SHA256SUMS').read_text().splitlines():
        value, name = line.split('  ')
        digest(value)
        require(name not in sums, 'duplicate checksum name')
        sums[name] = value
    require(set(sums) == FILES - {'SHA256SUMS'}, 'checksum inventory differs')
    for name, value in sums.items():
        require(sha((HERE / name).read_bytes()) == value, 'checksum differs: ' + name)
    data = json.loads((HERE / 'inventory.json').read_text())
    require(set(data) == {'comparison_commits', 'runs'}, 'unexpected inventory fields')
    require(data['comparison_commits'] == {
        '32ce907': '32ce907cc17695407fd02612ffd26bcbdcb41288',
        '4e7d637': '4e7d63762f8a6b6e8f879ae1a20d40631af22af3',
    }, 'comparison commits differ')
    require(set(data['runs']) == set(EXPECTED), 'run inventory differs')
    for run, expected in EXPECTED.items():
        item = data['runs'][run]
        require(set(item) == {'results', 'source_snapshot', 'static_manifest'}, 'unexpected run fields')
        names = {'onlyoffice-browser.json'} if run.startswith('onlyoffice') else {'slice.json', 'browser.json'}
        require(set(item['results']) == names, 'result inventory differs')
        root = args.private_root / ('closure-' + run) if args.private_root else None
        for name, result in item['results'].items():
            require(set(result) == {'raw_private_sha256', 'passed', 'failed', 'checks'}, 'unexpected result fields')
            digest(result['raw_private_sha256'])
            checks = result['checks']
            require(isinstance(checks, list), 'invalid checks')
            for check in checks:
                require(set(check) == {'name', 'ok'}, 'unexpected check fields')
                require(isinstance(check['name'], str) and re.fullmatch('[a-z0-9_]+', check['name']), 'invalid check name')
                require(type(check['ok']) is bool, 'invalid check boolean')
            require(len({c['name'] for c in checks}) == len(checks), 'duplicate check name')
            total = 46 if name == 'slice.json' else expected
            require(len(checks) == total, 'check count differs')
            require(type(result['passed']) is int and type(result['failed']) is int, 'invalid totals')
            require(result['passed'] == sum(c['ok'] for c in checks) == total and result['failed'] == 0, 'totals differ')
            if root:
                raw = (root / 'results' / name).read_bytes()
                require(sha(raw) == result['raw_private_sha256'], 'private checksum differs')
                original = json.loads(raw)
                require([{'name': c['name'], 'ok': c['ok']} for c in original['checks']] == checks, 'private checks differ')
                if 'passed' in original:
                    require((original['passed'], original['failed']) == (total, 0), 'private totals differ')
        source, static = item['source_snapshot'], item['static_manifest']
        require(len(source) == 29 and len(static) == 154 and not set(source) & set(static), 'snapshot counts differ')
        for path in source.keys() | static.keys():
            require(not Path(path).is_absolute() and '..' not in Path(path).parts, 'unsafe source path')
        for path, value in static.items():
            require(path.startswith('lab/real-seafile/static/'), 'invalid static path')
            digest(value)
        for path, record in source.items():
            require(set(record) == {'sha256', 'comparison'}, 'unexpected source fields')
            digest(record['sha256'])
            require(set(record['comparison']) == set(data['comparison_commits']), 'comparison inventory differs')
            for ref, comparison in record['comparison'].items():
                require(set(comparison) == {'sha256', 'equal'}, 'unexpected comparison fields')
                if comparison['sha256'] is not None:
                    digest(comparison['sha256'])
                require(type(comparison['equal']) is bool and comparison['equal'] == (record['sha256'] == comparison['sha256']), 'comparison differs')
                if root:
                    blob = subprocess.run(['git', 'show', data['comparison_commits'][ref] + ':' + path], cwd=HERE, capture_output=True)
                    require((sha(blob.stdout) if blob.returncode == 0 else None) == comparison['sha256'], 'Git source checksum differs')
        if root:
            app = root / 'app'
            actual = {p.relative_to(app).as_posix(): sha(p.read_bytes())
                      for p in app.rglob('*') if p.is_file()}
            recorded = {p: r['sha256'] for p, r in source.items()} | static
            require(actual == recorded, 'private snapshot inventory/checksums differ')
    print('Verified sanitized artifact inventory, checksums, counts, and unique check names'
          + ('; private bytes and Git comparisons rechecked.' if args.private_root else '.'))


if __name__ == '__main__':
    main()
