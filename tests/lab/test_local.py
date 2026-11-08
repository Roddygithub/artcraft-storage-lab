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
                if args[0] == 'podman':
                    log.write_text('true\n')
                if args[-3:] == ['run', '--rm', 'browser']:
                    raise RuntimeError('synthetic browser failure')

            argv = ['local.py', '--run-dir', str(run), '--static', str(assets), '--manifest', str(manifest)]
            old_mask = os.umask(0o077)
            @contextmanager
            def fake_backend(_run, _env):
                yield ['synthetic-compose']
            try:
                with patch.object(sys, 'argv', argv), patch.object(local, 'command', fake), \
                        patch.object(local, 'compose_backend', fake_backend):
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


if __name__ == '__main__':
    unittest.main()
