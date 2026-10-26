#!/usr/bin/env python3
"""Static artifact/applicability check only. Does not execute the implementation.

Default inputs are the isolated GR-081 copy workspaces. No tests, builds,
network, browser or service calls. Patches are applied only to temporary copies
for exact output-hash verification.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import shutil

ARTIFACTS = Path(__file__).resolve().parent
REPO = ARTIFACTS.parents[3]
MANIFEST = json.loads((ARTIFACTS / 'identity-binding-r1-manifest.json').read_text())
CACHE = Path(MANIFEST['workspace']).expanduser()
TRANSPORT_REV = MANIFEST['transportDependency']['rev']

def require(condition, message):
    if not condition:
        raise SystemExit(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def files(root):
    return {
        path.relative_to(root): path
        for path in root.rglob('*')
        if path.is_file() and '.git' not in path.relative_to(root).parts
    }


resolved_transport = subprocess.check_output(['git', 'rev-parse', TRANSPORT_REV], cwd=REPO, text=True).strip()
require(resolved_transport == TRANSPORT_REV, 'transport commit is unavailable in this checkout')
for app in ('wordcraft', 'gridcraft'):
    root = CACHE / 'work' / app
    require(TRANSPORT_REV in (root / 'Cargo.toml').read_text(), f'{app} Cargo.toml transport pin mismatch')
    require(TRANSPORT_REV in (root / 'Cargo.lock').read_text(), f'{app} Cargo.lock transport pin mismatch')

for name, expected in MANIFEST['patchSha256'].items():
    require(sha(ARTIFACTS / name) == expected, f'patch changed: {name}')

for app, expected in MANIFEST['baseCommits'].items():
    baseline = CACHE / 'baseline' / app
    work = CACHE / 'work' / app
    source = CACHE.parent / 'gr081-source' / app
    for checkout in [baseline, work, source]:
        actual = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=checkout, text=True).strip()
        require(actual == expected, f'wrong base commit: {checkout}')
    original_files = files(source)
    baseline_files = files(baseline)
    work_files = files(work)
    require(original_files.keys() == baseline_files.keys(), f'original source inventory changed: {app}')
    for relative, original in original_files.items():
        require(sha(original) == sha(baseline_files[relative]), f'original source changed: {app}/{relative}')
    expected_changed = {Path(row['path']) for row in MANIFEST['files'][app]}
    local_only = {Path(row['path']) for row in MANIFEST['localOnly'] if row['app'] == app}
    require(work_files.keys() == baseline_files.keys(), f'implementation inventory changed: {app}')
    changed = {relative for relative in work_files if sha(work_files[relative]) != sha(baseline_files[relative])}
    require(changed == expected_changed | local_only, f'unrecorded implementation changes: {app}')
    print(f'{app}: exact base commit; original source equals baseline; only recorded copy edits')

for group, rows in MANIFEST['files'].items():
    baseline = CACHE / 'baseline' / group
    work = REPO if group == 'storage-lab' else CACHE / 'work' / group
    for row in rows:
        relative = Path(row['path'])
        require(sha(baseline / relative) == row['baselineSha256'], f'baseline mismatch: {group}/{relative}')
        require(sha(work / relative) == row['implementationSha256'], f'implementation mismatch: {group}/{relative}')
        require('tests' not in relative.parts and not relative.name.endswith('tests.rs'), f'test file edited: {relative}')
        old = (baseline / relative).read_bytes()
        new = (work / relative).read_bytes()
        marker = b'#[cfg(test)]\nmod tests {'
        if marker in old:
            require(marker in new and old[old.index(marker):] == new[new.index(marker):], f'inline tests edited: {relative}')
    patch = ARTIFACTS / f'{group}-identity-binding-r1.patch'
    subprocess.run(['git', 'apply', '--unidiff-zero', '--check', str(patch)], cwd=baseline, check=True)
    with tempfile.TemporaryDirectory(prefix=f'gr081-{group}-patch-') as temp:
        target = Path(temp) / group
        shutil.copytree(baseline, target, ignore=shutil.ignore_patterns('.git'))
        subprocess.run(['patch', '-p1', '--forward', '--batch', '-i', str(patch)], cwd=target, check=True, stdout=subprocess.DEVNULL)
        applied = files(target)
        original = files(baseline)
        expected_changed = {Path(row['path']) for row in rows}
        changed = {relative for relative in applied.keys() | original.keys()
                   if relative not in applied or relative not in original or
                   sha(applied[relative]) != sha(original[relative])}
        require(changed == expected_changed, f'applied patch changed unexpected files: {group}')
        for row in rows:
            relative = Path(row['path'])
            require(sha(applied[relative]) == row['implementationSha256'],
                    f'applied patch output differs from manifest: {group}/{relative}')
    print(f'{group}: hashes match; patch applies and reproduces every recorded file')

for row in MANIFEST['localOnly']:
    require(sha(CACHE / 'work' / row['app'] / row['path']) == row['sha256'], 'local override changed')
print('Static artifact check complete. Compilation, tests, runtime behavior and security properties NOT VERIFIED.')
