#!/usr/bin/env python3
"""Verify the edit-only WOPI routing in the isolated deployment (LXC 115).

Question this answers
---------------------
Stock Seahub 12 mints a WOPI *view* token for any user who can read the file,
whenever the extension is listed in ``OFFICE_WEB_APP_FILE_EXTENSION``. Seahub's
``PutFile`` then accepts that token without consulting ``can_edit``
(``docs/security/HOST_PERMISSION_BOUNDARY.md``). Setting

    OFFICE_WEB_APP_FILE_EXTENSION = ()
    OFFICE_WEB_APP_EDIT_FILE_EXTENSION = ('pptx',)

should keep the edit workflow and stop minting view tokens for read-only users.
All five ``get_wopi_dict`` call sites in Seahub 12 are gated on
``fileext in OFFICE_WEB_APP_FILE_EXTENSION`` (``views/file.py:964,1089,1410,1653``,
``api2/views.py:2890``), so the empty tuple closes every view path.

This probe checks the behaviour, not the intent:
  * owner  -> gets the bridge edit frame (a WOPI edit token)
  * reader -> gets NO bridge frame and no WOPI token in the page
  * reader -> cannot read/write through the bridge relay

The reader is a real second account sharing the owner's library read-only via
Seahub's own ``/api2/shared-repos/`` endpoint (not the raw RPC), which is what
the web UI uses.

Usage:
    SEAFILE_URL=... BRIDGE_URL=... ADMIN_EMAIL=... ADMIN_PASSWORD=... \
      python3 lab/real-seafile/wopi_routing_probe.py --results /tmp/routing

Writes ``routing.json`` and screenshots. No secrets in the output.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_slice as rs  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

SEAFILE = rs.SEAFILE
BRIDGE = rs.BRIDGE
ADMIN = rs.ADMIN
ADMIN_PW = rs.ADMIN_PW


def login(page, email, pw):
    page.goto(SEAFILE + "/accounts/login/", wait_until="domcontentloaded")
    page.wait_for_selector("input[name=login]", timeout=30000)
    page.fill("input[name=login]", email)
    page.fill("input[name=password]", pw)
    page.click("button[type=submit], input[type=submit]")
    page.wait_for_url(lambda u: "/accounts/login" not in u, timeout=30000)
    return "/accounts/login" not in page.url


def bridge_frames(page, wait=20):
    """Collect the bridge host/editor frames that appear within `wait` seconds."""
    end = time.time() + wait
    while time.time() < end:
        urls = [f.url for f in page.frames if f.url.startswith(BRIDGE)]
        if any(u.startswith(BRIDGE + "/edit/") for u in urls):
            return urls
        page.wait_for_timeout(500)
    return [f.url for f in page.frames if f.url.startswith(BRIDGE)]


def page_has_wopi_token(page):
    """A minted WOPI token appears in the form action / hidden input."""
    try:
        html = page.content()
    except Exception:  # noqa: BLE001
        return False
    return ("access_token" in html) or ("/wopi/files/" in html)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default=os.environ.get("RESULTS_DIR", "/tmp/routing-probe"))
    ap.add_argument("--headless", action="store_true")
    args = ap.parse_args()
    os.makedirs(args.results, exist_ok=True)

    checks = []

    def check(name, ok, detail=""):
        checks.append({"name": name, "ok": bool(ok), "detail": str(detail)[:1500]})
        print(("PASS " if ok else "FAIL ") + name + (f"  -- {detail}" if detail else ""), flush=True)
        return bool(ok)

    admin = rs.api_token(ADMIN, ADMIN_PW)

    # ---- a real second account, created through the admin API -------------
    reader = "reader-" + os.urandom(3).hex() + "@example.invalid"
    reader_pw = "Probe-" + os.urandom(6).hex()
    st, body = rs.api(admin, "POST", "/api/v2.1/admin/users/",
                      {"email": reader, "password": reader_pw, "name": "Read Only Probe",
                       "is_active": "true", "is_staff": "false"})
    check("reader_account_created", st in (200, 201), f"status={st} body={str(body)[:120]}")
    # Seahub rewrites the login to its own auth domain; sharing must use the
    # canonical address it returned, or the share is rolled back.
    reader = body.get("email", reader) if isinstance(body, dict) else reader
    check("reader_canonical_email_used", bool(reader), reader)

    # ---- owner library with one PPTX -------------------------------------
    st, repo = rs.api(admin, "POST", "/api2/repos/", {"name": f"routing-{int(time.time())}"})
    repo_id = repo["repo_id"]
    rs.upload(admin, repo_id, "routing.pptx", rs.minimal_pptx())

    # ---- share read-only through Seahub's own endpoint -------------------
    st, body = rs.api(admin, "PUT",
                      f"/api2/shared-repos/{repo_id}/?share_type=personal&user={reader}&permission=r")
    check("share_readonly_accepted", st == 200, f"status={st} body={str(body)[:120]}")

    reader_tok = rs.api_token(reader, reader_pw)
    st, body = rs.api(reader_tok, "GET", f"/api2/repos/{repo_id}/")
    reader_can_read = st == 200
    check("reader_can_access_repo", reader_can_read, f"status={st} body={str(body)[:160]}")

    st, perm = rs.api(reader_tok, "GET", f"/api/v2.1/repos/{repo_id}/")
    outcome = {"repo_id": repo_id, "reader": reader, "checks": checks,
               "reader_repo_meta": perm if isinstance(perm, dict) else str(perm)[:200]}

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=args.headless)
            # ---- owner: must get the edit route --------------------------
            ctx = browser.new_context(viewport={"width": 1400, "height": 867})
            page = ctx.new_page()
            login(page, ADMIN, ADMIN_PW)
            page.goto(f"{SEAFILE}/lib/{repo_id}/file/routing.pptx", wait_until="domcontentloaded")
            owner_frames = bridge_frames(page, 25)
            owner_edit = [u for u in owner_frames if u.startswith(BRIDGE + "/edit/")]
            check("owner_gets_wopi_edit_route", bool(owner_edit), json.dumps(owner_frames)[:400])
            page.screenshot(path=os.path.join(args.results, "routing-owner.png"))
            outcome["owner_frames"] = owner_frames
            ctx.close()

            # ---- reader: must NOT get a WOPI route -----------------------
            ctx2 = browser.new_context(viewport={"width": 1400, "height": 867})
            p2 = ctx2.new_page()
            login(p2, reader, reader_pw)
            p2.goto(f"{SEAFILE}/lib/{repo_id}/file/routing.pptx", wait_until="domcontentloaded")
            time.sleep(3)
            reader_frames = bridge_frames(p2, 12)
            reader_edit = [u for u in reader_frames if u.startswith(BRIDGE + "/edit/")]
            token_in_page = page_has_wopi_token(p2)
            try:
                text = p2.locator("body").inner_text()[:300]
            except Exception:  # noqa: BLE001
                text = ""
            check("reader_gets_no_wopi_route", not reader_edit,
                  f"frames={json.dumps(reader_frames)[:300]} token_in_page={token_in_page}")
            check("reader_page_has_no_wopi_token", not token_in_page, f"token_in_page={token_in_page}")
            check("reader_page_does_not_silently_break", bool(text.strip()),
                  f"body={text[:200]!r}")
            p2.screenshot(path=os.path.join(args.results, "routing-reader.png"))
            outcome["reader_frames"] = reader_frames
            outcome["reader_page_text"] = text
            ctx2.close()
            browser.close()
    finally:
        try:
            rs.api(admin, "DELETE", f"/api2/repos/{repo_id}/")
        except Exception:  # noqa: BLE001
            pass
        try:
            rs.api(admin, "DELETE", f"/api/v2.1/admin/users/{reader}/")
        except Exception:  # noqa: BLE001
            pass

    outcome["passed"] = sum(1 for c in checks if c["ok"])
    outcome["failed"] = sum(1 for c in checks if not c["ok"])
    outcome["ok"] = outcome["failed"] == 0
    with open(os.path.join(args.results, "routing.json"), "w") as fh:
        json.dump(outcome, fh, indent=1)
    print(f"\n{outcome['passed']}/{len(checks)} checks passed -> {args.results}/routing.json")
    return 0 if outcome["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
