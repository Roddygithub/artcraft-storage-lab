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
    vector_save_started = threading.Event()
    vector_retry_started = threading.Event()
    save_count = 0
    last_save_name = None
    vector_save_count = 0
    vector_saved_bytes = None
    document_bytes = b"original bytes"


EDITOR = """<!doctype html><script>
window.addEventListener('message', (event) => {
  const msg = event.data;
  if (msg?.type === 'wordcraft:open') {
    parent.postMessage({type: 'wordcraft:dirty', dirty: true}, location.origin);
  }
  if (msg?.type === 'wordcraft:saveResult') {
    window.lastSaveResult = msg;
    (window.saveResults ||= []).push(msg);
    parent.postMessage({type: 'wordcraft:dirty', dirty: !msg.ok}, location.origin);
  }
});
window.requestSave = (ticket, text, name = 'synthetic.docx', saveAs = false) => {
  parent.postMessage({type: 'wordcraft:dirty', dirty: true}, location.origin);
  parent.postMessage({type: 'wordcraft:save', name,
    bytes: new TextEncoder().encode(text).buffer, ticket, saveAs}, location.origin);
};
window.requestOpen = () => parent.postMessage(
  {type: 'wordcraft:openRequest', purpose: 'open'}, location.origin);
setTimeout(() => parent.postMessage({type: 'wordcraft:ready'}, location.origin), 50);
</script>"""


VECTOR_EDITOR = """<!doctype html><script>
window.vectorcraft = {
  bytes: new Uint8Array(),
  openFile(_name, bytes) { this.bytes = new Uint8Array(bytes); return true; },
  captureDownloads() {},
  files() { return Promise.resolve([{path:'synthetic.svg', size:this.bytes.length}]); },
  readFile() { return Promise.resolve(this.bytes.slice()); },
  replace(bytes) { this.bytes = new Uint8Array(bytes); }
};
</script>"""


def fnv1a32(data):
    value = 2166136261
    for byte in data:
        value = ((value ^ byte) * 16777619) & 0xFFFFFFFF
    return value


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
        if self.path == "/vector-host":
            page = render("test-session", "vectorcraft", "/vector-editor", "synthetic.svg", True)
            return self._send(200, page.encode(), "text/html; charset=utf-8")
        if self.path == "/editor":
            return self._send(200, EDITOR.encode(), "text/html; charset=utf-8")
        if self.path == "/vector-editor":
            return self._send(200, VECTOR_EDITOR.encode(), "text/html; charset=utf-8")
        if self.path == "/session/test-session/document":
            return self._send(200, State.document_bytes, "application/octet-stream")
        return self._send(404, b"{}")

    def do_POST(self):
        size = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(size)
        if self.path == "/session/test-session/dirty":
            return self._send(200, b'{"ok":true}')
        if self.path != "/session/test-session/save":
            return self._send(404, b"{}")

        if self.headers.get("X-ArtCraft-Filename") == "synthetic.svg":
            State.vector_save_count += 1
            State.vector_saved_bytes = body
            if State.vector_save_count == 1:
                State.vector_save_started.set()
                return self._send(503, b'{"ok":false,"error":"synthetic first-attempt rejection"}')
            if State.vector_save_count == 2:
                State.vector_retry_started.set()
            return self._send(200, b'{"ok":true,"version":"vector-version"}')

        State.save_count += 1
        State.last_save_name = self.headers.get("X-ArtCraft-Filename")
        if State.save_count == 1:
            State.first_save_started.set()
            if not State.release_first_save.wait(5):
                return self._send(504, b'{"ok":false}')
            return self._send(200, b'{"ok":true,"version":"version-2"}')
        if State.save_count == 2:
            return self._send(200, b'{"ok":true,"version":"version-3"}')
        return self._send(500, b'{"ok":false,"error":"synthetic failure"}')


