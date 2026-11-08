#!/usr/bin/env python3
"""Test experimental Craft ports in the lab.

Usage (from lab directory):
    python3 test_experimental.py deckcraft
    python3 test_experimental.py --all

Runs the browser slice for the specified experimental editor.
Requires the bundle to be already wired via wire-built-bundle.sh.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def run_browser_slice(editor: str, fixture: str = "") -> int:
    """Run the browser slice for a specific editor."""
    env = os.environ.copy()
    env.update({
        "BROWSER_ONLY_EDITOR": editor,
        "BROWSER_SCRIPT": "run_browser.py",
    })
    if fixture:
        env["BROWSER_WORDCRAFT_FIXTURE"] = fixture

    # Use the same local.py runner but with experimental config
    cmd = [
        sys.executable, "local.py",
        "--run-dir", f"/tmp/exp-{editor}-{os.getpid()}",
        "--static", str(Path(__file__).parent / "static"),
        "--manifest", str(Path(__file__).parent / "static-sha256.json"),
        "--editor", editor,
    ]
    if fixture:
        cmd.extend(["--wordcraft-fixture", fixture])

    print(f"Running browser slice for {editor}...")
    result = subprocess.run(cmd, env=env, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout[-2000:])
    if result.stderr:
        print(result.stderr[-2000:], file=sys.stderr)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description="Test experimental Craft ports")
    parser.add_argument("editor", nargs="?", choices=[
        "deckcraft", "soundcraft", "photocraft", "designcraft", "svgstub"
    ], help="Editor to test (default: all)")
    parser.add_argument("--all", action="store_true", help="Test all experimental editors")
    parser.add_argument("--fixture", default="", help="Fixture name for WordCraft-style editors")
    args = parser.parse_args()

    editors = []
    if args.all:
        editors = ["deckcraft", "soundcraft", "photocraft", "designcraft", "svgstub"]
    elif args.editor:
        editors = [args.editor]
    else:
        parser.error("Specify an editor or --all")

    results = {}
    for ed in editors:
        print(f"\n{'='*60}")
        print(f"Testing experimental editor: {ed}")
        print(f"{'='*60}")
        code = run_browser_slice(ed, args.fixture)
        results[ed] = "PASS" if code == 0 else "FAIL"
        print(f"Result: {results[ed]}")

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for ed, res in results.items():
        print(f"  {ed:15s} {res}")

    failed = [ed for ed, res in results.items() if res == "FAIL"]
    if failed:
        print(f"\nFAILED: {', '.join(failed)}")
        sys.exit(1)
    else:
        print("\nAll passed.")
        sys.exit(0)


if __name__ == "__main__":
    main()