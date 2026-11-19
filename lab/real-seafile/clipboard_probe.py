#!/usr/bin/env python3
"""WordCraft clipboard probe against the isolated deployment (LXC 115).

Why this file exists
--------------------
The 2026-11-17 hardware probe declared "paste is visible but not persisted in
the saved DOCX" after searching for the marker in the *raw* DOCX bytes:

    marker2 in body.decode("utf-8", "replace")          # hw_probe.py:289

DOCX is a ZIP whose parts are DEFLATE-compressed, so that check can never
match -- it fails even when the paste was persisted. This probe replaces the
byte search with a real decompression of ``word/document.xml`` and records the
clipboard permission state of the editor frame, so the cause can be told apart
instead of guessed.

Checks
------
  editor_frame_found / document_loaded
  copy_editor_to_system     Ctrl+A, Ctrl+C, then three readers:
                            navigator.clipboard.readText() in the editor frame,
                            in the top page, and wl-paste on the real session
  clipboard_permission_state  Permissions-Policy view of clipboard-read/write
  paste_system_to_editor    wl-copy -> Ctrl+V -> Ctrl+S -> download -> unzip
  paste_survives_save       marker present in the *decompressed* saved DOCX
  paste_survives_reopen     marker present after a fresh browser context

Usage (on the Omarchy desktop, real Wayland session):

    SEAFILE_URL=... BRIDGE_URL=... ADMIN_EMAIL=... ADMIN_PASSWORD=... \
      python3 lab/real-seafile/clipboard_probe.py --results /tmp/clip

Writes ``clipboard.json`` and screenshots under --results. Never prints
credentials. Exits 0 only when every check passes.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import zipfile
from io import BytesIO

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_slice as rs  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

SEAFILE = rs.SEAFILE
BRIDGE = rs.BRIDGE
ADMIN = rs.ADMIN
ADMIN_PW = rs.ADMIN_PW

# The real desktop session is not inherited by background shells.
os.environ.setdefault("WAYLAND_DISPLAY", "wayland-1")
os.environ.setdefault("XDG_RUNTIME_DIR", "/run/user/1000")
DISP_ENV = dict(os.environ)


def docx_text(body: bytes) -> str:
    """Concatenate the decompressed XML of the main document part(s).

    This is the whole point of the probe: a DOCX marker is invisible to a raw
    byte search because the part is DEFLATE-compressed.
    """
    out = []
    with zipfile.ZipFile(BytesIO(body)) as z:
        for name in z.namelist():
            if name == "word/document.xml" or name.startswith("word/header") or name.startswith("word/footer"):
                out.append(z.read(name).decode("utf-8", "replace"))
    return "".join(out)


def status_text(host):
    if host is None:
        return ""
    try:
        return host.evaluate(
            "document.getElementById('status') ? document.getElementById('status').textContent : ''"
        ).strip()
    except Exception:  # noqa: BLE001
        return ""


def wait_status(host, want, timeout=90):
    end = time.time() + timeout
    while time.time() < end:
        s = status_text(host)
        if want(s):
            return s
        time.sleep(1)
    return status_text(host)


def find_frames(page, timeout=120):
    """Return (host_frame, editor_frame) for the bridge host and the editor bundle."""
    end = time.time() + timeout
    host = editor = None
    while time.time() < end:
        for f in page.frames:
            if f.url.startswith(BRIDGE + "/edit/"):
                host = f
            elif f.url.startswith(BRIDGE + "/editors/"):
                editor = f
        if host is not None and editor is not None:
            return host, editor
        page.wait_for_timeout(800)
    return host, editor


def login(page, email, pw):
    page.goto(SEAFILE + "/accounts/login/", wait_until="domcontentloaded")
    page.wait_for_selector("input[name=login]", timeout=30000)
    page.fill("input[name=login]", email)
    page.fill("input[name=password]", pw)
    page.click("button[type=submit], input[type=submit]")
    page.wait_for_url(lambda u: "/accounts/login" not in u, timeout=30000)
    return "/accounts/login" not in page.url


def open_doc(page, repo_id, name="clipboard.docx"):
    page.goto(f"{SEAFILE}/lib/{repo_id}/file/{name}", wait_until="domcontentloaded")
    host, editor = find_frames(page)
    s = wait_status(host, lambda t: "ready" in t.lower(), 120)
    return host, editor, s


def click_editor(page):
    box = page.locator("#office-frame").bounding_box()
    if not box:
        return False
    page.mouse.click(box["x"] + box["width"] / 2, box["y"] + 60 + (box["height"] - 60) / 2)
    return True


def read_os_clipboard():
    try:
        return subprocess.run(["wl-paste", "--no-newline"], capture_output=True, text=True,
                              env=DISP_ENV, timeout=10).stdout
    except Exception as exc:  # noqa: BLE001
        return f"<wl-paste error: {exc}>"


def write_os_clipboard(text):
    subprocess.run(["wl-copy", text], env=DISP_ENV, timeout=10, check=False)


PERM_JS = """async () => {
    const out = {origin: location.origin};
    for (const name of ['clipboard-read', 'clipboard-write']) {
        try {
            const st = await navigator.permissions.query({name});
            out[name] = st.state;
        } catch (e) { out[name] = 'query-failed: ' + String(e); }
    }
    out.secureContext = window.isSecureContext;
    // A readText() can hang waiting for a gesture; never let it block the probe.
    try {
        out.readText = await Promise.race([
            navigator.clipboard.readText(),
            new Promise(r => setTimeout(() => r('<timeout>'), 3000)),
        ]);
    } catch (e) { out.readTextError = String(e).slice(0, 300); }
    return out;
}"""


DELEGATE_JS = """
(() => {
  if (ONLY_TOP && window !== window.top) return;
  const orig = document.createElement.bind(document);
  document.createElement = function (tag) {
    const el = orig.apply(document, arguments);
    if (String(tag).toLowerCase() === 'iframe') {
      try { el.setAttribute('allow', 'clipboard-read; clipboard-write; fullscreen'); } catch (e) {}
    }
    return el;
  };
})();
"""


def delegate_script(only_top: bool) -> str:
    return DELEGATE_JS.replace("ONLY_TOP", "true" if only_top else "false")


def clipboard_permissions(frame):
    """Ask a frame what it is actually allowed to do with the clipboard."""
    if frame is None:
        return {"error": "no frame"}
    try:
        return frame.evaluate(PERM_JS)
    except Exception as exc:  # noqa: BLE001
        return {"error": str(exc)[:300]}


def read_text(frame):
    """Read the clipboard in a frame without ever blocking on a stuck promise."""
    if frame is None:
        return "<no frame>"
    try:
        return frame.evaluate(
            """async () => {
                try {
                    return await Promise.race([
                        navigator.clipboard.readText(),
                        new Promise(r => setTimeout(() => r('<timeout>'), 3000)),
                    ]);
                } catch (e) { return '<error: ' + String(e).slice(0, 200) + '>'; }
            }"""
        )
    except Exception as exc:  # noqa: BLE001
        return f"<error: {exc}>"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default=os.environ.get("RESULTS_DIR", "/tmp/clipboard-probe"))
    ap.add_argument("--headless", action="store_true", help="default is headed on the real session")
    ap.add_argument("--delegate-clipboard", choices=("none", "top", "both"), default="none",
                    help="causation experiment: inject the missing iframe allow attribute "
                         "at runtime (top = Seahub frame only, both = Seahub + bridge host). "
                         "Changes nothing on disk; proves which boundary drops the permission.")
    args = ap.parse_args()
    os.makedirs(args.results, exist_ok=True)

    checks = []

    def check(name, ok, detail=""):
        checks.append({"name": name, "ok": bool(ok), "detail": str(detail)[:1500]})
        print(("PASS " if ok else "FAIL ") + name + (f"  -- {detail}" if detail else ""), flush=True)
        return bool(ok)

    token = rs.api_token(ADMIN, ADMIN_PW)
    st, repo = rs.api(token, "POST", "/api2/repos/", {"name": f"clipboard-{int(time.time())}"})
    repo_id = repo["repo_id"]
    original = rs.minimal_docx("clipboard probe")
    rs.upload(token, repo_id, "clipboard.docx", original)

    marker_type = "copy" + os.urandom(4).hex()
    marker_paste = "paste" + os.urandom(4).hex()
    outcome = {"checks": checks, "marker_type": marker_type, "marker_paste": marker_paste}

    try:
        with sync_playwright() as p:
            gpu_args = [
                "--ozone-platform=wayland",
                "--enable-unsafe-webgpu",
                "--enable-features=Vulkan",
                "--ignore-gpu-blocklist",
                "--disable-dev-shm-usage",
                "--window-position=100,100",
                "--window-size=1400,900",
            ]
            browser = p.chromium.launch(headless=args.headless, args=([] if args.headless else gpu_args))
            ctx = browser.new_context(viewport={"width": 1400, "height": 867})
            if args.delegate_clipboard in ("top", "both"):
                ctx.add_init_script(delegate_script(only_top=(args.delegate_clipboard == "top")))
            if args.delegate_clipboard == "both":
                # The bridge host iframe lives in static HTML, so createElement patching
                # cannot reach it: rewrite the host document on the wire instead.
                def _host_route(route):
                    if route.request.resource_type != "document":
                        return route.continue_()
                    resp = route.fetch()
                    body = resp.text().replace(
                        '<iframe id="frame" title="editor" sandbox=',
                        '<iframe id="frame" title="editor" allow="clipboard-read; clipboard-write" sandbox=')
                    return route.fulfill(response=resp, body=body)
                ctx.route("**/edit/**", _host_route)
            page = ctx.new_page()
            ok = login(page, ADMIN, ADMIN_PW)
            check("browser_login", ok, page.url[:80])

            host, editor, s0 = open_doc(page, repo_id)
            check("editor_frame_found", host is not None and editor is not None,
                  f"host={bool(host)} editor={bool(editor)} status={s0!r}")
            check("document_loaded", "ready" in s0.lower(), f"status={s0!r}")

            # What the two iframes actually say, so the delegation experiment is
            # verifiable instead of assumed.
            def iframe_attrs(frame):
                if frame is None:
                    return {"error": "no frame"}
                try:
                    return frame.evaluate(
                        "() => [...document.querySelectorAll('iframe')].map(f => ({"
                        "src: (f.src || '').slice(0, 60),"
                        "allow: f.getAttribute('allow'),"
                        "sandbox: f.getAttribute('sandbox')}))")
                except Exception as exc:  # noqa: BLE001
                    return {"error": str(exc)[:200]}

            outcome["iframe_attrs"] = {"top_page": iframe_attrs(page.main_frame),
                                       "bridge_host": iframe_attrs(host)}
            print("iframe attrs:", json.dumps(outcome["iframe_attrs"])[:600], flush=True)

            perms = {
                "top_page": clipboard_permissions(page.main_frame),
                "bridge_host": clipboard_permissions(host),
                "editor": clipboard_permissions(editor),
            }
            outcome["clipboard_permissions"] = perms
            check("clipboard_permission_state", True, json.dumps(perms)[:900])

            # ---- copy: editor -> system -----------------------------------
            write_os_clipboard("clipboard-sentinel-" + os.urandom(3).hex())
            click_editor(page)
            page.keyboard.press("Control+End")
            page.keyboard.type(marker_type, delay=25)
            wait_status(host, lambda t: "unsaved" in t.lower(), 15)
            page.keyboard.press("Control+a")
            page.wait_for_timeout(300)
            page.keyboard.press("Control+c")
            page.wait_for_timeout(1500)

            editor_clip = read_text(editor)
            top_clip = read_text(page.main_frame)
            os_clip = read_os_clipboard()
            outcome["copy"] = {"editor_frame": editor_clip[:200], "top_page": top_clip[:200],
                               "os_clipboard": os_clip[:200], "os_len": len(os_clip)}
            copied = marker_type in editor_clip or marker_type in top_clip or marker_type in os_clip
            check("copy_editor_to_system", copied,
                  f"marker={marker_type} os_len={len(os_clip)} os_starts={os_clip[:40]!r} "
                  f"editor_has={marker_type in editor_clip} top_has={marker_type in top_clip}")

            page.screenshot(path=os.path.join(args.results, "clipboard-copy.png"))

            # ---- paste: system -> editor ----------------------------------
            write_os_clipboard(marker_paste)
            page.wait_for_timeout(500)
            click_editor(page)
            page.keyboard.press("Control+a")
            page.wait_for_timeout(300)
            page.keyboard.press("Control+v")
            dirty = wait_status(host, lambda t: "unsaved" in t.lower(), 15)
            check("paste_system_to_editor", "unsaved" in dirty.lower(), f"status={dirty[:80]!r}")

            n_before = len(rs.history(token, repo_id, "clipboard.docx"))
            page.keyboard.press("Control+s")
            saved = wait_status(host, lambda t: "saved to seafile" in t.lower(), 90)
            check("save_confirmed", "saved to seafile" in saved.lower(), saved[:80])

            hist = rs.history(token, repo_id, "clipboard.docx")
            grew = len(hist) > n_before
            creator = bool(hist) and hist[0].get("creator") == ADMIN
            check("save_creates_version", grew and creator,
                  f"history {n_before}->{len(hist)} grew={grew} creator_is_opener={creator}")

            body, _ = rs.download(token, repo_id, "clipboard.docx")
            text = docx_text(body)
            check("paste_survives_save", marker_paste in text,
                  f"marker={marker_paste} saved_len={len(body)} xml_len={len(text)} "
                  f"raw_byte_search_would_match={marker_paste.encode() in body}")
            check("typed_edit_survives_save", marker_type in text,
                  f"marker={marker_type} xml_len={len(text)}")
            outcome["saved_bytes"] = len(body)
            page.screenshot(path=os.path.join(args.results, "clipboard-saved.png"))

            # ---- reopen in a fresh context --------------------------------
            ctx2 = browser.new_context(viewport={"width": 1400, "height": 867})
            p2 = ctx2.new_page()
            login(p2, ADMIN, ADMIN_PW)
            host2, editor2, s2 = open_doc(p2, repo_id)
            check("reopen_editor_ready", "ready" in s2.lower(), f"status={s2!r}")
            body2, _ = rs.download(token, repo_id, "clipboard.docx")
            text2 = docx_text(body2)
            check("paste_survives_reopen", marker_paste in text2,
                  f"marker={marker_paste} xml_len={len(text2)}")
            p2.screenshot(path=os.path.join(args.results, "clipboard-reopen.png"))
            browser.close()
    finally:
        try:
            rs.api(token, "DELETE", f"/api2/repos/{repo_id}/")
        except Exception:  # noqa: BLE001
            pass

    outcome["passed"] = sum(1 for c in checks if c["ok"])
    outcome["failed"] = sum(1 for c in checks if not c["ok"])
    outcome["ok"] = outcome["failed"] == 0
    with open(os.path.join(args.results, "clipboard.json"), "w") as fh:
        json.dump(outcome, fh, indent=1)
    print(f"\n{outcome['passed']}/{len(checks)} checks passed -> {args.results}/clipboard.json")
    return 0 if outcome["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
