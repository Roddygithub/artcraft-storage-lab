#!/usr/bin/env python3
"""Check the GR-056 GridCraft bundle inventory and exact build provenance."""

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
MANIFEST = HERE / "hash-inventory.json"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    data = json.loads(MANIFEST.read_text())
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--static-root", type=Path,
                        default=Path(data["candidate_root"]).parent,
                        help="parent directory containing gridcraft/")
    parser.add_argument("--source-root", type=Path,
                        default=Path(data["source_root"]),
                        help="detached, patched GridCraft source checkout")
    args = parser.parse_args()
    bundle = args.static_root.resolve() / "gridcraft"
    source = args.source_root.resolve()
    expected = {entry["path"]: entry for entry in data["files"]}
    actual = {path.relative_to(bundle).as_posix()
              for path in bundle.rglob("*")
              if path.is_file() and path.name != ".trunk-lock"}
    if actual != set(expected):
        raise SystemExit(f"FAIL: candidate file set differs: {sorted(actual)}")
    for relative, entry in expected.items():
        path = bundle / relative
        if path.stat().st_size != entry["size_bytes"] or sha256(path) != entry["sha256"]:
            raise SystemExit(f"FAIL: size/hash mismatch: {path}")
    index = (bundle / "index.html").read_text()
    for relative in data["index_references"]:
        if relative not in index or relative not in expected:
            raise SystemExit(f"FAIL: index reference missing/unmanifested: {relative}")

    commit = subprocess.check_output(
        ["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
    if commit != data["source_commit"]:
        raise SystemExit(f"FAIL: source HEAD {commit} != {data['source_commit']}")
    patch = ROOT / data["patch_path"]
    if sha256(patch) != data["patch_sha256"]:
        raise SystemExit(f"FAIL: stored patch hash mismatch: {patch}")
    subprocess.run(["git", "-C", str(source), "apply", "--reverse", "--check", str(patch)],
                   check=True, stdout=subprocess.DEVNULL)
    # A successful reverse-apply check only proves that the patch's hunks
    # exist. Require the complete tracked source diff (apart from the declared
    # build overlay) to be exactly the pinned patch, and reject staged or
    # untracked additions that would otherwise evade that comparison.
    subprocess.run(["git", "-C", str(source), "diff", "--cached", "--quiet"],
                   check=True, stdout=subprocess.DEVNULL)
    untracked = subprocess.check_output(
        ["git", "-C", str(source), "ls-files", "--others", "--exclude-standard"],
        text=True,
    ).splitlines()
    if untracked:
        raise SystemExit(f"FAIL: untracked source files present: {untracked}")
    source_diff = subprocess.check_output(
        ["git", "-C", str(source), "diff", "--binary", "HEAD", "--", ".",
         f":!{data['overlay_path']}"],
    )
    diff_hash = hashlib.sha256(source_diff).hexdigest()
    if diff_hash != data["patch_sha256"]:
        raise SystemExit(
            f"FAIL: complete source diff hash {diff_hash} != pinned patch hash "
            f"{data['patch_sha256']}"
        )
    rev = data["transport_revision"]
    manifest = (source / "Cargo.toml").read_text()
    lock = (source / "Cargo.lock").read_text()
    manifest_pin = re.search(
        rf'craft-platform\s*=\s*\{{[^}}]*rev\s*=\s*"{re.escape(rev)}"',
        manifest,
    )
    lock_pin = (
        f"source = \"git+https://github.com/Roddygithub/artcraft-storage-lab.git?rev={rev}#{rev}\""
    )
    if not manifest_pin or lock_pin not in lock:
        raise SystemExit("FAIL: Cargo manifest/lock transport revision mismatch")
    overlay = source / data["overlay_path"]
    if sha256(overlay) != data["overlay_sha256"]:
        raise SystemExit(f"FAIL: build overlay digest mismatch: {overlay}")

    total = sum(entry["size_bytes"] for entry in data["files"])
    print(f"PASS: {len(expected)} GridCraft assets match paths, sizes and SHA-256 ({total} bytes)")
    print("PASS: index references, source commit, stored patch, transport pins and overlay digest match")


if __name__ == "__main__":
    main()
