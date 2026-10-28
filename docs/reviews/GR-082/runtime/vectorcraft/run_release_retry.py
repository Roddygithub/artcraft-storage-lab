#!/usr/bin/env python3
"""Retry Trunk post-processing using the completed locked Cargo release cache."""
import hashlib, json
from run_qualification import SOURCE, FONTS, BUNDLE, ENV, CHECKS, run
if __name__ == '__main__':
    run(['git','status','--porcelain'],SOURCE,'source-after-r1')
    run(['trunk','build','--release','--locked','--dist',str(BUNDLE)],SOURCE/'apps/vectorcraft-web','release-build-r2',env=dict(ENV,CRAFT_FONTS_DIR=str(FONTS),CRAFT_FONTS_REQUIRED='1'))
    run(['git','status','--porcelain'],SOURCE,'source-after')
    def files(root):
        return {str(p.relative_to(root)):{'size':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(root.rglob('*')) if p.is_file() and p.name != '.trunk-lock'}
    data={'source_commit':'43313f9451de7ab5b909801006b8881458f2bf04','bundle':str(BUNDLE),'files':files(BUNDLE),'fonts_commit':'a71c20e30af613287c504f7e685ca8fad77752bc','font_inputs':files(FONTS/'fonts')}
    data['source_inputs']={p:hashlib.sha256((SOURCE/p).read_bytes()).hexdigest() for p in ['Cargo.lock','Cargo.toml','apps/vectorcraft-web/index.html','.github/workflows/release.yml']}
    (CHECKS/'vectorcraft-bundle-manifest.json').write_text(json.dumps(data,indent=2)+'\n')
