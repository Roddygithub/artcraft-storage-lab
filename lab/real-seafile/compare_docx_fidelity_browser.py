#!/usr/bin/env python3
"""Open the same synthetic DOCX corpus through WordCraft and ONLYOFFICE.

Runs inside the isolated Playwright container. FIDELITY_VARIANT selects the Seahub route that
the parent runner has configured. A private state file under /state keeps the synthetic library
ID between variants; it is never copied into the committed evidence bundle.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from urllib.parse import urlsplit
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_slice as rs  # noqa: E402
import run_browser as rb  # noqa: E402
import docx_fidelity_corpus as corpus  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402


VARIANT = os.environ["FIDELITY_VARIANT"]
if VARIANT not in {"wordcraft", "onlyoffice"}:
    raise SystemExit("FIDELITY_VARIANT must be wordcraft or onlyoffice")
RESULTS = Path(os.environ.get("RESULTS_DIR", "/results")) / VARIANT
STATE = Path(os.environ.get("FIDELITY_STATE", "/state/library.json"))
BASE = rs.SEAFILE.rstrip("/")
BRIDGE = rs.BRIDGE.rstrip("/")
OUTCOME: dict = {"variant": VARIANT, "opened": []}
NETWORK_ERRORS: list[dict] = []


def _hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _prepare_library(token: str) -> tuple[str, dict[str, bytes]]:
    fixtures = corpus.corpus()
    if STATE.exists():
        saved = json.loads(STATE.read_text())
        repo = saved["repo"]
        expected = saved["sha256"]
        if expected != {name: _hash(data) for name, data in fixtures.items()}:
            raise RuntimeError("the private corpus state does not match the current deterministic fixture")
        for name, data in fixtures.items():
            got, _ = rs.download(token, repo, name)
            if _hash(got) != expected[name]:
                raise RuntimeError("fixture readback changed before the comparison")
        return repo, fixtures

    st, result = rs.api(token, "POST", "/api2/repos/", {"name": "ArtCraft synthetic DOCX fidelity"})
    if st != 200 or not isinstance(result, dict) or not result.get("repo_id"):
        raise RuntimeError("could not create the synthetic fidelity library")
    repo = result["repo_id"]
    expected = {name: _hash(data) for name, data in fixtures.items()}
    for name, data in fixtures.items():
        rs.upload(token, repo, name, data)
        got, _ = rs.download(token, repo, name)
        if _hash(got) != expected[name]:
            raise RuntimeError("Seafile fixture upload/readback hash mismatch")
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps({"repo": repo, "sha256": expected}, indent=2) + "\n")
    os.chmod(STATE, 0o600)
    return repo, fixtures


def _visible_text(page) -> str:
    bits = []
    for frame in page.frames:
        try:
            text = frame.locator("body").inner_text(timeout=1500)
            if text:
                bits.append(text[:12000])
        except Exception:  # editor canvases and cross-origin frames may not expose text
            pass
    return "\n".join(bits)


def _safe_location(url: str) -> str:
    """Keep only origin and path; never retain query strings or fragments."""
    parsed = urlsplit(url)
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"


def _dismiss_editor_tip(page, variant: str) -> None:
    if variant != "onlyoffice":
        return
    candidates = [page.get_by_text("Got it", exact=True)]
    candidates.extend(
        frame.get_by_text("Got it", exact=True)
        for frame in page.frames
        if "onlyoffice" in frame.url.lower()
    )
    for button in candidates:
        try:
            button.wait_for(state="visible", timeout=300)
            button.click(timeout=1000)
            return
        except Exception:
            pass


def _wait_for_editor(page, variant: str, timeout: int = 180) -> tuple[bool, bool]:
    end = time.monotonic() + timeout
    editor_frame_seen = False
    rendered_hint = False
    while time.monotonic() < end:
        frames = list(page.frames)
        if variant == "wordcraft":
            host = next((f for f in frames if f.name == "office_frame" or f.url.startswith(BRIDGE + "/edit/")), None)
            if host is not None:
                editor_frame_seen = True
                try:
                    status = host.evaluate("document.getElementById('status')?.textContent || ''")
                    rendered_hint = any(word in str(status).lower() for word in ("open", "ready", "loaded", "saved"))
                except Exception:
                    pass
        else:
            page_text = _visible_text(page).lower()
            if "error when prepare office online file preview page" in page_text:
                # Seahub's generic preparation failure is terminal. Waiting out the full
                # editor deadline can waste memory while an unusable document page is idle.
                return editor_frame_seen, False
            office_frames = [f for f in frames if "onlyoffice" in f.url.lower()]
            editor_frame_seen = bool(office_frames)
            for office in office_frames:
                try:
                    text = office.locator("body").inner_text(timeout=1000).lower()
                    rendered_hint = any(s in text for s in ("document editor", "main menu", "edit document"))
                    if not rendered_hint:
                        rendered_hint = office.locator("canvas").count() > 0
                except Exception:
                    continue
                if rendered_hint:
                    break
        if editor_frame_seen and rendered_hint:
            return editor_frame_seen, rendered_hint
        page.wait_for_timeout(1000)
    return editor_frame_seen, rendered_hint


def main() -> int:
    RESULTS.mkdir(parents=True, exist_ok=True)
    token = rs.api_token(rs.ADMIN, rs.ADMIN_PW)
    repo, fixtures = _prepare_library(token)
    OUTCOME["fixture_sha256"] = {name: _hash(data) for name, data in fixtures.items()}

    checks = []
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader",
                                          "--ignore-gpu-blocklist", "--enable-webgl", "--disable-dev-shm-usage"])
        ctx = browser.new_context(viewport={"width": 1440, "height": 1000}, ignore_https_errors=True)
        downloads = []
        def watch_page(new_page):
            new_page.on("download", lambda item: downloads.append(item.suggested_filename))
            new_page.on("requestfailed", lambda request: NETWORK_ERRORS.append({
                "kind": "request_failed",
                "location": _safe_location(request.url),
                "failure": (request.failure or "")[:160],
            }))
            new_page.on("response", lambda response: NETWORK_ERRORS.append({
                "kind": "http_error",
                "location": _safe_location(response.url),
                "status": response.status,
            }) if response.status >= 400 else None)

        ctx.on("page", watch_page)
        landing = ctx.new_page()
        watch_page(landing)
        landing.goto(f"{BASE}/accounts/login/", wait_until="domcontentloaded")
        landing.fill("input[name=login]", rs.ADMIN)
        landing.fill("input[name=password]", rs.ADMIN_PW)
        landing.click("button[type=submit], input[type=submit]")
        landing.wait_for_url(lambda url: "/accounts/login" not in url, timeout=30000)

        for name, content in fixtures.items():
            before, _ = rs.download(token, repo, name)
            before_hash = _hash(before)
            page = rb.open_from_seafile_list(landing, BASE, repo, name, timeout=45)
            frame_seen, rendered_hint = _wait_for_editor(page, VARIANT)
            _dismiss_editor_tip(page, VARIANT)
            visible = _visible_text(page)
            # The markers are synthetic and unique to this corpus case. Canvas-rendered text may
            # not be exposed to DOM; screenshot review remains the visual fidelity evidence.
            title = name.removeprefix("fidelity-").removesuffix(".docx").replace("-", " ")
            marker = {"prose": "Fidelity Case 1", "structure": "Fidelity Case 2", "layout": "Fidelity Case 3"}[title]
            marker_dom = marker.lower() in visible.lower()
            screenshot = RESULTS / f"{name.removesuffix('.docx')}.png"
            page.screenshot(path=str(screenshot), full_page=False)
            page2_screenshot = None
            if name == "fidelity-layout.docx" and frame_seen and rendered_hint:
                # Focus the document without editing, then move the caret to its end so both
                # editors scroll to the final page. Wheel-only scrolling proved unreliable in
                # ONLYOFFICE and could capture page 1 while naming it page 2.
                page.mouse.click(600, 390)
                page.keyboard.press("Control+End")
                page.wait_for_timeout(1500)
                page2_screenshot = RESULTS / "fidelity-layout-page2.png"
                page.screenshot(path=str(page2_screenshot), full_page=False)
            page.wait_for_timeout(1000)
            after, _ = rs.download(token, repo, name)
            after_hash = _hash(after)
            row = {
                "case": name,
                "editor_frame_seen": frame_seen,
                "render_ready_hint": rendered_hint,
                "case_title_in_dom_text": marker_dom,
                "seahub_prepare_error": "error when prepare office online file preview page" in visible.lower(),
                "screenshot": screenshot.name,
                "second_page_screenshot": page2_screenshot.name if page2_screenshot else None,
                "source_bytes_sha256": before_hash,
                "readback_unchanged": before_hash == after_hash,
            }
            checks.append(row)
            # Do not record or print the page URL, library ID, token, cookies, or raw DOM.
            print(f"{VARIANT}: {name}: frame={frame_seen} ready={rendered_hint} "
                  f"dom-title={marker_dom} unchanged={before_hash == after_hash}", flush=True)
            if page is not landing:
                page.close()
            landing.goto(f"{BASE}/library/{repo}/", wait_until="domcontentloaded")
        no_downloads = not downloads
        OUTCOME["opened"] = checks
        OUTCOME["network_errors"] = NETWORK_ERRORS
        OUTCOME["no_browser_downloads"] = no_downloads
        OUTCOME["checks_pass"] = all(
            row["editor_frame_seen"] and row["render_ready_hint"] and row["readback_unchanged"]
            for row in checks
        ) and no_downloads and len(checks) == len(fixtures)
        (RESULTS / "observations.json").write_text(json.dumps(OUTCOME, indent=2) + "\n")
        browser.close()
    return 0 if OUTCOME["checks_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
