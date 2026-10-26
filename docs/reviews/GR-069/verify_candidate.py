#!/usr/bin/env python3
"""Verify the exact FigCraft GR-048 build in staged and active roots."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
REPO=Path(__file__).resolve().parents[3]
MANIFEST=REPO/'docs/reviews/GR-069/candidate-inventory.json'
def sha(p:Path)->str:
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest()
def main()->int:
 d=json.loads(MANIFEST.read_text()); roots=[Path(d[k]) for k in ('source_root','staged_root','active_root')]
 for item in d['files']:
  for label,root in zip(('source','staged','active'),roots):
   p=root/item['path']
   if not p.is_file() or p.stat().st_size!=item['size_bytes'] or sha(p)!=item['sha256']:
    raise SystemExit(f'FAIL: {label} asset mismatch: {item["path"]}')
 print(f"PASS: {len(d['files'])} FigCraft assets; {sum(x['size_bytes'] for x in d['files'])} bytes; source, staged and active hashes match")
 return 0
if __name__=='__main__': raise SystemExit(main())
