#!/usr/bin/env python3
"""Run the retained GR-058 workflow against the GR-082 release, never deployed assets."""
import hashlib, json
from run_qualification import ROOT, CHECKS, BUNDLE, run
TEST = ROOT / 'tests/test_vectorcraft_gr082_release.py'
EVIDENCE = ROOT / 'docs/reviews/GR-082/runtime/vectorcraft'
UV = '/home/roddy/.local/share/mise/installs/uv/0.13.3/uv-x86_64-unknown-linux-gnu/uv'
if __name__ == '__main__':
    inputs = [TEST, ROOT/'tests/test_gr012_svg.py', ROOT/'tests/fixtures/synthetic.svg', ROOT/'integration/gateway/hostpage.py', EVIDENCE/'run_qualification.py', EVIDENCE/'run_smoke.py', EVIDENCE/'run_release_retry.py']
    (CHECKS/'vectorcraft-test-inputs.json').write_text(json.dumps({str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},indent=2)+'\n')
    run([UV,'run','--offline','--with','playwright','--python','3.14','--','python','-u',str(TEST),'--static-root',str(BUNDLE.parent),'--screenshot',str(EVIDENCE/'edited.png'),'--evidence-dir',str(EVIDENCE)],ROOT,'browser-smoke-r2',timeout=240)
