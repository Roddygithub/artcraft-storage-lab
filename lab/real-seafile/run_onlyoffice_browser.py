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
from pathlib import Path
import time
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
                for round_no, marker in enumerate(markers, 1):
                    before = rs.history(token, repo_id, name)
                    require(f"round{round_no}_history_available", bool(before))
                    ctx = browser.new_context(viewport={"width": 1400, "height": 900},
                                              ignore_https_errors=True)
                    ctx.set_default_timeout(30000)
                    rb.track_downloads(ctx, downloads)
                    try:
                        page = ctx.new_page()
                        page.goto(rs.SEAFILE + "/accounts/login/", wait_until="domcontentloaded")
                        page.fill("input[name=login]", rs.ADMIN)
                        page.fill("input[name=password]", rs.ADMIN_PW)
                        page.locator("button[type=submit], input[type=submit]").first.click()
                        page.wait_for_url(lambda url: "/accounts/login" not in url, timeout=30000)
                        editor = rb.open_from_seafile_list(page, rs.SEAFILE, repo_id, name)
                        # Pump navigation before the shared frame helper's bounded scan.
                        editor.wait_for_selector("iframe", timeout=60000)
                        frame = rb.find_frame(editor, rs.ONLYOFFICE + "/web-apps/", timeout=60)
                        require(f"round{round_no}_actual_onlyoffice_frame", frame is not None)
                        canvas = frame.locator("#id_viewer canvas").first
                        canvas.wait_for(state="visible", timeout=90000)
                        frame.locator("#editor_sdk").wait_for(state="visible", timeout=30000)
                        frame.locator("#toolbar").wait_for(state="visible", timeout=30000)
                        # Canvas readiness plus actual mutation/readback is mandatory; a
                        # missing frame/canvas cannot turn into a conditional pass.
                        canvas.click(position={"x": 150, "y": 150})
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
                                proved = baseline in text and all(m in text for m in markers[:round_no])
                                if proved:
                                    evidence[f"round{round_no}_version"] = {
                                        "commit": after[0]["id"], "object": after[0]["rev_file_id"],
                                        "attributed_to_authenticated_user": True}
                                    break
                        time.sleep(2)
                    require(f"round{round_no}_new_user_version_and_body_readback", proved)
                    require(f"round{round_no}_no_browser_download", not downloads)
                evidence["runtime"] = "PASS"
            finally:
                browser.close()
    except Exception as exc:
        # Playwright/API exceptions can contain credential-bearing URLs or bodies.
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
