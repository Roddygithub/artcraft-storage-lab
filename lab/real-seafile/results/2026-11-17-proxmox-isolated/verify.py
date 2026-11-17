"""Verify the isolated Proxmox deployment evidence: assertion counts, retained
proof in detail fields (version growth+creator, fresh browser context), and
byte equality of relayed vs read-back artifacts.

Also verifies:
- SHA256SUMS integrity
- All expected artifacts exist
- No contradictions between counters and individual assertions
- Provenance coherence when source files are available
- Hardware and session-expiry evidence structure
"""
import hashlib
import json
import re
import sys
from pathlib import Path

root = Path(__file__).resolve().parent

# Expected assertion counts per editor
expected = {"wordcraft": 24, "gridcraft": 27, "deckcraft": 15}

# Patterns for proof detection
VERSION = re.compile(r"history \d+->\d+ grew=True creator_is_opener=True")
FRESH = re.compile(r"new_browser_context=True url_has_login_redirect=False")

# Expected artifact pairs for byte-level verification
PAIRS = {
    "wordcraft": ("wordcraft-original.docx", "wordcraft-first-relay.docx", "wordcraft-first-readback.docx"),
    "gridcraft": ("gridcraft-original.xlsx", "gridcraft-first-relay.xlsx", "gridcraft-first-readback.xlsx"),
    "deckcraft": ("pptx-original.pptx", "pptx-first-relay.pptx", "pptx-readback.pptx"),
}

# Required artifact files (must exist)
REQUIRED_ARTIFACTS = [
    "wordcraft-browser.json", "gridcraft-browser.json", "deckcraft-browser.json",
    "hardware.json", "session-expiry.json",
    "provenance.json", "verify.py",
    "wordcraft-original.docx", "wordcraft-first-relay.docx", "wordcraft-first-readback.docx",
    "wordcraft-second-readback.docx", "wordcraft-opened.png", "wordcraft-saved.png",
    "gridcraft-original.xlsx", "gridcraft-first-relay.xlsx", "gridcraft-first-readback.xlsx",
    "gridcraft-second-readback.xlsx", "gridcraft-opened.png", "gridcraft-saved.png",
    "pptx-original.pptx", "pptx-first-relay.pptx", "pptx-readback.pptx",
    "deckcraft-opened.png", "pptx-saved.png",
    "hw-wordcraft-opened.png", "hw-wordcraft-saved.png", "hw-reader-readonly.png",
    "SHA256SUMS",
]

def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def load_json(path: Path) -> dict:
    """Load JSON with validation."""
    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {path}")
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {path}: {e}")

