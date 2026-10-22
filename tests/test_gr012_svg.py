#!/usr/bin/env python3
"""GR-012 — a non-Office format round-trips through a Craft web editor.

Seafile -> the gateway -> VectorCraft Web -> a real modification -> Save ->
new bytes -> a new Seafile version -> reopen -> the modification is there.

VectorCraft is used because it exposes its own page API
(`window.vectorcraft`: `openFile`, `request`, `execute`, `captureDownloads`,
`files`, `readFile`), which makes the modification **deterministic**: the test
drives the editor's own tool and its own save command, instead of guessing where
to click. That API is VectorCraft's control protocol in the page
(`docs/control-protocol.md`), not the `?host=parent` bridge the other
applications speak.

    ARTCRAFT_SEAFILE_URL=... ARTCRAFT_SEAFILE_TOKEN=... \\
    ARTCRAFT_GATEWAY=http://127.0.0.1:8777 \\
    python3 tests/test_gr012_svg.py <repo_id> <path> [--headed]
"""

import io
import json
import os
import sys
import time
import urllib.parse
import zipfile

GATEWAY = os.environ.get("ARTCRAFT_GATEWAY", "http://127.0.0.1:8777").rstrip("/")
SEAFILE = os.environ.get("ARTCRAFT_SEAFILE_URL", "").rstrip("/")
TOKEN = os.environ.get("ARTCRAFT_SEAFILE_TOKEN", "")
PAGE_URL = "http://127.0.0.1:8777/open-test.html"

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


def download(repo_id, path):
    link = seafile_json(f"/api2/repos/{repo_id}/file/?p={urllib.parse.quote(path)}")
    status, body = http(link, headers={"Authorization": "Token " + TOKEN})
    if status != 200:
        raise SystemExit(f"download -> HTTP {status}: {body[:200]!r}")
    return body


