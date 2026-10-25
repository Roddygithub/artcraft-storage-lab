#!/usr/bin/env python3
"""Browser-enforce CSP on the actual gateway POST /open/ response.

Run with Playwright and its cached Chromium installed:
    python3 tests/test_gr042_hostpage_csp_browser.py
"""

import os
import sys
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from integration.gateway.server import Gateway, Handler  # noqa: E402


TOKEN = "synthetic-csp-token"


class SyntheticSeafile:
    def thirdparty_file_info(self, token):
        assert token == TOKEN
        return {"repo_id": "synthetic", "file_path": "/csp.docx",
                "file_name": "csp.docx", "username": "synthetic",
                "permission": "rw", "can_edit": True, "file_id": "id-1",
                "head_commit_id": "head-1"}

    def thirdparty_file_content(self, token, expected_file_id, max_bytes=None):
        assert token == TOKEN and expected_file_id == "id-1"
        return b"synthetic document"


class ParentHandler(BaseHTTPRequestHandler):
    gateway_url = ""

    def log_message(self, *_args):
        pass

    def do_GET(self):
        if urllib.parse.urlsplit(self.path).path == "/submit":
            body = ("<!doctype html><iframe name='host'></iframe><form id='f' "
                    f"method='POST' action='{self.gateway_url}' target='host'>"
                    f"<input name='access_token' value='{TOKEN}'></form>"
                    "<script>document.getElementById('f').submit()</script>").encode()
        else:
            body = b"<!doctype html><title>synthetic parent</title>"
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class TestHandler(Handler):
    def do_GET(self):
        if urllib.parse.urlsplit(self.path).path == "/artcraft/test-editor":
            body = ("<!doctype html><script>parent.postMessage("
                    "{type:'wordcraft:ready',version:1}, location.origin)</script>")
            return self._send(200, body, "text/html; charset=utf-8")
        return super().do_GET()


def main():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise SystemExit("Playwright is required; install Playwright and Chromium") from exc

    parent = ThreadingHTTPServer(("127.0.0.1", 0), ParentHandler)
    allowed_origin = f"http://127.0.0.1:{parent.server_port}"
    os.environ["ARTCRAFT_SEAFILE_ORIGIN"] = allowed_origin
    gateway = Gateway(SyntheticSeafile(), {"docx": {"app": "wordcraft",
                                                        "url": "/artcraft/test-editor"}})
    host = ThreadingHTTPServer(("127.0.0.1", 0), TestHandler)
    host.gateway = gateway
    ParentHandler.gateway_url = f"http://127.0.0.1:{host.server_port}/open/"
    threads = [threading.Thread(target=s.serve_forever, daemon=True)
               for s in (parent, host)]
    for thread in threads:
        thread.start()
    gateway_url = f"http://127.0.0.1:{host.server_port}/open/"

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            try:
                def submit(page, parent_url):
                    page.goto(parent_url)
                    page.evaluate("""({url, token}) => {
                      const frame = document.createElement('iframe');
                      frame.name = 'host'; document.body.append(frame);
                      const form = document.createElement('form');
                      form.method = 'POST'; form.action = url; form.target = 'host';
                      const input = document.createElement('input');
                      input.name = 'access_token'; input.value = token;
                      form.append(input); document.body.append(form); form.submit();
                    }""", {"url": gateway_url, "token": TOKEN})
                    return page.frame_locator("iframe")

                page = browser.new_page()
                page.add_init_script("""window.__cspViolations=[];
                  addEventListener('securitypolicyviolation', e =>
                    window.__cspViolations.push(e.violatedDirective));""")
                submit(page, allowed_origin + "/")
                host_frame = page.frame_locator("iframe")
                host_frame.locator("#state").wait_for(timeout=10_000)
                host_document = next(frame for frame in page.frames
                                     if frame.url.startswith(gateway_url))
                host_frame.locator("#state").filter(has_text="csp.docx opened").wait_for(
                    timeout=10_000)
                style_position = host_frame.locator("#bar").evaluate(
                    "e => getComputedStyle(e).position")
                assert style_position == "absolute", style_position
                violations = host_document.evaluate("() => window.__cspViolations")
                assert violations == [], violations
                print("PASS: actual POST /open/ response framed by configured Seafile origin")
                print("PASS: nonce inline script fetched/opened the synthetic document; nonce style applied; no CSP violations")

                blocked = browser.new_page()
                messages = []
                blocked.on("console", lambda msg: messages.append(msg.text))
                blocked.goto(f"http://localhost:{parent.server_port}/")
                blocked.evaluate("""url => {
                  const f=document.createElement('iframe'); f.src=url;
                  document.body.append(f);
                }""", allowed_origin + "/submit")
                blocked.wait_for_timeout(500)
                assert not any(frame.url.startswith(gateway_url) for frame in blocked.frames), [
                    frame.url for frame in blocked.frames]
                assert any("frame-ancestors" in message for message in messages), messages
                print("PASS: actual POST /open/ response refused a disallowed outer ancestor")
            finally:
                browser.close()
    finally:
        for server in (host, parent):
            server.shutdown()
            server.server_close()
        for thread in threads:
            thread.join(timeout=3)


if __name__ == "__main__":
    main()