def check_file_exists(path: Path, name: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Required artifact missing: {name} ({path})")
    if path.stat().st_size == 0:
        raise ValueError(f"Required artifact is empty: {name} ({path})")

def verify_editor_evidence(editor: str, n: int, d: dict) -> None:
    """Verify a single editor's browser evidence."""
    # 1. Counters match and no failures
    passed = d.get("passed", -1)
    failed = d.get("failed", -1)
    assertion_count = d.get("assertion_count", -1)
    checks = d.get("checks", [])
    
    if passed != n:
        raise AssertionError(f"{editor}: passed={passed} != expected={n}")
    if failed != 0:
        raise AssertionError(f"{editor}: failed={failed} != 0")
    if assertion_count != n:
        raise AssertionError(f"{editor}: assertion_count={assertion_count} != expected={n}")
    if len(checks) != n:
        raise AssertionError(f"{editor}: checks length={len(checks)} != expected={n}")
    
    # 2. Every check has ok=true
    for i, c in enumerate(checks):
        if not c.get("ok", False):
            raise AssertionError(f"{editor}: check {i} ({c.get('name', 'unnamed')}) has ok=false: {c.get('detail', '')}")
    
    # 3. Version-proof checks (identified by detail containing "grew=")
    versioned = [c for c in checks if "grew=" in c.get("detail", "")]
    min_versions = 1 if editor == "deckcraft" else 2
    if len(versioned) < min_versions:
        raise AssertionError(f"{editor}: version-proof checks={len(versioned)} < min={min_versions}")
    for c in versioned:
        if not VERSION.search(c.get("detail", "")):
            raise AssertionError(f"{editor}: version check missing required pattern: {c.get('detail', '')}")
    
    # 4. Fresh-session proof
    fresh = [c for c in checks if FRESH.search(c.get("detail", ""))]
    if not fresh:
        raise AssertionError(f"{editor}: no fresh-session proof found")
    for c in fresh:
        if not FRESH.search(c.get("detail", "")):
            raise AssertionError(f"{editor}: fresh-session check missing required pattern: {c.get('detail', '')}")
    
    # 5. Downloads check
    downloads = [c for c in checks if "did_not_download" in c.get("name", "")]
    if not downloads:
        raise AssertionError(f"{editor}: no did_not_download check found")
    for c in downloads:
        if not c.get("ok", False):
            raise AssertionError(f"{editor}: did_not_download check failed: {c.get('detail', '')}")
    
    # 6. Byte-level verification (relay == readback, original != readback)
    o, r, b = PAIRS[editor]
    if sha(root / r) != sha(root / b):
        raise AssertionError(f"{editor}: relay != readback ({r} vs {b})")
    if sha(root / o) == sha(root / b):
        raise AssertionError(f"{editor}: original == readback ({o} vs {b})")

def verify_hardware_evidence(d: dict) -> None:
    """Verify hardware acceptance evidence structure."""
    checks = d.get("checks", [])
    passed = d.get("passed", 0)
    failed = d.get("failed", 0)
    ok = d.get("ok", False)
    
    # Count actual pass/fail
    actual_passed = sum(1 for c in checks if c.get("ok", False))
    actual_failed = sum(1 for c in checks if not c.get("ok", False))
    
    if actual_passed != passed:
        raise AssertionError(f"hardware: passed counter mismatch: declared={passed} actual={actual_passed}")
    if actual_failed != failed:
        raise AssertionError(f"hardware: failed counter mismatch: declared={failed} actual={actual_failed}")
    if ok and failed > 0:
        raise AssertionError("hardware: ok=true but failed>0")
    
    # Required checks must exist
    required_names = {
        "wayland_session_reachable", "browser_login_headed_real_session",
        "webgl_renderer_reported", "gpu_is_physical_nvidia_not_software",
        "webgpu_adapter_available", "wordcraft_editor_ready_headed",
        "save_creates_version_by_user", "network_outage_save_fails_dirty_kept",
        "network_recovered_save_succeeds",
    }
    found_names = {c.get("name", "") for c in checks}
    missing = required_names - found_names
    if missing:
        raise AssertionError(f"hardware: missing required checks: {missing}")
    
    # Specific validations
    for c in checks:
        name = c.get("name", "")
        if name == "clipboard_editor_to_os":
            # Must be NOT VERIFIED or FAIL, not PASS
            detail = c.get("detail", "")
            if c.get("ok", False) and "NOT VERIFIED" not in detail:
                raise AssertionError(f"hardware: clipboard_editor_to_os marked PASS but detail lacks NOT VERIFIED: {detail}")
        if name == "clipboard_os_to_editor_accepted":
            # Must note canvas limitation
            detail = c.get("detail", "")
            if "canvas" not in detail.lower() and "limitation" not in detail.lower():
                raise AssertionError(f"hardware: clipboard_os_to_editor_accepted missing canvas limitation note: {detail}")

def verify_session_expiry_evidence(d: dict) -> None:
    """Verify session expiry evidence structure."""
    checks = d.get("checks", [])
    passed = d.get("passed", 0)
    failed = d.get("failed", 0)
    ok = d.get("ok", False)
    
    actual_passed = sum(1 for c in checks if c.get("ok", False))
    actual_failed = sum(1 for c in checks if not c.get("ok", False))
    
    if actual_passed != passed:
        raise AssertionError(f"session-expiry: passed counter mismatch: declared={passed} actual={actual_passed}")
    if actual_failed != failed:
        raise AssertionError(f"session-expiry: failed counter mismatch: declared={failed} actual={actual_failed}")
    if ok and failed > 0:
        raise AssertionError("session-expiry: ok=true but failed>0")
    
    required_names = {
        "short_ttl_applied_and_seahub_restarted",
        "editor_opened_with_short_ttl",
        "edit_typed_before_expiry",
        "expired_save_must_not_create_version",
        "reopen_after_expiry_usable",
        "reopen_save_succeeds_creates_version",
        "ttl_restored_and_seahub_restarted",
    }
    found_names = {c.get("name", "") for c in checks}
    missing = required_names - found_names
    if missing:
        raise AssertionError(f"session-expiry: missing required checks: {missing}")
    
    # Verify expired save did not create version
    for c in checks:
        if c.get("name") == "expired_save_must_not_create_version":
            detail = c.get("detail", "")
            if "history 1->1" not in detail:
                raise AssertionError(f"session-expiry: expired_save must show history 1->1: {detail}")
            if "download" not in detail.lower():
                raise AssertionError(f"session-expiry: expired_save must mention download: {detail}")

def verify_provenance(d: dict) -> None:
    """Verify provenance coherence with available source files."""
    # Check browser runner hash matches deployed version
    runner_hash = d.get("browser_runner_sha256", "")
    if runner_hash:
        # The deployed copy is at deploy-proxmox/e2e/run_browser.py
        deployed = Path("/home/roddy/.cache/artcraft-storage-lab/deploy-proxmox/e2e/run_browser.py")
        if deployed.exists():
            actual = sha(deployed)
            if actual != runner_hash:
                raise AssertionError(f"provenance: browser_runner_sha256 mismatch: declared={runner_hash} actual={actual}")
    
    # Check sanitizer hash
    sanitizer_hash = d.get("sanitizer_sha256", "")
    if sanitizer_hash:
        sanitizer = Path("/home/roddy/Projects/artcraft-storage-lab/scripts/sanitize-browser-evidence.py")
        if sanitizer.exists():
            actual = sha(sanitizer)
            if actual != sanitizer_hash:
                raise AssertionError(f"provenance: sanitizer_sha256 mismatch: declared={sanitizer_hash} actual={actual}")

def verify_sha256sums() -> None:
    """Verify SHA256SUMS file integrity."""
    sums_file = root / "SHA256SUMS"
    if not sums_file.exists():
        raise FileNotFoundError("SHA256SUMS file missing")
    
    content = sums_file.read_text().strip()
    if not content:
        raise ValueError("SHA256SUMS is empty")
    
    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) < 2:
            raise ValueError(f"SHA256SUMS malformed line: {line}")
        expected_hash, filename = parts[0], parts[1]
        filepath = root / filename
        if not filepath.exists():
            raise FileNotFoundError(f"SHA256SUMS references missing file: {filename}")
        actual_hash = sha(filepath)
        if actual_hash != expected_hash:
            raise AssertionError(f"SHA256SUMS mismatch for {filename}: expected={expected_hash} actual={actual_hash}")

