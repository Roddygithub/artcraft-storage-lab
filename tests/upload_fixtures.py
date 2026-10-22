#!/usr/bin/env python3
"""Upload the synthetic fixtures to a Seafile library, for the integration tests.

    ARTCRAFT_SEAFILE_URL=... ARTCRAFT_SEAFILE_TOKEN=... \\
    python3 tests/upload_fixtures.py <repo_id> [folder] [fixture_dir]

Only synthetic files are uploaded. Never point this at a library that holds
real data.
"""

import os
import sys
import urllib.parse

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "integration"))

from gateway.seafile import Seafile  # noqa: E402


def ensure_folder(seafile, repo_id, folder):
    """Create the folder if it is not there yet. Returns its path."""
    if not folder or folder == "/":
        return "/"
    listing = seafile._json(f"{seafile.base_url}/api2/repos/{repo_id}/dir/?p=/")
    for entry in listing:
        if entry.get("type") == "dir" and entry.get("name") == folder:
            return "/" + folder
    body = urllib.parse.urlencode({"operation": "mkdir"}).encode()
    seafile._request(
        f"{seafile.base_url}/api2/repos/{repo_id}/dir/?p={urllib.parse.quote('/' + folder)}",
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=body,
    )
    return "/" + folder


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(2)
    repo_id = sys.argv[1]
    folder = sys.argv[2] if len(sys.argv) > 2 else "artcraft-lab"
    fixture_dir = sys.argv[3] if len(sys.argv) > 3 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "fixtures"
    )

    seafile = Seafile.from_env()
    target = ensure_folder(seafile, repo_id, folder)
    for name in sorted(os.listdir(fixture_dir)):
        path = os.path.join(fixture_dir, name)
        if not os.path.isfile(path):
            continue
        with open(path, "rb") as handle:
            data = handle.read()
        file_id = seafile.upload_file(repo_id, target, name, data, replace=True)
        print(f"uploaded {name} ({len(data)} bytes) -> id {file_id}")


if __name__ == "__main__":
    main()
