#!/usr/bin/env python3
"""Synthetic ONLYOFFICE ODT regression. Runtime NOT RUN until executed in the lab.

Uses trusted browser input only. DocServer's save UI is observation, not proof
of Seafile persistence: the callback may run only after the last client closes.
No command-service save, edited-byte upload, or browser download is accepted.
"""
from __future__ import annotations

import io
import json
import os
import re
from pathlib import Path
import time
import traceback
import uuid
import xml.etree.ElementTree as ET
import zipfile

OFFICE = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
TEXT = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"


def odt_text(data):
    """Read only ODF office:body/office:text paragraphs, never package metadata."""
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            if archive.read("mimetype") != b"application/vnd.oasis.opendocument.text":
                raise ValueError("not ODT")
            info = archive.getinfo("content.xml")
            if info.file_size > 8 * 1024 * 1024:
                raise ValueError("ODT content exceeds lab limit")
            root = ET.fromstring(archive.read(info))
        body = root.find(f"{{{OFFICE}}}body/{{{OFFICE}}}text")
        if root.tag != f"{{{OFFICE}}}document-content" or body is None:
            raise ValueError("missing ODF text body")
        # Deleted revisions are stored under the body but are not current text.
        for parent in body.iter():
            for child in list(parent):
                if child.tag == f"{{{TEXT}}}tracked-changes":
                    parent.remove(child)
        return "\n".join("".join(p.itertext()) for p in body.iter()
                         if p.tag in (f"{{{TEXT}}}p", f"{{{TEXT}}}h"))
    except (zipfile.BadZipFile, KeyError, ET.ParseError, RuntimeError) as exc:
        raise ValueError("unreadable ODT") from exc


def persisted_revision(before, after, user):
    """A changed object alone is insufficient: require a new user-attributed commit."""
    return bool(before and after and after[0].get("id")
                and after[0]["id"] not in {row.get("id") for row in before}
                and after[0].get("rev_file_id")
                and after[0]["rev_file_id"] != before[0].get("rev_file_id")
                and after[0].get("creator") == user)


