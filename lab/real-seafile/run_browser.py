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
    }
    ids = {name: rs.upload(admin, repo_id, name, content) for name, (_, content, _) in fixtures.items()}
    figcraft_fixture = None

    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist",
                                          "--enable-webgl", "--disable-dev-shm-usage"])
        ctx = browser.new_context(viewport={"width": 1400, "height": 900}, ignore_https_errors=True)
        page = ctx.new_page()
        console: list[str] = []
        page.on("console", lambda m: console.append(f"[{m.type}] {m.text}"[:300]))
        page.on("pageerror", lambda e: console.append(f"[pageerror] {e}"[:300]))

        # login
        page.goto(f"{rs.SEAFILE}/accounts/login/", wait_until="domcontentloaded")
        page.fill("input[name=login]", rs.ADMIN)
        page.fill("input[name=password]", rs.ADMIN_PW)
        page.click("button[type=submit], input[type=submit]")
        page.wait_for_url(lambda u: "/accounts/login" not in u, timeout=30000)
        check("browser_login", "/accounts/login" not in page.url, page.url)

        # FigCraft has no file format we can write by hand: let the app make one through its page
        # API on the standalone editor page, then upload it to Seafile and run the host flow on it.
        try:
            fig = ctx.new_page()
            fig.goto(f"{rs.BRIDGE}/editors/figcraft/index.html", wait_until="commit", timeout=60000)
            fig.wait_for_function("typeof window.figcraft === 'object'", timeout=120000)
            fig.wait_for_function("window.figcraft.commands().then(() => true).catch(() => false)", timeout=120000)
            made = fig.evaluate("""async () => {
                const f = window.figcraft;
                f.captureDownloads(true);
                try { await f.execute('node.create', {kind: 'frame', name: 'Home'}); } catch (e) {}
                const r = await f.execute('file.save', {path: 'test.figcraft'});
                if (r && r.pending) { try { await f.request('ui.dialog.confirm', {}); } catch (e) {} }
                for (let i = 0; i < 40; i++) {
                    const files = f.files() || [];
                    const hit = files.find(x => String(x.path).endsWith('test.figcraft'));
                    if (hit) { const b = f.readFile('test.figcraft'); return Array.from(b); }
                    await new Promise(r => setTimeout(r, 250));
                }
                return null;
            }""")
            fig.close()
            if made:
                figcraft_fixture = bytes(made)
                ids["test.figcraft"] = rs.upload(admin, repo_id, "test.figcraft", figcraft_fixture)
                fixtures["test.figcraft"] = ("figcraft", figcraft_fixture, "")
            check("figcraft_fixture_made_by_the_app", bool(made), f"{len(made) if made else 0} bytes")
        except Exception as e:  # noqa: BLE001
            check("figcraft_fixture_made_by_the_app", False, str(e)[:300])

        for name, (editor, content, query) in fixtures.items():
            app = editor
            t0 = time.time()
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
            check(f"{editor}_save_creates_seafile_version_by_user", saved and after[0]["creator"] == admin_username,
                  f"history {len(before)}->{len(after)} top={after[0] if after else None} status={status()!r}")
            if saved:
                got, _ = rs.download(admin, repo_id, name)
                check(f"{editor}_saved_bytes_look_like_{name.rsplit('.',1)[1]}", rs.content_matches(name, got), f"len={len(got)}")

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