def main():
    State.first_save_started.clear()
    State.release_first_save.clear()
    State.vector_save_started.clear()
    State.vector_retry_started.clear()
    State.save_count = 0
    State.last_save_name = None
    State.vector_save_count = 0
    State.vector_saved_bytes = None
    State.document_bytes = b"original bytes"
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

            page.evaluate("() => document.getElementById('frame').contentWindow.requestOpen()")
            page.wait_for_function("() => document.getElementById('state').innerText.includes('return to Seafile')")
            assert page.evaluate("() => window.__lastDirty === true"), "open request must not clear dirty state"

            page.evaluate("() => document.getElementById('frame').contentWindow.requestSave('ticket-a', 'first edit')")
            assert State.first_save_started.wait(5), "first save request did not reach the host"
            page.wait_for_function("() => window.__saveInFlight === true")
            print("first save in flight:", page.evaluate("() => ({dirty:window.__lastDirty,saving:window.__saveInFlight})"))
            assert page.evaluate("() => window.__lastDirty === true")
            assert page.evaluate("() => window.__editorConfirmedSave === false")

            # A later editor snapshot arrives before A's durable acknowledgement.
            # It must be rejected locally and must not cause A's acknowledgement
            # to clear the newer dirty revision.
            page.evaluate("() => document.getElementById('frame').contentWindow.requestSave('ticket-b', 'later edit')")
            page.wait_for_function("() => document.getElementById('frame').contentWindow.saveResults?.some(x => x.ticket === 'ticket-b' && !x.ok)")
            assert State.save_count == 1, "overlapping save must not reach storage"

            State.release_first_save.set()
            page.wait_for_function("() => document.getElementById('frame').contentWindow.saveResults?.some(x => x.ticket === 'ticket-a' && x.ok)")
            page.wait_for_function("() => window.__saveInFlight === false && window.__saveConfirmationPending === false")
            assert page.evaluate("() => window.__lastDirty === true"), "A acknowledgement must not clear B's later edit"
            assert page.evaluate("() => window.__editorConfirmedSave === false")
            assert "Saved" not in page.locator("#state").inner_text()

            # Once A has completed, retrying B is allowed and can be confirmed.
            page.evaluate("() => document.getElementById('frame').contentWindow.requestSave('ticket-c', 'later edit', 'Renamed title.docx')")
            page.wait_for_function("() => document.getElementById('frame').contentWindow.saveResults?.some(x => x.ticket === 'ticket-c' && x.ok)")
            page.wait_for_function("() => window.__editorConfirmedSave === true")
            assert page.evaluate("() => window.__lastDirty === false")
            assert State.last_save_name == "synthetic.docx", "host save must remain bound to the originally selected file"

            page.evaluate("() => document.getElementById('frame').contentWindow.requestSave('ticket-save-as', 'copy', 'copy.docx', true)")
            page.wait_for_function("() => document.getElementById('frame').contentWindow.saveResults?.some(x => x.ticket === 'ticket-save-as' && !x.ok)")
            assert State.save_count == 2, "Save As must not reach storage"

            page.evaluate("() => document.getElementById('frame').contentWindow.requestSave('ticket-export', 'pdf', 'export.pdf', false)")
            page.wait_for_function("() => document.getElementById('frame').contentWindow.saveResults?.some(x => x.ticket === 'ticket-export' && !x.ok)")
            assert State.save_count == 2, "cross-format export must not reach storage"

            page.evaluate("() => document.getElementById('frame').contentWindow.requestSave('ticket-d', 'failed edit')")
            page.wait_for_function("() => window.__lastSave?.ok === false")
            page.wait_for_function("() => document.getElementById('frame').contentWindow.lastSaveResult")
            assert page.evaluate("() => window.__lastDirty === true"), "failed save must stay dirty"
            assert page.evaluate("() => window.__editorConfirmedSave === false")
            page.goto(url.rstrip("/") + "/vector-host")
            page.wait_for_function("() => document.getElementById('frame').contentWindow?.vectorcraft")

            original = bytes.fromhex("46e9bb16c707a921")
            changed = bytes.fromhex("33d4b4702b82e0e2")
            assert len(original) == len(changed)
            assert original != changed
            assert fnv1a32(original) == fnv1a32(changed), "fixture must collide under the old FNV-1a check"

            # The unchanged initial document must not be spuriously saved.
            page.wait_for_timeout(900)
            assert State.vector_save_count == 0

            # These distinct same-length byte sequences collided in the prior
            # 32-bit fingerprint implementation. Exact comparison must save B.
            page.evaluate("bytes => document.getElementById('frame').contentWindow.vectorcraft.replace(bytes)", list(changed))
            assert State.vector_save_started.wait(5), "changed VectorCraft bytes were skipped"
            page.wait_for_function("() => window.__lastSave?.ok === false")
            assert page.evaluate("() => window.__lastDirty === true"), "failed VectorCraft write must remain dirty"
            assert State.vector_retry_started.wait(5), "VectorCraft did not retry the unchanged edited bytes"
            page.wait_for_function("() => window.__lastSave?.ok === true")
            assert State.vector_saved_bytes == changed, "host must persist the exact changed bytes"
            page.wait_for_timeout(900)
            assert State.vector_save_count == 2, "failure must retry once, then identical saved bytes must not create duplicate versions"
            browser.close()
    finally:
        State.release_first_save.set()
        server.shutdown()
        thread.join(timeout=3)
        server.server_close()
    print("PASS: overlapping save is rejected without reaching storage")
    print("PASS: earlier acknowledgement cannot clear a later dirty revision")
    print("PASS: retry after prior save completes is durably confirmed")
    print("PASS: failed save cannot be cleared by the synthetic editor's dirty=false")
    print("PASS: host saves stay bound to the selected filename; Save As and cross-format exports are rejected")
    print("PASS: file-open request explains the single-file Seafile session boundary")
    print("PASS: distinct equal-length VectorCraft bytes with a 32-bit FNV-1a collision are persisted")
    print("PASS: VectorCraft retries after a rejected write, then skips unchanged persisted bytes")
    print("NOTE: synthetic local protocol test; not a Craft/Seafile E2E")


if __name__ == "__main__":
    main()
