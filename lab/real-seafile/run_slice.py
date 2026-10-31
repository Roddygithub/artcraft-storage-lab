#!/usr/bin/env python3
"""Real-Seafile validation slice (HTTP level, no browser).

Runs inside the compose network against a stock Seafile CE 13, ONLYOFFICE Docs CE and the
bridge. Stdlib only. Writes RESULTS_DIR/slice.json and leaves raw HTML pages next to it.

What it proves, step by step (each step is a named check in the JSON):
  seahub_*      Seahub config/version, the WOPI branch really fires for .docx/.svg, the
                ONLYOFFICE branch really fires for .xlsx, on this Seahub version.
  discovery_*   Seahub fetched the bridge discovery XML and built a form POST to the bridge.
  bridge_*      opening through the bridge, relay info/file/save, version precondition,
                external-writer conflict, idempotent save, read-only refusal.
  seahub_putfile_ignores_can_edit   Seahub itself accepts PutFile with a read-only token
                (the gap the fake host reproduces) -- measured, not assumed.
  history_*     Seafile version history shows the save, attributed to the editing user.
  onlyoffice_*  Docs server healthy, api.js served, JWT accepted, and it can fetch a file
                from Seahub (conversion round-trip).
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import html
import http.cookiejar
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
import zipfile

SEAFILE = os.environ["SEAFILE_URL"].rstrip("/")
BRIDGE = os.environ["BRIDGE_URL"].rstrip("/")
ONLYOFFICE = os.environ["ONLYOFFICE_URL"].rstrip("/")
OO_SECRET = os.environ.get("ONLYOFFICE_JWT_SECRET", "")
ADMIN = os.environ["ADMIN_EMAIL"]
ADMIN_PW = os.environ["ADMIN_PASSWORD"]
RESULTS = os.environ.get("RESULTS_DIR", ".")

checks: list[dict] = []


def check(name: str, ok: bool, detail=""):
    checks.append({"name": name, "ok": bool(ok), "detail": str(detail)[:2000]})
    print(("PASS " if ok else "FAIL ") + name + (f"  -- {detail}" if detail else ""), flush=True)
    return ok


class Http:
    """Tiny client; one cookie jar per instance (= one browser session)."""

    def __init__(self):
        self.jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.jar))
        self.opener.addheaders = []

    def req(self, method, url, data=None, headers=None, timeout=60):
        h = dict(headers or {})
        if isinstance(data, dict):
            data = urllib.parse.urlencode(data).encode()
            h.setdefault("Content-Type", "application/x-www-form-urlencoded")
        r = urllib.request.Request(url, data=data, method=method, headers=h)
        try:
            with self.opener.open(r, timeout=timeout) as resp:
                return resp.status, dict(resp.headers), resp.read()
        except urllib.error.HTTPError as e:
            return e.code, dict(e.headers), e.read()

    def cookie(self, name):
        for c in self.jar:
            if c.name == name:
                return c.value
        return None


def wait_for(url, needle=None, tries=60, delay=5, label=""):
    h = Http()
    for i in range(tries):
        try:
            st, _, body = h.req("GET", url, timeout=10)
            if st < 500 and (needle is None or needle in body):
                return True
        except Exception as e:  # noqa: BLE001
            last = e
        time.sleep(delay)
    return False


# ---------------------------------------------------------------- Seafile API helpers
def api_token(email, pw):
    st, _, body = Http().req("POST", f"{SEAFILE}/api2/auth-token/", {"username": email, "password": pw})
    assert st == 200, (st, body[:200])
    return json.loads(body)["token"]


def api(token, method, path, data=None, headers=None, raw=False):
    h = {"Authorization": f"Token {token}", "Accept": "application/json"}
    h.update(headers or {})
    st, hdrs, body = Http().req(method, f"{SEAFILE}{path}", data, h)
    if raw:
        return st, hdrs, body
    try:
        return st, json.loads(body)
    except ValueError:
        return st, body.decode("utf-8", "replace")


def multipart(fields: dict, filename: str, content: bytes):
    boundary = "----lab" + uuid.uuid4().hex
    out = io.BytesIO()
    for k, v in fields.items():
        out.write(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode())
    out.write(f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{filename}\"\r\n"
              f"Content-Type: application/octet-stream\r\n\r\n".encode())
    out.write(content)
    out.write(f"\r\n--{boundary}--\r\n".encode())
    return out.getvalue(), f"multipart/form-data; boundary={boundary}"


def upload(token, repo, name, content):
    st, link = api(token, "GET", f"/api2/repos/{repo}/upload-link/?p=/")
    assert st == 200, (st, link)
    body, ctype = multipart({"parent_dir": "/", "replace": "1"}, name, content)
    st, _, resp = Http().req("POST", link + "?ret-json=1", body, {"Content-Type": ctype, "Authorization": f"Token {token}"})
    assert st == 200, (st, resp[:200])
    return json.loads(resp)[0]["id"]


def update_via_api(token, repo, name, content):
    """An external writer: the sync client / WebDAV / another editor, seen from Seafile."""
    st, link = api(token, "GET", f"/api2/repos/{repo}/update-link/?p=/")
    assert st == 200, (st, link)
    body, ctype = multipart({"target_file": f"/{name}"}, name, content)
    st, _, resp = Http().req("POST", link, body, {"Content-Type": ctype, "Authorization": f"Token {token}"})
    assert st == 200, (st, resp[:200])
    return resp.decode().strip('"')


def download(token, repo, name):
    st, link = api(token, "GET", f"/api2/repos/{repo}/file/?p=/{name}&reuse=0")
    assert st == 200, (st, link)
    st, _, body = Http().req("GET", link)
    assert st == 200
    return body, link


def history(token, repo, name):
    st, data = api(token, "GET", f"/api/v2.1/repos/{repo}/file/history/?path=/{urllib.parse.quote(name)}&page=1&per_page=50")
    if st != 200 or not isinstance(data, dict):
        st, data = api(token, "GET", f"/api2/repos/{repo}/file/history/?p=/{urllib.parse.quote(name)}")
    items = data.get("data") or data.get("commits") or []
    return [{"id": c.get("commit_id") or c.get("id"), "rev_file_id": c.get("rev_file_id"),
             "creator": c.get("creator_email") or c.get("creator_name") or c.get("creator"),
             "desc": c.get("description") or c.get("desc")} for c in items]


# ---------------------------------------------------------------- Seahub browser session
def seahub_login(email, pw) -> Http:
    h = Http()
    st, _, body = h.req("GET", f"{SEAFILE}/accounts/login/")
    assert st == 200, st
    csrf = h.cookie("sfcsrftoken") or h.cookie("csrftoken")
    m = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', body.decode("utf-8", "replace"))
    token_field = m.group(1) if m else csrf
    st, hdrs, body = h.req("POST", f"{SEAFILE}/accounts/login/",
                           {"csrfmiddlewaretoken": token_field, "login": email, "password": pw},
                           {"Referer": f"{SEAFILE}/accounts/login/"})
    assert st in (200, 302), (st, body[:300])
    assert h.cookie("sessionid"), "no sessionid cookie after login"
    return h


def file_page(h: Http, repo, name, query=""):
    st, hdrs, body = h.req("GET", f"{SEAFILE}/lib/{repo}/file/{urllib.parse.quote(name)}{query}")
    text = body.decode("utf-8", "replace")
    with open(os.path.join(RESULTS, f"page-{name}.html"), "w") as fh:
        fh.write(text)
    return st, text


def _js_unescape(v: str) -> str:
    return html.unescape(re.sub(r"\\u([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1), 16)), v))


def parse_wopi_form(text):
    """Seahub's WOPI page. Seahub <= 11 renders a <form action=... method=post> with hidden
    inputs; Seahub 12/13 render ``wopi_file_view_react.html`` with JS literals
    (``actionURL: '...'``, ``accessToken: '...'``, ``accessTokenTtl: '...'``) and the React
    bundle builds the form POST in the browser. Both are read here."""
    m = re.search(r"actionURL:\s*'([^']+)'", text)
    if m:
        action = _js_unescape(m.group(1))
        tok = re.search(r"accessToken:\s*'([^']*)'", text)
        ttl = re.search(r"accessTokenTtl:\s*'([^']*)'", text)
        if not tok or not tok.group(1):
            return None
        src = urllib.parse.parse_qs(urllib.parse.urlsplit(action).query).get("WOPISrc", [""])[0]
        return {"action": action, "access_token": _js_unescape(tok.group(1)), "access_token_ttl": ttl.group(1) if ttl else "", "wopi_src": src}
    m = re.search(r'<form[^>]+action="([^"]+)"[^>]*>', text)
    if not m:
        return None
    action = html.unescape(m.group(1))
    tok = re.search(r'name="access_token"\s+value="([^"]+)"', text) or re.search(r'value="([^"]+)"\s+name="access_token"', text)
    ttl = re.search(r'name="access_token_ttl"\s+value="([^"]+)"', text) or re.search(r'value="([^"]+)"\s+name="access_token_ttl"', text)
    if not tok:
        return None
    src = urllib.parse.parse_qs(urllib.parse.urlsplit(action).query).get("WOPISrc", [""])[0]
    return {"action": action, "access_token": tok.group(1), "access_token_ttl": ttl.group(1) if ttl else "", "wopi_src": src}


# ---------------------------------------------------------------- bridge helpers
def bridge_open(form):
    h = Http()
    st, hdrs, body = h.req("POST", form["action"],
                           {"access_token": form["access_token"], "access_token_ttl": form["access_token_ttl"]},
                           {"Origin": SEAFILE, "Referer": SEAFILE + "/"})
    text = body.decode("utf-8", "replace")
    cfg = None
    m = re.search(r'<script type="application/json" id="bridge-config"[^>]*>(.*?)</script>', text, re.S)
    if m:
        cfg = json.loads(html.unescape(m.group(1)))
    return st, hdrs, text, cfg


def relay(op, cfg, headers=None, body=None):
    h = {"X-Bridge-Request": "1", "X-Wopi-Token": cfg["token"], "X-Wopi-Src": cfg["src"],
         "Origin": BRIDGE, "Sec-Fetch-Site": "same-origin"}
    h.update(headers or {})
    if body is not None:
        h.setdefault("Content-Type", "application/octet-stream")
    return Http().req("POST", f"{BRIDGE}/relay/{op}", body if body is not None else b"", h)


def jwt(payload: dict) -> str:
    def b64(b):
        return base64.urlsafe_b64encode(b).rstrip(b"=").decode()
    header = b64(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    body = b64(json.dumps(payload, separators=(",", ":")).encode())
    sig = hmac.new(OO_SECRET.encode(), f"{header}.{body}".encode(), hashlib.sha256).digest()
    return f"{header}.{body}.{b64(sig)}"


def minimal_docx(text: str) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml",
                   '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                   '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                   '<Default Extension="xml" ContentType="application/xml"/>'
                   '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>')
        z.writestr("_rels/.rels",
                   '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>')
        z.writestr("word/document.xml",
                   '<?xml version="1.0" encoding="UTF-8"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                   f'<w:body><w:p><w:r><w:t>{html.escape(text)}</w:t></w:r></w:p></w:body></w:document>')
    return buf.getvalue()


def minimal_xlsx() -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml",
                   '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                   '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                   '<Default Extension="xml" ContentType="application/xml"/>'
                   '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
                   '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
                   '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/></Types>')
        # GridCraft refuses a workbook without a styles part ("no styles part" modal) -- WordCraft is laxer.
        z.writestr("xl/styles.xml",
                   '<?xml version="1.0" encoding="UTF-8"?><styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
                   '<fonts count="1"><font><sz val="11"/><name val="Calibri"/></font></fonts><fills count="1"><fill><patternFill patternType="none"/></fill></fills>'
                   '<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>'
                   '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
                   '<cellXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/></cellXfs></styleSheet>')
        z.writestr("_rels/.rels",
                   '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>')
        z.writestr("xl/workbook.xml",
                   '<?xml version="1.0" encoding="UTF-8"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
                   '<sheets><sheet name="Sheet1" sheetId="1" r:id="rId1"/></sheets></workbook>')
        z.writestr("xl/_rels/workbook.xml.rels",
                   '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
                   '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>')
        z.writestr("xl/worksheets/sheet1.xml",
                   '<?xml version="1.0" encoding="UTF-8"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData><row r="1"><c r="A1"><v>1</v></c></row></sheetData></worksheet>')
    return buf.getvalue()


MINIMAL_PDF = (b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
               b"3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 200 200]>>endobj\nxref\n0 4\n0000000000 65535 f \n"
               b"0000000009 00000 n \n0000000052 00000 n \n0000000101 00000 n \ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n160\n%%EOF\n")
MINIMAL_DXF = b"0\nSECTION\n2\nENTITIES\n0\nLINE\n8\n0\n10\n0\n20\n0\n11\n10\n21\n10\n0\nENDSEC\n0\nEOF\n"


def minimal_pptx() -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml",
                   '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                   '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                   '<Default Extension="xml" ContentType="application/xml"/>'
                   '<Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/></Types>')
        z.writestr("_rels/.rels",
                   '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/></Relationships>')
        z.writestr("ppt/presentation.xml",
                   '<?xml version="1.0" encoding="UTF-8"?><p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:sldIdLst/></p:presentation>')
    return buf.getvalue()


def content_matches(name: str, data: bytes) -> bool:
    ext = name.rsplit(".", 1)[-1].lower()
    if ext in ("docx", "xlsx", "pptx"):
        return data[:2] == b"PK"
    if ext == "pdf":
        return data.startswith(b"%PDF")
    if ext == "dxf":
        return b"SECTION" in data[:200] or b"ENTITIES" in data
    if ext == "svg":
        return b"<svg" in data[:300]
    return True


SVG_V1 = b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><rect width="10" height="10" fill="red"/></svg>'
SVG_V2 = b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><rect width="10" height="10" fill="blue"/></svg>'
SVG_EXT = b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><circle r="5" cx="5" cy="5" fill="green"/></svg>'


def main() -> int:
    os.makedirs(RESULTS, exist_ok=True)
    print("waiting for Seafile ...", flush=True)
    check("seafile_up", wait_for(f"{SEAFILE}/api2/ping/", b"pong"), SEAFILE)
    check("bridge_up", wait_for(f"{BRIDGE}/healthz", tries=12), BRIDGE)
    oo_up = wait_for(f"{ONLYOFFICE}/healthcheck", b"true", tries=60)
    check("onlyoffice_up", oo_up, ONLYOFFICE)

    st, info = api(api_token(ADMIN, ADMIN_PW), "GET", "/api2/server-info/")
    check("seahub_server_info", st == 200, json.dumps(info)[:300])
    seafile_version = info.get("version") if isinstance(info, dict) else "?"

    admin = api_token(ADMIN, ADMIN_PW)
    st, me = api(admin, "GET", "/api2/account/info/")
    admin_username = me.get("email", ADMIN) if isinstance(me, dict) else ADMIN
    st, repo = api(admin, "POST", "/api2/repos/", {"name": f"wopi-slice-{int(time.time())}"})
    assert st == 200, (st, repo)
    repo_id = repo["repo_id"]
    print("repo", repo_id, flush=True)

    svg_id = upload(admin, repo_id, "test.svg", SVG_V1)
    docx_id = upload(admin, repo_id, "test.docx", minimal_docx("hello from the lab"))
    xlsx_id = upload(admin, repo_id, "test.xlsx", minimal_xlsx())
    pdf_id = upload(admin, repo_id, "test.pdf", MINIMAL_PDF)
    dxf_id = upload(admin, repo_id, "test.dxf", MINIMAL_DXF)
    pptx_id = upload(admin, repo_id, "test.pptx", minimal_pptx())

    # second user, read-only share
    reader = "reader@lab.test"
    reader_pw = uuid.uuid4().hex
    st, resp = api(admin, "POST", "/api/v2.1/admin/users/", {"email": reader, "password": reader_pw, "name": "reader"})
    if st in (200, 201) and isinstance(resp, dict):
        reader_username = resp.get("email", reader)          # Seahub 13: xxx@auth.local
    else:                                                    # left over from a previous run: look it up, reset the password
        st, found = api(admin, "GET", f"/api/v2.1/admin/search-user/?query={urllib.parse.quote(reader)}")
        users = (found or {}).get("user_list") or [] if isinstance(found, dict) else []
        reader_username = next((u["email"] for u in users if u.get("contact_email") == reader or u.get("email") == reader), reader)
        st, resp = api(admin, "PUT", f"/api/v2.1/admin/users/{urllib.parse.quote(reader_username)}/", {"password": reader_pw})
    check("reader_user_ready", st in (200, 201), f"{reader_username} {json.dumps(resp)[:120]}")
    st, resp = api(admin, "PUT", f"/api2/repos/{repo_id}/dir/shared_items/?p=/",
                   {"share_type": "user", "username": reader_username, "permission": "r"})
    check("reader_share_readonly", st == 200 and isinstance(resp, dict) and not resp.get("failed"), json.dumps(resp)[:200])

    # ---- Seahub routing on this version -------------------------------------
    sess = seahub_login(ADMIN, ADMIN_PW)
    st, page_svg = file_page(sess, repo_id, "test.svg")
    form_svg = parse_wopi_form(page_svg)
    check("seahub_svg_routes_to_wopi", st == 200 and form_svg is not None and form_svg["action"].startswith(BRIDGE + "/edit/vectorcraft"),
          f"version={seafile_version} action={(form_svg or {}).get('action', '')[:120]}")
    st, page_docx = file_page(sess, repo_id, "test.docx")
    form_docx = parse_wopi_form(page_docx)
    check("seahub_docx_routes_to_wopi_wordcraft", st == 200 and form_docx is not None and form_docx["action"].startswith(BRIDGE + "/edit/wordcraft"),
          (form_docx or {}).get("action", "")[:120])
    st, page_xlsx = file_page(sess, repo_id, "test.xlsx")
    form_xlsx = parse_wopi_form(page_xlsx)
    check("seahub_xlsx_routes_to_wopi_gridcraft", st == 200 and form_xlsx is not None and form_xlsx["action"].startswith(BRIDGE + "/edit/gridcraft"),
          (form_xlsx or {}).get("action", "")[:120])
    st, page_pdf = file_page(sess, repo_id, "test.pdf")
    check("seahub_pdf_default_is_viewer_not_wopi", st == 200 and parse_wopi_form(page_pdf) is None,
          "Seahub 13 view_lib_file: PDF branch precedes the office branch unless ?edit_pdf=true")
    st, page_pdf2 = file_page(sess, repo_id, "test.pdf", "?edit_pdf=true")
    form_pdf = parse_wopi_form(page_pdf2)
    check("seahub_pdf_edit_pdf_routes_to_wopi_pdfcraft", st == 200 and form_pdf is not None and form_pdf["action"].startswith(BRIDGE + "/edit/pdfcraft"),
          (form_pdf or {}).get("action", "")[:120])
    st, page_dxf = file_page(sess, repo_id, "test.dxf")
    form_dxf = parse_wopi_form(page_dxf)
    check("seahub_dxf_routes_to_wopi_cadcraft", st == 200 and form_dxf is not None and form_dxf["action"].startswith(BRIDGE + "/edit/cadcraft"),
          (form_dxf or {}).get("action", "")[:120])
    st, page_pptx = file_page(sess, repo_id, "test.pptx")
    check("seahub_pptx_routes_to_onlyoffice", st == 200 and "api/documents/api.js" in page_pptx and parse_wopi_form(page_pptx) is None,
          "apijs referenced" if "api/documents/api.js" in page_pptx else "no api.js reference")
    # every ArtCraft editor opens through the bridge with the right bundle
    for label, form, editor, fid in (("docx", form_docx, "wordcraft", docx_id), ("xlsx", form_xlsx, "gridcraft", xlsx_id),
                                     ("pdf", form_pdf, "pdfcraft", pdf_id), ("dxf", form_dxf, "cadcraft", dxf_id)):
        if not form:
            check(f"bridge_open_{label}", False, "no WOPI form")
            continue
        st, hdrs, _, c = bridge_open(form)
        ok = st == 200 and c is not None and c.get("editorId") == editor and c.get("version") == fid and c.get("userCanWrite") is True
        check(f"bridge_open_{label}_{editor}", ok, f"status={st} editorUrl={(c or {}).get('editorUrl')} version_ok={(c or {}).get('version') == fid}")
        if c:
            st, h2, body = Http().req("GET", f"{BRIDGE}{c['editorUrl'].split('?')[0]}")
            check(f"bridge_serves_{editor}_bundle", st == 200 and b"<html" in body[:400].lower() or b"<!doctype" in body[:50].lower(), f"status={st} len={len(body)}")
    if form_svg:
        check("discovery_form_token_not_in_url", "access_token" not in form_svg["action"], form_svg["action"][:120])
        check("discovery_wopisrc_is_seahub", form_svg["wopi_src"].startswith(SEAFILE + "/api2/wopi/files/") or form_svg["wopi_src"].startswith(SEAFILE + "/api/v2.1/wopi/files/"), form_svg["wopi_src"])
    if not form_svg:
        print(json.dumps({"checks": checks}, indent=1), file=open(os.path.join(RESULTS, "slice.json"), "w"))
        return 1

    # ---- bridge open + relay ---------------------------------------------------
    st, hdrs, host_page, cfg = bridge_open(form_svg)
    check("bridge_open_host_page", st == 200 and cfg is not None and cfg.get("userCanWrite") is True,
          f"status={st} csp={'Content-Security-Policy' in hdrs} version={(cfg or {}).get('version')}")
    check("bridge_host_page_frame_ancestors_seahub", f"frame-ancestors {SEAFILE}" in hdrs.get("Content-Security-Policy", ""),
          hdrs.get("Content-Security-Policy", "")[:200])
    v1 = cfg["version"]
    check("bridge_version_is_seafile_obj_id", v1 == svg_id, f"{v1} vs upload id {svg_id}")

    st, h2, body = relay("file", cfg)
    check("relay_file_returns_bytes", st == 200 and body == SVG_V1 and h2.get("X-Wopi-Version") == v1, f"status={st} len={len(body)}")

    st, h2, body = relay("save", cfg, {"X-Expected-Version": v1, "X-File-Name": "test.svg"}, SVG_V2)
    r = json.loads(body) if st == 200 else {}
    check("relay_save_ok", st == 200 and r.get("version") and r["version"] != v1, f"status={st} body={body[:200]!r}")
    v2 = r.get("version", v1)
    got, _ = download(admin, repo_id, "test.svg")
    check("seafile_has_new_bytes", got == SVG_V2, f"len={len(got)}")
    hist = history(admin, repo_id, "test.svg")
    check("history_two_versions_attributed_to_admin", len(hist) >= 2 and hist[0]["creator"] == admin_username and hist[0]["rev_file_id"] == v2,
          json.dumps(hist[:3]))

    # stale precondition -> 409, no overwrite
    st, h2, body = relay("save", cfg, {"X-Expected-Version": v1, "X-File-Name": "test.svg"}, SVG_V1)
    got, _ = download(admin, repo_id, "test.svg")
    check("relay_stale_version_409_no_overwrite", st == 409 and got == SVG_V2, f"status={st} body={body[:200]!r}")

    # external writer -> bridge must see the new version and refuse the stale one
    ext_id = update_via_api(admin, repo_id, "test.svg", SVG_EXT)
    st, h2, body = relay("save", cfg, {"X-Expected-Version": v2, "X-File-Name": "test.svg"}, SVG_V1)
    got, _ = download(admin, repo_id, "test.svg")
    check("relay_external_change_409_no_overwrite", st == 409 and got == SVG_EXT and json.loads(body).get("current") == ext_id,
          f"status={st} body={body[:200]!r} ext_id={ext_id}")

    # idempotent: identical bytes -> no new version
    before = len(history(admin, repo_id, "test.svg"))
    st, h2, body = relay("save", cfg, {"X-Expected-Version": ext_id, "X-File-Name": "test.svg"}, SVG_EXT)
    after = len(history(admin, repo_id, "test.svg"))
    check("relay_identical_bytes_idempotent", st == 200 and after == before, f"status={st} history {before}->{after} body={body[:120]!r}")

    # rename / signature guards
    st, _, body = relay("save", cfg, {"X-Expected-Version": ext_id, "X-File-Name": "other.svg"}, SVG_V1)
    check("relay_rename_refused_400", st == 400, f"status={st} {body[:100]!r}")
    st, _, body = relay("save", cfg, {"X-Expected-Version": ext_id, "X-File-Name": "test.svg"}, b"%PDF-1.4 not an svg")
    check("relay_wrong_signature_415", st == 415, f"status={st} {body[:100]!r}")

    # locks through Seahub
    st, _, body = relay("lock", cfg, {"X-Wopi-Override": "LOCK", "X-Wopi-Lock": "lab-lock-1"})
    check("relay_lock_seahub_ok", st == 200, f"{st} {body[:100]!r}")
    st, _, body = relay("lock", cfg, {"X-Wopi-Override": "LOCK", "X-Wopi-Lock": "lab-lock-2"})
    check("relay_lock_conflict_409", st == 409 and json.loads(body).get("lock") == "lab-lock-1", f"{st} {body[:100]!r}")
    st, _, body = relay("lock", cfg, {"X-Wopi-Override": "UNLOCK", "X-Wopi-Lock": "lab-lock-1"})
    check("relay_unlock_ok", st == 200, f"{st} {body[:100]!r}")

    # ---- read-only user ---------------------------------------------------------
    try:
        rsess = seahub_login(reader, reader_pw)
    except AssertionError:
        rsess = seahub_login(reader_username, reader_pw)
    st, page_r = file_page(rsess, repo_id, "test.svg")
    form_r = parse_wopi_form(page_r)
    check("seahub_readonly_gets_wopi_view_form", st == 200 and form_r is not None, (form_r or {}).get("action", "")[:120])
    if form_r:
        form_r["action"] = form_r["action"]  # vectorcraft editor; the host page is the same for every editor
        st, hdrs, _, rcfg = bridge_open(form_r)
        check("bridge_readonly_open", st == 200 and rcfg and rcfg.get("userCanWrite") is False, f"status={st} canWrite={(rcfg or {}).get('userCanWrite')}")
        cur, _ = download(admin, repo_id, "test.svg")
        st, _, body = relay("save", rcfg, {"X-Expected-Version": rcfg["version"], "X-File-Name": "test.svg"}, SVG_V1)
        now, _ = download(admin, repo_id, "test.svg")
        check("bridge_readonly_save_refused_403", st == 403 and now == cur, f"status={st} {body[:100]!r}")
        # Seahub itself, bypassing the bridge: does PutFile honour can_edit?
        st, _, body = Http().req("POST", f"{rcfg['src']}/contents?access_token={rcfg['token']}", SVG_V1,
                                 {"X-WOPI-Override": "PUT", "Content-Type": "application/octet-stream"})
        now2, _ = download(admin, repo_id, "test.svg")
        hist_r = history(admin, repo_id, "test.svg")
        check("seahub_putfile_ignores_can_edit", st == 200 and now2 == SVG_V1 and hist_r[0]["creator"] == reader_username,
              f"status={st} overwritten={now2 == SVG_V1} top_creator={hist_r[0]['creator'] if hist_r else None}  (ok=True means the Seahub gap is real)")

    # ---- ONLYOFFICE ---------------------------------------------------------------
    if oo_up:
        st, _, body = Http().req("GET", f"{ONLYOFFICE}/web-apps/apps/api/documents/api.js")
        check("onlyoffice_apijs_200", st == 200 and len(body) > 1000, f"status={st} len={len(body)}")
        tok = jwt({"c": "version"})
        st, _, body = Http().req("POST", f"{ONLYOFFICE}/coauthoring/CommandService.ashx",
                                 json.dumps({"c": "version", "token": tok}).encode(),
                                 {"Content-Type": "application/json", "Authorization": f"Bearer {tok}"})
        try:
            r = json.loads(body)
        except ValueError:
            r = {"raw": body[:200].decode("utf-8", "replace")}
        check("onlyoffice_jwt_command_ok", st == 200 and r.get("error") == 0, json.dumps(r)[:200])
        # Conversion round-trip: ONLYOFFICE fetches the docx from Seahub (same fetch path its editor uses).
        st, dl = api(admin, "GET", f"/api2/repos/{repo_id}/file/?p=/test.docx&reuse=1")   # fresh, reusable link
        payload = {"async": False, "filetype": "docx", "key": uuid.uuid4().hex, "outputtype": "pdf", "title": "test.docx", "url": dl}
        payload["token"] = jwt(payload)
        st, _, body = Http().req("POST", f"{ONLYOFFICE}/ConvertService.ashx", json.dumps(payload).encode(),
                                 {"Content-Type": "application/json", "Accept": "application/json", "Authorization": f"Bearer {payload['token']}"}, timeout=180)
        try:
            r = json.loads(body)
        except ValueError:
            r = {"raw": body[:300].decode("utf-8", "replace")}
        ok = st == 200 and r.get("endConvert") is True and r.get("fileUrl")
        if ok:
            st2, _, pdf = Http().req("GET", r["fileUrl"])
            ok = st2 == 200 and pdf.startswith(b"%PDF")
        check("onlyoffice_fetches_from_seahub_and_converts", bool(ok), json.dumps(r)[:200])

    summary = {"seafile_version": seafile_version, "repo_id": repo_id, "ran_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               "passed": sum(c["ok"] for c in checks), "failed": sum(not c["ok"] for c in checks), "checks": checks}
    with open(os.path.join(RESULTS, "slice.json"), "w") as fh:
        json.dump(summary, fh, indent=1)
    print(f"\n{summary['passed']} passed, {summary['failed']} failed", flush=True)
    return 0 if summary["failed"] == 0 else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001
        import traceback
        traceback.print_exc()
        with open(os.path.join(RESULTS, "slice.json"), "w") as fh:
            json.dump({"aborted": repr(exc), "checks": checks}, fh, indent=1)
        sys.exit(2)
