#!/usr/bin/env python3
"""Verify the staged FilmCraft bundle and its local static-root copy."""

import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "hash-inventory.json"


def main():
    manifest = json.loads(MANIFEST.read_text())
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--static-root", type=Path, default=Path(manifest["candidate_parent"]))
    root = cli.parse_args().static_root.resolve() / "filmcraft"
    expected = {item["path"]: item for item in manifest["files"]}
    actual = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    if actual != set(expected) or len(actual) != len(expected):
        raise SystemExit(f"FAIL: unexpected FilmCraft file set: {sorted(actual)}")
    for name, item in expected.items():
        data = (root / name).read_bytes()
        if len(data) != item["size_bytes"] or hashlib.sha256(data).hexdigest() != item["sha256"]:
            raise SystemExit(f"FAIL: size/hash mismatch: {name}")
    html = (root / "index.html").read_text()
    wasm = (root / "filmcraft_web_bg.wasm").read_bytes()
    for reference in manifest["index_references"]:
        if reference not in html:
            raise SystemExit(f"FAIL: index reference missing: {reference}")
    for reference in manifest["runtime_references"]:
        if reference.encode() not in wasm:
            raise SystemExit(f"FAIL: runtime reference missing: {reference}")
    print(f"PASS: {len(expected)} FilmCraft files match size and SHA-256 ({sum(i['size_bytes'] for i in expected.values())} bytes)")
    print("PASS: index and runtime references are present")


if __name__ == "__main__":
    main()
