#!/usr/bin/env python3
"""Verify the retained active offline-check summary."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

data = json.loads((HERE / "summary.json").read_text())
assert data["source"] == "be51c3b577fda9834de4364a35d0784d28f62492"
assert data["passed"] == 20 and data["failed"] == 0
assert len(data["checks"]) == 20
assert len({item["name"] for item in data["checks"]}) == 20
assert all(item["exit"] == 0 for item in data["checks"])
print("PASS: 20/20 active offline command groups at source be51c3b")
