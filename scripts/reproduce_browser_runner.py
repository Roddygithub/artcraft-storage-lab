#!/usr/bin/env python3
"""Reproduce the deployed browser runner from the repo version.

The deployed copy has a STATIC path modification applied via sed.
This script reproduces that transformation deterministically.
"""

import hashlib
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
    # Read repo version
    repo_content = REPO_RUNNER.read_text()
    repo_hash = sha256(REPO_RUNNER)
    
    # Apply transformation
    transformed = transform(repo_content)
    transformed_hash = hashlib.sha256(transformed.encode()).hexdigest()
    
    # Read deployed version
    deployed_hash = sha256(DEPLOYED_RUNNER)
    
    print(f"Repo version SHA256:     {repo_hash}")
    print(f"Transformed SHA256:      {transformed_hash}")
    print(f"Deployed version SHA256: {deployed_hash}")
    print(f"Transform matches deployed: {transformed_hash == deployed_hash}")
    
    if transformed_hash != deployed_hash:
        print("ERROR: Transformation does not match deployed version!", file=sys.stderr)
        return 1
    
    # Also verify the sanitizer
    sanitizer_repo = Path("scripts/sanitize-browser-evidence.py")
    sanitizer_hash = sha256(sanitizer_repo)
    provenance = Path("lab/real-seafile/results/2026-11-17-proxmox-isolated/provenance.json")
    import json
    with open(provenance) as f:
        prov = json.load(f)
    expected_sanitizer = prov.get("sanitizer_sha256", "")
    print(f"\nSanitizer repo SHA256:   {sanitizer_hash}")
    print(f"Expected in provenance:  {expected_sanitizer}")
    print(f"Sanitizer matches:       {sanitizer_hash == expected_sanitizer}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
