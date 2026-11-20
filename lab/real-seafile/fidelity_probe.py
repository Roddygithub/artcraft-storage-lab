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
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from difflib import SequenceMatcher
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_slice as rs  # noqa: E402
import fidelity_corpus  # noqa: E402
import fidelity_compare  # noqa: E402

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


def compare_saved_file(save_confirmed, kind, fixture, body, marker, mark):
    """Never count the original upload as a successful saved-file comparison."""
    if not save_confirmed:
        mark(f"{kind}_fidelity", False,
             "NOT_VERIFIED: the editor never saved, so comparing the fixture with itself would be vacuous")
        return None
    return fidelity_compare.compare(fixture, body, marker=marker)


def write_json(path: Path, result: dict) -> None:
    """Write a complete fidelity report using the probe's normal JSON format."""
    path.write_text(json.dumps(result, indent=1, ensure_ascii=False) + "\n")


def visible_marker(image: bytes, marker: str) -> bool | None:
    """OCR the fresh editor screenshot; None means the check could not run."""
    if not shutil.which("tesseract"):
        return None
    try:
        result = subprocess.run(["tesseract", "stdin", "stdout", "--psm", "11"],
                                input=image, capture_output=True, timeout=20, check=True)
    except (OSError, subprocess.SubprocessError):
        return None
    text = re.sub(r"[^a-z0-9]", "", result.stdout.decode("utf-8", "replace").lower())
    needle = re.sub(r"[^a-z0-9]", "", marker.lower())
    if not needle:
        return False
    return any(SequenceMatcher(None, needle, text[i:i + len(needle)]).ratio() >= .86
               for i in range(max(1, len(text) - len(needle) + 1)))


def reopen_verified(*, login_ok: bool, ready: bool, relay_body: bytes | None,
                    saved_body: bytes, marker_visible: bool | None) -> bool:
    """A fresh editor load and visible edited content are required; API readback is irrelevant."""
    return bool(login_ok and ready and relay_body == saved_body and marker_visible is True)


def _sha(body: bytes) -> str:
    return hashlib.sha256(body).hexdigest()


