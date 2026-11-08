#!/usr/bin/env python3
"""One fresh, private rootless Podman lab; no user socket required."""
import argparse
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import secrets
import shutil
import signal
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]


def manifest(directory):
    result = {}
    for path in sorted(directory.rglob('*')):
        if path.is_symlink() or not (path.is_file() or path.is_dir()):
            raise ValueError(f'non-regular asset: {path}')
        if path.is_file():
            with path.open('rb') as source:
                result[path.relative_to(directory).as_posix()] = hashlib.file_digest(
                    source, 'sha256').hexdigest()
    return result


def snapshot(run, assets, expected):
    # Copy first, then verify the bytes that services will actually read.
    for name in ('bridge', 'lab'):
        shutil.copytree(ROOT / name, run / 'app' / name,
                        ignore=shutil.ignore_patterns('results', 'cache', '__pycache__',
                                                     '.cache', *(['static'] if name == 'lab' else [])))
    target = run / 'app/lab/real-seafile/static'
    shutil.copytree(assets, target, symlinks=True)
    actual = manifest(target)
    if not actual or actual != expected:
        raise ValueError('static SHA256 manifest mismatch (exact membership and hashes required)')
    (run / 'static-sha256.json').write_text(json.dumps(actual, indent=2) + '\n')
    shutil.copyfile(run / 'app/lab/real-seafile/compose.yml', run / 'compose.yml')


def render_settings(text, without_wopi=False):
    """Managed lab block; ONLYOFFICE-only isolation is diagnostic, not coexistence.

    Explicitly override earlier WOPI assignments in the disposable generated
    configuration. Never apply this to an existing production instance.
    """
    lines = text.splitlines(keepends=True)
    if without_wopi:
        lines = [line for line in lines
                 if not line.startswith(('ENABLE_OFFICE_WEB_APP', 'OFFICE_WEB_APP_'))]
    return ''.join(lines) + ('\nENABLE_OFFICE_WEB_APP = False\n' if without_wopi else '')