def main():
    # Lazy imports keep the semantic-reader regression entirely offline/stdlib.
    import run_slice as rs
    import run_browser as rb
    from playwright.sync_api import sync_playwright

    os.umask(0o077)
    results = Path(rs.RESULTS)
    results.mkdir(parents=True, exist_ok=True)
    checks = []
    evidence = {"checks": checks, "save_ui_scope": "DocServer UI only; Seafile callback proved separately",
                "runtime": "RUNNING"}

    def require(name, ok):
        checks.append({"name": name, "ok": bool(ok)})
        print(("PASS " if ok else "FAIL ") + name, flush=True)
        if not ok:
            raise AssertionError(name)

    try:
        token = rs.api_token(rs.ADMIN, rs.ADMIN_PW)
        status, account = rs.api(token, "GET", "/api2/account/info/")
        require("authenticated_api_user", status == 200 and bool(account.get("email")))
        user = account["email"]
        status, repo = rs.api(token, "POST", "/api2/repos/",
                              {"name": "onlyoffice-browser-" + uuid.uuid4().hex})
        require("fresh_synthetic_library", status == 200 and bool(repo.get("repo_id")))
        repo_id = repo["repo_id"]
        evidence["repo_id"] = repo_id
        name = "onlyoffice-regression.odt"
        original = rs.minimal_odt()
        baseline = odt_text(original)
        require("fixture_has_baseline", baseline == "hello")
        rs.upload(token, repo_id, name, original)  # Setup only; never upload edited bytes.
        markers = ["ooedit" + uuid.uuid4().hex, "ooreopen" + uuid.uuid4().hex]
        evidence["markers"] = markers
        downloads = []
        with sync_playwright() as p:
            browser = p.chromium.launch(args=["--disable-dev-shm-usage"])
            try:
                # Each final Find query gets its own fresh authenticated editor.
                # No positive result from a previous query can satisfy it.
                rounds = [(marker, None) for marker in markers] + [
                    (None, value) for value in [baseline, *markers]]
                for round_no, (marker, query) in enumerate(rounds, 1):
                    before = rs.history(token, repo_id, name)
                    require(f"round{round_no}_history_available", bool(before))
                    ctx = browser.new_context(viewport={"width": 1400, "height": 900},
                                              ignore_https_errors=True)
                    ctx.set_default_timeout(30000)
                    rb.track_downloads(ctx, downloads)
                    try:
                        page = ctx.new_page()
                        page.on("console", lambda m: (results / "onlyoffice-console.txt").open("a").write(
                            f"{m.type}: {m.text[:300]}\n"))
                        page.on("requestfailed", lambda r: (results / "onlyoffice-console.txt").open("a").write(
                            f"REQFAIL {r.url[:200]} {r.failure}\n"))
                        page.goto(rs.SEAFILE + "/accounts/login/", wait_until="domcontentloaded")
                        page.fill("input[name=login]", rs.ADMIN)
                        page.fill("input[name=password]", rs.ADMIN_PW)
                        page.locator("button[type=submit], input[type=submit]").first.click()
                        page.wait_for_url(lambda url: "/accounts/login" not in url, timeout=30000)
                        editor = rb.open_from_seafile_list(page, rs.SEAFILE, repo_id, name)
                        # Pump navigation before the shared frame helper's bounded scan.
                        try:
                            editor.wait_for_selector("iframe", timeout=60000)
                        except Exception:
                            # Private diagnostic only: never published, may contain a
                            # credential-bearing URL or host-supplied HTML.
                            (results / f"onlyoffice-round{round_no}-page.html").write_text(
                                editor.content(), errors="replace")
                            (results / f"onlyoffice-round{round_no}-url.txt").write_text(
                                editor.url, errors="replace")
                            raise
                        frame = rb.find_frame(editor, rs.ONLYOFFICE + "/", timeout=60, name="frameEditor")
                        if frame is None:
                            (results / f"onlyoffice-round{round_no}-frames.txt").write_text(
                                repr(rb.frames_dump(editor)), errors="replace")
                        # DocServer mounts a version-prefixed path (/9.4.0-<hash>/web-apps/...).
                        require(f"round{round_no}_actual_onlyoffice_frame",
                                frame is not None and "/web-apps/" in frame.url)
                        canvas = frame.locator("canvas#id_viewer").first
                        try:
                            canvas.wait_for(state="visible", timeout=90000)
                        except Exception:
                            (results / f"onlyoffice-round{round_no}-frame.html").write_text(
                                frame.content(), errors="replace")
                            (results / f"onlyoffice-round{round_no}-canvas-count.txt").write_text(
                                f"{frame.locator('canvas').count()}\n")
                            raise
                        frame.locator("#editor_sdk").wait_for(state="visible", timeout=30000)
                        frame.locator("#toolbar").wait_for(state="visible", timeout=30000)
                        if marker is None:
                            # Final output must be opened by a new editor, not merely
                            # downloaded through the storage API. Native Find searches
                            # the parsed current document without injecting editor APIs.
                            editor.keyboard.press("Control+f")
                            search = frame.locator("#search-adv-text input")
                            search.wait_for(state="visible", timeout=30000)
                            frame.locator("#search-adv-results-number").filter(
                                has_text=re.compile(r"^No search results$")
                            ).wait_for(state="visible", timeout=30000)
                            search.fill(query)
                            search.press("Enter")
                            frame.locator("#search-adv-results-number").filter(
                                has_text=re.compile(r"\b[1-9][0-9]*\b")
                            ).wait_for(state="visible", timeout=30000)
                            require(f"final_reopen_current_text_{round_no - 3}", True)
                            editor.screenshot(path=str(results / f"onlyoffice-final-reopen-{round_no}.png"))
                            require(f"final_reopen_{round_no}_no_browser_download", not downloads)
                            continue
                        # Canvas readiness plus actual mutation/readback is mandatory; a
                        # missing frame/canvas cannot turn into a conditional pass.
                        # The overlay canvas above #id_viewer owns pointer input.
                        frame.locator("canvas#id_viewer_overlay").first.click(position={"x": 150, "y": 150})
                        editor.keyboard.press("Control+End")
                        editor.keyboard.press("Enter")
                        editor.keyboard.type(marker, delay=35)
                        editor.keyboard.press("Control+s")
                        editor.wait_for_timeout(3000)
                        # Retain only a fixed vocabulary from UI, never DOM/config/URLs.
                        ui = frame.locator("body").inner_text(timeout=10000).lower()
                        evidence[f"round{round_no}_save_ui"] = {
                            word: word in ui for word in ("saving", "saved", "all changes", "connection lost")}
                        screenshot = results / f"onlyoffice-round{round_no}-save.png"
                        if screenshot.exists():
                            screenshot.chmod(0o600)
                        editor.screenshot(path=str(screenshot))
                        editor.close()  # Last editor client close permits native callback.
                    finally:
                        ctx.close()  # No old editor client survives into the next round.
                    deadline = time.monotonic() + 180
                    proved = False
                    while time.monotonic() < deadline:
                        after = rs.history(token, repo_id, name)
                        if persisted_revision(before, after, user):
                            data, _ = rs.download(token, repo_id, name)  # API readback only.
                            text = odt_text(data)
                            stable = rs.history(token, repo_id, name)
                            if stable and stable[0] == after[0]:
                                text_l = text.lower()
                                proved = baseline in text and all(m.lower() in text_l for m in markers[:round_no])
                                if proved:
                                    evidence[f"round{round_no}_version"] = {
                                        "commit": after[0]["id"], "object": after[0]["rev_file_id"],
                                        "attributed_to_authenticated_user": True}
                                    break
                        time.sleep(2)
                    if not proved:
                        try:
                            data_after, _ = rs.download(token, repo_id, name)
                            tail = odt_text(data_after)[:400]
                        except Exception as exc:
                            tail = f"unreadable: {exc}"
                        (results / f"onlyoffice-round{round_no}-history.json").write_text(
                            json.dumps({"before": before, "after": rs.history(token, repo_id, name),
                                        "markers": markers[:round_no], "text": tail}, indent=2))
                    require(f"round{round_no}_new_user_version_and_body_readback", proved)
                    require(f"round{round_no}_no_browser_download", not downloads)
                evidence["runtime"] = "PASS"
            finally:
                browser.close()
    except Exception as exc:
        # Playwright/API exceptions can contain credential-bearing URLs or bodies.
        # The launcher results directory is private; this file must never be published.
        (results / "onlyoffice-private-error.txt").write_text(traceback.format_exc())
        evidence["runtime"] = "FAIL"
        evidence["error_type"] = type(exc).__name__
        print("FAIL onlyoffice_browser (details suppressed; inspect private evidence)", flush=True)
    finally:
        report = results / "onlyoffice-browser.json"
        if report.exists():
            report.chmod(0o600)
        with report.open("w") as output:
            json.dump(evidence, output, indent=2)
    return 0 if evidence["runtime"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
