#!/usr/bin/env python3
"""Read-only check of the GR-036 synthetic Seafile file and version history."""

import argparse
import hashlib
import io
import json
import os
import urllib.parse
import urllib.request
import zipfile


def request(base, path, token):
    headers = {"Authorization": "Token " + token} if token else {}
    req = urllib.request.Request(base.rstrip("/") + path, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as response:
        return response.status, response.read()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("repo_id")
    parser.add_argument("path")
    args = parser.parse_args()
    base = os.environ["ARTCRAFT_SEAFILE_URL"]
    token = os.environ["ARTCRAFT_SEAFILE_TOKEN"]
    encoded_path = urllib.parse.quote(args.path)

    _, history_body = request(
        base,
        f"/api2/repos/{args.repo_id}/file/history/?p={encoded_path}",
        token,
    )
    history = json.loads(history_body)["commits"]
    _, detail_body = request(
        base,
        f"/api2/repos/{args.repo_id}/file/detail/?p={encoded_path}",
        token,
    )
    detail = json.loads(detail_body)
    _, link_body = request(
        base,
        f"/api2/repos/{args.repo_id}/file/?p={encoded_path}",
        token,
    )
    download_url = json.loads(link_body)
    try:
        with urllib.request.urlopen(download_url, timeout=20) as response:
            data = response.read()
    except Exception:
        # The file-server URL can carry a short-lived capability in its query.
        raise SystemExit("Seafile content readback failed; download URL redacted") from None

    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        manifest = archive.read("manifest.json")
    result = {
        "history_count": len(history),
        "latest_commit_id": history[0]["id"],
        "latest_history_file_id": history[0]["rev_file_id"],
        "detail_file_id": detail["id"],
        "size": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "manifest_contains_layer_1": b"Layer 1" in manifest,
    }
    checks = (
        result["history_count"] >= 2
        and result["latest_history_file_id"] == result["detail_file_id"]
        and result["size"] == 4984
        and result["sha256"]
        == "92e93c2b993b7de073a2c870aba522d7f9112647d9d1181d2b8592df665936b3"
        and result["manifest_contains_layer_1"]
    )
    print(json.dumps({"checks_pass": checks, **result}, sort_keys=True))
    if not checks:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
