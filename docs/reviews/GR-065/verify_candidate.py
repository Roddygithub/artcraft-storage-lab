#!/usr/bin/env python3
"""Verify the staged DesignCraft bundle and per-file index SRI."""

import argparse
import base64
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "hash-inventory.json"


class IndexIntegrity(HTMLParser):
    def __init__(self):
        super().__init__()
        self.items = {}

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        href = attributes.get("href")
        integrity = attributes.get("integrity")
        if href and integrity:
            href = href.removeprefix("./")
            if href in self.items:
                raise ValueError(f"duplicate href in index: {href}")
            self.items[href] = integrity


def main():
    manifest = json.loads(MANIFEST.read_text())
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--static-root", type=Path, default=Path(manifest["candidate_parent"]))
    root = cli.parse_args().static_root.resolve() / "designcraft"
    expected = {item["path"]: item for item in manifest["files"]}
    actual = {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}
    if actual != set(expected) or len(actual) != len(expected):
        raise SystemExit(f"FAIL: unexpected DesignCraft file set: {sorted(actual)}")
    for path, item in expected.items():
        payload = (root / path).read_bytes()
        if len(payload) != item["size_bytes"] or hashlib.sha256(payload).hexdigest() != item["sha256"]:
            raise SystemExit(f"FAIL: candidate size/hash mismatch: {path}")

    index = (root / "index.html").read_text()
    index_refs = manifest["index_references"]
    sri_items = manifest["index_integrity"]
    sri_by_path = {item["path"]: item["value"] for item in sri_items}
    if len(index_refs) != len(set(index_refs)) or len(sri_by_path) != len(sri_items):
        raise SystemExit("FAIL: duplicate index or SRI manifest entries")
    parser = IndexIntegrity()
    try:
        parser.feed(index)
    except ValueError as error:
        raise SystemExit(f"FAIL: {error}") from error
    if parser.items != sri_by_path or set(index_refs) != set(sri_by_path):
        raise SystemExit("FAIL: index href/integrity associations differ from the manifest")
    for path, value in sri_by_path.items():
        algorithm, encoded = value.split("-", 1)
        digest = base64.b64encode(hashlib.new(algorithm, (root / path).read_bytes()).digest()).decode()
        if digest != encoded:
            raise SystemExit(f"FAIL: SRI digest does not match referenced file: {path}")
    size = sum(item["size_bytes"] for item in manifest["files"])
    print(f"PASS: {len(expected)} DesignCraft files match size and SHA-256 ({size} bytes)")
    print("PASS: each index href maps to its matching per-file SRI")


if __name__ == "__main__":
    main()
