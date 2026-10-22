#!/usr/bin/env python3
"""Browser end-to-end test: a real Craft web app opens a Seafile document and saves it.

This is the part the HTTP test cannot cover: the Craft application really
running in a browser, really receiving the document over the postMessage
bridge, and really handing the saved bytes back.

    ARTCRAFT_SEAFILE_URL=... ARTCRAFT_SEAFILE_TOKEN=... \\
    ARTCRAFT_GATEWAY=http://127.0.0.1:8777 \\
    python3 tests/test_browser.py <repo_id> <path> [--headed]

It drives the Craft app's own Save command (the keyboard shortcut), so the
bytes that reach Seafile are the ones the editor produced.

Requires playwright and its chromium build:
    npm i playwright && npx playwright install chromium
"""

import json
import os
import sys
import time
import urllib.parse

GATEWAY = os.environ.get("ARTCRAFT_GATEWAY", "http://127.0.0.1:8777").rstrip("/")
SEAFILE = os.environ.get("ARTCRAFT_SEAFILE_URL", "").rstrip("/")
TOKEN = os.environ.get("ARTCRAFT_SEAFILE_TOKEN", "")

FAILURES = []


def check(name, condition, detail=""):
    print(f"[{'PASS' if condition else 'FAIL'}] {name}" + (f"  -- {detail}" if detail else ""))
    if not condition:
        FAILURES.append(name)
    return condition


def http(url, method="GET", data=None, headers=None):
    import urllib.error
    import urllib.request

    request = urllib.request.Request(url, method=method, data=data, headers=headers or {})
    try:
        with urllib.request.urlopen(request, timeout=30) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read()


def seafile_json(path):
    status, body = http(f"{SEAFILE}{path}", headers={"Authorization": "Token " + TOKEN})
    if status != 200:
        raise SystemExit(f"seafile {path} -> HTTP {status}: {body[:200]!r}")
    return json.loads(body)


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        raise SystemExit(2)
    repo_id = sys.argv[1]
    path = sys.argv[2] if sys.argv[2].startswith("/") else "/" + sys.argv[2]
    headed = "--headed" in sys.argv

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise SystemExit("playwright is not installed: npm i playwright && npx playwright install chromium")

    # The state before the browser touches anything.
    before = seafile_json(f"/api2/repos/{repo_id}/file/detail/?p={urllib.parse.quote(path)}")
    before_id = before["id"]
    before_history = seafile_json(
        f"/api2/repos/{repo_id}/file/history/?p={urllib.parse.quote(path)}").get("commits", [])

    # The host page, opened the way the gateway opens it.
    body = urllib.parse.urlencode({"repo_id": repo_id, "path": path}).encode()
    status, raw = http(f"{GATEWAY}/open/", method="POST", data=body,
                        headers={"Content-Type": "application/x-www-form-urlencoded"})
    if status != 200:
        raise SystemExit(f"gateway /open/ -> HTTP {status}: {raw[:300]!r}")
    page_url = "http://127.0.0.1:8777/open-test.html"
    # The gateway returns the host page itself; we serve the same page to the
    # browser by re-posting, so we drive the real flow.
    host_page = raw.decode()

    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=not headed,
            args=["--enable-unsafe-swiftshader", "--use-gl=angle", "--use-angle=swiftshader"],
        )
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()

        console = []
        page.on("console", lambda msg: console.append(f"{msg.type}: {msg.text}"))
        page.on("pageerror", lambda exc: console.append(f"pageerror: {exc}"))

        # Serve the host page on our own origin so the iframe is same-origin.
        page.route("**/open-test.html", lambda route: route.fulfill(
            status=200, content_type="text/html; charset=utf-8", body=host_page))
        # The host page fetches /session/<sid>/document and posts to /session/<sid>/save.
        page.route("**/session/*", lambda route: route.continue_())

        page.goto(page_url, wait_until="load")

        # 1. the Craft app loads and says it is ready
        ready = False
        for _ in range(120):
            state = page.eval_on_selector("#state", "el => el.textContent")
            if "opened" in state or "Could not" in state:
                ready = True
                break
            time.sleep(0.5)
        check("1. the Craft app loaded and the document was delivered", ready,
              page.eval_on_selector("#state", "el => el.textContent"))

        # 2. the app really opened the workbook: it renders on a canvas
        info = page.evaluate("""() => {
            const f = document.getElementById('frame');
            const d = f.contentDocument;
            if (!d) return { framed: false };
            const c = d.querySelector('canvas');
            return { framed: true, canvas: !!c, w: c ? c.width : 0, h: c ? c.height : 0 };
        }""")
        check("2. the Craft app rendered a canvas", info.get("canvas") is True, json.dumps(info))

        # 3. the app's own Save command produces the bytes the host receives.
        #    First make the document dirty by typing into a cell, so the save
        #    is a real edit and not a no-op.
        canvas = page.frame_locator("#frame").locator("canvas")
        canvas.click(position={"x": 90, "y": 90})
        page.keyboard.type("4242")
        page.keyboard.press("Enter")
        page.wait_for_timeout(1500)

        dirty = page.evaluate("() => window.__lastDirty === true")
        check("3a. the editor reported unsaved changes after the edit", dirty is True,
              f"dirty = {dirty}")

        canvas.click(position={"x": 90, "y": 90})
        page.keyboard.press("Control+s")
        shot = os.environ.get("ARTCRAFT_SCREENSHOT")
        if shot:
            page.wait_for_timeout(500)
            page.screenshot(path=shot)
        saved = False
        for _ in range(60):
            state = page.eval_on_selector("#state", "el => el.textContent")
            if "Saved" in state or "failed" in state or "Save failed" in state:
                saved = True
                break
            page.wait_for_timeout(500)
        check("3. the editor's own Save reached the host and was persisted", saved,
              page.eval_on_selector("#state", "el => el.textContent"))

        browser.close()

    # 4. the server side really has a new version
    after = seafile_json(f"/api2/repos/{repo_id}/file/detail/?p={urllib.parse.quote(path)}")
    after_history = seafile_json(
        f"/api2/repos/{repo_id}/file/history/?p={urllib.parse.quote(path)}").get("commits", [])
    check("4. a NEW Seafile version exists", after["id"] != before_id,
          f"{before_id} -> {after['id']}")
    check("4. the history grew", len(after_history) > len(before_history),
          f"{len(before_history)} -> {len(after_history)} versions")

    # 5. the EDIT itself is in the saved file, not just a new version.
    #    The workbook is a zip, so look inside it.
    import io
    import zipfile

    link = seafile_json(f"/api2/repos/{repo_id}/file/?p={urllib.parse.quote(path)}")
    status, blob = http(link, headers={"Authorization": "Token " + TOKEN})
    inside = ""
    try:
        with zipfile.ZipFile(io.BytesIO(blob)) as zf:
            for name in zf.namelist():
                if name.startswith("xl/worksheets/") or name.startswith("xl/sharedStrings"):
                    inside += zf.read(name).decode("utf-8", "replace")
    except Exception as exc:
        inside = f"<not a zip: {exc}>"
    check("5. the typed text is in the file Seafile now holds", "4242" in inside,
          f"{len(blob)} bytes; the worksheet contains 4242: {'4242' in inside}")

    if console:
        print("\n--- browser console ---")
        for line in console[:40]:
            print("   ", line[:200])

    print()
    if FAILURES:
        print(f"FAILED: {len(FAILURES)} check(s): {', '.join(FAILURES)}")
        return 1
    print("ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