def _new_version(before: list[dict], after: list[dict]) -> bool:
    return bool(before and after and after[0].get("id") != before[0].get("id"))


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
    from playwright.sync_api import sync_playwright

    fixture = fidelity_corpus.corpus()[name]
    st, repo = rs.api(token, "POST", "/api2/repos/", {"name": f"fid-{kind}-{int(time.time())}"})
    repo_id = repo["repo_id"]
    rs.upload(token, repo_id, name, fixture)
    out = {"kind": kind, "editor": {"docx": "WordCraft", "xlsx": "GridCraft",
                                    "pptx": "DeckCraft"}[kind]}
    save_confirmed = False
    marker = f"fid{kind}{os.urandom(3).hex()}"
    out["fixture_sha256"] = _sha(fixture)
    (results / f"{kind}-original{Path(name).suffix}").write_bytes(fixture)
    save_payload = None
    history_before = rs.history(token, repo_id, name)
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

            save_requests = []

            def capture_save(request):
                if request.method == "POST" and request.url.endswith("/relay/save"):
                    try:
                        payload = request.post_data_buffer
                        if payload:
                            save_requests.append(payload)
                    except Exception:  # noqa: BLE001
                        pass

            page.on("request", capture_save)
            page.keyboard.press("Control+s")
            saved_status = wait_status(host, lambda t: "saved to seafile" in t.lower(), 90)
            save_confirmed = mark(f"{kind}_save_confirmed",
                                  "saved to seafile" in saved_status.lower(),
                                  saved_status[:80])
            page.remove_listener("request", capture_save)
            save_payload = save_requests[-1] if save_requests else None
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
    out["saved_readback_sha256"] = _sha(body)
    out["save_payload_sha256"] = _sha(save_payload) if save_payload is not None else None
    if save_payload is not None:
        (results / f"{kind}-save-payload{Path(name).suffix}").write_bytes(save_payload)
    mark(f"{kind}_save_payload_matches_seafile_readback",
         save_payload is not None and save_payload == body,
         f"payload_sha256={_sha(save_payload) if save_payload is not None else 'missing'} "
         f"readback_sha256={_sha(body)}")
    history_after = rs.history(token, repo_id, name)
    end = time.time() + 60
    while not _new_version(history_before, history_after) and time.time() < end:
        time.sleep(1)
        history_after = rs.history(token, repo_id, name)
    mark(f"{kind}_save_created_seafile_version", _new_version(history_before, history_after),
         f"before={len(history_before)} after={len(history_after)}")
    comparison = compare_saved_file(save_confirmed, kind, fixture, body, marker, mark)
    if comparison is None:
        out["comparison"] = {"verdicts": {}, "counts": {},
                             "regressions": [], "note": "NOT_VERIFIED (no save occurred)"}
        return out
    out["comparison"] = {"verdicts": comparison.get("verdicts"),
                         "counts": comparison.get("counts"),
                         "regressions": comparison.get("regressions")}
    write_json(results / f"{kind}-comparison.json", comparison)
    mark(f"{kind}_saved_file_structurally_valid", "error" not in comparison,
         str(comparison.get("error"))[:150])
    for feature, verdict in (comparison.get("verdicts") or {}).items():
        mark(f"{kind}_fidelity_{feature}", verdict in ("PRESERVED", "NOT_SUPPORTED"), verdict)

    # ---- reopen in a fresh context and verify the editor's own load -------
    login_ok = ready = False
    relay_body = None
    marker_visible = None
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            ctx = browser.new_context(viewport={"width": 1400, "height": 867})
            page = ctx.new_page()
            relay_responses = []

            def capture_relay(response):
                if response.url.endswith("/relay/file"):
                    try:
                        relay_responses.append((response.status, response.body()))
                    except Exception:  # noqa: BLE001
                        pass

            page.on("response", capture_relay)
            login_ok = login(page, ADMIN, ADMIN_PW)
            mark(f"{kind}_reopen_login", login_ok, f"url={page.url[:120]}")
            if login_ok:
                host, editor, s = open_doc(page, repo_id, name)
                ready = "ready" in s.lower() and host is not None and editor is not None
                mark(f"{kind}_reopen_ready", ready, f"status={s!r}")
                if ready:
                    page.wait_for_timeout(1500)
                    screenshot = page.screenshot(path=results / f"{kind}-reopened.png")
                    marker_visible = visible_marker(screenshot, marker)
                    marker_detail = ("Tesseract marker OCR passed" if marker_visible is True else
                                     "NOT_VERIFIED: Tesseract is unavailable or failed" if marker_visible is None else
                                     "FAIL: edited marker was not visible in reopened editor")
                    mark(f"{kind}_reopened_marker_visible",
                         marker_visible is True, marker_detail)
            relay_body = next((data for status, data in reversed(relay_responses)
                               if status == 200), None)
            mark(f"{kind}_reopen_editor_received_saved_bytes",
                 relay_body == body,
                 f"relay_statuses={[s for s, _ in relay_responses]} "
                 f"relay_sha256={_sha(relay_body) if relay_body is not None else 'missing'}")
            browser.close()
    except Exception as exc:  # noqa: BLE001
        mark(f"{kind}_reopen_error", False, str(exc)[:150])

    reopen_ok = reopen_verified(login_ok=login_ok, ready=ready, relay_body=relay_body,
                                saved_body=body, marker_visible=marker_visible)
    mark(f"{kind}_editor_reopen_verified", reopen_ok,
         "fresh authenticated editor received saved bytes and visibly rendered marker" if reopen_ok
         else "NOT_VERIFIED: browser reopen gate did not pass")
    if relay_body is not None and ready:
        (results / f"{kind}-reopen-relay{Path(name).suffix}").write_bytes(relay_body)
        comparison2 = fidelity_compare.compare(fixture, relay_body, marker=marker)
        write_json(results / f"{kind}-comparison-reopen.json", comparison2)
        stable = comparison.get("verdicts") == comparison2.get("verdicts")
        mark(f"{kind}_fidelity_stable_across_editor_reopen", reopen_ok and stable,
             "editor-relayed verdicts identical" if stable else "editor-relayed verdicts changed")
    else:
        mark(f"{kind}_fidelity_stable_across_editor_reopen", False,
             "NOT_VERIFIED: fresh editor did not provide a readable /relay/file response")

    # API readback is an independent storage-integrity check, not editor-reopen evidence.
    try:
        body2, _ = rs.download(token, repo_id, name)
        (results / f"{kind}-post-reopen-readback{Path(name).suffix}").write_bytes(body2)
        out["post_reopen_api_sha256"] = _sha(body2)
        mark(f"{kind}_post_reopen_api_bytes_unchanged", body2 == body,
             f"sha256={_sha(body2)}")
    except Exception as exc:  # noqa: BLE001
        mark(f"{kind}_post_reopen_api_readback", False, str(exc)[:150])
    out["reopen"] = {"login_ok": login_ok, "editor_ready": ready,
                     "relay_sha256": _sha(relay_body) if relay_body is not None else None,
                     "marker_visible": marker_visible, "verified": reopen_ok}
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
    outcome["provenance"] = {
        "source_commit": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                                         text=True, check=True).stdout.strip(),
        "scripts_sha256": {Path(path).name: _sha(Path(path).read_bytes()) for path in (
            __file__, fidelity_compare.__file__, fidelity_corpus.__file__)},
    }

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
    write_json(results / "fidelity.json", outcome)
    print(f"\n{outcome['passed']}/{len(checks)} checks passed -> {results}/fidelity.json")
    return 0 if outcome["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
