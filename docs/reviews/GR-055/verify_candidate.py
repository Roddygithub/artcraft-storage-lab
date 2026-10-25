#!/usr/bin/env python3
"""Verify GR-055 staged WordCraft candidate file membership and hashes."""

import argparse
import hashlib
import json
from pathlib import Path

MANIFEST = Path(__file__).with_name("checks") / "hash-inventory.json"


def main():
    data = json.loads(MANIFEST.read_text())
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--static-root",
        type=Path,
        default=Path(data["static_root"]),
        help="candidate parent static root (defaults to recorded cache path)",
    )
    args = parser.parse_args()
    root = args.static_root.resolve() / "wordcraft"
    expected = {entry["path"]: entry for entry in data["files"]}
    actual = {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()
              and p.name != ".trunk-lock"}
    if actual != set(expected):
        raise SystemExit(f"FAIL: candidate file set differs: actual={sorted(actual)}")
    for relative, entry in expected.items():
        path = root / relative
        payload = path.read_bytes()
        digest = hashlib.sha256(payload).hexdigest()
        if len(payload) != entry["size_bytes"] or digest != entry["sha256"]:
            raise SystemExit(f"FAIL: size/hash mismatch: {path}")
    index = (root / "index.html").read_text()
    for relative in data["index_references"]:
        if relative not in index or relative not in expected:
            raise SystemExit(f"FAIL: index reference missing or unmanifested: {relative}")
    print(f"PASS: {len(expected)} staged WordCraft files match recorded paths, sizes and SHA-256")
    print("PASS: all recorded index references are present in the candidate manifest")


if __name__ == "__main__":
    main()