def stop(proc):
    if proc.poll() is not None:
        return
    try:
        os.killpg(proc.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        proc.wait(timeout=10)


@contextmanager
def compose_backend(run, env):
    native = shutil.which('podman-compose')
    if native:
        yield [native, '--podman-args=--remote=false']
        return
    plugin = shutil.which('docker-compose')
    if not plugin:
        plugin = next((str(p) for p in (Path.home() / '.docker/cli-plugins/docker-compose',
                                  '/usr/lib/docker/cli-plugins/docker-compose',
                                  '/usr/local/lib/docker/cli-plugins/docker-compose',
                                  '/usr/libexec/docker/cli-plugins/docker-compose',
                                  '/usr/local/libexec/docker/cli-plugins/docker-compose')
                       if os.path.isfile(p) and os.access(p, os.X_OK)), None)
    if not plugin:
        raise RuntimeError('install podman-compose or the Docker Compose v2 plugin')
    # A private API socket avoids starting or changing the user's shared Podman service.
    with tempfile.TemporaryDirectory(prefix='craftlab-api-') as directory:
        socket = Path(directory) / 'podman.sock'
        address = 'unix://' + str(socket)
        env['DOCKER_HOST'] = address
        with (run / 'api.log').open('ab') as output:
            proc = subprocess.Popen(['podman', '--remote=false', 'system', 'service',
                                     '--time=0', address], env=env, stdout=output,
                                    stderr=subprocess.STDOUT, start_new_session=True)
            try:
                deadline = time.monotonic() + 15
                while not socket.exists():
                    if proc.poll() is not None or time.monotonic() >= deadline:
                        raise RuntimeError('private Podman API did not start; see api.log')
                    time.sleep(0.1)
                yield [plugin]
            finally:
                stop(proc)


def command(args, cwd, env, log, timeout=120):
    with log.open('ab') as output:
        proc = subprocess.Popen(args, cwd=cwd, env=env, stdout=output,
                                stderr=subprocess.STDOUT, start_new_session=True)
        try:
            code = proc.wait(timeout=timeout)
        except BaseException:
            stop(proc)
            raise
        if code:
            raise RuntimeError(f'{args[0]} failed ({code}); see private {log.name}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir', type=Path, required=True)
    parser.add_argument('--static', type=Path, required=True)
    parser.add_argument('--manifest', type=Path, required=True,
                        help='JSON object: relative POSIX filename -> lowercase SHA256')
    for name, default in [('seafile', 8000), ('onlyoffice', 8100), ('bridge', 8778)]:
        parser.add_argument(f'--{name}-port', type=int, default=default)
    parser.add_argument('--editor', default='')
    parser.add_argument('--wordcraft-fixture', default='')
    parser.add_argument('--onlyoffice-regression', action='store_true',
                        help='run the ODT edit/save/reopen regression instead of Craft scenarios')
    parser.add_argument('--without-wopi', action='store_true',
                        help='omit the bridge WOPI keys to isolate stock ONLYOFFICE (diagnostic only)')
    parser.add_argument('--experimental', action='store_true',
                        help='use experimental editors.json and Seahub settings (Rust ports)')
    args = parser.parse_args()
    if args.onlyoffice_regression and (args.editor or args.wordcraft_fixture):
        parser.error('ONLYOFFICE regression cannot select a Craft editor or fixture')
    run = args.run_dir.expanduser().resolve()
    if run == ROOT or ROOT in run.parents:
        parser.error('run directory must be outside the repository')
    ports = [args.seafile_port, args.onlyoffice_port, args.bridge_port]
    if len(set(ports)) != 3 or any(not 1 <= p <= 65535 for p in ports):
        parser.error('ports must be distinct and between 1 and 65535')
    expected = json.loads(args.manifest.read_text())
    os.umask(0o077)
    run.mkdir(mode=0o700, parents=True, exist_ok=False)
    snapshot(run, args.static.resolve(), expected)
    project = 'craftlab-' + secrets.token_hex(8)
    values = {key: secrets.token_hex(32) for key in (
        'SEAFILE_MYSQL_DB_PASSWORD', 'INIT_SEAFILE_MYSQL_ROOT_PASSWORD',
        'REDIS_PASSWORD', 'JWT_PRIVATE_KEY', 'ONLYOFFICE_JWT_SECRET', 'ADMIN_PASSWORD')}
    values['ADMIN_EMAIL'] = 'synthetic-' + secrets.token_hex(8) + '@lab.test'
    (run / '.env').write_text(''.join(f'{k}={v}\n' for k, v in values.items()))
    # Do not inherit remote Podman/Docker targets or compose overrides.
    env = {k: v for k, v in os.environ.items()
           if not k.startswith(('CONTAINER_', 'DOCKER_', 'COMPOSE_', 'PODMAN_'))}
    env.update(values)
    env.update({f'{name.upper()}_PORT': str(port) for name, port in
                zip(('seafile', 'onlyoffice', 'bridge'), ports)})
    # Determine editor config early for env
    if args.experimental:
        editor_config = run / 'app/lab/real-seafile/editors.experimental.json'
    else:
        editor_config = run / 'app/lab/real-seafile/editors.json'
    env.update(BROWSER_ONLY_EDITOR=args.editor,
               BROWSER_WORDCRAFT_FIXTURE=args.wordcraft_fixture,
               BROWSER_SCRIPT='run_onlyoffice_browser.py' if args.onlyoffice_regression else 'run_browser.py',
               BROWSER_EDITOR_CONFIG=str(editor_config))
    log = run / 'launcher.log'
    command(['podman', '--remote=false', 'info', '--format', '{{.Host.Security.Rootless}}'], run, env, log)
    if log.read_text().strip() != 'true':
        raise RuntimeError('Podman must report rootless=true')
    (run / 'project.txt').write_text(project + '\n')
    (run / 'results').mkdir()
    # Configure only the Seafile container belonging to this new project.
    if args.experimental:
        config_path = run / 'app/lab/real-seafile/seahub_settings.experimental.py'
    else:
        config_path = run / 'app/lab/real-seafile/seahub_settings.extra.py'
    config = config_path.read_text()
    config = config.replace('__ONLYOFFICE_JWT_SECRET__', values['ONLYOFFICE_JWT_SECRET'])
    config = render_settings(config, args.without_wopi)
    # editor_config is already defined above in both branches
    script = ("from pathlib import Path; import time\n"
              "p=Path('/shared/seafile/conf/seahub_settings.py')\n"
              "for _ in range(120):\n"
              " if p.is_file(): break\n"
              " time.sleep(5)\n"
              "else: raise SystemExit('Seahub config never appeared')\n"
              f"with p.open('a') as f: f.write('\\n' + {config!r})\n")
    with compose_backend(run, env) as backend:
        compose = backend + ['-f', str(run / 'compose.yml'), '-p', project, '--profile', 'test']
        try:
            command(compose + ['up', '-d', 'db', 'redis', 'seafile', 'onlyoffice', 'bridge'],
                    run, env, log, 900)
            command(compose + ['exec', '-T', 'seafile', 'python3', '-c', script], run, env, log, 630)
            command(compose + ['restart', 'seafile'], run, env, log)
            ready = ("import time, urllib.request\n"
                     "for _ in range(90):\n"
                     " try:\n"
                     "  if urllib.request.urlopen('http://127.0.0.1:8000/api2/ping/', timeout=5).status == 200: break\n"
                     " except Exception: pass\n"
                     " time.sleep(2)\n"
                     "else: raise SystemExit('Seahub did not become ready')\n")
            command(compose + ['exec', '-T', 'seafile', 'python3', '-c', ready], run, env, log, 240)
            services = ('browser',) if args.onlyoffice_regression else ('slice', 'browser')
            for service in services:
                command(compose + ['run', '--rm', service], run, env, log, 3600)
        finally:
            try:
                command(compose + ['logs', '--no-color'], run, env, run / 'services.log')
            finally:
                command(compose + ['down', '--remove-orphans'], run, env, log, 180)
    print(f'Private evidence: {run / "results"}')


if __name__ == '__main__':
    def interrupted(*_):
        raise KeyboardInterrupt

    signal.signal(signal.SIGTERM, interrupted)
    try:
        main()
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as exc:
        sys.exit(str(exc))
