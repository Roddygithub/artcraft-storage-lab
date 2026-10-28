#!/usr/bin/env python3
"""Rebuild the exact VectorCraft release outside deployment; retain command output."""
import hashlib, json, os, pathlib, subprocess, sys, time
ROOT = pathlib.Path(__file__).resolve().parents[5]
CHECKS = ROOT / 'docs/reviews/GR-082/checks'
SOURCE = pathlib.Path('/home/roddy/.cache/artcraft-storage-lab/upstream-refresh-sources/vectorcraft')
FONTS = SOURCE.parent / 'vectorcraft-craft-fonts'
BUNDLE = SOURCE.parent.parent / 'upstream-refresh-outputs/vectorcraft-v0.17.0-static/vectorcraft'
ENV = dict(os.environ, PATH='/home/roddy/.cargo/bin:/home/roddy/.local/bin:' + os.environ['PATH'], RUSTUP_TOOLCHAIN='1.95.0')

def run(args, cwd, name, timeout=1800, env=ENV):
    path = CHECKS / ('vectorcraft-' + name + '.txt')
    with path.open('w') as log:
        log.write('cwd=' + str(cwd) + '\ncommand=' + json.dumps(args) + '\n'); log.flush()
        start = time.monotonic()
        try:
            result = subprocess.run(args, cwd=cwd, env=env, stdout=log, stderr=subprocess.STDOUT, timeout=timeout)
            code = result.returncode
        except subprocess.TimeoutExpired:
            code = 124
            log.write('\nTIMEOUT: subprocess.run deadline exceeded\n')
        log.write(f'\nexit={code}\nelapsed_seconds={time.monotonic()-start:.3f}\n')
    print(name, code, flush=True)
    if code: sys.exit(code)

if __name__ == '__main__':
    if not FONTS.exists():
        run(['git','clone','https://github.com/storytold/craft-fonts.git',str(FONTS)], SOURCE.parent, 'fonts-clone')
    run(['git','checkout','--detach','a71c20e30af613287c504f7e685ca8fad77752bc'], FONTS, 'fonts-checkout')
    run(['git','rev-parse','HEAD','v0.17.0'], SOURCE, 'source-identity')
    run(['git','status','--porcelain'], SOURCE, 'source-before')
    for tool in ['rustc','cargo','trunk']:
        run([tool,'--version'], SOURCE, tool+'-version')
    env = dict(ENV, CRAFT_FONTS_DIR=str(FONTS), CRAFT_FONTS_REQUIRED='1')
    run(['trunk','build','--release','--locked','--dist',str(BUNDLE)], SOURCE/'apps/vectorcraft-web', 'release-build-r1', env=env)
    run(['git','status','--porcelain'], SOURCE, 'source-after')
    files = lambda root: {str(p.relative_to(root)): {'size':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(root.rglob('*')) if p.is_file() and p.name != '.trunk-lock'}
    data = {'source_commit':'43313f9451de7ab5b909801006b8881458f2bf04','bundle':str(BUNDLE),'files':files(BUNDLE),'fonts_commit':'a71c20e30af613287c504f7e685ca8fad77752bc','font_inputs':files(FONTS/'fonts')}
    data['source_inputs'] = {p:hashlib.sha256((SOURCE/p).read_bytes()).hexdigest() for p in ['Cargo.lock','Cargo.toml','apps/vectorcraft-web/index.html','.github/workflows/release.yml']}
    (CHECKS/'vectorcraft-bundle-manifest.json').write_text(json.dumps(data,indent=2)+'\n')
