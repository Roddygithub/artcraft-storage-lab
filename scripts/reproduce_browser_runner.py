#!/usr/bin/env python3
"""Reproduce the deployed browser runner from the repo version.

The deployed copy has a STATIC path modification applied via sed.
This script reproduces that transformation deterministically.

Usage:
  python3 scripts/reproduce_browser_runner.py
"""

import hashlib
import json
import sys
from pathlib import Path

REPO_RUNNER = Path("lab/real-seafile/run_browser.py")
DEPLOYED_RUNNER = Path("/home/roddy/.cache/artcraft-storage-lab/deploy-proxmox/e2e/run_browser.py")

# The transformation: replace the STATIC path
STATIC_REPO = 'STATIC = "/app/lab/real-seafile/static"'
STATIC_DEPLOYED = 'STATIC = "/home/roddy/.cache/artcraft-storage-lab/pptx-candidate-20261108/static"'

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def transform(content: str) -> str:
    """Apply the STATIC path transformation."""
    return content.replace(STATIC_REPO, STATIC_DEPLOYED)

def main():
    # 1. Verify repo version hash
    if not REPO_RUNNER.exists():
        print(f"ERROR: Repo runner not found at {REPO_RUNNER}", file=sys.stderr)
        return 1
    repo_content = REPO_RUNNER.read_text()
    repo_hash = sha256(REPO_RUNNER)
    expected_repo_hash = "6aaf9de837d3fb129754ccaffe219a7ed83c448724cc97e0b3284f7bb3d27eb2"
    if repo_hash != expected_repo_hash:
        print(f"ERROR: Repo runner hash mismatch! Expected {expected_repo_hash}, got {repo_hash}", file=sys.stderr)
        return 1
    print(f"Repo version SHA256:     {repo_hash} (matches expected)")

    # 2. Apply transformation and verify it produces the expected hash
    transformed = transform(repo_content)
    transformed_hash = hashlib.sha256(transformed.encode()).hexdigest()
    expected_deployed_hash = "fbb85c91b9f64a9e55e9b09402d16f53b8784c1b72784911bfe4f0e1540c9b64"
    if transformed_hash != expected_deployed_hash:
        print(f"ERROR: Transformation hash mismatch! Expected {expected_deployed_hash}, got {transformed_hash}", file=sys.stderr)
        return 1
    print(f"Transformed SHA256:      {transformed_hash} (matches expected deployed hash)")

    # 3. Verify deployed copy exists and matches (if available)
    deployed_hash = None
    if DEPLOYED_RUNNER.exists():
        deployed_hash = sha256(DEPLOYED_RUNNER)
        if deployed_hash != expected_deployed_hash:
            print(f"ERROR: Deployed copy hash mismatch! Expected {expected_deployed_hash}, got {deployed_hash}", file=sys.stderr)
            return 1
        print(f"Deployed version SHA256: {deployed_hash} (matches)")
    else:
        print(f"Deployed copy not found at {DEPLOYED_RUNNER} (skipped in CI)")

    # 4. Verify sanitizer
    sanitizer_repo = Path("scripts/sanitize-browser-evidence.py")
    if not sanitizer_repo.exists():
        print(f"ERROR: Sanitizer not found at {sanitizer_repo}", file=sys.stderr)
        return 1
    sanitizer_hash = sha256(sanitizer_repo)
    expected_sanitizer_hash = "f61186d8f6acfcc458d7677800658a1f59d626cc9df19b22af999771c1312e75"
    if sanitizer_hash != expected_sanitizer_hash:
        print(f"ERROR: Sanitizer hash mismatch! Expected {expected_sanitizer_hash}, got {sanitizer_hash}", file=sys.stderr)
        return 1
    print(f"Sanitizer repo SHA256:   {sanitizer_hash} (matches expected)")

    # 5. Verify provenance.json has correct hashes
    provenance_path = Path("lab/real-seafile/results/2026-11-17-proxmox-isolated/provenance.json")
    if provenance_path.exists():
        with open(provenance_path) as f:
            prov = json.load(f)
        if prov.get("browser_runner_sha256") != expected_deployed_hash:
            print(f"ERROR: provenance.json browser_runner_sha256 mismatch!", file=sys.stderr)
            return 1
        if prov.get("sanitizer_sha256") != expected_sanitizer_hash:
            print(f"ERROR: provenance.json sanitizer_sha256 mismatch!", file=sys.stderr)
            return 1
        if prov.get("browser_runner_repo_sha256") != expected_repo_hash:
            print(f"ERROR: provenance.json browser_runner_repo_sha256 mismatch!", file=sys.stderr)
            return 1
        print("Provenance.json hashes:  OK")
    else:
        print("WARNING: provenance.json not found", file=sys.stderr)

    print("\n✅ All provenance checks passed!")
    return 0


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == "__main__":
    sys.exit(main())