#!/usr/bin/env python3
"""Expired-session save regression through the real gateway and host page.

Run with cached Playwright Chromium:
    uv run --with playwright --python 3.14 -- python tests/test_gr043_expired_session_browser.py
"""

import io
import os
import sys
import threading
import time
import urllib.parse
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from integration.gateway.server import Gateway, Handler  # noqa: E402

TOKEN = "synthetic-gr043-token"


def synthetic_docx():
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w") as archive:
        archive.writestr("[Content_Types].xml", "<Types>wordprocessingml.document</Types>")
    return out.getvalue()


class SyntheticSeafile:
    def __init__(self):
        self.saves = 0
        self.document_bytes = synthetic_docx()

    def thirdparty_file_info(self, token):
        assert token == TOKEN
        return {"repo_id": "synthetic", "file_path": "/expiry.docx",
                "file_name": "expiry.docx", "username": "synthetic",
                "permission": "rw", "can_edit": True, "file_id": "id-1",
                "head_commit_id": "head-1"}

    def thirdparty_file_content(self, token, expected_file_id, max_bytes=None):
        assert token == TOKEN and expected_file_id == "id-1"
        return self.document_bytes

    def thirdparty_file_save(self, *_args):
        self.saves += 1
        raise AssertionError("expired session must never call synthetic Seafile save")


class ParentHandler(BaseHTTPRequestHandler):
    gateway_url = ""

    def log_message(self, *_args):
        pass

    def do_GET(self):
        body = ("<!doctype html><iframe id='host' name='host'></iframe>"
                f"<form method='POST' action='{self.gateway_url}' target='host'>"
                f"<input name='access_token' value='{TOKEN}'></form>")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body.encode())


class TestHandler(Handler):
    protocol_version = "HTTP/1.0"

    def do_GET(self):
        if urllib.parse.urlsplit(self.path).path == "/artcraft/test-editor":
            body = """<!doctype html><button id="save">Save synthetic edit</button>
<script>
window.__opened = false;
window.__saveResult = null;
parent.postMessage({type:"wordcraft:ready", version:1}, location.origin);
addEventListener("message", event => {
  if (event.origin !== location.origin) return;
  if (event.data?.type === "wordcraft:open") window.__opened = event.data.bytes.length > 0;
  if (event.data?.type === "wordcraft:saveResult") window.__saveResult = event.data;
});
document.getElementById("save").onclick = () => {
  parent.postMessage({type:"wordcraft:dirty", dirty:true}, location.origin);
  parent.postMessage({type:"wordcraft:save", ticket:"ticket-1", name:"expiry.docx",
    bytes:new Uint8Array([1,2,3])}, location.origin);
};
</script>"""
            return self._send(200, body, "text/html; charset=utf-8")
        return super().do_GET()


def main():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise SystemExit("Playwright is required; install Playwright and Chromium") from exc

    parent = ThreadingHTTPServer(("127.0.0.1", 0), ParentHandler)
    parent.daemon_threads = True
    old_seafile_origin = os.environ.get("ARTCRAFT_SEAFILE_ORIGIN")
    os.environ["ARTCRAFT_SEAFILE_ORIGIN"] = f"http://127.0.0.1:{parent.server_port}"
    seafile = SyntheticSeafile()
    gateway = Gateway(seafile, {"docx": {"app": "wordcraft", "url": "/artcraft/test-editor"}})
    host = ThreadingHTTPServer(("127.0.0.1", 0), TestHandler)
    host.daemon_threads = True
    host.gateway = gateway
    ParentHandler.gateway_url = f"http://127.0.0.1:{host.server_port}/open/"
    servers = (parent, host)
    threads = [threading.Thread(target=server.serve_forever, daemon=True) for server in servers]
    for thread in threads:
        thread.start()

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            try:
                page = browser.new_page()
                page.set_default_timeout(5_000)
                page.on("dialog", lambda dialog: dialog.dismiss())
                save_responses = []
                page.on("response", lambda response: save_responses.append(response.status)
                        if response.url.endswith("/save") else None)
                page.goto(f"http://127.0.0.1:{parent.server_port}/")
                page.locator("form").evaluate("form => form.submit()")
                host_frame = page.frame_locator("#host")
                host_frame.locator("#state").filter(has_text="expiry.docx opened").wait_for(timeout=10_000)
                editor = host_frame.frame_locator("#frame")
                editor_frame = next(frame for frame in page.frames
                                    if frame.url.endswith("/artcraft/test-editor"))
                editor.locator("#save").wait_for(timeout=10_000)
                editor.locator("body").wait_for(timeout=10_000)
                assert editor.locator("body").evaluate("() => window.__opened") is True
                assert len(gateway.sessions._sessions) == 1
                session = next(iter(gateway.sessions._sessions.values()))
                expired_at = time.time() - gateway.sessions.ttl - 1
                session.created = expired_at
                session.last_seen = expired_at

                editor.locator("#save").click()
                host_frame.locator("#state").filter(has_text="Save failed:").wait_for(timeout=10_000)
                state_text = host_frame.locator("#state").inner_text()
                assert "expired or is unavailable; return to Seafile and reopen the file" in state_text, state_text
                editor_frame.wait_for_function("() => window.__saveResult !== null", timeout=3_000)
                result = editor.locator("body").evaluate("() => window.__saveResult")
                assert result["ticket"] == "ticket-1" and result["ok"] is False, result
                assert "expired or is unavailable" in result["error"], result
                host_state = host_frame.locator("body").evaluate("() => ({dirty: window.__lastDirty, save: window.__lastSave})")
                assert host_state["dirty"] is True and host_state["save"]["ok"] is False, host_state
                assert save_responses == [404], save_responses
                assert gateway.sessions._sessions == {}
                assert seafile.saves == 0, seafile.saves
                print("PASS: actual POST /open/ created the session; synthetic editor opened the document")
                print("PASS: expired actual /session/<sid>/save returned HTTP 404 with reopen guidance")
                print("PASS: host UI stayed dirty; editor received saveResult ok:false; synthetic Seafile save calls=0")
            finally:
                browser.close()
    finally:
        for server in servers:
            server.shutdown()
            server.server_close()
        for thread in threads:
            thread.join(timeout=3)
        if old_seafile_origin is None:
            os.environ.pop("ARTCRAFT_SEAFILE_ORIGIN", None)
        else:
            os.environ["ARTCRAFT_SEAFILE_ORIGIN"] = old_seafile_origin


if __name__ == "__main__":
    main()
