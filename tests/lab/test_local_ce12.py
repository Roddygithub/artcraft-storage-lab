"""Offline checks for the isolated Seafile CE12 browser launcher; never starts containers."""
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('local_ce12', ROOT / 'lab/real-seafile/local_ce12.py')
local_ce12 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(local_ce12)


class CE12LauncherTest(unittest.TestCase):
    def test_compose_isolated_and_image_pinned(self):
        compose = (ROOT / 'lab/real-seafile/compose.ce12.yml').read_text()
        self.assertNotIn('container_name:', compose)
        self.assertNotIn('name: seafile-net', compose)
        self.assertIn('127.0.0.1:${SEAFILE_PORT}:80', compose)
        self.assertIn('${SEAFILE_IMAGE}', compose)
        self.assertIn('@sha256:', local_ce12.SEAFILE_IMAGE)

    def test_deckcraft_route_settings_are_generated_from_selected_editors(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            config = run / 'app/lab/real-seafile/editors.json'
            config.parent.mkdir(parents=True)
            config.write_text((ROOT / 'lab/real-seafile/editors.json').read_text())
            script = local_ce12.configure_app(run, ['wordcraft', 'gridcraft', 'deckcraft'])
            mapping = json.loads(config.read_text())
            self.assertEqual(mapping['deckcraft']['extensions'], ['pptx'])
            self.assertIn("OFFICE_WEB_APP_FILE_EXTENSION = ('docx', 'xlsx', 'pptx', 'pdf', 'dxf', 'svg', 'figcraft')", script)
            self.assertIn('ENABLE_ONLYOFFICE = False', script)

    def test_private_env_permissions(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / '.env'
            local_ce12.write_private_env(path, {'SYNTHETIC_SECRET': 'not-real'})
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)

    def test_missing_editor_bundle_fails_before_creating_run_dir(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            static = base / 'static'; static.mkdir()
            manifest = base / 'manifest.json'; manifest.write_text('{}')
            run = base / 'run'
            argv = ['local_ce12.py', '--run-dir', str(run), '--static', str(static),
                    '--manifest', str(manifest), '--editors', 'deckcraft']
            with patch.object(sys, 'argv', argv), patch('sys.stderr'):
                with self.assertRaises(SystemExit) as error:
                    local_ce12.main()
            self.assertEqual(error.exception.code, 2)
            self.assertFalse(run.exists())


if __name__ == '__main__':
    unittest.main()
