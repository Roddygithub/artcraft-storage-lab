#!/usr/bin/env python3
"""Browser-level host protocol checks using a synthetic editor frame.

Run with a Python environment that has Playwright and Chromium installed:
    python3 tests/test_hostpage_protocol.py

This is a local protocol simulation, not a Craft or Seafile end-to-end test.
"""

import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from playwright.sync_api import sync_playwright

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from integration.gateway.hostpage import render  # noqa: E402


class State:
    first_save_started = threading.Event()
    release_first_save = threading.Event()
    save_count = 0


EDITOR = """<!doctype html><script>
window.addEventListener('message', (event) => {
  const msg = event.data;
  if (msg?.type === 'wordcraft:open') {
    parent.postMessage({type: 'wordcraft:dirty', dirty: true}, location.origin);
  }
  if (msg?.type === 'wordcraft:saveResult') {
    window.lastSaveResult = msg;
    parent.postMessage({type: 'wordcraft:dirty', dirty: !msg.ok}, location.origin);
  }
});
window.requestSave = () => parent.postMessage({
  type: 'wordcraft:save', name: 'synthetic.docx',
  bytes: new TextEncoder().encode('edited bytes').buffer, ticket: 'ticket-1'
}, location.origin) || parent.postMessage({type: 'wordcraft:dirty', dirty: false}, location.origin);
setTimeout(() => parent.postMessage({type: 'wordcraft:ready'}, location.origin), 50);
</script>"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_args):
        pass

    def _send(self, status, body, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/":
            page = render("test-session", "wordcraft", "/editor", "synthetic.docx", True)
            return self._send(200, page.encode(), "text/html; charset=utf-8")
        if self.path == "/editor":
            return self._send(200, EDITOR.encode(), "text/html; charset=utf-8")
        if self.path == "/session/test-session/document":
            return self._send(200, b"original bytes", "application/octet-stream")
        return self._send(404, b"{}")

    def do_POST(self):
        size = int(self.headers.get("Content-Length", "0"))
        self.rfile.read(size)
        if self.path == "/session/test-session/dirty":
            return self._send(200, b'{"ok":true}')
        if self.path != "/session/test-session/save":
            return self._send(404, b"{}")

        State.save_count += 1
        if State.save_count == 1:
            State.first_save_started.set()
            if not State.release_first_save.wait(5):
                return self._send(504, b'{"ok":false}')
            return self._send(200, b'{"ok":true,"version":"version-2"}')
        return self._send(500, b'{"ok":false,"error":"synthetic failure"}')


def main():
    State.first_save_started.clear()
    State.release_first_save.clear()
    State.save_count = 0
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    url = f"http://127.0.0.1:{server.server_port}/"
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url)
            page.wait_for_function("() => document.getElementById('frame').contentWindow?.requestSave")
            page.wait_for_function("() => window.__lastDirty === true")

            page.evaluate("() => document.getElementById('frame').contentWindow.requestSave()")
            assert State.first_save_started.wait(5), "first save request did not reach the host"
            page.wait_for_function("() => window.__saveInFlight === true")
            print("first save in flight:", page.evaluate("() => ({dirty:window.__lastDirty,saving:window.__saveInFlight})"))
            assert page.evaluate("() => window.__lastDirty === true")
            assert page.evaluate("() => window.__editorConfirmedSave === false")

            State.release_first_save.set()
            page.wait_for_function("() => window.__editorConfirmedSave === true")
            assert page.evaluate("() => window.__lastDirty === false")

            page.evaluate("() => document.getElementById('frame').contentWindow.requestSave()")
            page.wait_for_function("() => window.__lastSave?.ok === false")
            page.wait_for_function("() => document.getElementById('frame').contentWindow.lastSaveResult")
            assert page.evaluate("() => window.__lastDirty === true"), "failed save must stay dirty"
            assert page.evaluate("() => window.__editorConfirmedSave === false")
            browser.close()
    finally:
        State.release_first_save.set()
        server.shutdown()
        thread.join(timeout=3)
        server.server_close()
    print("PASS: pre-save dirty=false is ignored while durable save is in flight")
    print("PASS: host dirty state clears only after durable response and editor confirmation")
    print("PASS: failed save cannot be cleared by the synthetic editor's dirty=false")
    print("NOTE: synthetic local protocol test; not a Craft/Seafile E2E")


if __name__ == "__main__":
    main()