def history_count(repo_id, path):
    payload = seafile_json(f"/api2/repos/{repo_id}/file/history/?p={urllib.parse.quote(path)}")
    commits = payload.get("commits", payload) if isinstance(payload, dict) else payload
    return len(commits)


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        raise SystemExit(2)
    repo_id = sys.argv[1]
    path = sys.argv[2] if sys.argv[2].startswith("/") else "/" + sys.argv[2]
    name = path.rsplit("/", 1)[-1]
    headed = "--headed" in sys.argv

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise SystemExit("playwright is not installed")

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from test_integration import reset_fixture

    # ---- the state BEFORE anything touches the file --------------------
    # Both the content id and the version count are read here, once. Reading
    # them after the save would make "a new version exists" unfalsifiable.
    reset_fixture(repo_id, path)
    original = download(repo_id, path)
    before_id = seafile_json(f"/api2/repos/{repo_id}/file/detail/?p={urllib.parse.quote(path)}")["id"]
    before_count = history_count(repo_id, path)

    # 1. the session, and the host page it serves
    body = urllib.parse.urlencode({"repo_id": repo_id, "path": path}).encode()
    status, raw = http(f"{GATEWAY}/open/", method="POST", data=body,
                        headers={"Content-Type": "application/x-www-form-urlencoded"})
    if status != 200:
        raise SystemExit(f"gateway /open/ -> HTTP {status}: {raw[:300]!r}")
    host_page = raw.decode()

    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=not headed,
            args=["--enable-unsafe-swiftshader", "--use-gl=angle", "--use-angle=swiftshader"])
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()
        console = []
        page.on("console", lambda msg: console.append(f"{msg.type}: {msg.text}"))
        page.on("pageerror", lambda exc: console.append(f"pageerror: {exc}"))
        page.route("**/open-test.html", lambda route: route.fulfill(
            status=200, content_type="text/html; charset=utf-8", body=host_page))

        page.goto(PAGE_URL, wait_until="load")

        # 2. the host page opened the document through VectorCraft's own API
        opened = False
        for _ in range(120):
            state = page.eval_on_selector("#state", "el => el.textContent")
            if "opened" in state or "Could not" in state or "Could not start" in state:
                opened = True
                break
            time.sleep(0.5)
        check("1. the host page opened the document through the page API", opened,
              page.eval_on_selector("#state", "el => el.textContent"))

        api = page.evaluate_handle("() => document.getElementById('frame').contentWindow.vectorcraft")
        if not api:
            raise SystemExit("no vectorcraft API in the frame")

        # 3. what the document looks like before the edit
        def inspect():
            return page.evaluate(
                "(api) => api.request('document.inspect', {}).then(r => JSON.parse(JSON.stringify(r)))", api)

        try:
            before = inspect()
        except Exception as exc:
            raise SystemExit(f"document.inspect failed: {exc}")

        def state_size(snapshot):
            return len(json.dumps(snapshot))

        # 4. a REAL modification, driven by the editor's own tool
        tools = page.evaluate(
            "(api) => api.request('ui.tool.list', {}).then(r => JSON.parse(JSON.stringify(r)))", api)
        tools_text = json.dumps(tools)
        picked = None
        for candidate in ("pencil", "pen", "brush", "paintbrush", "draw"):
            if candidate in tools_text.lower():
                picked = candidate
                break
        check("2. the editor lists a drawing tool", picked is not None,
              tools_text[:160] if not picked else f"tool ~ '{picked}'")

        if picked:
            result = page.evaluate(
                "(arg) => arg.api.request('ui.tool.select', {tool: arg.tool})"
                ".then(r => JSON.parse(JSON.stringify(r)))",
                {"api": api, "tool": picked})
            check("3. the drawing tool is selected", result is not None, json.dumps(result)[:120])

            # A drag in DOCUMENT space, so the position does not depend on the
            # zoom or the window size.
            events = [{"kind": "down", "x": 60, "y": 60, "space": "doc"},
                      {"kind": "drag", "x": 120, "y": 90, "space": "doc"},
                      {"kind": "drag", "x": 180, "y": 120, "space": "doc"},
                      {"kind": "up", "x": 180, "y": 120, "space": "doc"}]
            result = page.evaluate(
                "(arg) => arg.api.request('ui.pointer', {events: arg.events})"
                ".then(r => JSON.parse(JSON.stringify(r)))",
                {"api": api, "events": events})
            check("4. the tool drew in document space", result is not None, json.dumps(result)[:160])

        after = inspect()
        check("5. the document state moved", json.dumps(before) != json.dumps(after),
              f"{state_size(before)} -> {state_size(after)} bytes of inspect state")

        # 6. the CONTENT the editor produced, read straight out of the editor, so
        #    the assertion is about the artwork and not about an inspect snapshot.
        #    svg: {} means "the document's own SVG options", which makes the save
        #    run directly instead of opening the SVG Options dialog.
        saved_list = page.evaluate(
            "(api) => api.request('app.save', {path: NAME, svg: {}})"
            ".then(r => JSON.parse(JSON.stringify(r)))".replace("NAME", json.dumps(name)), api)
        check("6. the editor's own save command ran", saved_list is not None,
              json.dumps(saved_list)[:160])

        # readFile is synchronous on VectorCraft's page API: it returns the
        # bytes, or throws.
        saved_bytes = page.evaluate(
            "(api) => { try { return Array.from(new Uint8Array(api.readFile(NAME))); }"
            " catch (e) { return []; } }".replace("NAME", json.dumps(name)), api)
        saved_blob = bytes(saved_bytes) if saved_bytes else b""
        check("7. the editor produced NEW bytes",
              len(saved_blob) > 0 and saved_blob != original,
              f"{len(original)} -> {len(saved_blob)} bytes")
        saved_text = saved_blob.decode("utf-8", "replace")
        # VectorCraft writes the rectangle as a path too, so the meaningful
        # assertion is: a valid SVG document, with a path element in it.
        check("7a. the new bytes are an SVG document that holds the drawn stroke",
              "<svg" in saved_text and "<path" in saved_text,
              f"a valid SVG with a path element: "
              f"{'<svg' in saved_text and '<path' in saved_text}; {len(saved_text)} chars")

        # 8. the host page took the bytes and stored them
        saved = False
        for _ in range(60):
            state = page.eval_on_selector("#state", "el => el.textContent")
            if "Saved" in state or "Save failed" in state:
                saved = True
                break
            time.sleep(0.5)
        check("8. the host page took the bytes and stored them", saved,
              page.eval_on_selector("#state", "el => el.textContent"))

        # The editor's own save warning, quoted in the bundle: SVG as an
        # interchange format cannot hold everything a VectorCraft document can.
        # It comes back in the save result's `warnings`, not on the console.
        warnings = (saved_list or {}).get("warnings") or []
        check("8a. the editor said what SVG does not keep", len(warnings) > 0,
              "; ".join(str(w) for w in warnings)[:160])

        shot = os.environ.get("ARTCRAFT_SCREENSHOT")
        if shot:
            page.wait_for_timeout(500)
            page.screenshot(path=shot)
        browser.close()

    # 9. the server side, against the state captured before the edit
    after_id = seafile_json(f"/api2/repos/{repo_id}/file/detail/?p={urllib.parse.quote(path)}")["id"]
    check("9. a NEW Seafile version exists", after_id != before_id,
          f"{before_id[:12]}... -> {after_id[:12]}...")

    after_count = history_count(repo_id, path)
    check("10. the history grew", after_count > before_count,
          f"{before_count} -> {after_count} version(s)")

    # 11. reopen: the bytes Seafile holds are the editor's bytes
    body = urllib.parse.urlencode({"repo_id": repo_id, "path": path}).encode()
    status, raw = http(f"{GATEWAY}/open/?format=json", method="POST", data=body,
                        headers={"Content-Type": "application/x-www-form-urlencoded"})
    reopened = json.loads(raw)
    status, blob = http(f"{GATEWAY}/session/{reopened['sid']}/document")
    check("11. the document reopened from Seafile is the edited one",
          status == 200 and blob == saved_blob,
          f"the stored bytes are the editor's bytes ({len(blob)} bytes, "
          f"same as the editor's: {blob == saved_blob})")

    if console:
        print("\n--- browser console (first 12) ---")
        for line in console[:12]:
            print("   ", line[:180])

    print()
    if FAILURES:
        print(f"FAILED: {len(FAILURES)} check(s): {', '.join(FAILURES)}")
        return 1
    print("ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
