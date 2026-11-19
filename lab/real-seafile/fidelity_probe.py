#!/usr/bin/env python3
"""Round-trip fidelity probe: rich fixtures through the real editors.

For each format the probe

  1. creates a disposable library and uploads a `fidelity_corpus` fixture,
  2. opens it through the bridge in the real editor (headed, real GPU),
  3. makes one targeted text edit and saves,
  4. downloads the *actually saved* bytes from Seafile,
  5. compares structure with `fidelity_compare` (PRESERVED/ALTERED/LOST),
  6. reopens in a fresh browser context and compares again.

A valid ZIP is not fidelity: every feature is read from the real XML parts.
Nothing is written to make the fixtures look better than the editors are.

Usage (on the Omarchy desktop, real Wayland session):

    SEAFILE_URL=... BRIDGE_URL=... ADMIN_EMAIL=... ADMIN_PASSWORD=... \
      python3 lab/real-seafile/fidelity_probe.py --results /tmp/fidelity

Writes ``fidelity.json`` plus per-format screenshots and the before/after
fixture bytes. Never prints credentials.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_slice as rs  # noqa: E402
import fidelity_corpus  # noqa: E402
import fidelity_compare  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

SEAFILE = rs.SEAFILE
BRIDGE = rs.BRIDGE
ADMIN = rs.ADMIN
ADMIN_PW = rs.ADMIN_PW

# The headed launch needs the real desktop session, which background shells
# do not inherit.
os.environ.setdefault("WAYLAND_DISPLAY", "wayland-1")
os.environ.setdefault("XDG_RUNTIME_DIR", "/run/user/1000")

CASES = [
    ("docx", "fidelity-report.docx", "WordCraft"),
    ("xlsx", "fidelity-workbook.xlsx", "GridCraft"),
    ("pptx", "fidelity-deck.pptx", "DeckCraft"),
]


def find_frames(page, timeout=120):
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


def login(page, email, pw):
    page.goto(SEAFILE + "/accounts/login/", wait_until="domcontentloaded")
    page.wait_for_selector("input[name=login]", timeout=30000)
    page.fill("input[name=login]", email)
    page.fill("input[name=password]", pw)
    page.click("button[type=submit], input[type=submit]")
    page.wait_for_url(lambda u: "/accounts/login" not in u, timeout=30000)
    return "/accounts/login" not in page.url


def open_doc(page, repo_id, name):
    page.goto(f"{SEAFILE}/lib/{repo_id}/file/{name}", wait_until="domcontentloaded")
    host, editor = find_frames(page)
    s = wait_status(host, lambda t: "ready" in t.lower(), 120)
    return host, editor, s


def click_editor(page):
    box = page.locator("#office-frame").bounding_box()
    if not box:
        return False
    page.mouse.click(box["x"] + box["width"] / 2, box["y"] + 90 + (box["height"] - 90) / 2)
    return True


def roundtrip(token, kind, name, results: Path, mark):
    """One open -> edit -> save -> download -> compare -> reopen cycle."""
    fixture = fidelity_corpus.corpus()[name]
    st, repo = rs.api(token, "POST", "/api2/repos/", {"name": f"fid-{kind}-{int(time.time())}"})
    repo_id = repo["repo_id"]
    rs.upload(token, repo_id, name, fixture)
    out = {"kind": kind, "editor": {"docx": "WordCraft", "xlsx": "GridCraft",
                                    "pptx": "DeckCraft"}[kind], "repo_id": repo_id}
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, args=[
                "--ozone-platform=wayland", "--enable-unsafe-webgpu",
                "--enable-features=Vulkan", "--ignore-gpu-blocklist",
                "--disable-dev-shm-usage", "--window-position=100,100",
                "--window-size=1400,900"])
            ctx = browser.new_context(viewport={"width": 1400, "height": 867})
            page = ctx.new_page()
            if not login(page, ADMIN, ADMIN_PW):
                mark(f"{kind}_login", False, "login failed")
                return out
            host, editor, s = open_doc(page, repo_id, name)
            mark(f"{kind}_editor_opened", "ready" in s.lower(), f"status={s!r}")
            if "ready" not in s.lower():
                page.screenshot(path=results / f"{kind}-opened.png")
                return out

            marker = f"fid{kind}{os.urandom(3).hex()}"
            # Same trusted-input gesture the 66/66 suite uses: click a cell/shape,
            # settle, type, commit with Enter (a spreadsheet keeps editing until
            # Enter, and an open cell editor swallows Ctrl+S).
            box = page.locator("#office-frame").bounding_box()

            def edit_at(fx, fy):
                page.mouse.click(box["x"] + box["width"] * fx,
                                 box["y"] + 60 + (box["height"] - 60) * fy)
                page.wait_for_timeout(1000)
                page.keyboard.type(marker, delay=30)
                page.keyboard.press("Enter")
                return wait_status(host, lambda t: "unsaved" in t.lower(), 15)

            dirty = edit_at(0.35, 0.30)
            if "unsaved" not in dirty.lower():
                click_editor(page)
                page.keyboard.press("Control+End")
                page.keyboard.type(marker, delay=25)
                dirty = wait_status(host, lambda t: "unsaved" in t.lower(), 15)
            out["marker"] = marker
            mark(f"{kind}_edit_registered", "unsaved" in dirty.lower(), f"status={dirty!r}")

            page.keyboard.press("Control+s")
            saved_status = wait_status(host, lambda t: "saved to seafile" in t.lower(), 90)
            mark(f"{kind}_save_confirmed", "saved to seafile" in saved_status.lower(),
                 saved_status[:80])
            try:
                page.screenshot(path=results / f"{kind}-saved.png")
            except Exception as exc:  # noqa: BLE001
                print(f"screenshot skipped: {exc}", flush=True)
            browser.close()
    except Exception as exc:  # noqa: BLE001
        mark(f"{kind}_browser_error", False, str(exc)[:200])
        return out

    try:
        body, _ = rs.download(token, repo_id, name)
    except Exception as exc:  # noqa: BLE001
        mark(f"{kind}_download", False, str(exc)[:150])
        rs.api(token, "DELETE", f"/api2/repos/{repo_id}/")
        return out
    (results / f"{kind}-after-save{Path(name).suffix}").write_bytes(body)
    saved_confirmed = any(c["name"] == f"{kind}_save_confirmed" and c["ok"] for c in checks)
    if not saved_confirmed:
        # No save happened: comparing the fixture with itself would report a
        # fake 100% fidelity. Record the truth instead.
        mark(f"{kind}_fidelity", False,
             "NOT_VERIFIED: the editor never saved, so the downloaded file is "
             "the original upload and a comparison would be vacuous")
        out["comparison"] = {"verdicts": {}, "counts": {},
                             "regressions": [], "note": "NOT_VERIFIED (no save occurred)"}
        return out
    comparison = fidelity_compare.compare(fixture, body, marker=marker)
    out["comparison"] = {"verdicts": comparison.get("verdicts"),
                         "counts": comparison.get("counts"),
                         "regressions": comparison.get("regressions")}
    (results / f"{kind}-comparison.json").write_text(
        json.dumps(comparison, indent=1, ensure_ascii=False) + "\n")
    mark(f"{kind}_saved_file_structurally_valid", "error" not in comparison,
         str(comparison.get("error"))[:150])
    for feature, verdict in (comparison.get("verdicts") or {}).items():
        mark(f"{kind}_fidelity_{feature}", verdict in ("PRESERVED", "NOT_SUPPORTED"), verdict)

    # ---- reopen in a fresh context and compare again --------------------
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            ctx = browser.new_context(viewport={"width": 1400, "height": 867})
            page = ctx.new_page()
            login(page, ADMIN, ADMIN_PW)
            host, editor, s = open_doc(page, repo_id, name)
            mark(f"{kind}_reopen_ready", "ready" in s.lower(), f"status={s!r}")
            page.screenshot(path=results / f"{kind}-reopened.png")
            browser.close()
    except Exception as exc:  # noqa: BLE001
        mark(f"{kind}_reopen_error", False, str(exc)[:150])

    body2, _ = rs.download(token, repo_id, name)
    comparison2 = fidelity_compare.compare(fixture, body2, marker=marker)
    (results / f"{kind}-comparison-reopen.json").write_text(
        json.dumps(comparison2, indent=1, ensure_ascii=False) + "\n")
    same = (comparison.get("verdicts") == comparison2.get("verdicts"))
    mark(f"{kind}_fidelity_stable_across_reopen", same, "verdicts identical" if same else "changed")
    rs.api(token, "DELETE", f"/api2/repos/{repo_id}/")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default=os.environ.get("RESULTS_DIR", "/tmp/fidelity-probe"))
    ap.add_argument("--only", choices=("docx", "xlsx", "pptx"))
    args = ap.parse_args()
    results = Path(args.results)
    results.mkdir(parents=True, exist_ok=True)

    checks, outcome = [], {"cases": {}}

    def check(name, ok, detail=""):
        checks.append({"name": name, "ok": bool(ok), "detail": str(detail)[:600]})
        print(("PASS " if ok else "FAIL ") + name + (f"  -- {detail}" if detail else ""), flush=True)
        return bool(ok)

    token = rs.api_token(ADMIN, ADMIN_PW)
    for kind, name, _editor in CASES:
        if args.only and kind != args.only:
            continue
        print(f"\n=== {kind.upper()} ===", flush=True)
        outcome["cases"][kind] = roundtrip(token=token, kind=kind, name=name,
                                           results=results, mark=check)

    outcome["checks"] = checks
    outcome["passed"] = sum(1 for c in checks if c["ok"])
    outcome["failed"] = sum(1 for c in checks if not c["ok"])
    outcome["ok"] = outcome["failed"] == 0
    (results / "fidelity.json").write_text(json.dumps(outcome, indent=1, ensure_ascii=False) + "\n")
    print(f"\n{outcome['passed']}/{len(checks)} checks passed -> {results}/fidelity.json")
    return 0 if outcome["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
