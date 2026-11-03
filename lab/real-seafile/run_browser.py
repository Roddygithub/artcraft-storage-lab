#!/usr/bin/env python3
"""Browser slice: a real user path through real Seahub 13 -> bridge host page -> upstream
ArtCraft bundle, in headless Chromium (Playwright) inside the compose network.

Per editor (docx/WordCraft, xlsx/GridCraft, pdf/PdfCraft, dxf/CADCraft):
  1. log into Seahub, open /lib/<repo>/file/<name> (PDF with ?edit_pdf=true);
  2. Seahub's React WOPI page posts the access token to the bridge; a frame on the bridge
     origin appears (host page), which frames the editor bundle;
  3. wait for the editor's `<app>:ready`, the host's `open`, and the editor to load the bytes;
  4. ask the editor to save (Ctrl/Cmd+S inside the editor frame); the host relays PutFile;
  5. verify through the Seafile API that a new version by the user exists, and that the host
     page reports it.
Writes RESULTS_DIR/browser.json and screenshots.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_slice as rs  # noqa: E402  (reuse API helpers; stdlib only)

from playwright.sync_api import sync_playwright  # noqa: E402

RESULTS = os.environ.get("RESULTS_DIR", ".")
checks: list[dict] = []


def check(name, ok, detail=""):
    checks.append({"name": name, "ok": bool(ok), "detail": str(detail)[:1500]})
    print(("PASS " if ok else "FAIL ") + name + (f"  -- {detail}" if detail else ""), flush=True)
    return bool(ok)


def find_frame(page, prefix, timeout=60, name=None, parent=None):
    """Seahub posts the token into <iframe name="office_frame">; Playwright may keep reporting
    that frame's URL as about:blank after a form-POST navigation, so match by name/parent too."""
    end = time.time() + timeout
    while time.time() < end:
        for f in page.frames:
            if f.url.startswith(prefix):
                return f
            if name and f.name == name and (parent is None or f.parent_frame == parent):
                return f
            if parent is not None and f.parent_frame == parent and name is None:
                return f
        time.sleep(0.5)
    return None


def wait_for_saved_response(page, captured, timeout=180):
    """Bounded wait for the first successful (HTTP 200, nonempty) /relay/file capture on
    `captured` while pumping Playwright's synchronous event callbacks: sync Playwright only
    dispatches response callbacks inside Playwright calls, so a sleep-only loop over the
    Python list would starve them and never see a response that arrives while Python sleeps.
    Returns the captured body, or None on timeout."""
    end = time.time() + timeout
    while time.time() < end:
        for st, b in list(captured):
            if st == 200 and b:
                return b
        page.wait_for_timeout(1000)
    return None


def track_downloads(context, downloads):
    """Observe downloads on existing pages and popups, before navigation starts."""
    def attach(page):
        page.on("download", lambda download: downloads.append(download))
    context.on("page", attach)
    for page in context.pages:
        attach(page)


def save_and_capture(page, status_fn, timeout=90):
    """Capture the real save request and wait for host confirmation while pumping events."""
    bodies = []
    def capture(request):
        if request.method == "POST" and request.url.endswith("/relay/save"):
            body = request.post_data_buffer
            if body:
                bodies.append(body)
    page.on("request", capture)
    try:
        page.keyboard.press("Control+s")
        end = time.monotonic() + timeout
        while time.monotonic() < end:
            if bodies and (status_fn() or "").strip().lower() in (
                "saved to seafile", "saved (reconciled after a lost response)"
            ):
                return bodies[0], True
            page.wait_for_timeout(min(100, max(0, (end - time.monotonic()) * 1000)))
        return (bodies[0] if bodies else None), False
    finally:
        page.remove_listener("request", capture)


def open_from_seafile_list(page, base, repo_id, name, timeout=30):
    """Click the actual file-list link; Seahub may open it here or in a new tab."""
    page.goto(f"{base.rstrip('/')}/library/{repo_id}/", wait_until="domcontentloaded")
    previous_pages = set(page.context.pages)
    previous_url = page.url
    page.get_by_role("link", name=name, exact=True).click(timeout=timeout * 1000)
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        opened = [p for p in page.context.pages if p not in previous_pages]
        target = opened[-1] if opened else page
        if opened or page.url != previous_url:
            target.wait_for_load_state("domcontentloaded", timeout=timeout * 1000)
            return target
        page.wait_for_timeout(50)
    raise TimeoutError("file-list click did not open an editor page")


def frames_dump(page):
    return [(f.name, f.url[:70], (f.parent_frame.name if f.parent_frame else None)) for f in page.frames]


