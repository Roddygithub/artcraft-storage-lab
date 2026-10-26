#!/usr/bin/env python3
"""Verify GR-067 staged and active EffectCraft assets against the pinned build."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
MANIFEST = REPO / 'docs/reviews/GR-067/candidate-inventory.json'

def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def inventory(root: Path) -> list[str]:
    return sorted(p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file())

def main() -> int:
    data = json.loads(MANIFEST.read_text())
    build = Path(data['build_cache'])
    staged = Path(data['staged_root'])
    active = Path(data['active_root'])
    expected = [item['path'] for item in data['files']]
    if inventory(staged) != expected or inventory(active) != expected:
        raise SystemExit('FAIL: candidate file membership differs from manifest')
    for item in data['files']:
        rel = item['path']
        for label, root in [('build', build), ('staged', staged), ('active', active)]:
            path = root / rel
            if path.stat().st_size != item['size_bytes'] or digest(path) != item['sha256']:
                raise SystemExit(f'FAIL: {label} asset mismatch: {rel}')
    print(f"PASS: {len(expected)} EffectCraft assets; {sum(x['size_bytes'] for x in data['files'])} bytes; build, staged and active hashes match")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
