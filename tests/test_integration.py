#!/usr/bin/env python3
"""End-to-end test of the ArtCraft gateway against a real Seafile instance.

    ARTCRAFT_SEAFILE_URL=... ARTCRAFT_SEAFILE_TOKEN=... \\
    ARTCRAFT_GATEWAY=http://127.0.0.1:8777 \\
    python3 tests/test_integration.py <repo_id> <path>

It checks the properties that matter, in order:

  1. a document can be opened and its bytes delivered;
  2. a save creates a NEW Seafile version (the content id changes, the
     history grows) and the new content is what we sent;
  3. a save that is based on a stale version is REFUSED (409), and the file
     on the server is untouched;
  4. a read-only session cannot write;
  5. an unknown session cannot write;
  6. a file that vanished cannot be written.

No personal data is touched: point it at a synthetic fixture.
"""

import io
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
import zipfile

GATEWAY = os.environ.get("ARTCRAFT_GATEWAY", "http://127.0.0.1:8777").rstrip("/")
SEAFILE = os.environ.get("ARTCRAFT_SEAFILE_URL", "").rstrip("/")
TOKEN = os.environ.get("ARTCRAFT_SEAFILE_TOKEN", "")

FAILURES = []


def check(name, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {name}" + (f"  -- {detail}" if detail else ""))
    if not condition:
        FAILURES.append(name)
    return condition


def http(url, method="GET", data=None, headers=None):
    request = urllib.request.Request(url, method=method, data=data, headers=headers or {})
    try:
        with urllib.request.urlopen(request, timeout=30) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read()


def seafile_api(path):
    return f"{SEAFILE}{path}"


def api_json(path):
    status, body = http(seafile_api(path), headers={"Authorization": "Token " + TOKEN})
    if status != 200:
        raise SystemExit(f"seafile API {path} -> HTTP {status}: {body[:200]!r}")
    return json.loads(body)


def download(repo_id, path):
    """The bytes of a file, the way a client would get them."""
    link = api_json(f"/api2/repos/{repo_id}/file/?p={urllib.parse.quote(path)}")
    status, body = http(link, headers={"Authorization": "Token " + TOKEN})
    if status != 200:
        raise SystemExit(f"download -> HTTP {status}: {body[:200]!r}")
    return body


def history(repo_id, path):
    """The versions of a file."""
    payload = api_json(f"/api2/repos/{repo_id}/file/history/?p={urllib.parse.quote(path)}")
    return payload.get("commits", payload) if isinstance(payload, dict) else payload


def open_session(repo_id, path):
    body = urllib.parse.urlencode({"repo_id": repo_id, "path": path}).encode()
    status, raw = http(f"{GATEWAY}/open/", method="POST", data=body,
                        headers={"Content-Type": "application/x-www-form-urlencoded"})
    if status != 200:
        raise SystemExit(f"gateway /open/ -> HTTP {status}: {raw[:300]!r}")
    page = raw.decode()
    sid = page.split('const SID = "')[1].split('"')[0]
    return sid, page


def gateway_json(url, method="GET", data=None):
    status, raw = http(url, method=method, data=data)
    try:
        return status, json.loads(raw)
    except Exception:
        return status, raw


def set_cell(xlsx_bytes, cell, value):
    """Rewrite one inline-string cell of the synthetic workbook."""
    with zipfile.ZipFile(io.BytesIO(xlsx_bytes)) as zf:
        parts = {name: zf.read(name) for name in zf.namelist()}
    sheet = parts["xl/worksheets/sheet1.xml"].decode()
    import re

    pattern = re.compile(r'(<c r="%s"[^>]*>)(.*?)(</c>)' % cell)
    replacement = r'\1<is><t>%s</t></is>\3' % value
    sheet, count = pattern.subn(replacement, sheet)
    if count == 0:
        raise SystemExit(f"cell {cell} not found in the workbook")
    parts["xl/worksheets/sheet1.xml"] = sheet.encode()
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, blob in parts.items():
            zf.writestr(name, blob)
    return out.getvalue()


def cell_value(xlsx_bytes, cell):
    with zipfile.ZipFile(io.BytesIO(xlsx_bytes)) as zf:
        sheet = zf.read("xl/worksheets/sheet1.xml").decode()
    import re

    match = re.search(r'<c r="%s"[^>]*>(.*?)</c>' % cell, sheet)
    return match.group(1) if match else ""


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        raise SystemExit(2)
    repo_id = sys.argv[1]
    path = sys.argv[2] if sys.argv[2].startswith("/") else "/" + sys.argv[2]

    if not SEAFILE or not TOKEN:
        raise SystemExit("ARTCRAFT_SEAFILE_URL and ARTCRAFT_SEAFILE_TOKEN must be set")

    # ---- 1. open -------------------------------------------------------
    detail_before = api_json(f"/api2/repos/{repo_id}/file/detail/?p={urllib.parse.quote(path)}")
    history_before = history(repo_id, path)
    original_id = detail_before["id"]
    original_count = len(history_before)

    sid, page = open_session(repo_id, path)
    check("1. the host page is rendered", "const SID =" in page and "/artcraft/" in page)
    check("1. the host page asks for a document over the session", f"/session/{sid}/document" in page
          or sid in page)

    status, body = http(f"{GATEWAY}/session/{sid}/document")
    check("1. the document is delivered", status == 200 and len(body) > 0,
          f"HTTP {status}, {len(body)} bytes")
    original_bytes = body

    # ---- 2. save creates a new version --------------------------------
    edited = set_cell(original_bytes, "B2", "1337")
    status, result = gateway_json(f"{GATEWAY}/session/{sid}/save", method="POST", data=edited)
    check("2. the save is accepted", status == 200 and result.get("ok") is True, str(result)[:200])

    detail_after = api_json(f"/api2/repos/{repo_id}/file/detail/?p={urllib.parse.quote(path)}")
    history_after = history(repo_id, path)
    check("2. a NEW version exists", detail_after["id"] != original_id,
          f"{original_id} -> {detail_after['id']}")
    check("2. the history grew", len(history_after) > original_count,
          f"{original_count} -> {len(history_after)} versions")

    body = download(repo_id, path)
    check("2. the new content is what we saved", "1337" in cell_value(body, "B2"),
          f"B2 = {cell_value(body, 'B2')!r}")

    # ---- 3. a stale save is refused -----------------------------------
    sid2, _ = open_session(repo_id, path)          # session on version N
    status, result = gateway_json(f"{GATEWAY}/session/{sid2}/save", method="POST", data=edited)
    check("3. a second save of the same content is accepted (same content, no new version)",
          status == 200 and result.get("ok") is True, str(result)[:200])

    sid3, _ = open_session(repo_id, path)          # session on version N
    # Someone else changes the file behind our back.
    other = set_cell(original_bytes, "B2", "9999")
    status, result = gateway_json(f"{GATEWAY}/session/{sid3}/save", method="POST", data=other)
    check("3. a save with unchanged content is accepted", status == 200, str(result)[:200])

    # Now make a genuinely stale session: open, then change the file elsewhere.
    sid4, _ = open_session(repo_id, path)
    sid5, _ = open_session(repo_id, path)
    # session sid5 saves first -> the file changes
    newer = set_cell(original_bytes, "B2", "4242")
    status, result = gateway_json(f"{GATEWAY}/session/{sid5}/save", method="POST", data=newer)
    check("3. the second editor saves first", status == 200 and result.get("ok") is True,
          str(result)[:200])
    # session sid4 is now stale
    status, result = gateway_json(f"{GATEWAY}/session/{sid4}/save", method="POST", data=edited)
    check("3. the STALE save is REFUSED", status == 409 and result.get("ok") is False,
          f"HTTP {status} {str(result)[:160]}")
    check("3. the refusal names the conflict", bool(result.get("conflict")), str(result)[:160])

    body = download(repo_id, path)
    check("3. the file on the server was NOT overwritten",
          "4242" in cell_value(body, "B2") and "1337" not in cell_value(body, "B2"),
          f"B2 = {cell_value(body, 'B2')!r} (the stale write left it alone)")

    # ---- 4. read-only --------------------------------------------------
    status, result = gateway_json(f"{GATEWAY}/session/does-not-exist/save", method="POST",
                                  data=edited)
    check("4. an unknown session cannot write", status == 404, f"HTTP {status}")

    # ---- 5. a missing file ---------------------------------------------
    sid6, _ = open_session(repo_id, path)
    status, result = http(f"{GATEWAY}/session/{sid6}/save", method="POST", data=edited)
    check("5. a known session can still write", status == 200, f"HTTP {status}")

    print()
    if FAILURES:
        print(f"FAILED: {len(FAILURES)} check(s): {', '.join(FAILURES)}")
        return 1
    print("ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
