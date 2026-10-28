#!/usr/bin/env python3
"""Actual-WASM PhotoCraft v0.16 memory-host save/ACK/fresh-editor smoke."""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import hashlib
import json
from pathlib import Path
import threading
import time
import zipfile

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/reviews/GR-082/runtime/photocraft"
BUNDLE = Path("/home/roddy/.cache/artcraft-storage-lab/upstream-refresh-sources/photocraft/dist/web")
SERVED = []


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass

    def translate_path(self, path):
        name = path.split("?", 1)[0].lstrip("/")
        if name in ("host.html", "synthetic.pcraft"):
            return str(EVIDENCE / name)
        candidate = (BUNDLE / name).resolve()
        root = BUNDLE.resolve()
        if candidate.is_relative_to(root):
            return str(candidate)
        return str(root / "__outside_bundle__")

    def copyfile(self, source, outputfile):
        payload = source.read()
        outputfile.write(payload)
        path = self.path.split("?", 1)[0].lstrip("/") or "index.html"
        if path not in ("host.html", "synthetic.pcraft"):
            SERVED.append({"path": path, "size": len(payload), "sha256": hashlib.sha256(payload).hexdigest()})


def main():
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    manifest_path = ROOT / "docs/reviews/GR-082/checks/photocraft-bundle-final.sha256"
    files = sorted(p for p in BUNDLE.rglob("*") if p.is_file())
    before = {str(p.relative_to(BUNDLE)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    manifest_path.write_text("".join(f"{before[str(p.relative_to(BUNDLE))]}  {p.relative_to(BUNDLE)}\n" for p in files))
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(Handler, directory=str(BUNDLE)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    evidence = {"bundle": str(BUNDLE), "bundle_hashes_before": before, "requests": [], "downloads": []}

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--enable-unsafe-swiftshader", "--use-gl=angle", "--use-angle=swiftshader"])
            page = browser.new_page(viewport={"width": 1280, "height": 800}, device_scale_factor=1)
            page.on("response", lambda response: evidence["requests"].append({"url": response.url, "status": response.status, "size": response.headers.get("content-length")}) if response.url.startswith(f"http://127.0.0.1:{server.server_port}/") else None)
            page.on("download", lambda download: evidence["downloads"].append(download.suggested_filename))
            page.goto(f"http://127.0.0.1:{server.server_port}/host.html")
            page.wait_for_function("() => window.smoke?.events?.some(e => e.type === 'photocraft:opened')", timeout=60000)
            page.wait_for_timeout(300)
            evidence["initial_state"] = page.evaluate("() => window.smoke.events")

            # Create an actual paint layer first; the fixture intentionally has none.
            page.mouse.click(176, 169)
            page.wait_for_timeout(250)
            page.mouse.move(208, 223)
            page.wait_for_timeout(500)
            page.mouse.click(453, 223)
            page.wait_for_timeout(350)
            page.keyboard.press("Enter")
            page.wait_for_timeout(350)

            # At a fixed 1280x800 viewport, the 64x64 document is centered in the
            # canvas at (498, 569). Draw a short black brush mark into the synthetic file.
            page.mouse.move(484, 555)
            page.mouse.down()
            page.mouse.move(512, 583, steps=6)
            page.mouse.up()
            page.wait_for_timeout(400)
            page.wait_for_function("() => window.smoke.dirty === true", timeout=10000)
            page.screenshot(path=str(EVIDENCE / "edited.png"), full_page=True)
            page.keyboard.press("Control+s")
            page.wait_for_function("() => window.smoke.saved?.byteLength > 0", timeout=30000)
            page.wait_for_function("() => window.smoke.request?.ticket", timeout=10000)
            evidence["save_state"] = page.evaluate("() => ({events:window.smoke.events, request:window.smoke.request, dirtyBeforeAck:window.smoke.dirtyBeforeAck, savedSha256:window.smoke.savedSha256, savedBytes:window.smoke.saved?.byteLength})")
            assert evidence["save_state"]["dirtyBeforeAck"] is True
            saved = bytes(page.evaluate("() => Array.from(window.smoke.saved)"))
            saved_path = EVIDENCE / "saved.pcraft"
            saved_path.write_bytes(saved)
            with zipfile.ZipFile(saved_path) as archive:
                doc = json.loads(archive.read("manifest.json"))["document"]
            assert doc["id"] == 82 and doc["size"] == {"width": 64, "height": 64}
            assert doc["layers"], "the saved native manifest must include the editor-created layer"
            evidence["saved_document"] = {"document_id": doc["id"], "size": doc["size"], "layers": [{"id": layer["id"], "name": layer["name"]} for layer in doc["layers"]], "sha256": hashlib.sha256(saved).hexdigest()}

            page.evaluate("() => window.ack()")
            page.wait_for_function("() => window.smoke.dirty === false && window.smoke.events.some(e => e.type === 'photocraft:dirty' && e.dirty === false && e.ticket)", timeout=10000)
            page.screenshot(path=str(EVIDENCE / "saved.png"), full_page=True)
            page.evaluate("() => window.reopen()")
            page.wait_for_function("() => window.smoke.events.some(e => e.generation === 2 && e.type === 'photocraft:opened')", timeout=60000)
            page.wait_for_timeout(500)
            evidence["reopen_state"] = page.evaluate("() => ({generation:window.smoke.generation, events:window.smoke.events.filter(e => e.generation === 2), dirty:window.smoke.dirty})")
            assert evidence["reopen_state"]["dirty"] is False
            assert evidence["reopen_state"]["events"][-1]["documentId"] == "82"
            page.screenshot(path=str(EVIDENCE / "reopened.png"), full_page=True)
            evidence["asset_transfers"] = SERVED
            evidence["download_count"] = len(evidence["downloads"])
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)

    after = {str(p.relative_to(BUNDLE)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(p for p in BUNDLE.rglob("*") if p.is_file())}
    evidence["bundle_hashes_after"] = after
    evidence["asset_transfers"] = SERVED
    assert before == after, "bundle assets changed during the browser run"
    assert evidence["downloads"] == []
    allowed_missing_fonts = [request for request in evidence["requests"] if request["url"].endswith("/fonts/manifest.txt") and request["status"] == 404]
    assert all(request["status"] == 200 or request in allowed_missing_fonts for request in evidence["requests"]), json.dumps(evidence["requests"], indent=2)
    assert all(before[item["path"]] == item["sha256"] for item in SERVED)
    assert any(item["path"].endswith(".wasm") for item in SERVED)
    (EVIDENCE / "browser-evidence.json").write_text(json.dumps(evidence, indent=2) + "\n")
    print("PASS: release WASM opened, edited and saved native bytes through the synthetic in-memory host;")
    print("PASS: matching ticket ACK marked the captured snapshot clean and a fresh editor iframe reopened the saved identity.")
    print("LIMIT: no Seafile persistence, production host, or identity-binding deployment was exercised.")


if __name__ == "__main__":
    main()
