#!/usr/bin/env python3
"""Verify GR-058 staged VectorCraft candidate membership, bytes, and index links."""

import argparse
import base64
import hashlib
import json
from pathlib import Path
import re

INVENTORY = Path(__file__).with_name("inventory.json")


def main():
    data = json.loads(INVENTORY.read_text())
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--static-root", type=Path, default=Path(data["static_root"]),
                        help="candidate parent static root (defaults to recorded cache path)")
    root = (parser.parse_args().static_root / "vectorcraft").resolve()
    expected = {entry["path"]: entry for entry in data["files"]}
    actual = {p.relative_to(root).as_posix() for p in root.rglob("*")
              if p.is_file() and p.name != ".trunk-lock"}
    if actual != set(expected):
        raise SystemExit(f"FAIL: candidate file set differs: actual={sorted(actual)}")
    for relative, entry in expected.items():
        path = root / relative
        payload = path.read_bytes()
        digest = hashlib.sha256(payload).hexdigest()
        if len(payload) != entry["size_bytes"] or digest != entry["sha256"]:
            raise SystemExit(f"FAIL: size/hash mismatch: {path}")
    index = (root / "index.html").read_text()
    observed_references = sorted(set(re.findall(
        r"\./[^\"'\s<>]+?\.(?:js|wasm|ico|png|ttf|woff2?)", index)))
    if observed_references != data["index_references"]:
        raise SystemExit("FAIL: index references differ from inventory")
    for relative in data["index_references"]:
        if relative not in index or relative.removeprefix("./") not in expected:
            raise SystemExit(f"FAIL: index reference missing or unmanifested: {relative}")
        if not (root / relative.removeprefix("./")).is_file():
            raise SystemExit(f"FAIL: index target does not exist: {relative}")
    tags = re.findall(r"<(?:link|script)\b[^>]*>", index, flags=re.IGNORECASE)
    observed_integrity = []
    for tag in tags:
        target = re.search(r"\b(?:href|src)=['\"]([^'\"]+)['\"]", tag, flags=re.IGNORECASE)
        integrity = re.search(r"\bintegrity=['\"]([^'\"]+)['\"]", tag, flags=re.IGNORECASE)
        if target and integrity:
            observed_integrity.append({"path": target.group(1), "integrity": integrity.group(1)})
    if observed_integrity != data["index_integrity"]:
        raise SystemExit("FAIL: index integrity references differ from inventory")
    for entry in observed_integrity:
        relative = entry["path"].removeprefix("./")
        if relative not in expected:
            raise SystemExit(f"FAIL: integrity target is not manifested: {entry['path']}")
        payload = (root / relative).read_bytes()
        sri = "sha384-" + base64.b64encode(hashlib.sha384(payload).digest()).decode()
        if sri != entry["integrity"]:
            raise SystemExit(f"FAIL: integrity mismatch: {entry['path']}")
    print(f"PASS: {len(expected)} staged VectorCraft files match recorded paths, sizes and SHA-256")
    print(f"PASS: all {len(data['index_references'])} index references resolve to manifested files")
    print(f"PASS: all {len(observed_integrity)} index SHA-384 integrity values match")


if __name__ == "__main__":
    main()
