import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lab" / "real-seafile"))
import switch_docx_route as route_switch  # noqa: E402
from switch_docx_route import switch_settings  # noqa: E402


class FidelityRouteSwitchTests(unittest.TestCase):
    def test_docx_moves_to_onlyoffice_without_leaving_wopi_enabled(self):
        source = "\n".join((
            "ENABLE_ONLYOFFICE = True",
            "ENABLE_OFFICE_WEB_APP = True",
            "ONLYOFFICE_FILE_EXTENSION = ('doc', 'ppt', 'xls', 'odt')",
            "ONLYOFFICE_EDIT_FILE_EXTENSION = ('odt', 'odp')",
            "OFFICE_WEB_APP_FILE_EXTENSION = ('docx', 'xlsx', 'pptx')",
            "OFFICE_WEB_APP_EDIT_FILE_EXTENSION = ('docx', 'xlsx', 'pptx')",
        ))

        result = switch_settings(source)

        self.assertIn("ENABLE_ONLYOFFICE = True", result)
        self.assertIn("ENABLE_OFFICE_WEB_APP = False", result)
        self.assertIn("ONLYOFFICE_FILE_EXTENSION = ('docx', 'doc', 'ppt', 'xls', 'odt')", result)
        self.assertIn("ONLYOFFICE_EDIT_FILE_EXTENSION = ('docx', 'odt', 'odp')", result)
        self.assertIn("OFFICE_WEB_APP_FILE_EXTENSION = ('xlsx', 'pptx')", result)
        self.assertIn("OFFICE_WEB_APP_EDIT_FILE_EXTENSION = ('xlsx', 'pptx')", result)

    def test_route_switch_fails_closed_when_a_setting_is_ambiguous(self):
        with self.assertRaises(ValueError):
            switch_settings("ENABLE_OFFICE_WEB_APP = True\nENABLE_OFFICE_WEB_APP = True")

    def test_route_switch_is_inert_without_explicit_disposable_lab_opt_in(self):
        with tempfile.TemporaryDirectory() as tmp:
            settings = Path(tmp) / "seahub_settings.py"
            settings.write_text("unchanged")
            for argv in (["switch_docx_route.py"],
                         ["switch_docx_route.py", "--apply-disposable-lab"]):
                with self.subTest(argv=argv), \
                     patch.object(route_switch, "SETTINGS", settings), \
                     patch.object(sys, "argv", argv), \
                     patch.dict(os.environ, {}, clear=True):
                    with self.assertRaises(SystemExit):
                        route_switch.main()
            self.assertEqual(settings.read_text(), "unchanged")


if __name__ == "__main__":
    unittest.main()
