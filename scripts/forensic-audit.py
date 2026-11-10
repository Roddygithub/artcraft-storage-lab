#!/usr/bin/env python3
"""Mechanical forensic audit of committed lab evidence.

This is not an independent review: it is a self-audit run by the implementer.
It re-hashes every retained evidence directory, runs each verifier, checks that
provenance source commits exist in this repository and are ancestors of HEAD,
and scans retained JSON for per-run identifiers, tokens and WOPI secrets.

usage:
  python3 scripts/forensic-audit.py --output <new-private-dir>
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / 'lab/real-seafile/results'
SECRET_PATTERNS = {
    'per-run account': re.compile(r'synthetic-[0-9a-f]{6,}'),
    'seahub internal account': re.compile(r'[0-9a-f]{16,}@auth\.local'),
    'plain WOPI source URL': re.compile(r'WOPISrc=http'),
    'unredacted WOPI file id': re.compile(r'wopi/files/[0-9a-f]{8,}'),
    'access token field': re.compile(r'"(access_token|refresh_token)"'),
    'repo identifier key': re.compile(r'"repo_id"\s*:'),
}


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(['git', *args], cwd=ROOT, text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


def audit_hashes(directory: Path, failures: list) -> int:
    sums = directory / 'SHA256SUMS'
    if not sums.is_file():
        return 0
    seen = set()
    for line in sums.read_text().splitlines():
        digest, name = line.split('  ')
        relative = Path(name)
        if relative.is_absolute() or '..' in relative.parts or name in seen:
            failures.append(f'{directory.name}: unsafe or duplicate path {name}')
            continue
        seen.add(name)
        target = directory / relative
        if not target.is_file():
            failures.append(f'{directory.name}: missing {name}')
            continue
        actual = hashlib.sha256(target.read_bytes()).hexdigest()
        if actual != digest:
            failures.append(f'{directory.name}: hash mismatch for {name}')
    files = {p.relative_to(directory).as_posix() for p in directory.rglob('*')
             if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc'
             } - {'SHA256SUMS'}
    if seen != files:
        failures.append(f'{directory.name}: SHA256SUMS does not cover {sorted(files ^ seen)}')
    return len(seen)


def audit_verifier(directory: Path, failures: list) -> bool:
    verifier = directory / 'verify.py'
    if not verifier.is_file():
        return False
    result = subprocess.run([sys.executable, str(verifier)], cwd=directory,
                            text=True, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    if result.returncode:
        failures.append(f'{directory.name}: verify.py failed: {result.stdout.strip()[:300]}')
        return False
    return True


def audit_provenance(directory: Path, failures: list) -> int:
    provenance = directory / 'provenance.json'
    if not provenance.is_file():
        return 0
    checked = 0
    for value in json.loads(provenance.read_text()).values():
        for text in ([value] if isinstance(value, str) else
                     [item for item in value if isinstance(item, str)]
                     if isinstance(value, list) else []):
            # Dates such as 20261108 are not commits; require a hex letter or a full SHA.
            for sha in re.findall(r'\b[0-9a-f]{7,40}\b', text):
                if len(sha) == 8 and sha.startswith('20'):
                    continue
                if git('cat-file', '-e', f'{sha}^{{commit}}').returncode:
                    failures.append(f'{directory.name}: provenance SHA {sha} is not a commit')
                    continue
                if git('merge-base', '--is-ancestor', sha, 'HEAD').returncode:
                    failures.append(f'{directory.name}: provenance SHA {sha} is not an ancestor of HEAD')
                checked += 1
    return checked


def audit_secrets(directory: Path, failures: list) -> int:
    scanned = 0
    for path in directory.rglob('*.json'):
        text = path.read_text()
        scanned += 1
        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                failures.append(f'{directory.name}/{path.name}: retained {label}')
    return scanned


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--output', type=Path, required=True,
                        help='new private directory outside the repository')
    args = parser.parse_args()
    output = args.output.expanduser().resolve()
    if output == ROOT or ROOT in output.parents:
        parser.error('logs must stay outside the repository')
    output.mkdir(parents=True, exist_ok=False)

    failures: list = []
    rows = []
    for directory in sorted(RESULTS.iterdir()):
        if not directory.is_dir():
            continue
        row = {'directory': directory.name,
               'hashes': audit_hashes(directory, failures),
               'verifier': audit_verifier(directory, failures),
               'provenance_commits': audit_provenance(directory, failures),
               'secrets_scanned': audit_secrets(directory, failures)}
        rows.append(row)
        print(f"{directory.name}: hashes={row['hashes']} verifier={row['verifier']} "
              f"provenance={row['provenance_commits']} json={row['secrets_scanned']}",
              flush=True)

    head = git('rev-parse', 'HEAD').stdout.strip()
    summary = {'scope': 'mechanical self-audit, not an independent review',
               'head': head, 'directories': rows,
               'failures': failures, 'passed': not failures}
    (output / 'summary.json').write_text(json.dumps(summary, indent=1) + '\n')
    if failures:
        print(f"\nFAIL: {len(failures)} finding(s)")
        for failure in failures:
            print(' - ' + failure)
        return 1
    print(f"\nPASS: {len(rows)} evidence directories, hashes, verifiers, provenance "
          f"and secret scan at {head[:12]}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
