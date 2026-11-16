#!/usr/bin/env python3
"""Verify static-sha256.json manifests for retained evidence directories.

Used by CI to ensure manifest integrity and consistency across evidence runs.
The actual editor bundles are not in the repo (they're in the local cache),
so this verifies that the manifest files themselves are consistent and have
the expected structure (167 entries for the pinned editor tree).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MANIFESTS = [
    'lab/real-seafile/results/2026-11-16-seafile12-byteproof/static-sha256.json',
    'lab/real-seafile/results/2026-11-15-seafile12-detail/static-sha256.json',
    'lab/real-seafile/results/2026-11-15-seafile12-replay/static-sha256.json',
]

EXPECTED_COUNT = 167
EXPECTED_KEY_PREFIXES = ('wordcraft/', 'gridcraft/', 'deckcraft/', 'host-shim.js')


def main() -> int:
    all_ok = True
    first_manifest = None

    for mf_path in MANIFESTS:
        mf = ROOT / mf_path
        try:
            d = json.loads(mf.read_text())
        except FileNotFoundError:
            print(f'FAIL: manifest not found: {mf_path}')
            return 1
        except json.JSONDecodeError as e:
            print(f'FAIL: invalid JSON in {mf_path}: {e}')
            return 1

        # Verify entry count
        if len(d) != EXPECTED_COUNT:
            print(f'FAIL: {mf_path} has {len(d)} entries, expected {EXPECTED_COUNT}')
            all_ok = False

        # Verify expected key prefixes exist
        for prefix in EXPECTED_KEY_PREFIXES:
            if not any(k.startswith(prefix) for k in d):
                print(f'FAIL: {mf_path} missing entries with prefix {prefix}')
                all_ok = False

        # Verify all values are 64-char hex strings
        for k, v in d.items():
            if not (isinstance(v, str) and len(v) == 64 and all(c in '0123456789abcdef' for c in v)):
                print(f'FAIL: {mf_path} entry {k} has invalid hash: {v!r}')
                all_ok = False

        # Verify consistency with first manifest
        if first_manifest is None:
            first_manifest = d
        elif d != first_manifest:
            print(f'FAIL: {mf_path} differs from first manifest')
            # Find first difference
            for k in set(first_manifest) | set(d):
                if first_manifest.get(k) != d.get(k):
                    print(f'  diff at {k}: first={first_manifest.get(k)!r} this={d.get(k)!r}')
                    break
            all_ok = False

        print(f'OK: {mf_path} ({len(d)} entries, consistent)')

    return 0 if all_ok else 1


if __name__ == '__main__':
    sys.exit(main())