def main():
    os.makedirs(RESULTS, exist_ok=True)
    admin = rs.api_token(rs.ADMIN, rs.ADMIN_PW)
    st, me = rs.api(admin, "GET", "/api2/account/info/")
    admin_username = me.get("email", rs.ADMIN)
    st, repo = rs.api(admin, "POST", "/api2/repos/", {"name": f"browser-slice-{int(time.time())}"})
    repo_id = repo["repo_id"]
    fixtures = {
        "test.docx": ("wordcraft", rs.minimal_docx("hello from the browser slice"), ""),
        "test.xlsx": ("gridcraft", rs.minimal_xlsx(), ""),
        "test.pdf": ("pdfcraft", rs.MINIMAL_PDF, "?edit_pdf=true"),
        "test.dxf": ("cadcraft", rs.MINIMAL_DXF, ""),
        "test.svg": ("vectorcraft", rs.SVG_V1, ""),          # page-API shim, not an upstream bridge
        "test.pptx": ("deckcraft", rs.minimal_pptx(), ""),    # lab host.rs port, built from upstream source
        "test.png": ("photocraft", rs.MINIMAL_PNG, ""),       # lab host.rs port, built from upstream source
    }
    STATIC = "/app/lab/real-seafile/static"
    # Editors whose bundle is not in the lab (not built yet) are skipped, not failed.
    for name in list(fixtures):
        if not os.path.isdir(os.path.join(STATIC, fixtures[name][0])):
            print(f"skip {name}: no bundle for {fixtures[name][0]}", flush=True)
            del fixtures[name]
    ids = {name: rs.upload(admin, repo_id, name, content) for name, (_, content, _) in fixtures.items()}
    figcraft_fixture = None

    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist",
                                          "--enable-webgl", "--disable-dev-shm-usage"])
        ctx = browser.new_context(viewport={"width": 1400, "height": 900}, ignore_https_errors=True)
        # Standalone editor pages used only to make fixtures: Playwright's evaluate needs eval, which
        # the editor-page CSP forbids. The real host flow below keeps the CSP (that is part of the test).
        fixctx = browser.new_context(viewport={"width": 1200, "height": 800}, bypass_csp=True)
        page = ctx.new_page()
        console: list[str] = []
        downloads: list = []
        track_downloads(ctx, downloads)
        page.on("console", lambda m: console.append(f"[{m.type}] {m.text}"[:300]))
        page.on("pageerror", lambda e: console.append(f"[pageerror] {e}"[:300]))

        def attach(page):
            page.on("console", lambda m: console.append(f"[{m.type}] {m.text}"[:300]))
            page.on("pageerror", lambda e: console.append(f"[pageerror] {e}"[:300]))
            return page

        def wordcraft_real_edit_flow(page, name, content, box, status, before):
            """ROADMAP step 3, WordCraft DOCX slice: type a real change into the editor (trusted
            input through the browser input pipeline, no byte injection, no helper upload), Save
            through the bridge, then close this editor and reopen the file from Seafile in a
            fresh browser session; there the reopened editor must parse, display and re-save the
            saved content and accept a second typed interactive edit. Every capture follows the
            editor's own save/open paths (relay request bodies, Seafile history/API); markers
            are only ever typed into the focused editor."""
            marker = "browsertyped" + os.urandom(5).hex()   # alphanumeric: no autocorrect damage
            marker2 = "browserreopened" + os.urandom(5).hex()
            phrase = f" The typed marker is {marker}. "
            phrase2 = f" Reopened here, typed again: {marker2}. "

            # -- a real typed edit before Save: the marker is always INSERTED FIRST, and only
            #    then is the dirty state checked (an already-dirty editor cannot skip it) ----
            page.mouse.click(box["x"] + box["width"] / 2, box["y"] + 60 + (box["height"] - 60) / 2)
            time.sleep(1)
            page.keyboard.press("Control+End")           # caret to the end of the document
            page.keyboard.type(phrase, delay=30)
            def dirty():
                return "unsaved" in (status() or "").lower()
            end = time.time() + 15
            while time.time() < end and not dirty():
                time.sleep(0.5)
            if not dirty():
                # some builds swallow char-by-char typing: IME-style insert into the same
                # focused editor (still real input, never a file replacement)
                page.keyboard.insert_text(phrase)
                end = time.time() + 15
                while time.time() < end and not dirty():
                    time.sleep(0.5)
            check("wordcraft_typed_edit_before_save_is_visible_as_unsaved_changes", dirty(),
                  f"marker={marker} status={status()!r}")
            page.screenshot(path=os.path.join(RESULTS, "wordcraft-typed.png"))

            # -- Save (editor keeps focus; Ctrl+S inside the editor frame). The editor's own
            #    save payload is captured off the relay request the host page sends for it,
            #    so the marker is verified at the editor boundary before anything else. ---
            save_bodies: list = []
            def on_save_req(r):
                if r.method == "POST" and r.url.endswith("/relay/save"):
                    try:
                        b = r.post_data_buffer
                        if b:
                            save_bodies.append(b)
                    except Exception:  # noqa: BLE001
                        pass
            page.on("request", on_save_req)
            page.keyboard.press("Control+s")
            end = time.time() + 60
            confirmed = False
            while time.time() < end:
                if "saved to seafile" in (status() or "").lower():
                    confirmed = True
                    break
                time.sleep(1)
            check("wordcraft_save_request_carries_the_typed_marker",
                  bool(save_bodies) and marker.lower() in rs.docx_text(save_bodies[0]).lower(),
                  f"captured={len(save_bodies)} marker={marker}")
            page.remove_listener("request", on_save_req)
            check("wordcraft_save_confirmed_by_host_page", confirmed, f"status={status()!r}")
            after = before
            end = time.time() + 60
            while time.time() < end:
                after = rs.history(admin, repo_id, name)
                if len(after) > len(before):
                    break
                time.sleep(1)
            check("wordcraft_save_creates_seafile_version_by_user",
                  len(after) > len(before) and after[0]["creator"] == admin_username,
                  f"history {len(before)}->{len(after)} top={after[0] if after else None} status={status()!r}")

            # -- Seafile now holds the specific new text ---------------------------
            got, _ = rs.download(admin, repo_id, name)
            check("wordcraft_saved_docx_contains_the_typed_marker",
                  marker.lower() in rs.docx_text(got).lower(),
                  f"marker={marker} len={len(got)} bytes_identical_to_original={got == content}")
            check("wordcraft_save_is_not_identical_bytes", got != content, f"{len(content)} -> {len(got)} bytes")
            check("wordcraft_saved_docx_bytes_look_right", rs.content_matches(name, got), f"len={len(got)}")
            page.screenshot(path=os.path.join(RESULTS, "wordcraft-saved.png"))

            # -- close the old editor, reopen from Seafile in a fresh session ---------
            page.close()
            page = attach(ctx.new_page())
            reopen = browser.new_context(viewport={"width": 1400, "height": 900}, ignore_https_errors=True)
            track_downloads(reopen, downloads)
            reopen.on("page", attach)
            p2 = reopen.new_page()
            relay_file: list = []          # the reopened host page's own /relay/file fetches
            save2_bodies: list = []        # the reopened editor's own Ctrl+S save payloads
            def on_response(r):
                if r.url.endswith("/relay/file"):
                    try:
                        relay_file.append((r.status, r.body()))
                    except Exception:  # noqa: BLE001
                        pass
            def on_open_req(r):
                if r.method == "POST" and r.url.endswith("/relay/save"):
                    try:
                        b = r.post_data_buffer
                        if b:
                            save2_bodies.append(b)
                    except Exception:  # noqa: BLE001
                        pass
            reopen.on("response", on_response)
            reopen.on("request", on_open_req)
            p2.goto(f"{rs.SEAFILE}/accounts/login/", wait_until="domcontentloaded")
            p2.fill("input[name=login]", rs.ADMIN)
            p2.fill("input[name=password]", rs.ADMIN_PW)
            p2.click("button[type=submit], input[type=submit]")
            p2.wait_for_url(lambda u: "/accounts/login" not in u, timeout=30000)
            check("wordcraft_reopen_fresh_seafile_session", "/accounts/login" not in p2.url, p2.url)
            p2 = open_from_seafile_list(p2, rs.SEAFILE, repo_id, name)
            check("wordcraft_reopened_from_seafile_file_list", True)
            host2 = find_frame(p2, rs.BRIDGE + "/edit/", 60, name="office_frame", parent=p2.main_frame)
            check("wordcraft_reopen_host_frame_from_seahub", host2 is not None, f"frames={frames_dump(p2)}")
            def status2():
                if host2 is None:
                    return ""
                try:
                    return host2.evaluate("document.getElementById('status') ? document.getElementById('status').textContent : document.body.innerText.slice(0,200)")
                except Exception as e:  # noqa: BLE001
                    return f"<{e}>"
            body = wait_for_saved_response(p2, relay_file, 180)
            p2.screenshot(path=os.path.join(RESULTS, "wordcraft-reopened.png"))
            check("wordcraft_reopen_editor_ready_and_document_opened", body is not None,
                  f"relay/file responses={len(relay_file)} after {time.time()-t0:.0f}s")
            # the bytes the editor received on its own open path are the saved version
            check("wordcraft_reopen_bytes_identical_to_the_saved_version", body is not None and body == got,
                  f"len={len(body) if body else 0} vs saved {len(got)}")

            # Receiving bytes is not enough: the reopened editor must parse, display and
            # accept an interactive edit of what it loaded, and save it again. Type marker2
            # (inserted exactly once, first) and save again in the SAME reopened session.
            box2 = p2.locator("#office-frame").bounding_box()
            ok2 = False
            if host2 is not None and body is not None and box2 is not None:
                p2.mouse.click(box2["x"] + box2["width"] / 2, box2["y"] + 60 + (box2["height"] - 60) / 2)
                time.sleep(1)
                p2.keyboard.press("Control+End")
                p2.keyboard.type(phrase2, delay=30)
                def dirty2():
                    return "unsaved" in (status2() or "").lower()
                end = time.time() + 20
                while time.time() < end and not dirty2():
                    time.sleep(0.5)
                if not dirty2():
                    p2.keyboard.insert_text(phrase2)
                    end = time.time() + 15
                    while time.time() < end and not dirty2():
                        time.sleep(0.5)
                check("wordcraft_reopen_typed_edit_is_visible_as_unsaved_changes", dirty2(),
                      f"marker={marker2} status={status2()!r}")
                p2.keyboard.press("Control+s")
                end = time.time() + 60
                while time.time() < end:
                    if "saved to seafile" in (status2() or "").lower():
                        ok2 = True
                        break
                    time.sleep(1)
                check("wordcraft_reopen_save_confirmed_by_host_page", ok2, f"status={status2()!r}")
                before2 = len(after)          # history after the first save
                after2 = after
                end = time.time() + 60
                while time.time() < end and ok2:
                    after2 = rs.history(admin, repo_id, name)
                    if len(after2) > before2:
                        break
                    time.sleep(1)
                check("wordcraft_reopen_second_save_creates_seafile_version_by_user",
                      ok2 and len(after2) > before2 and after2[0]["creator"] == admin_username,
                      f"history {before2}->{len(after2)} top={after2[0] if after2 else None} status={status2()!r}")
                got2, _ = rs.download(admin, repo_id, name)
                check("wordcraft_reopen_seafile_holds_both_markers",
                      marker.lower() in rs.docx_text(got2).lower() and marker2.lower() in rs.docx_text(got2).lower(),
                      f"marker={marker2} len={len(got2)}")
            else:
                check("wordcraft_reopen_typed_edit_is_visible_as_unsaved_changes", False,
                      f"no editor/box/open bytes: host={host2 is not None} opened={body is not None} box={box2 is not None}")
                check("wordcraft_reopen_save_confirmed_by_host_page", False, "no editor flow at reopen")
                check("wordcraft_reopen_second_save_creates_seafile_version_by_user", False, "no editor flow at reopen")
                check("wordcraft_reopen_seafile_holds_both_markers", False, "no editor flow at reopen")
            p2.screenshot(path=os.path.join(RESULTS, "wordcraft-reopened-saved.png"))
            # semantic reopen, judged by the reopened editor's own behaviour: what it
            # re-serializes on Ctrl+S still contains the ORIGINAL typed marker (it parsed and
            # holds the saved content, not just the received bytes) and, separately, the
            # marker typed AFTER reopening (it rendered and accepted an interactive edit).
            check("wordcraft_reopen_editor_holds_the_original_marker",
                  bool(save2_bodies) and marker.lower() in rs.docx_text(save2_bodies[0]).lower(),
                  f"captured={len(save2_bodies)} marker={marker}")
            check("wordcraft_reopen_editor_holds_the_second_typed_marker",
                  bool(save2_bodies) and marker2.lower() in rs.docx_text(save2_bodies[0]).lower(),
                  f"captured={len(save2_bodies)} marker={marker2}")
            check("wordcraft_saves_did_not_download", not downloads, f"downloads={len(downloads)}")
            reopen.close()
            return page

        def gridcraft_real_edit_flow(page, name, content, box, status, before):
            """ROADMAP step 3, GridCraft XLSX slice: click an actual editor cell, type a
            distinct value with trusted mouse/keyboard input only, save through the existing
            host/bridge, then close this editor and reopen the same file from Seafile in a
            fresh authenticated session and type a second value there. Every assertion on the
            value is semantic (parsed out of the editor's own /relay/save payload and of the
            Seafile readback), on top of byte-level deltas and version attribution; downloads
            are tracked and none is ever accepted as a save."""
            marker = "gridtyped" + os.urandom(5).hex()
            marker2 = "gridreopened" + os.urandom(5).hex()

            def typed(p, bx, fx, fy, value, status_fn):
                """Click inside the editor frame at a relative point, type `value` into the
                focused cell and commit it (Enter); returns True when the host page shows
                unsaved changes. Char-by-char typing is retried as an IME-style insert into
                the SAME focused editor -- still real input, never a file replacement."""
                p.mouse.click(bx["x"] + bx["width"] * fx, bx["y"] + 60 + (bx["height"] - 60) * fy)
                p.wait_for_timeout(1000)
                p.keyboard.type(value, delay=30)
                p.keyboard.press("Enter")
                def dirty():
                    return "unsaved" in (status_fn() or "").lower()
                end = time.time() + 15
                while time.time() < end and not dirty():
                    p.wait_for_timeout(500)
                if not dirty():
                    p.keyboard.insert_text(value)
                    p.keyboard.press("Enter")
                    end = time.time() + 15
                    while time.time() < end and not dirty():
                        p.wait_for_timeout(500)
                return dirty()

            def semantic(cells, value):
                return any(v.casefold() == value for v in (cells or {}).values())

            def parse_or_fail(payload, tag):
                """A required-failure path: an unreadable payload must produce a FAILed
                check, never an assertion skipped to the generic path."""
                if payload is None:
                    check(f"gridcraft_{tag}_payload_is_a_readable_xlsx_with_the_value", False, "no /relay/save payload captured")
                    return None
                try:
                    return rs.xlsx_cells(payload)
                except ValueError as e:
                    check(f"gridcraft_{tag}_payload_is_a_readable_xlsx_with_the_value", False, str(e))
                    return None

            def host_status(host):
                if host is None:
                    return ""
                try:
                    return host.evaluate("document.getElementById('status') ? document.getElementById('status').textContent : document.body.innerText.slice(0,200)")
                except Exception as e:  # noqa: BLE001
                    return f"<{e}>"

            def version_by_user(prev):
                end = time.time() + 60
                hist = prev
                while time.time() < end:
                    hist = rs.history(admin, repo_id, name)
                    if len(hist) > len(prev):
                        return hist
                    time.sleep(1)
                return hist

            # -- first real edit: click an actual cell, type a distinct value ------------
            dirty1 = typed(page, box, 0.35, 0.30, marker, status)
            check("gridcraft_typed_edit_before_save_is_visible_as_unsaved_changes", dirty1,
                  f"marker={marker} status={status()!r}")
            page.screenshot(path=os.path.join(RESULTS, "gridcraft-typed.png"))

            # -- Save through the host/bridge; value verified inside the editor's own payload
            payload, confirmed = save_and_capture(page, status)
            payload_cells = parse_or_fail(payload, "save_request")
            if payload_cells is not None:
                check("gridcraft_save_request_carries_the_typed_value", semantic(payload_cells, marker),
                      f"payload={len(payload)}B marker={marker} cells={sorted(payload_cells)[:14]}")
            check("gridcraft_save_confirmed_by_host_page", confirmed, f"status={status()!r}")
            after = version_by_user(before)
            check("gridcraft_save_creates_seafile_version_by_user",
                  len(after) > len(before) and after[0]["creator"] == admin_username,
                  f"history {len(before)}->{len(after)} top={after[0] if after else None}")

            # -- Seafile now holds the specific new value (semantic) and differs by bytes --
            got, _ = rs.download(admin, repo_id, name)
            try:
                got_cells = rs.xlsx_cells(got)
                check("gridcraft_saved_xlsx_semantically_contains_the_typed_value", semantic(got_cells, marker),
                      f"marker={marker} cells={sorted(got_cells)[:14]}")
                check("gridcraft_saved_xlsx_keeps_the_fixture_value", got_cells.get("A1") == "1",
                      f"A1={got_cells.get('A1')!r} (the typed cell is not A1: click at 30% canvas height)")
            except ValueError as e:
                check("gridcraft_saved_xlsx_semantically_contains_the_typed_value", False, str(e))
                check("gridcraft_saved_xlsx_keeps_the_fixture_value", False, str(e))
            check("gridcraft_save_is_not_identical_bytes", got != content, f"{len(content)} -> {len(got)} bytes")
            check("gridcraft_saved_xlsx_bytes_look_right", rs.content_matches(name, got), f"len={len(got)}")
            page.screenshot(path=os.path.join(RESULTS, "gridcraft-saved.png"))

            # -- close the old editor, reopen from Seafile in a fresh session -------------
            page.close()
            page = attach(ctx.new_page())
            reopen = browser.new_context(viewport={"width": 1400, "height": 900}, ignore_https_errors=True)
            track_downloads(reopen, downloads)
            reopen.on("page", attach)       # downloads/responses tracked before any navigation
            p2 = reopen.new_page()
            relay_file: list = []           # the reopened host page's own /relay/file fetches
            def on_response(r):
                if r.url.endswith("/relay/file"):
                    try:
                        relay_file.append((r.status, r.body()))
                    except Exception:  # noqa: BLE001
                        pass
            reopen.on("response", on_response)
            p2.goto(f"{rs.SEAFILE}/accounts/login/", wait_until="domcontentloaded")
            p2.fill("input[name=login]", rs.ADMIN)
            p2.fill("input[name=password]", rs.ADMIN_PW)
            p2.click("button[type=submit], input[type=submit]")
            p2.wait_for_url(lambda u: "/accounts/login" not in u, timeout=30000)
            check("gridcraft_reopen_fresh_seafile_session", "/accounts/login" not in p2.url, p2.url)
            p2 = open_from_seafile_list(p2, rs.SEAFILE, repo_id, name)
            check("gridcraft_reopened_from_seafile_file_list", True)
            host2 = find_frame(p2, rs.BRIDGE + "/edit/", 60, name="office_frame", parent=p2.main_frame)
            check("gridcraft_reopen_host_frame_from_seahub", host2 is not None, f"frames={frames_dump(p2)}")
            def status2():
                return host_status(host2)
            body = wait_for_saved_response(p2, relay_file, 180)
            p2.screenshot(path=os.path.join(RESULTS, "gridcraft-reopened.png"))
            check("gridcraft_reopen_editor_ready_and_document_opened", body is not None,
                  f"relay/file responses={len(relay_file)} after {time.time()-t0:.0f}s")
            check("gridcraft_reopen_bytes_identical_to_the_saved_version", body is not None and body == got,
                  f"len={len(body) if body else 0} vs saved {len(got)}")
            try:
                body_cells = rs.xlsx_cells(body) if body else {}
                check("gridcraft_reopen_parsed_the_saved_value", semantic(body_cells, marker),
                      f"cells={sorted(body_cells)[:14]}")
            except ValueError as e:
                body_cells = None
                check("gridcraft_reopen_parsed_the_saved_value", False, str(e))

            # Receiving/parsing the saved bytes is not enough: the reopened editor must render
            # them and accept an interactive edit of the sheet, then save again through the
            # same bridge -- and its own payload must still hold the FIRST edit.
            box2 = p2.locator("#office-frame").bounding_box()
            payload2 = None
            if host2 is not None and body is not None and box2 is not None and body_cells is not None:
                dirty2 = typed(p2, box2, 0.60, 0.55, marker2, status2)
                check("gridcraft_reopen_typed_edit_is_visible_as_unsaved_changes", dirty2,
                      f"marker={marker2} status={status2()!r}")
                payload2, ok2 = save_and_capture(p2, status2)
                cells2 = parse_or_fail(payload2, "reopen_save_request")
                if cells2 is not None:
                    check("gridcraft_reopen_editor_holds_the_original_value", semantic(cells2, marker),
                          f"marker={marker} cells={sorted(cells2)[:14]}")
                    check("gridcraft_reopen_editor_holds_the_second_typed_value", semantic(cells2, marker2),
                          f"marker={marker2} cells={sorted(cells2)[:14]}")
                check("gridcraft_reopen_save_confirmed_by_host_page", ok2, f"status={status2()!r}")
                after2 = version_by_user(after)
                check("gridcraft_reopen_second_save_creates_seafile_version_by_user",
                      ok2 and len(after2) > len(after) and after2[0]["creator"] == admin_username,
                      f"history {len(after)}->{len(after2)} top={after2[0] if after2 else None}")
                got2, _ = rs.download(admin, repo_id, name)
                try:
                    got2_cells = rs.xlsx_cells(got2)
                    check("gridcraft_reopen_seafile_holds_both_values",
                          semantic(got2_cells, marker) and semantic(got2_cells, marker2),
                          f"marker={marker2} cells={sorted(got2_cells)[:14]}")
                except ValueError as e:
                    check("gridcraft_reopen_seafile_holds_both_values", False, str(e))
                check("gridcraft_second_save_is_not_identical_bytes", payload2 != payload,
                      f"{len(payload) if payload else 0} -> {len(payload2) if payload2 else 0} bytes")
            else:
                check("gridcraft_reopen_typed_edit_is_visible_as_unsaved_changes", False,
                      f"host={host2 is not None} opened={body is not None} box={box2 is not None} parsed={body_cells is not None}")
                check("gridcraft_reopen_editor_holds_the_original_value", False, "no reopened editor flow")
                check("gridcraft_reopen_editor_holds_the_second_typed_value", False, "no reopened editor flow")
                check("gridcraft_reopen_save_confirmed_by_host_page", False, "no reopened editor flow")
                check("gridcraft_reopen_second_save_creates_seafile_version_by_user", False, "no reopened editor flow")
                check("gridcraft_reopen_seafile_holds_both_values", False, "no reopened editor flow")
                check("gridcraft_second_save_is_not_identical_bytes", False, "no reopened editor flow")
            p2.screenshot(path=os.path.join(RESULTS, "gridcraft-reopened-saved.png"))
            check("gridcraft_saves_did_not_download", not downloads, f"downloads={len(downloads)}")
            reopen.close()
            return page

        # login
        page.goto(f"{rs.SEAFILE}/accounts/login/", wait_until="domcontentloaded")
        page.fill("input[name=login]", rs.ADMIN)
        page.fill("input[name=password]", rs.ADMIN_PW)
        page.click("button[type=submit], input[type=submit]")
        page.wait_for_url(lambda u: "/accounts/login" not in u, timeout=30000)
        check("browser_login", "/accounts/login" not in page.url, page.url)

        # Apps with no hand-writable format and no page API: let the standalone app save a new
        # document as a browser download, and use those bytes as the Seafile fixture.
        for editor, fname, ext in (("soundcraft", "test.scraft", "scraft"), ("designcraft", "test.designcraft", "designcraft")):
            if not os.path.isdir(os.path.join(STATIC, editor)):
                continue
            try:
                sp = fixctx.new_page()
                sp.goto(f"{rs.BRIDGE}/editors/{editor}/index.html?empty", wait_until="commit", timeout=60000)
                sp.wait_for_function("!document.getElementById('%s_loading')" % editor, timeout=120000)
                time.sleep(2)
                sp.mouse.click(600, 400)
                with sp.expect_download(timeout=30000) as dl:
                    sp.keyboard.press("Control+s")
                    time.sleep(2)
                    sp.keyboard.press("Enter")   # a name/format dialog, if the app shows one
                path = dl.value.path()
                data = open(path, "rb").read()
                sp.close()
                ids[fname] = rs.upload(admin, repo_id, fname, data)
                fixtures[fname] = (editor, data, "")
                check(f"{editor}_fixture_downloaded_from_the_app", len(data) > 0, f"{dl.value.suggested_filename} {len(data)} bytes")
            except Exception as e:  # noqa: BLE001
                check(f"{editor}_fixture_downloaded_from_the_app", False, str(e)[:300])

        # FigCraft has no file format we can write by hand: let the app make one through its page
        # API on the standalone editor page, then upload it to Seafile and run the host flow on it.
        if os.path.isdir(os.path.join(STATIC, "figcraft")):
            try:
                fig = fixctx.new_page()
                fig.goto(f"{rs.BRIDGE}/editors/figcraft/index.html?control", wait_until="commit", timeout=60000)   # ?control: opt-in page API
                # function form: the editor page's CSP forbids eval, which a string expression would use
                fig.wait_for_function("() => typeof window.figcraft === 'object'", timeout=120000)
                fig.wait_for_function("() => window.figcraft.commands().then(() => true).catch(() => false)", timeout=120000)
                made = fig.evaluate("""async () => {
                    const f = window.figcraft;
                    f.captureDownloads(true);
                    try { await f.execute('node.create', {kind: 'frame', name: 'Home'}); } catch (e) {}
                    // FigCraft's web build refuses a path ("no file system in the browser"): a plain
                    // Save goes through the download path, which captureDownloads keeps.
                    // ...and a path-less Save wants a path first: use the app's own shortcut through the
                    // control channel, then accept the name/format dialog.
                    try { await f.execute('file.save', {path: 'test.figcraft'}); } catch (e) {
                        try { await f.request('ui.key', {key: 's', cmd: true}); } catch (e2) {}
                        await new Promise(r => setTimeout(r, 800));
                        try { await f.request('ui.dialog.confirm', {}); } catch (e3) {}
                    }
                    for (let i = 0; i < 40; i++) {
                        const files = f.files() || [];
                        if (files.length) { const name = String(files[files.length - 1].path); const b = f.readFile(name); return {name, bytes: Array.from(b)}; }
                        await new Promise(r => setTimeout(r, 250));
                    }
                    return null;
                }""")
                fig.close()
                if made:
                    figcraft_fixture = bytes(made["bytes"])
                    fname = "test." + (made["name"].rsplit(".", 1)[-1] if "." in made["name"] else "figcraft")
                    ids[fname] = rs.upload(admin, repo_id, fname, figcraft_fixture)
                    fixtures[fname] = ("figcraft", figcraft_fixture, "")
                check("figcraft_fixture_made_by_the_app", bool(made), f"{made['name'] if made else ''} {len(made['bytes']) if made else 0} bytes")
            except Exception as e:  # noqa: BLE001
                check("figcraft_fixture_made_by_the_app", False, str(e)[:300])

        else:
            print("skip FigCraft fixture: no bundle for figcraft", flush=True)

        queue = list(fixtures.items())
        seen_native = set()
        while queue:
            name, (editor, content, query) = queue.pop(0)
            app = editor
            downloads.clear()
            t0 = time.time()
            if editor == "wordcraft":
                original = page
                page = open_from_seafile_list(page, rs.SEAFILE, repo_id, name)
                if page is not original:
                    attach(page)
                check("wordcraft_opened_from_seafile_file_list", True)
            elif editor == "gridcraft":
                original = page
                page = open_from_seafile_list(page, rs.SEAFILE, repo_id, name)
                if page is not original:
                    attach(page)
                check("gridcraft_opened_from_seafile_file_list", True)
            else:
                page.goto(f"{rs.SEAFILE}/lib/{repo_id}/file/{name}{query}", wait_until="domcontentloaded")
            host = find_frame(page, rs.BRIDGE + "/edit/", 60, name="office_frame", parent=page.main_frame)
            check(f"{editor}_host_frame_from_seahub", host is not None, f"frames={frames_dump(page)}")
            if host is None:
                page.screenshot(path=os.path.join(RESULTS, f"{editor}-no-host.png"))
                continue
            # Playwright does not expose the frames below a form-POST-navigated iframe here, so the
            # editor is driven through the page: focus by clicking inside it, then trusted key presses.
            box = page.locator("#office-frame").bounding_box()
            # host page status text reflects ready/open/dirty/saved
            def status():
                try:
                    return host.evaluate("document.getElementById('status') ? document.getElementById('status').textContent : document.body.innerText.slice(0,200)")
                except Exception as e:  # noqa: BLE001
                    return f"<{e}>"
            end = time.time() + 180
            opened = False
            while time.time() < end:
                s = status()
                if s and ("open" in s.lower() or "ready" in s.lower() or "loaded" in s.lower() or "saved" in s.lower()):
                    opened = True
                    break
                time.sleep(1)
            page.screenshot(path=os.path.join(RESULTS, f"{editor}-opened.png"))
            check(f"{editor}_editor_ready_and_document_opened", opened, f"status={status()!r} after {time.time()-t0:.0f}s")
            if not opened or box is None:
                continue
            before = rs.history(admin, repo_id, name)
            if editor == "wordcraft":
                # ROADMAP step 3 slice: real typed edit before Save + fresh-session reopen
                page = wordcraft_real_edit_flow(page, name, content, box, status, before)
                continue
            if editor == "gridcraft":
                # ROADMAP step 3 slice: real cell edit, save + fresh-session reopen
                page = gridcraft_real_edit_flow(page, name, content, box, status, before)
                continue
            # focus the editor canvas (below the host bar) and ask it to save
            page.mouse.click(box["x"] + box["width"] / 2, box["y"] + 60 + (box["height"] - 60) / 2)
            time.sleep(1)
            page.keyboard.press("Control+s")
            time.sleep(3)
            if status() and "sav" not in status().lower():
                page.keyboard.press("Meta+s")
                time.sleep(2)
            if status() and "sav" not in status().lower():
                page.screenshot(path=os.path.join(RESULTS, f"{editor}-after-ctrl-s.png"))
                page.keyboard.press("Enter")       # a save-options dialog, if the app opened one
            end = time.time() + 60
            saved = False
            while time.time() < end:
                after = rs.history(admin, repo_id, name)
                if len(after) > len(before):
                    saved = True
                    break
                time.sleep(1)
            page.screenshot(path=os.path.join(RESULTS, f"{editor}-saved.png"))
            after = rs.history(admin, repo_id, name)
            if not saved and downloads and editor not in seen_native:
                # The app saved under its own native name (e.g. test.deckcraft for a .pptx): the host
                # page turned that into a download. Use those bytes as a fixture in the native format
                # and run the flow again on it; the first pass is recorded as the export path.
                dl = downloads[-1]
                native_name = dl.suggested_filename
                data = open(dl.path(), "rb").read()
                seen_native.add(editor)
                check(f"{editor}_save_as_native_format_is_exported_as_download", len(data) > 0, f"{native_name} {len(data)} bytes; status={status()!r}")
                ids[native_name] = rs.upload(admin, repo_id, native_name, data)
                queue.append((native_name, (editor, data, "")))
                continue
            if not saved and editor in seen_native and "saved to seafile" in (status() or "").lower():
                # Native-format second pass: the app re-serialised the file it had just produced, so the
                # bytes are identical and Seafile records no new version. The bridge verified them.
                got, _ = rs.download(admin, repo_id, name)
                check(f"{editor}_native_save_verified_idempotent", got == content, f"history {len(before)}->{len(after)} status={status()!r}")
                continue
            check(f"{editor}_save_creates_seafile_version_by_user", saved and after[0]["creator"] == admin_username,
                  f"history {len(before)}->{len(after)} top={after[0] if after else None} status={status()!r}")
            if saved:
                got, _ = rs.download(admin, repo_id, name)
                check(f"{editor}_saved_{name.rsplit('.',1)[1]}_bytes_look_right", rs.content_matches(name, got), f"len={len(got)}")

        with open(os.path.join(RESULTS, "browser-console.log"), "w") as fh:
            fh.write("\n".join(console))
        browser.close()

    summary = {"ran_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "repo_id": repo_id,
               "passed": sum(c["ok"] for c in checks), "failed": sum(not c["ok"] for c in checks), "checks": checks}
    with open(os.path.join(RESULTS, "browser.json"), "w") as fh:
        json.dump(summary, fh, indent=1)
    print(f"\n{summary['passed']} passed, {summary['failed']} failed", flush=True)
    return 0 if summary["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
