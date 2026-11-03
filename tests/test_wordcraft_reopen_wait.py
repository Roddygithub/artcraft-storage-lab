#!/usr/bin/env python3
"""Regression, aptarchy plan-4f938657073b slice 1: the WordCraft reopen wait in
lab/real-seafile/run_browser.py must be able to see a /relay/file response that arrives
after the wait begins. The former wait only scanned a Python list and called time.sleep,
while sync Playwright dispatches response callbacks only inside Playwright calls -- so the
response and its captured body never became visible. Loopback-only stdlib HTTP server +
real Playwright/Chromium; no Seafile, no editor bundle."""
import os
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import patch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lab", "real-seafile"))

# run_slice reads these at import; supply synthetic values, restore afterwards.
_REAL: dict = {}
for _k, _v in (("SEAFILE_URL", "http://127.0.0.1:1/seahub"),
               ("BRIDGE_URL", "http://127.0.0.1:1/bridge"),
               ("ONLYOFFICE_URL", "http://127.0.0.1:1/onlyoffice"),
               ("ADMIN_EMAIL", "synthetic@example.invalid"),
               ("ADMIN_PASSWORD", "synthetic-not-a-real-password")):
    _REAL[_k] = os.environ.get(_k)
    os.environ[_k] = _v
try:
    import run_browser
finally:
    for _k, _v in _REAL.items():
        if _v is None:
            os.environ.pop(_k, None)
        else:
            os.environ[_k] = _v

import run_slice as rs  # noqa: E402  (fixtures: rs.minimal_docx / rs.docx_text)

DELAY_MS = 1200
failures: list[str] = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (f"  -- {detail}" if detail else ""), flush=True)
    if not ok:
        failures.append(name)


class Fixture:
    """Loopback-only server: / serves a page that fetches /relay/file after DELAY_MS;
    /relay/file serves the next planned (status, body)."""

    def __init__(self, plan, save_status=200, reconciled=False):
        self.plan = plan
        self.save_status = save_status
        self.reconciled = reconciled

    def start(self):
        outer = self

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                self.rfile.read(int(self.headers.get("Content-Length", "0")))
                self.send_response(outer.save_status)
                self.send_header("Content-Length", "2")
                self.end_headers()
                self.wfile.write(b"{}")

            def do_GET(self):
                if self.path == "/relay/file":
                    with outer.lock:
                        if outer.plan:
                            status, body = outer.plan.pop(0)
                        else:
                            status, body = 404, b""
                    self.send_response(status)
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
                elif self.path.startswith("/library/") or self.path.startswith("/lib/"):
                    body = (b'<a href="/lib/fixture/file/same.docx">same.docx</a>'
                            b'<a target="_blank" href="/lib/fixture/file/popup.docx">popup.docx</a>'
                            b'<a href="/download">download</a>')
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html")
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
                elif self.path in ("/save", "/nosave"):
                    script = (b"document.addEventListener('keydown',e=>{"
                              b"if(e.ctrlKey&&e.key==='s'){e.preventDefault();"
                              b"setTimeout(()=>fetch('/relay/save',{method:'POST',body:'fixture-payload'})"
                              b".then(r=>{if(r.ok)setTimeout(()=>document.getElementById('status').textContent='saved to seafile',150)}),150);}})")
                    if outer.reconciled:
                        script = script.replace(b"saved to seafile", b"saved (reconciled after a lost response)")
                    if self.path == "/nosave":
                        script = b"document.addEventListener('keydown',e=>e.preventDefault())"
                    body = b'<div id="status">unsaved</div><script>' + script + b'</script>'
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html")
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
                elif self.path == "/download":
                    body = b"fixture-download"
                    self.send_response(200)
                    self.send_header("Content-Disposition", "attachment; filename=fixture.bin")
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
                elif self.path == "/":
                    page = b"<div>ready</div><script>setTimeout(function(){fetch('/relay/file').catch(function(){});},%d);</script>" % DELAY_MS
                    self.send_response(200)
                    self.send_header("Content-Length", str(len(page)))
                    self.send_header("Content-Type", "text/html")
                    self.end_headers()
                    self.wfile.write(page)
                else:
                    self.send_response(404)
                    self.send_header("Content-Length", "0")
                    self.end_headers()

            def log_message(self, *args):
                pass

        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.lock = threading.Lock()
        self.url = f"http://127.0.0.1:{self.httpd.server_port}"
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()
        return self

    def stop(self):
        self.httpd.shutdown()
        self.httpd.server_close()


def on_response(relay_list):
    """Exactly the production capture: status + body via a real response callback."""
    def _cb(r):
        if r.url.endswith("/relay/file"):
            try:
                relay_list.append((r.status, r.body()))
            except Exception:  # noqa: BLE001
                pass
    return _cb


def legacy_sleep_only_wait(captured, timeout):
    """The former production loop verbatim (modulo sleep interval), for the regression."""

    class NoPage:  # the old loop never used Playwright
        def wait_for_timeout(self, ms):
            time.sleep(ms / 1000)
    end = time.time() + timeout
    while time.time() < end:
        for st, b in list(captured):
            if st == 200 and b:
                return b
        time.sleep(1)
    return None


