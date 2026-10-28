#!/usr/bin/env python3
"""Inspect captured synthetic native bytes; never uploads a file."""
import hashlib,json,pathlib,sys,zipfile
p=pathlib.Path(sys.argv[1])
with zipfile.ZipFile(p) as z:m=json.loads(z.read('manifest.json'))
d=m['document']
assert d['id']==82
assert d['size']=={'width':64,'height':64}
assert len(d['layers'])>0, 'UI layer edit absent'
print(json.dumps({'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'documentId':d['id'],'layers':[(l['id'],l['name']) for l in d['layers']]},indent=2))
