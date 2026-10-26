#!/usr/bin/env python3
"""Verify GR-064 DeckCraft candidate files and index integrity references."""

import argparse
import base64
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "hash-inventory.json"


class IntegrityReferences(HTMLParser):
    def __init__(self):
        super().__init__()
        self.references = {}

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        path = attributes.get("href")
        integrity = attributes.get("integrity")
        if path and integrity:
            path = path.removeprefix("./")
            if path in self.references:
                raise ValueError(f"duplicate href/integrity entry: {path}")
            self.references[path] = integrity


def validate_integrity_references(index, index_references, integrity_entries):
    parser = IntegrityReferences()
    parser.feed(index)
    expected = {item["path"]: item["value"] for item in integrity_entries}
    if len(expected) != len(integrity_entries):
        raise ValueError("duplicate SRI path in manifest")
    if len(set(index_references)) != len(index_references):
        raise ValueError("duplicate index reference in manifest")
    if parser.references != expected:
        raise ValueError("index href/integrity associations differ from the manifest")
    if set(expected) != set(index_references):
        raise ValueError("every index reference must have exactly one recorded SRI")
    return expected


def main():
    data = json.loads(MANIFEST.read_text())
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--static-root", type=Path, default=Path(data["candidate_parent"]),
                        help="parent directory containing deckcraft/")
    args = parser.parse_args()
    root = args.static_root.resolve() / "deckcraft"
    expected = {entry["path"]: entry for entry in data["files"]}
    actual = {p.relative_to(root).as_posix() for p in root.rglob("*")
              if p.is_file() and p.name != ".trunk-lock"}
    if actual != set(expected):
        raise SystemExit(f"FAIL: candidate file set differs: {sorted(actual)}")
    for relative, entry in expected.items():
        payload = (root / relative).read_bytes()
        if len(payload) != entry["size_bytes"] or hashlib.sha256(payload).hexdigest() != entry["sha256"]:
            raise SystemExit(f"FAIL: candidate size/hash mismatch: {relative}")

    index = (root / "index.html").read_text()
    for relative in data["index_references"]:
        if relative not in index or relative not in expected:
            raise SystemExit(f"FAIL: missing or unmanifested index reference: {relative}")
    integrity_entries = data["index_integrity"]
    index_references = data["index_references"]
    try:
        expected_integrity = validate_integrity_references(index, index_references, integrity_entries)
    except ValueError as error:
        raise SystemExit(f"FAIL: {error}") from error
    for relative, integrity in expected_integrity.items():
        algorithm, encoded = integrity.split("-", 1)
        payload = (root / relative).read_bytes()
        candidate = base64.b64encode(hashlib.new(algorithm, payload).digest()).decode()
        if candidate != encoded:
            raise SystemExit(f"FAIL: SRI digest does not match its referenced file: {relative}")

    total = sum(entry["size_bytes"] for entry in data["files"])
    print(f"PASS: {len(expected)} DeckCraft files match the recorded paths, sizes and SHA-256 ({total} bytes)")
    print("PASS: each index href maps to its manifest path and matching SRI digest")


if __name__ == "__main__":
    main()
