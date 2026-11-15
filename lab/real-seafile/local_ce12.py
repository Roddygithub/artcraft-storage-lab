#!/usr/bin/env python3
"""Run synthetic ArtCraft browser workflows on an isolated Seafile CE 12 stack."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import secrets
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SEAFILE_IMAGE = 'docker.io/seafileltd/seafile-mc@sha256:7bbe7043facbc639a8e6144f32d50dc4d771191ecaa68002efb2b0237fb90358'

spec = importlib.util.spec_from_file_location('artcraft_local', HERE / 'local.py')
local = importlib.util.module_from_spec(spec)
spec.loader.exec_module(local)


def write_private_env(path, values):
    old_mask = os.umask(0o077)
    try:
        path.write_text(''.join(f'{key}={value}\n' for key, value in values.items()))
        path.chmod(0o600)
    finally:
        os.umask(old_mask)


def wait_for_seahub(port, timeout=600):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(f'http://127.0.0.1:{port}/api2/ping/', timeout=3) as response:
                if response.status == 200:
                    return
        except (OSError, urllib.error.URLError):
            pass
        time.sleep(2)
    raise RuntimeError('Seafile CE12 did not become ready; inspect launcher.log and service logs')


def configure_app(run, selected):
    editor_path = run / 'app/lab/real-seafile/editors.json'
    mapping = json.loads(editor_path.read_text())
    if 'deckcraft' in selected:
        mapping['deckcraft'] = {
            'app': 'deckcraft',
            'label': 'DeckCraft v0.16.0 (upstream, unpatched)',
            'extensions': ['pptx'],
            'url': '/editors/deckcraft/index.html?host=parent',
        }
    editor_path.write_text(json.dumps(mapping, indent=2) + '\n')
    # Match the exact CE12 WOPI tuple from the earlier successful isolated replay.
    extensions = ('docx', 'xlsx', 'pptx', 'pdf', 'dxf', 'svg', 'figcraft')
    quoted = repr(tuple(extensions))
    settings = (
        '\n# Isolated ArtCraft CE12 browser test only\n'
        'ENABLE_ONLYOFFICE = False\n'
        'ENABLE_OFFICE_WEB_APP = True\n'
        "OFFICE_WEB_APP_BASE_URL = 'http://bridge:8778/wopi/discovery.xml'\n"
        f'OFFICE_WEB_APP_FILE_EXTENSION = {quoted}\n'
        'ENABLE_OFFICE_WEB_APP_EDIT = True\n'
        f'OFFICE_WEB_APP_EDIT_FILE_EXTENSION = {quoted}\n'
        'WOPI_ACCESS_TOKEN_EXPIRATION = 1800\n'
    )
    script = (
        'from pathlib import Path; import time\n'
        "p=Path('/shared/seafile/conf/seahub_settings.py')\n"
        'for _ in range(120):\n'
        ' if p.is_file(): break\n'
        ' time.sleep(5)\n'
        "else: raise SystemExit('Seahub config never appeared')\n"
        f'with p.open("a") as f: f.write({settings!r})\n'
    )
    return script


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir', type=Path, required=True, help='new private directory outside the repository')
    parser.add_argument('--static', type=Path, required=True, help='verified static bundles; include DeckCraft v0.16.0')
    parser.add_argument('--manifest', type=Path, required=True, help='exact lowercase SHA-256 manifest JSON for --static')
    parser.add_argument('--editors', nargs='+', choices=('wordcraft', 'gridcraft', 'deckcraft'),
                        default=('wordcraft', 'gridcraft', 'deckcraft'))
    parser.add_argument('--seafile-port', type=int, default=18080)
    args = parser.parse_args()
    run = args.run_dir.expanduser().resolve()
    if run == ROOT or ROOT in run.parents:
        parser.error('run directory must be outside the repository')
    if run.exists():
        parser.error('run directory must not already exist')
    if not 1 <= args.seafile_port <= 65535:
        parser.error('--seafile-port must be between 1 and 65535')
    if len(args.editors) != len(set(args.editors)):
        parser.error('--editors cannot contain duplicates')
    expected = json.loads(args.manifest.read_text())
    static = args.static.expanduser().resolve()
    missing = [name for name in args.editors if not (static / name).is_dir()]
    if missing:
        parser.error(f'--static lacks selected editor bundles: {", ".join(missing)}')
    run.mkdir(mode=0o700, parents=True)
    local.snapshot(run, static, expected)
    shutil.copy2(HERE / 'compose.ce12.yml', run / 'compose.yml')
    (run / 'data/mysql').mkdir(parents=True)
    (run / 'data/seafile').mkdir(parents=True)
    (run / 'results').mkdir()
    values = {
        'SEAFILE_IMAGE': SEAFILE_IMAGE,
        'SEAFILE_DB_IMAGE': 'docker.io/library/mariadb:10.11',
        'SEAFILE_MEMCACHED_IMAGE': 'docker.io/library/memcached:1.6.29',
        'SEAFILE_PORT': str(args.seafile_port),
        'INIT_SEAFILE_MYSQL_ROOT_PASSWORD': secrets.token_urlsafe(32),
        'SEAFILE_MYSQL_DB_PASSWORD': secrets.token_urlsafe(32),
        'INIT_SEAFILE_ADMIN_EMAIL': 'synthetic-' + secrets.token_hex(8) + '@lab.test',
        'INIT_SEAFILE_ADMIN_PASSWORD': secrets.token_urlsafe(32),
        'JWT_PRIVATE_KEY': secrets.token_hex(32),
    }
    write_private_env(run / '.env', values)
    project = 'artcraft-ce12-' + secrets.token_hex(8)
    (run / 'project.txt').write_text(project + '\n')
    env = {key: value for key, value in os.environ.items()
           if not key.startswith(('CONTAINER_', 'DOCKER_', 'COMPOSE_', 'PODMAN_'))}
    env.update(values)
    env['COMPOSE_PROJECT_NAME'] = project
    log = run / 'launcher.log'
    local.command(['podman', '--remote=false', 'info', '--format', '{{.Host.Security.Rootless}}'], run, env, log)
    if log.read_text().strip() != 'true':
        raise RuntimeError('Podman must report rootless=true')
    # The bridge reads editors.json at startup, so add DeckCraft before `up`.
    script = configure_app(run, args.editors)
    compose = None
    with local.compose_backend(run, env) as backend:
        compose = backend + ['-f', str(run / 'compose.yml'), '-p', project]
        try:
            local.command(compose + ['up', '-d', 'db', 'memcached', 'seafile', 'bridge'], run, env, log, 900)
            wait_for_seahub(args.seafile_port)
            local.command(compose + ['exec', '-T', 'seafile', 'python3', '-c', script], run, env, log, 630)
            local.command(compose + ['restart', 'seafile'], run, env, log)
            wait_for_seahub(args.seafile_port)
            for editor in args.editors:
                result_dir = f'/results/{editor}'
                (run / 'results' / editor).mkdir()
                local.command(compose + ['run', '--rm', '-e', f'RESULTS_DIR={result_dir}',
                                         '-e', f'BROWSER_ONLY_EDITOR={editor}', 'browser'],
                              run, env, log, 1500)
        finally:
            try:
                local.command(compose + ['logs', '--no-color'], run, env, run / 'services.log', 180)
            finally:
                local.command(compose + ['down', '--remove-orphans'], run, env, log, 180)
    print(f'Private CE12 browser evidence: {run / "results"}')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as exc:
        sys.exit(str(exc))
