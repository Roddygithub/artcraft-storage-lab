#!/usr/bin/env python3
"""Hash tracked + untracked nonignored source and the archived patch; no credentials."""
import hashlib, pathlib, subprocess, json, sys
source=pathlib.Path('/home/roddy/.cache/artcraft-storage-lab/upstream-refresh-sources/photocraft')
root=pathlib.Path(__file__).resolve().parents[5]
files=subprocess.check_output(['git','ls-files','-z','--cached','--others','--exclude-standard'],cwd=source).decode().split('\0')
rows=[]
for name in sorted(set(filter(None,files))):
 p=source/name
 if p.is_file(): rows.append(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {name}\n')
output=root/'docs/reviews/GR-082/checks'/('photocraft-source-'+sys.argv[1]+'.sha256')
output.write_text(''.join(rows))
print('source HEAD',subprocess.check_output(['git','rev-parse','HEAD'],cwd=source).decode().strip())
print('source manifest',hashlib.sha256(output.read_bytes()).hexdigest(),output)
patch=root/'docs/reviews/GR-082/ports/photocraft-v0.16.0.patch'
print('patch',hashlib.sha256(patch.read_bytes()).hexdigest())
