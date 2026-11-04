#!/usr/bin/env python3
"""Route DOCX to ONLYOFFICE in the disposable fidelity-comparison Seahub."""
from pathlib import Path
import os
import sys


SETTINGS = Path("/shared/seafile/conf/seahub_settings.py")
REPLACEMENTS = (
    # Seahub may prepare a WOPI error for an unlisted extension while WOPI remains enabled,
    # then carry that error into the OnlyOffice page. Disable WOPI only for this isolated
    # comparison variant; ONLYOFFICE remains enabled below.
    ("ENABLE_OFFICE_WEB_APP = True", "ENABLE_OFFICE_WEB_APP = False"),
    ("ONLYOFFICE_FILE_EXTENSION = ('doc', 'ppt', 'xls',", "ONLYOFFICE_FILE_EXTENSION = ('docx', 'doc', 'ppt', 'xls',"),
    ("ONLYOFFICE_EDIT_FILE_EXTENSION = ('odt',", "ONLYOFFICE_EDIT_FILE_EXTENSION = ('docx', 'odt',"),
    ("OFFICE_WEB_APP_FILE_EXTENSION = ('docx', 'xlsx'", "OFFICE_WEB_APP_FILE_EXTENSION = ('xlsx'"),
    ("OFFICE_WEB_APP_EDIT_FILE_EXTENSION = ('docx', 'xlsx'", "OFFICE_WEB_APP_EDIT_FILE_EXTENSION = ('xlsx'"),
)


def switch_settings(source: str) -> str:
    for old, new in REPLACEMENTS:
        if source.count(old) != 1:
            raise ValueError("expected exactly one disposable Seahub setting to replace")
        source = source.replace(old, new, 1)
    return source


def main() -> None:
    if len(sys.argv) == 2 and sys.argv[1] == "--check":
        source = sys.stdin.read()
        sys.stdout.write(switch_settings(source))
        return
    if len(sys.argv) != 2 or sys.argv[1] != "--apply-disposable-lab":
        raise SystemExit("use --check or explicitly opt into the disposable lab")
    if os.environ.get("ARTCRAFT_DISPOSABLE_SEAFILE") != "1":
        raise SystemExit("refusing to write without ARTCRAFT_DISPOSABLE_SEAFILE=1")
    source = SETTINGS.read_text()
    SETTINGS.write_text(switch_settings(source))


if __name__ == "__main__":
    main()