def main():
    saved = rs.minimal_docx("reopen wait regression fixture")
    from playwright.sync_api import sync_playwright
    t0 = time.time()
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader",
                                          "--ignore-gpu-blocklist", "--enable-webgl", "--disable-dev-shm-usage"])

        # -- delayed success: the response arrives while the wait is already running --------
        fx = Fixture(plan=[(200, saved)]).start()
        page = browser.new_page()
        relay_file: list = []
        page.on("response", on_response(relay_file))
        page.goto(f"{fx.url}/", wait_until="load")
        # The production wait is the FIRST Playwright call after arranging the delayed fetch.
        body = run_browser.wait_for_saved_response(page, relay_file, timeout=15)
        check("wait_returns_bytes_captured_after_the_wait_began", body == saved,
              f"got {len(body) if body else 0} of {len(saved)} bytes after {time.time()-t0:.0f}s")
        check("returned_bytes_are_the_document_fixture", body is not None and rs.docx_text(body) == "reopen wait regression fixture",
              f"status={relay_file[0][0] if relay_file else None} responses={len(relay_file)}")
        page.close()
        fx.stop()

        # -- bounded failure: only an unsuccessful OR empty response qualifies as a reject --
        # note: Chromium/Playwright cannot retrieve the body of a zero-length response over the
        # network, so the empty capture is supplied in the list shape the production filter reads.
        fx = Fixture(plan=[(500, b"boom")]).start()
        page = browser.new_page()
        relay_file: list = []
        page.on("response", on_response(relay_file))
        page.goto(f"{fx.url}/", wait_until="load")
        relay_file.append((200, b""))   # an empty successful capture must be rejected too
        body = run_browser.wait_for_saved_response(page, relay_file, timeout=6)
        check("wait_times_out_without_a_qualifying_response", body is None,
              f"responses={[(s, len(b)) for s, b in relay_file]}")
        page.close()
        fx.stop()

        # -- the delayed-success case FAILS with the former sleep-only wait -----------------
        fx = Fixture(plan=[(200, saved)]).start()
        page = browser.new_page()
        relay_file: list = []
        page.on("response", on_response(relay_file))
        page.goto(f"{fx.url}/", wait_until="load")
        old_body = legacy_sleep_only_wait(relay_file, timeout=4)
        check("delayed_success_fails_with_the_former_sleep_only_wait", old_body is None,
              f"after 4s no callbacks were dispatched; responses={len(relay_file)}")
        # the response WAS received by the browser: one Pumped Playwright call surfaces it
        page.wait_for_timeout(DELAY_MS + 200)
        check("former_wait_starved_a_response_the_browser_received",
              relay_file and relay_file[-1] == (200, saved),
              f"captured={[(s, len(b)) for s, b in relay_file]}")
        # the production wait, given the same situation, finds it immediately
        new_body = run_browser.wait_for_saved_response(page, relay_file, timeout=10)
        check("production_wait_finds_the_starved_response", new_body == saved, f"len={len(new_body) if new_body else 0}")
        page.close()
        fx.stop()
        fx = Fixture(plan=[]).start()
        context = browser.new_context()
        page = context.new_page()
        downloads = []
        run_browser.track_downloads(context, downloads)
        same = run_browser.open_from_seafile_list(page, fx.url, "fixture", "same.docx")
        check("file_list_click_supports_same_tab", same is page and same.url.endswith("/file/same.docx"))
        with same.expect_download():
            same.get_by_role("link", name="download", exact=True).click()
        check("download_observed_on_existing_page", len(downloads) == 1)
        popup = run_browser.open_from_seafile_list(page, fx.url, "fixture", "popup.docx")
        check("file_list_click_supports_new_tab", popup is not page and popup.url.endswith("/file/popup.docx"))
        with popup.expect_download():
            popup.get_by_role("link", name="download", exact=True).click()
        check("download_observed_on_popup", len(downloads) == 2)
        context.close()
        fx.stop()

        # Invoke the production save helper against delayed real HTTP request callbacks.
        for save_status, reconciled in ((200, False), (200, True), (500, False)):
            tag = f"{save_status}" + ("_reconciled" if reconciled else "")
            fx = Fixture(plan=[], save_status=save_status, reconciled=reconciled).start()
            page = browser.new_page()
            page.goto(fx.url + "/save")
            with patch.object(page, "remove_listener", wraps=page.remove_listener) as removed:
                body, confirmed = run_browser.save_and_capture(
                    page, lambda: page.locator("#status").inner_text(), timeout=1)
            check(f"delayed_save_{tag}_captures_payload", body == b"fixture-payload")
            check(f"save_{tag}_confirmation_matches_outcome", confirmed == (save_status == 200))
            check(f"save_{tag}_removes_callback", removed.call_count == 1)
            page.close()
            fx.stop()

        fx = Fixture(plan=[]).start()
        page = browser.new_page()
        page.goto(fx.url + "/nosave")
        with patch.object(page, "remove_listener", wraps=page.remove_listener) as removed:
            result = run_browser.save_and_capture(page, lambda: "unsaved", timeout=0.2)
        check("save_timeout_rejects_missing_request", result == (None, False))
        check("save_timeout_removes_callback", removed.call_count == 1)
        def unavailable_status():
            raise RuntimeError("status unavailable")
        page.goto(fx.url + "/save")
        with patch.object(page, "remove_listener", wraps=page.remove_listener) as removed:
            try:
                run_browser.save_and_capture(page, unavailable_status, timeout=1)
                check("save_status_error_propagates", False)
            except RuntimeError:
                check("save_status_error_propagates", True)
        check("save_status_error_removes_callback", removed.call_count == 1)
        page.close()
        fx.stop()
        browser.close()

    print(f"\n{len(failures)} failed", flush=True)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
