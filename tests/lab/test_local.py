"""Offline launcher checks; never executes Podman."""
import importlib.util
from contextlib import contextmanager
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('local', Path(__file__).resolve().parents[2] / 'lab/real-seafile/local.py')
local = importlib.util.module_from_spec(spec)
spec.loader.exec_module(local)


class LauncherTest(unittest.TestCase):
    def test_public_origins_rejected_before_run_directory_or_commands(self):
        invalid = ['https://127.1', 'https://127.0.0.1', 'https://2130706433',
                   'https://0177.0.0.1', 'https://0x7f000001', 'https://127.0.0x1', 'https://0x',
                   'http://seafile.test', 'https://user:pass@seafile.test',
                   'https://seafile.test/', 'https://seafile.test/path',
                   'https://seafile.test?x', 'https://seafile.test#x',
                   'https://seafile.test:0', 'https://seafile.test:65536',
                   'https://seafile.test:abc', 'https://', 'https://bad_host.test',
                   'https://seafile.test.', 'https://seafile.test\n',
                   'https://seafile.test\\evil', 'https://[::1]',
                   'https://seafile.test:443@bridge.test', 'https://seafile.test?#', '']
        pairs = [(url, 'https://bridge.test') for url in invalid]
        pairs += [('https://seafile.test', url) for url in invalid]
        pairs += [('https://SAME.test:443', 'https://same.test:8443'),
                  ('https://seafile.test', None), (None, 'https://bridge.test'),
                  ('', None), (None, ''), ('', '')]
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory) / 'run'
            for seafile, bridge in pairs:
                argv = ['local.py', '--run-dir', str(run), '--static', '/unused',
                        '--manifest', '/unused']
                for flag, value in [('--seafile-public-url', seafile),
                                    ('--bridge-public-url', bridge)]:
                    if value is not None:
                        argv += [flag, value]
                with self.subTest(seafile=seafile, bridge=bridge), \
                        patch.object(sys, 'argv', argv), \
                        patch.object(local, 'command') as command, \
                        patch('sys.stderr'):
                    with self.assertRaises(SystemExit) as error:
                        local.main()
                    self.assertEqual(error.exception.code, 2)
                    self.assertFalse(run.exists())
                    command.assert_not_called()

    def test_public_settings_and_compose_defaults(self):
        seafile = local.https_origin('https://Seafile.test:8443')
        bridge = local.https_origin('https://Bridge.test')
        source = (local.ROOT / 'lab/real-seafile/seahub_settings.extra.py').read_text()
        self.assertEqual(local.render_settings(source), source)
        settings = {}
        exec(local.render_settings(source, seafile_public_url=seafile,
                                   bridge_public_url=bridge), settings)
        self.assertEqual(settings['SERVICE_URL'], seafile)
        self.assertEqual(settings['FILE_SERVER_ROOT'], seafile + '/seafhttp')
        self.assertEqual(settings['OFFICE_WEB_APP_BASE_URL'], bridge + '/wopi/discovery.xml')
        self.assertEqual(settings['CSRF_TRUSTED_ORIGINS'], [seafile])
        self.assertEqual(settings['SECURE_PROXY_SSL_HEADER'], ('HTTP_X_FORWARDED_PROTO', 'https'))
        self.assertTrue(settings['ENABLE_OFFICE_WEB_APP'])
        self.assertTrue(settings['ENABLE_ONLYOFFICE'])
        compose = (local.ROOT / 'lab/real-seafile/compose.yml').read_text()
        for line in ['BRIDGE_PUBLIC_URL=${BRIDGE_PUBLIC_URL:-http://bridge:8778}',
                     'BRIDGE_SEAHUB_ORIGIN=${SEAFILE_PUBLIC_URL:-http://seafile.lab}']:
            self.assertIn(line, compose)
        self.assertEqual(compose.count('SEAFILE_URL=${SEAFILE_PUBLIC_URL:-http://seafile.lab}'), 2)
        self.assertEqual(compose.count('BRIDGE_URL=${BRIDGE_PUBLIC_URL:-http://bridge:8778}'), 2)
        self.assertIn('127.0.0.1:${SEAFILE_PORT:-8000}:80', compose)

    def test_settings_can_omit_the_wopi_keys(self):
        text = ('ENABLE_ONLYOFFICE = True\nENABLE_OFFICE_WEB_APP = True\n'
                'OFFICE_WEB_APP_BASE_URL = "http://bridge:8778/wopi/discovery.xml"\n'
                'OFFICE_WEB_APP_FILE_EXTENSION = ("docx",)\n')
        self.assertEqual(local.render_settings(text), text)
        isolated = local.render_settings(text, without_wopi=True)
        self.assertEqual(isolated, 'ENABLE_ONLYOFFICE = True\n\nENABLE_OFFICE_WEB_APP = False\n')

    def test_experimental_flag_parsed(self):
        """Argparse accepts --experimental flag."""
        import sys
        with patch.object(sys, 'argv', ['local.py', '--experimental', '--run-dir', '/tmp/x', '--static', '/tmp/s', '--manifest', '/tmp/m.json']):
            try:
                local.main()
            except SystemExit:
                pass  # Expected: missing files
            except FileNotFoundError:
                pass  # Expected: manifest not found
            except Exception as e:
                if '--experimental' in str(e):
                    self.fail(f"Experimental flag not recognized: {e}")
        text = ('ENABLE_ONLYOFFICE = True\nENABLE_OFFICE_WEB_APP = True\n'
                'OFFICE_WEB_APP_BASE_URL = "http://bridge:8778/wopi/discovery.xml"\n'
                'OFFICE_WEB_APP_FILE_EXTENSION = ("docx",)\n')
        self.assertEqual(local.render_settings(text), text)
        isolated = local.render_settings(text, without_wopi=True)
        self.assertEqual(isolated, 'ENABLE_ONLYOFFICE = True\n\nENABLE_OFFICE_WEB_APP = False\n')

    def test_user_and_libexec_compose_plugins_are_discovered(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            for expected in (str(base / 'home/.docker/cli-plugins/docker-compose'),
                             '/usr/libexec/docker/cli-plugins/docker-compose',
                             '/usr/local/libexec/docker/cli-plugins/docker-compose'):
                def fake_popen(args, **_kwargs):
                    Path(args[-1].removeprefix('unix://')).touch()
                    return object()
                with patch.object(local.shutil, 'which', return_value=None), \
                        patch.object(local.Path, 'home', return_value=base / 'home'), \
                        patch.object(local.os.path, 'isfile', side_effect=lambda p: str(p) == expected), \
                        patch.object(local.os, 'access', return_value=True), \
                        patch.object(local.subprocess, 'Popen', fake_popen), \
                        patch.object(local, 'stop'):
                    with local.compose_backend(base, {}) as backend:
                        self.assertEqual(backend, [expected])

    def test_compose_fallback_owns_only_its_private_api(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            process = object()
            calls = []
            def fake_popen(args, **kwargs):
                calls.append(args)
                Path(args[-1].removeprefix('unix://')).touch()
                return process
            env = {'DOCKER_HOST': 'must-be-replaced'}
            with patch.object(local.shutil, 'which', side_effect=[None, '/synthetic/docker-compose']), \
                    patch.object(local.subprocess, 'Popen', fake_popen), \
                    patch.object(local, 'stop') as stop:
                with self.assertRaisesRegex(ValueError, 'synthetic'):
                    with local.compose_backend(base, env) as backend:
                        self.assertEqual(backend, ['/synthetic/docker-compose'])
                        self.assertEqual(calls[0][:5], ['podman', '--remote=false', 'system', 'service', '--time=0'])
                        self.assertEqual(env['DOCKER_HOST'], calls[0][-1])
                        socket = Path(env['DOCKER_HOST'].removeprefix('unix://'))
                        self.assertEqual(socket.parent.stat().st_mode & 0o777, 0o700)
                        raise ValueError('synthetic interruption')
                stop.assert_called_once_with(process)
            self.assertFalse(socket.parent.exists())

    def test_exact_snapshot(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            assets = base / 'assets'
            assets.mkdir()
            (assets / 'runtime.js').write_text('actual runtime')
            expected = local.manifest(assets)
            for label, supplied in [('ok', expected), ('missing', {}),
                                    ('extra', dict(expected, obsolete='0' * 64)),
                                    ('wrong', {'runtime.js': '0' * 64})]:
                run = base / label
                run.mkdir()
                if label == 'ok':
                    local.snapshot(run, assets, supplied)
                    self.assertFalse((run / 'app/lab/real-seafile/results').exists())
                    for name in ('host.js', 'host.html'):
                        self.assertEqual((run / 'app/bridge/static' / name).read_bytes(),
                                         (local.ROOT / 'bridge/static' / name).read_bytes())
                else:
                    with self.assertRaises(ValueError):
                        local.snapshot(run, assets, supplied)
            (assets / 'link').symlink_to(assets / 'runtime.js')
            with self.assertRaises(ValueError):
                local.manifest(assets)

    def test_rootful_rejected_before_compose(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            assets = base / 'assets'
            assets.mkdir()
            (assets / 'index.html').write_text('synthetic')
            expected = base / 'manifest.json'
            expected.write_text(json.dumps(local.manifest(assets)))
            calls = []

            def fake(args, cwd, env, log, timeout=120):
                calls.append(args)
                log.write_text('false\n')

            argv = ['local.py', '--run-dir', str(base / 'run'), '--static', str(assets),
                    '--manifest', str(expected)]
            old_mask = os.umask(0o077)
            try:
                with patch.object(sys, 'argv', argv), patch.object(local, 'command', fake):
                    with self.assertRaisesRegex(RuntimeError, 'rootless=true'):
                        local.main()
                self.assertEqual(len(calls), 1)
                self.assertEqual(calls[0][0], 'podman')
            finally:
                os.umask(old_mask)

    def test_failure_cleanup_and_private_credentials(self):
        self.check_failure_cleanup_and_private_credentials(False)
        self.check_failure_cleanup_and_private_credentials(True)

    def check_failure_cleanup_and_private_credentials(self, public):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            assets = base / 'assets'
            assets.mkdir()
            (assets / 'index.html').write_text('synthetic')
            manifest = base / 'manifest.json'
            manifest.write_text(json.dumps(local.manifest(assets)))
            run = base / 'run'
            calls = []

            def fake(args, cwd, env, log, timeout=120):
                calls.append(args)
                self.assertEqual(env['SEAFILE_PUBLIC_URL'], 'https://seafile.test' if public else '')
                self.assertEqual(env['BRIDGE_PUBLIC_URL'], 'https://bridge.test' if public else '')
                if args[-2:-1] == ['-c'] and 'with p.open' in args[-1]:
                    self.assertEqual('SERVICE_URL' in args[-1], public)
                    self.assertEqual('https://bridge.test/wopi/discovery.xml' in args[-1], public)
                if args[0] == 'podman':
                    log.write_text('true\n')
                if args[-3:] == ['run', '--rm', 'browser']:
                    raise RuntimeError('synthetic browser failure')

            argv = ['local.py', '--run-dir', str(run), '--static', str(assets), '--manifest', str(manifest)]
            if public:
                argv += ['--seafile-public-url', 'https://seafile.test',
                         '--bridge-public-url', 'https://bridge.test']
            old_mask = os.umask(0o077)
            @contextmanager
            def fake_backend(_run, _env):
                yield ['synthetic-compose']
            try:
                with patch.object(sys, 'argv', argv), patch.object(local, 'command', fake), \
                        patch.object(local, 'compose_backend', fake_backend), \
                        patch.dict(os.environ, {'SEAFILE_PUBLIC_URL': 'https://inherited.test',
                                                'BRIDGE_PUBLIC_URL': 'https://inherited-bridge.test'}):
                    with self.assertRaisesRegex(RuntimeError, 'synthetic browser failure'):
                        local.main()
                    self.assertEqual(calls[-1][-2:], ['down', '--remove-orphans'])
                    self.assertLess(next(i for i, c in enumerate(calls) if c[-1] == 'slice'),
                                    next(i for i, c in enumerate(calls) if c[-1] == 'browser'))
                    self.assertEqual((run / '.env').stat().st_mode & 0o777, 0o600)
                    self.assertEqual(run.stat().st_mode & 0o777, 0o700)
                    with self.assertRaises(FileExistsError):
                        local.main()
            finally:
                os.umask(old_mask)

    def test_diagnostic_browser_never_hides_http_failure(self):
        for diagnostic in (False, True):
            with tempfile.TemporaryDirectory() as directory:
                base = Path(directory)
                assets = base / 'assets'
                assets.mkdir()
                (assets / 'index.html').write_text('synthetic')
                manifest = base / 'manifest.json'
                manifest.write_text(json.dumps(local.manifest(assets)))
                calls = []
                def fake(args, cwd, env, log, timeout=120):
                    calls.append(args)
                    if args[0] == 'podman':
                        log.write_text('true\n')
                    if args[-3:] == ['run', '--rm', 'slice']:
                        raise RuntimeError('synthetic HTTP failure')
                @contextmanager
                def backend(*_):
                    yield ['synthetic-compose']
                argv = ['local.py', '--run-dir', str(base / 'run'), '--static', str(assets), '--manifest', str(manifest)]
                if diagnostic:
                    argv.append('--diagnostic-browser-after-http-failure')
                old_mask = os.umask(0o077)
                try:
                    with patch.object(sys, 'argv', argv), patch.object(local, 'command', fake), patch.object(local, 'compose_backend', backend):
                        with self.assertRaisesRegex(RuntimeError, 'synthetic HTTP failure'):
                            local.main()
                    self.assertEqual(any(c[-3:] == ['run', '--rm', 'browser'] for c in calls), diagnostic)
                    self.assertEqual(calls[-1][-2:], ['down', '--remove-orphans'])
                finally:
                    os.umask(old_mask)


if __name__ == '__main__':
    unittest.main()
