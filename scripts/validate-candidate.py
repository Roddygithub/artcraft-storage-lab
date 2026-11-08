#!/usr/bin/env python3
"""Run the active offline checks with bounded, private logs and a compact summary.

Real browser validation remains lab/real-seafile/local.py. This runner never
claims HTTPS, format compatibility or independent review from offline checks.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
PYTHON_CHECKS = [
    'tests/bridge/test_bridge.py', 'tests/lab/test_local.py',
    'tests/test_candidate_scope.py', 'tests/test_gridcraft_real_edit.py',
    'tests/test_pdfcraft_real_edit.py', 'tests/test_cadcraft_real_edit.py',
    'tests/test_vector_fig_real_edit.py', 'tests/test_docx_fidelity_corpus.py',
    'tests/test_wordcraft_browser_fixture.py', 'tests/test_wordcraft_reopen_wait.py',
    'tests/test_pptx_roundtrip_fixture.py', 'tests/test_deckcraft_real_edit.py', 'tests/test_deckcraft_render_wait.py',
    'tests/test_xlsx_fixture.py', 'tests/test_gr041_craft_zip_limits.py',
]
NODE_CHECKS = ['tests/bridge/test_host.mjs', 'tests/bridge/test_host_shim.mjs',
               'tests/bridge/test_shim.mjs']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True,
                        help='new private directory outside the repository')
    args = parser.parse_args()
    output = args.output.expanduser().resolve()
    if output == ROOT or ROOT in output.parents:
        parser.error('logs must stay outside the repository')
    os.umask(0o077)
    output.mkdir(parents=True, exist_ok=False)
    commands = [(p, [sys.executable, p]) for p in PYTHON_CHECKS]
    commands += [(p, ['node', p]) for p in NODE_CHECKS]
    commands += [('shell-syntax', ['bash', '-n', 'lab/real-seafile/up.sh'])]

    def check(item):
        name, command = item
        start = time.monotonic()
        log = name.replace('/', '_') + '.log'
        with (output / log).open('w') as stream:
            try:
                code = subprocess.run(command, cwd=ROOT, stdout=stream,
                                      stderr=subprocess.STDOUT, timeout=180).returncode
            except (OSError, subprocess.TimeoutExpired) as exc:
                stream.write(str(exc) + '\n')
                code = 124
        return dict(name=name, exit=code, seconds=round(time.monotonic() - start, 2), log=log)

    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(check, commands))
    failed = [r['name'] for r in results if r['exit']]
    summary = dict(source=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                   scope='active offline checks only', passed=len(results)-len(failed),
                   failed=len(failed), checks=results)
    (output / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(f"Offline: {summary['passed']}/{len(results)} passed; {len(failed)} failed")
    for name in failed:
        print('FAIL ' + name)
    print('Private logs: ' + str(output))
    return bool(failed)


if __name__ == '__main__':
    sys.exit(main())
