#!/usr/bin/env python3
import os, pathlib, subprocess, tempfile, hashlib
src=pathlib.Path('/home/roddy/.cache/artcraft-storage-lab/upstream-refresh-sources/photocraft')
root=pathlib.Path(__file__).resolve().parents[5]
patch=root/'docs/reviews/GR-082/ports/photocraft-v0.16.0.patch'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=src).decode().strip()=='b1794c6e0608ccfc887213dcf58398977c5cb75e'
index=src/'temp/gr082-qualification.index'
try:
 env=os.environ.copy();env['GIT_INDEX_FILE']=str(index)
 def run(*args):
  print('COMMAND',list(args),flush=True)
  p=subprocess.run(args,cwd=src,env=env,check=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
  print(p.stdout.decode(), 'EXIT',p.returncode,flush=True)
  return p.stdout
 run('git','read-tree','HEAD')
 run('git','apply','--cached','--check',str(patch))
 run('git','apply','--cached',str(patch))
 assert not run('git','diff','--exit-code') # actual worktree equals archived patched index
 run('git','diff','--check','HEAD')
 print('Exact archived patch matches working tree; patch SHA256',hashlib.sha256(patch.read_bytes()).hexdigest())
finally:
 index.unlink(missing_ok=True)
