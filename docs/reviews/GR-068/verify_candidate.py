#!/usr/bin/env python3
"""Verify the active PdfCraft Web assets against the GR-057 candidate."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
REPO=Path(__file__).resolve().parents[3]
MANIFEST=REPO/'docs/reviews/GR-068/candidate-inventory.json'
def digest(p:Path)->str:
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''): h.update(block)
 return h.hexdigest()
def main()->int:
 d=json.loads(MANIFEST.read_text()); src=Path(d['candidate_root']); dst=Path(d['active_static_root'])
 for x in d['files']:
  for root,label in ((src,'candidate'),(dst,'active')):
   p=root/x['path']
   if not p.is_file() or p.stat().st_size!=x['size_bytes'] or digest(p)!=x['sha256']:
    raise SystemExit(f'FAIL: {label} mismatch: {x["path"]}')
 print(f"PASS: {len(d['files'])} PdfCraft assets; {sum(x['size_bytes'] for x in d['files'])} bytes; candidate and active hashes match")
 return 0
if __name__=='__main__': raise SystemExit(main())
