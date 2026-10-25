#!/usr/bin/env python3
"""Verify GR-054 source pins; optionally recheck the read-only local observation.

A match is inventory integrity, never source provenance or candidate readiness.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]


def git(*args, cwd=ROOT):
    return subprocess.check_output(['git', *args], cwd=cwd)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def verify(local_root=None):
    data = json.loads(Path(__file__).with_name('inventory.json').read_text())
    errors = []
    for name, expected in data['source_files'].items():
        path = ROOT / name
        if not path.is_file() or sha(path.read_bytes()) != expected:
            errors.append(f'working source mismatch: {name}')
        if sha(git('show', f"{data['source_base']}:{name}")) != expected:
            errors.append(f'base source mismatch: {name}')
    if local_root is not None:
        root = Path(local_root).resolve()
        actual = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
        if actual != set(data['local_files']):
            errors.append('local file set mismatch')
        for name, expected in data['local_files'].items():
            path = root / name
            if (not path.is_file() or path.stat().st_size != expected['bytes']
                    or sha(path.read_bytes()) != expected['sha256']):
                errors.append(f'local bytes mismatch: {name}')
        # Git metadata is read from the supplied checkout, never inferred from names.
        checkout = root.parent.parent
        for name, expected in data['local_files'].items():
            path = str(root / name)
            tracked = bool(git('ls-files', '--', path, cwd=checkout).strip())
            ignored = subprocess.run(['git', 'check-ignore', '-q', '--', path],
                                     cwd=checkout).returncode
            if ignored not in (0, 1):
                errors.append(f'git ignore check failed: {name}')
            if tracked != expected['tracked'] or (ignored == 0) != expected['ignored']:
                errors.append(f'local tracking mismatch: {name}')
        for name, expected in data['index_links'].items():
            path = root / name
            if not path.is_file():
                errors.append(f'index missing: {name}')
                continue
            refs = sorted(set(re.findall(r'\./[\w./-]+\.(?:js|wasm|ico|png)', path.read_text())))
            observed = {ref: (path.parent / ref).is_file() for ref in refs}
            if observed != expected:
                errors.append(f'index linkage changed: {name}')
    return data, errors


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--local-static-root', help='optional local checkout static tree; read only')
    args = parser.parse_args()
    try:
        data, errors = verify(args.local_static_root)
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f'FAIL: {exc}', file=sys.stderr)
        sys.exit(1)
    if errors:
        print('\n'.join(f'FAIL: {error}' for error in errors), file=sys.stderr)
        sys.exit(1)
    print(f"PASS: {len(data['source_files'])} source pins match base and working files")
    if args.local_static_root:
        print(f"PASS: {len(data['local_files'])} local files, per-file Git tracking/ignore status, and index links match inventory")
        print('Known missing PhotoCraft index target remains missing; provenance/readiness NOT VERIFIED')
    else:
        print('Local operational assets NOT CHECKED; use --local-static-root to recheck')