def verify_all_artifacts_exist() -> None:
    """Verify all required artifacts exist and are non-empty."""
    for artifact in REQUIRED_ARTIFACTS:
        check_file_exists(root / artifact, artifact)

def main() -> int:
    try:
        # 1. Verify all required artifacts exist
        verify_all_artifacts_exist()
        
        # 2. Verify SHA256SUMS integrity
        verify_sha256sums()
        
        # 3. Verify editor evidence
        total = 0
        for editor, n in expected.items():
            d = load_json(root / f"{editor}-browser.json")
            verify_editor_evidence(editor, n, d)
            total += n
        
        # 4. Verify hardware evidence
        hw = load_json(root / "hardware.json")
        verify_hardware_evidence(hw)
        
        # 5. Verify session expiry evidence
        se = load_json(root / "session-expiry.json")
        verify_session_expiry_evidence(se)
        
        # 6. Verify provenance coherence
        prov = load_json(root / "provenance.json")
        verify_provenance(prov)
        
        print(f"PASS: {total}/{sum(expected.values())} assertions with retained proof; "
              f"DOCX/XLSX/PPTX relay==readback; originals differ; no downloads substituted saves")
        print("PASS: hardware evidence structure verified")
        print("PASS: session-expiry evidence structure verified")
        print("PASS: provenance coherence verified")
        print("PASS: SHA256SUMS integrity verified")
        print("PASS: all required artifacts present and non-empty")
        return 0
        
    except (AssertionError, FileNotFoundError, ValueError) as e:
        print(f"FAIL: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())