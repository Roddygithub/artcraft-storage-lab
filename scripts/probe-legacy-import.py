#!/usr/bin/env python3
"""Bundle-level legacy/OpenDocument import probe: no Seafile, no bridge.

Loads each pinned Craft web bundle in a same-origin wrapper page, speaks the
upstream `?host=parent` protocol directly (`<app>:ready`, `<app>:open`), then
captures the document the editor itself serializes on Save. The marker must be
present in that payload, which is what proves the editor parsed the legacy bytes
into its document model rather than only accepting them.

This isolates editor import from the host, the bridge and Seafile: a failure here
is an editor-bundle limitation, not a routing or WOPI problem. The real Seafile
replay is `lab/real-seafile/local.py --viewing`.

usage:
  uv run --with playwright --with pillow python scripts/probe-legacy-import.py \
      --static ~/.cache/artcraft-storage-lab/pptx-candidate-20261108/static \
      --output ~/.cache/artcraft-storage-lab/legacy-import-bundle

Exit 0 only when every routed fixture is imported and carries the marker.
"""
from __future__ import annotations

import argparse
import functools
import http.server
import json
import os
from pathlib import Path
import socketserver
import sys
import threading
import time

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("SEAFILE_URL", "http://seafile.test")
os.environ.setdefault("BRIDGE_URL", "http://bridge.test")
os.environ.setdefault("ADMIN_EMAIL", "test@example.test")
os.environ.setdefault("ADMIN_PASSWORD", "test")
os.environ.setdefault("RESULTS_DIR", "/tmp/artcraft-offline-tests")
sys.path.insert(0, str(ROOT / "lab/real-seafile"))
import run_slice as rs  # noqa: E402

# Routed formats only: the documented-import subset of lab/real-seafile/run_slice.py.
CASES = {name: editor for name, (ext, editor) in rs.LEGACY_VIEWING.items() if editor}

WRAPPER = """<!doctype html><meta charset="utf-8">
<body style="margin:0;background:#888">
<iframe id=f style="width:1400px;height:860px;border:0"></iframe>
<script>
window.__msgs = [];
window.__saves = [];
var app = new URLSearchParams(location.search).get("app");
document.getElementById("f").src = "/" + app + "/index.html?host=parent";
addEventListener("message", function (e) {
  var d = e.data || {};
  if (typeof d.type !== "string") return;
  var meta = {type: d.type};
  for (var k in d) if (typeof d[k] !== "object") meta[k] = d[k];
  window.__msgs.push(meta);
  if (d.bytes) window.__saves.push(Array.from(new Uint8Array(d.bytes)));
});
</script>"""


class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):  # keep the probe output readable
        pass

    def do_GET(self):
        if self.path.startswith("/__probe.html"):
            body = WRAPPER.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()


class Server(socketserver.TCPServer):
    allow_reuse_address = True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--static", type=Path, required=True, help="directory holding the <app>/ bundles")
    parser.add_argument("--fixtures", type=Path, default=ROOT / "lab/real-seafile/fixtures/legacy")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    handler = functools.partial(Handler, directory=str(args.static))
    server = Server(("127.0.0.1", 0), handler)
    port = server.server_address[1]
    threading.Thread(target=server.serve_forever, daemon=True).start()
    args.output.mkdir(parents=True, exist_ok=True)

    from playwright.sync_api import sync_playwright

    results = []
    failed = 0
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader",
                                          "--ignore-gpu-blocklist", "--disable-dev-shm-usage"])
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        for name, editor in CASES.items():
            record = {"fixture": name, "editor": editor, "ok": False}
            path = args.fixtures / name
            if not path.is_file():
                record["error"] = f"missing fixture {path}"
                results.append(record)
                failed += 1
                continue
            content = path.read_bytes()
            page = context.new_page()
            page.goto(f"http://127.0.0.1:{port}/__probe.html?app={editor}", wait_until="domcontentloaded")
            try:
                deadline = time.monotonic() + 180
                while time.monotonic() < deadline:
                    if any(m["type"] == f"{editor}:ready" for m in page.evaluate("window.__msgs")):
                        break
                    time.sleep(0.5)
                else:
                    raise TimeoutError(f"{editor}:ready never arrived")
                page.evaluate("""async ([app, name, bytes]) => {
                    const frame = document.getElementById('f').contentWindow;
                    frame.postMessage({type: app + ':open', name, bytes: Uint8Array.from(bytes).buffer},
                                      location.origin);
                }""", [editor, name, list(content)])
                deadline = time.monotonic() + 120
                while time.monotonic() < deadline:
                    if any(m["type"] == f"{editor}:dirty" for m in page.evaluate("window.__msgs")):
                        break
                    time.sleep(0.5)
                frame_box = page.locator("#f").bounding_box()
                page.mouse.click(frame_box["x"] + frame_box["width"] / 2,
                                 frame_box["y"] + frame_box["height"] / 2)
                time.sleep(0.5)
                if editor == "gridcraft":
                    # Import-only .xls/.ods open behind a notice; Enter dismisses it.
                    page.keyboard.press("Enter")
                    time.sleep(1)
                page.keyboard.press("Control+s")
                deadline = time.monotonic() + 60
                saves = []
                while time.monotonic() < deadline:
                    saves = page.evaluate("window.__saves")
                    if saves:
                        break
                    time.sleep(0.5)
                record["save_payloads"] = [len(s) for s in saves]
                kinds = []
                for saved in saves:
                    ok, kind = rs.viewing_payload_has_marker(bytes(saved))
                    kinds.append(kind)
                    if ok:
                        record["ok"] = True
                        record["kind"] = kind
                        break
                record["kinds"] = kinds
                page.screenshot(path=str(args.output / f"{name.replace('.', '_')}.png"))
            except Exception as exc:  # noqa: BLE001 - a failed case must be reported, not raised
                record["error"] = f"{type(exc).__name__}: {exc}"
            finally:
                page.close()
            if not record["ok"]:
                failed += 1
            results.append(record)
            print(("PASS " if record["ok"] else "FAIL ") + f"{name} -> {editor} "
                  + (record.get("kind") or record.get("error") or ""), flush=True)
        browser.close()
    server.shutdown()

    summary = {"cases": results, "passed": sum(r["ok"] for r in results), "failed": failed}
    (args.output / "summary.json").write_text(json.dumps(summary, indent=1) + "\n")
    print(f"\n{summary['passed']} passed, {failed} failed", flush=True)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
