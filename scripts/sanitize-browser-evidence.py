#!/usr/bin/env python3
"""Sanitize raw ArtCraft browser evidence for publication.

The runner records, for every assertion, a `detail` string holding what it
actually observed (history length before/after, whether the newest Seafile
version is attributed to the opening account, captured byte lengths, host
status text). An earlier evidence drop stripped `detail` along with the
per-run identifiers, which turned checkable claims back into bare booleans.

This script keeps `detail` and redacts only the identifiers that must not be
published: synthetic accounts, repository/file/version ids (UUID and hex),
access tokens and URL query strings. It fails closed: if any forbidden
pattern survives redaction, it exits nonzero instead of writing the file.

Usage:
    python3 scripts/sanitize-browser-evidence.py RAW.json OUT.json [--editor NAME]
    python3 scripts/sanitize-browser-evidence.py --check OUT.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys

EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+")
UUID = re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b")
HEX_ID = re.compile(r"\b[0-9a-f]{32,64}\b")
QUERY = re.compile(r"\?[^?<\s'\"<>)]+")
TOKEN = re.compile(r"(access_token=)[^&\s'\"<>)]+")
# Patterns that must never appear in published evidence.
FORBIDDEN = (EMAIL, UUID, HEX_ID)


def redact(text: str) -> str:
    text = TOKEN.sub(r"\1<redacted>", text)
    text = QUERY.sub("?<query>", text)
    text = EMAIL.sub("<synthetic-account>", text)
    text = UUID.sub("<id>", text)
    text = HEX_ID.sub("<id>", text)
    return text


def sanitize(raw: dict, editor: str | None = None) -> dict:
    checks = [
        {
            "name": str(c["name"]),
            "ok": bool(c["ok"]),
            "detail": redact(str(c.get("detail", ""))),
        }
        for c in raw["checks"]
    ]
    payload = {
        "assertion_count": len(checks),
        "passed": sum(1 for c in checks if c["ok"]),
        "failed": sum(1 for c in checks if not c["ok"]),
        "checks": checks,
    }
    if editor:
        payload = {"editor": editor, **payload}
    return payload


def leaks(payload: dict) -> list[str]:
    text = json.dumps(payload)
    found = []
    for pattern in FORBIDDEN:
        for match in pattern.finditer(text):
            found.append(match.group(0))
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", help="raw browser.json to sanitize")
    parser.add_argument("output", nargs="?", help="sanitized JSON to write")
    parser.add_argument("--editor", help="editor name to record (default: inferred from output name)")
    parser.add_argument("--check", metavar="PATH", help="only verify an existing file is clean")
    args = parser.parse_args()

    if args.check:
        payload = json.loads(open(args.check, encoding="utf-8").read())
        found = leaks(payload)
        if found:
            print(f"LEAK in {args.check}: {sorted(set(found))[:5]}", file=sys.stderr)
            return 1
        print(f"clean: {args.check}")
        return 0

    if not args.input or not args.output:
        parser.error("input and output are required unless --check is used")

    editor = args.editor
    if editor is None and args.output.endswith("-browser.json"):
        editor = args.output.rsplit("/", 1)[-1][: -len("-browser.json")]
    raw = json.loads(open(args.input, encoding="utf-8").read())
    if "checks" not in raw:
        parser.error(f"{args.input} has no 'checks' array")
    payload = sanitize(raw, editor)
    found = leaks(payload)
    if found:
        print(f"refusing to write {args.output}: unredacted {sorted(set(found))[:5]}", file=sys.stderr)
        return 1
    with open(args.output, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=1)
        fh.write("\n")
    print(f"{args.output}: {payload['passed']}/{payload['assertion_count']} with detail retained")
    return 0


if __name__ == "__main__":
    sys.exit(main())
