#!/usr/bin/env python3
"""Smoke the exact staged PdfCraft Web/WASM build with an in-memory parent."""

import argparse
import hashlib
import http.server
import json
import threading
from pathlib import Path


HOST_HTML = r"""<!doctype html>
<meta charset="utf-8"><title>GR-057 PdfCraft host</title>
<style>body{margin:0;background:#202124;color:white;font:14px sans-serif}header{height:40px;padding:4px 12px;display:flex;gap:12px;align-items:center}iframe{display:block;width:100vw;height:calc(100vh - 48px);border:0}</style>
<header><b>GR-057 in-memory host</b><span id="status">Waiting for PdfCraft…</span></header>
<iframe id="editor" src="index.html?host=parent"></iframe>
<script>
const frame=document.querySelector('#editor');
window.__evidence={ready:0,dirty:[],saves:[],saved:null,reopened:false};
async function openBytes(){
  let bytes;
  if(window.__evidence.saved){bytes=Uint8Array.from(window.__evidence.saved)}
  else{bytes=new Uint8Array(await(await fetch('/synthetic.pdf')).arrayBuffer())}
  frame.contentWindow.postMessage({type:'pdfcraft:open',name:'synthetic.pdf',bytes},location.origin,[bytes.buffer]);
  document.querySelector('#status').textContent=window.__evidence.saved?'Reopened saved bytes':'Opened synthetic PDF';
}
addEventListener('message',async e=>{
  if(e.source!==frame.contentWindow||e.origin!==location.origin)return;
  const m=e.data||{};
  if(m.type==='pdfcraft:ready'){window.__evidence.ready++;await openBytes()}
  if(m.type==='pdfcraft:dirty'){window.__evidence.dirty.push(!!m.dirty);document.querySelector('#status').textContent='dirty='+!!m.dirty}
  if(m.type==='pdfcraft:save'){
    const bytes=m.bytes instanceof ArrayBuffer?new Uint8Array(m.bytes):m.bytes;
    window.__evidence.saved=Array.from(bytes);
    window.__evidence.saves.push({ticket:m.ticket,name:m.name,length:bytes.length,sha256:null});
    document.querySelector('#status').textContent='Stored '+bytes.length+' bytes; ACK '+m.ticket;
    frame.contentWindow.postMessage({type:'pdfcraft:saveResult',ticket:m.ticket,ok:true},location.origin);
  }
});
window.__reopen=()=>{window.__evidence.reopened=true;frame.src='index.html?host=parent&fresh='+Date.now()};
</script>"""


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, directory, fixture_bytes, **kwargs):
        self.fixture_bytes = fixture_bytes
        super().__init__(*args, directory=str(directory), **kwargs)

    def do_GET(self):
        if self.path.split("?", 1)[0] == "/":
            body = HOST_HTML.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if self.path.split("?", 1)[0] == "/synthetic.pdf":
            self.send_response(200)
            self.send_header("Content-Type", "application/pdf")
            self.send_header("Content-Length", str(len(self.fixture_bytes)))
            self.end_headers()
            self.wfile.write(self.fixture_bytes)
            return
        return super().do_GET()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--evidence-dir", type=Path, required=True)
    args = parser.parse_args()
    candidate, fixture, evidence_dir = args.candidate.resolve(), args.fixture.resolve(), args.evidence_dir.resolve()
    if not (candidate / "index.html").is_file() or not list(candidate.glob("*_bg.wasm")):
        raise SystemExit("candidate index or WASM missing")
    if not fixture.is_file():
        raise SystemExit("synthetic PDF fixture missing")
    pdf = fixture.read_bytes()
    evidence_dir.mkdir(parents=True, exist_ok=True)
    (evidence_dir / "synthetic.pdf").write_bytes(pdf)
    handler = lambda *a, **kw: Handler(*a, directory=candidate, fixture_bytes=pdf, **kw)
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise SystemExit("Playwright is required") from exc
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--enable-unsafe-swiftshader", "--use-gl=angle", "--use-angle=swiftshader"])
            try:
                page = browser.new_page(viewport={"width": 1280, "height": 800})
                failed = []
                page.on("pageerror", lambda error: failed.append(str(error)))
                page.goto(f"http://127.0.0.1:{server.server_port}/", wait_until="load")
                page.wait_for_function("() => window.__evidence.ready > 0", timeout=180_000)
                page.wait_for_timeout(8_000)
                page.screenshot(path=str(evidence_dir / "opened.png"), full_page=True)
                canvas = page.frame_locator("#editor").locator("canvas").first
                # The first fillable text field is visibly centered near page x=750/y=315;
                # the editor canvas begins below the synthetic host header.
                canvas.click(position={"x": 520, "y": 260})
                page.keyboard.press("Control+A")
                page.keyboard.type("GR-057 visible PDF form edit")
                page.wait_for_function("() => window.__evidence.dirty.includes(true)", timeout=30_000)
                page.screenshot(path=str(evidence_dir / "edited.png"), full_page=True)
                page.keyboard.press("Control+s")
                page.wait_for_function("() => window.__evidence.saves.length === 1", timeout=60_000)
                page.wait_for_function("() => window.__evidence.dirty.at(-1) === false", timeout=30_000)
                page.evaluate("window.__reopen()")
                page.wait_for_function("() => window.__evidence.ready >= 2", timeout=180_000)
                page.wait_for_timeout(8_000)
                page.screenshot(path=str(evidence_dir / "reopened.png"), full_page=True)
                ev = page.evaluate("() => window.__evidence")
                assert len(ev["saved"]) > len(pdf), (len(pdf), len(ev["saved"]))
                assert ev["dirty"].count(True) >= 1 and ev["dirty"][-1] is False, ev["dirty"]
                saved_hash = hashlib.sha256(bytes(ev["saved"])).hexdigest()
                ev["saves"][0]["sha256"] = saved_hash
                report = {
                    "result": "PASS",
                    "fixture_bytes": len(pdf),
                    "fixture_sha256": hashlib.sha256(pdf).hexdigest(),
                    "saved_bytes": len(ev["saved"]),
                    "saved_sha256": saved_hash,
                    "ready_count": ev["ready"],
                    "dirty_sequence": ev["dirty"],
                    "saves": ev["saves"],
                    "visible_edit": "GR-057 visible PDF form edit",
                    "fresh_iframe_reopen": ev["reopened"] and ev["ready"] >= 2,
                    "console_page_errors": failed,
                    "scope": "actual built PdfCraft WASM; synthetic in-memory parent ACK; no Seafile persistence",
                }
                (evidence_dir / "browser-evidence.json").write_text(json.dumps(report, indent=2) + "\n")
                print(json.dumps(report, indent=2))
                assert not failed, failed
            finally:
                browser.close()
    finally:
        server.shutdown()
        thread.join(timeout=3)
        server.server_close()


if __name__ == "__main__":
    main()
