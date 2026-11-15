import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent
summary = json.loads((root / "summary.json").read_text())
assert summary["source"] == "123d2a0ca8435e93e37b6d2f31fb73ac016fc5fb"
assert summary["passed"] == 21 and summary["failed"] == 0
assert len(summary["checks"]) == 21 and all(c["exit"] == 0 for c in summary["checks"])
expected_logs = {c["log"] for c in summary["checks"]}
assert all(Path(n).name == n and n.endswith(".log") for n in expected_logs)
assert expected_logs == {p.name for p in root.glob("*.log")}
entries = set()
for line in (root / "SHA256SUMS").read_text().splitlines():
    digest, name = line.split("  ", 1)
    path = Path(name)
    assert not path.is_absolute() and ".." not in path.parts and name not in entries
    target = root / path
    assert target.is_file() and not target.is_symlink()
    assert hashlib.sha256(target.read_bytes()).hexdigest() == digest
    entries.add(name)
actual = {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file() and p.name != "SHA256SUMS"}
assert entries == actual
print("PASS: offline validation 21/21; exact logs, path-safe complete manifest, and hashes")
