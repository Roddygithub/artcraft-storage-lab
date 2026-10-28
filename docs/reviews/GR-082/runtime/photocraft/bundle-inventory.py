#!/usr/bin/env python3
import hashlib,pathlib,sys
root=pathlib.Path(__file__).resolve().parents[5]
bundle=pathlib.Path('/home/roddy/.cache/artcraft-storage-lab/upstream-refresh-sources/photocraft/dist/web')
assert list(bundle.glob('*.wasm')), 'no actual WASM bundle'
files=sorted(p for p in bundle.rglob('*') if p.is_file())
output=root/'docs/reviews/GR-082/checks'/('photocraft-bundle-'+sys.argv[1]+'.sha256')
output.write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(bundle))+'\n' for p in files))
print(output.read_text());print('manifest',hashlib.sha256(output.read_bytes()).hexdigest())
