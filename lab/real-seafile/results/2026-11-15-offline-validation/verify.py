#!/usr/bin/env python3
"""Verify the retained active offline-check summary."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

data = json.loads((HERE / "summary.json").read_text())
assert data["source"] == "4a5ab576da0e0a0f227e672d8ea6258ea90c9acc"
assert data["passed"] == 20 and data["failed"] == 0
assert len(data["checks"]) == 20
assert len({item["name"] for item in data["checks"]}) == 20
assert all(item["exit"] == 0 for item in data["checks"])
print("PASS: 20/20 active offline command groups at source 4a5ab57")
