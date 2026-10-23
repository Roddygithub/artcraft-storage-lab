#!/usr/bin/env python3
"""Exercise the pinned VectorCraft web engine without Seafile credentials."""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading

from playwright.sync_api import sync_playwright

from test_gr012_svg import has_expected_stroke, has_serialized_stroke


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "integration/static/vectorcraft"
FIXTURE = ROOT / "tests/fixtures/synthetic.svg"


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


def main():
    server = ThreadingHTTPServer(
        ("127.0.0.1", 0), partial(QuietHandler, directory=str(APP)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True, args=[
                "--enable-unsafe-swiftshader", "--use-gl=angle", "--use-angle=swiftshader"])
            page = browser.new_page()
            page.goto(f"http://127.0.0.1:{server.server_port}/")
            page.wait_for_function("() => window.vectorcraft?.openFile", timeout=30000)
            original = list(FIXTURE.read_bytes())
            assert page.evaluate(
                "([name, bytes]) => { vectorcraft.captureDownloads(true); "
                "return vectorcraft.openFile(name, new Uint8Array(bytes)); }",
                ["synthetic.svg", original])
            page.evaluate("() => vectorcraft.request('ui.tool.select', {tool:'pencil'})")
            events = [
                {"kind": "down", "x": 60, "y": 60, "space": "doc"},
                {"kind": "drag", "x": 120, "y": 90, "space": "doc"},
                {"kind": "drag", "x": 180, "y": 120, "space": "doc"},
                {"kind": "up", "x": 180, "y": 120, "space": "doc"},
            ]
            page.evaluate("events => vectorcraft.request('ui.pointer', {events})", events)
            page.evaluate("() => vectorcraft.request('app.save', {path:'synthetic.svg',svg:{}})")
            saved = page.evaluate(
                "() => Array.from(new Uint8Array(vectorcraft.readFile('synthetic.svg'))) ")
            assert saved and saved != original and has_serialized_stroke(bytes(saved))
            assert page.evaluate(
                "([name, bytes]) => vectorcraft.openFile(name, new Uint8Array(bytes))",
                ["synthetic.svg", saved])
            reopened = page.evaluate("() => vectorcraft.request('document.inspect', {})")
            assert has_expected_stroke(reopened)
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)
    print("PASS: VectorCraft edited and serialized the synthetic SVG pencil stroke")
    print("PASS: reopened VectorCraft parses the stroke with its expected geometry")
    print("NOTE: local editor engine only; no host gateway or Seafile persistence")


if __name__ == "__main__":
    main()
