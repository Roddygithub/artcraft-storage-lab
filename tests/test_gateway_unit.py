#!/usr/bin/env python3
"""Unit checks for the gateway's security-critical logic.

These are the rules that must hold no matter what the network does. They need
no Seafile instance: they exercise the gateway's own code.

    python3 tests/test_gateway_unit.py
"""

import os
import sys
import time
import threading
import zipfile
import io
import http.client
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import urllib.parse

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "integration"))

from gateway.server import (MAX_CONTENT_TYPES_XML_BYTES, Gateway, Handler,
                            load_dispatch, payload_matches_name)  # noqa: E402
from gateway.seafile import Seafile, SeafileError  # noqa: E402
from gateway.sessions import SessionStore  # noqa: E402

FAILURES = []


def check(name, condition, detail=""):
    print(f"[{'PASS' if condition else 'FAIL'}] {name}" + (f"  -- {detail}" if detail else ""))
    if not condition:
        FAILURES.append(name)
    return condition


class FakeSeafile:
    """Just enough of the Seafile client for the gateway's checks."""

    def __init__(self, permission="rw", obj_id="aaaa", content=b"hello"):
        self.permission = permission
        self.obj_id = obj_id
        self.content = content
        self.written = []
        self.detail_calls = 0
        self.user = "alice"
        self.head_id = "head-a"
        self.save_detail_barrier = None
        self.save_detail_calls = 0
        self._write_lock = threading.Lock()

    def file_detail(self, repo_id, path):
        self.detail_calls += 1
        return {"id": self.obj_id, "permission": self.permission, "size": len(self.content)}

    def thirdparty_file_info(self, access_token):
        return {"repo_id": "repo", "file_path": "/a.docx", "file_name": "a.docx",
                "username": self.user, "file_id": self.obj_id,
                "head_commit_id": self.head_id, "permission": self.permission,
                "can_edit": self.permission in ("rw", "cloud-edit", "preview-edit")}

    def user_file_detail(self, repo_id, path, username, access_token):
        info = self.thirdparty_file_info(access_token)
        return {"id": info["file_id"], "permission": info["permission"],
                "head_commit_id": info["head_commit_id"], "size": len(self.content)}

    def download(self, repo_id, path):
        return self.content

    def thirdparty_file_content(self, access_token, expected_file_id, max_bytes=None):
        if self.obj_id != expected_file_id:
            from gateway.seafile import SeafileError
            raise SeafileError("conflict", status=409)
        return self.content

    def thirdparty_file_save(self, access_token, expected_id, expected_head, name, data):
        if self.save_detail_barrier:
            barrier = self.save_detail_barrier
            self.save_detail_calls += 1
            if self.save_detail_calls >= 2:
                self.save_detail_barrier = None
            barrier.wait()
        with self._write_lock:
            if self.permission not in ("rw", "cloud-edit", "preview-edit"):
                from gateway.seafile import SeafileError
                raise SeafileError("permission revoked", status=403)
            if self.obj_id != expected_id or self.head_id != expected_head:
                from gateway.seafile import SeafileError
                raise SeafileError("conflict", status=409)
            self.content = data
            self.obj_id = "bbbb"
            self.head_id = "head-b"
            self.written.append(("repo", "/a.docx", data))
            return {"file_id": self.obj_id, "head_commit_id": self.head_id}

    def update_file(self, repo_id, path, data):
        self.written.append((repo_id, path, data))
        self.obj_id = "bbbb"
        return self.obj_id


class UpstreamErrorHandler(BaseHTTPRequestHandler):
    def log_message(self, *_args):
        pass

    def do_GET(self):
        self.send_response(403)
        self.send_header("Content-Length", "0")
        self.end_headers()


class EchoSaveErrorHandler(BaseHTTPRequestHandler):
    def log_message(self, *_args):
        pass

    def do_POST(self):
        body = f"proxy error at {self.path}".encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class LargeContentHandler(BaseHTTPRequestHandler):
    def log_message(self, *_args):
        pass

    def do_GET(self):
        body = b"x" * 64
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def make_gateway(seafile, dispatch=None):
    dispatch = dispatch or {
        "xlsx": {"app": "gridcraft", "url": "/artcraft/gridcraft/?host=parent"},
        "docx": {"app": "wordcraft", "url": "/artcraft/wordcraft/?host=parent"},
    }
    return Gateway(seafile, dispatch)


def valid_docx():
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w") as archive:
        archive.writestr("[Content_Types].xml",
                         "<Types><Override ContentType="
                         "application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"
                         "/></Types>")
    return out.getvalue()


def open_user_session(gw):
    session, error = gw.open_session("user-token")
    check("a user-bound token opens", session is not None, str(error))
    return session


def main():
    # ---- the extension rule ------------------------------------------------
    gw = make_gateway(FakeSeafile())
    check("the extension is the one after the last dot",
          gw.app_for("report.final.docx") is not None and gw.app_for("archive.tar.gz") is None,
          "report.final.docx -> docx")
    check("the extension is lowercased",
          gw.app_for("REPORT.XLSX") is not None, "REPORT.XLSX -> xlsx")
    check("a file with no dot has no editor", gw.app_for("README") is None)

    # ---- a read-only session cannot write ---------------------------------
    seafile = FakeSeafile(permission="r")
    gw = make_gateway(seafile)
    session, error = gw.open_session("user-token")
    check("a read-only file opens in view mode", session is not None and session.can_edit is False,
          f"can_edit={getattr(session, 'can_edit', None)}")
    result, status = gw.save(session, valid_docx())
    check("a read-only session cannot write", status == 403 and result["ok"] is False, str(result)[:120])
    check("a refused write writes nothing", seafile.written == [], f"{len(seafile.written)} write(s)")

    # ---- the permission is re-read on every write --------------------------
    seafile = FakeSeafile(permission="rw")
    gw = make_gateway(seafile)
    session = open_user_session(gw)
    check("an editable file may write", session.can_edit is True)
    # the permission is taken away while the editor is open
    seafile.permission = "r"
    result, status = gw.save(session, valid_docx())
    check("a revoked permission stops the write", status == 403 and result["ok"] is False,
          f"HTTP {status}")
    check("the revoked write wrote nothing", seafile.written == [])

    # ---- a stale session is refused ---------------------------------------
    seafile = FakeSeafile(permission="rw", obj_id="aaaa")
    gw = make_gateway(seafile)
    session = open_user_session(gw)
    seafile.obj_id = "cccc"          # somebody else saved
    result, status = gw.save(session, valid_docx())
    check("a stale save is refused", status == 409 and result.get("conflict") is True, f"HTTP {status}")
    check("the refused stale save wrote nothing", seafile.written == [])

    # ---- a current session writes -----------------------------------------
    seafile = FakeSeafile(permission="rw", obj_id="aaaa")
    gw = make_gateway(seafile)
    session = open_user_session(gw)
    result, status = gw.save(session, valid_docx())
    check("a current save is accepted", status == 200 and result["ok"] is True, str(result)[:120])
    check("the write happened", len(seafile.written) == 1)
    check("the session now holds the new content id", session.file_id == "bbbb",
          f"file_id={session.file_id}")

    # ---- the document size limit ------------------------------------------
    seafile = FakeSeafile()
    gw = make_gateway(seafile)
    gw.max_bytes = 10
    session = open_user_session(gw)
    result, status = gw.save(session, b"x" * 11)
    check("a document over the limit is refused", status == 413 and result["ok"] is False,
          f"HTTP {status}")
    check("the oversized save wrote nothing", seafile.written == [])

    # ---- an unknown extension is refused ----------------------------------
    gw = make_gateway(FakeSeafile())
    check("an extension with no editor is refused", gw.app_for("a.unknownext") is None)

    # ---- direct HTTP-style opening is closed -----------------------------
    session, error = gw.open_session_direct("repo", "/a.docx")
    check("direct repo/path opening is disabled", session is None and "disabled" in error)

    httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    httpd.gateway = gw
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    connection = http.client.HTTPConnection("127.0.0.1", httpd.server_port, timeout=3)
    origin = f"http://127.0.0.1:{httpd.server_port}"
    connection.request("POST", "/open/?format=json",
                       urllib.parse.urlencode({"repo_id": "repo", "path": "/a.docx"}),
                       {"Content-Type": "application/x-www-form-urlencoded", "Origin": origin,
                        "Connection": "close"})
    response = connection.getresponse()
    body = response.read().decode()
    connection.close()
    check("HTTP direct /open cannot mint a session",
          response.status == 401 and "access_token" in body,
          f"HTTP {response.status}: {body[:120]}")

    connection = http.client.HTTPConnection("127.0.0.1", httpd.server_port, timeout=3)
    connection.request("POST", "/open/?format=json",
                       urllib.parse.urlencode({"access_token": "user-token"}),
                       {"Content-Type": "application/x-www-form-urlencoded",
                        "Origin": "https://attacker.invalid", "Connection": "close"})
    response = connection.getresponse()
    body = response.read().decode()
    connection.close()
    check("cross-origin POST cannot open or save a document", response.status == 403,
          f"HTTP {response.status}")

    previous_seafile_origin = os.environ.get("ARTCRAFT_SEAFILE_ORIGIN")
    os.environ["ARTCRAFT_SEAFILE_ORIGIN"] = "https://seafile.example.test"
    connection = http.client.HTTPConnection("127.0.0.1", httpd.server_port, timeout=3)
    connection.request("POST", "/open/?format=json",
                       urllib.parse.urlencode({"access_token": "user-token"}),
                       {"Content-Type": "application/x-www-form-urlencoded",
                        "Origin": "https://seafile.example.test", "Connection": "close"})
    allowed_response = connection.getresponse()
    allowed_body = allowed_response.read().decode()
    connection.close()
    foreign = http.client.HTTPConnection("127.0.0.1", httpd.server_port, timeout=3)
    foreign.request("POST", "/session/not-a-session/dirty", "true",
                    {"Content-Type": "text/plain", "Origin": "https://seafile.example.test",
                     "Connection": "close"})
    foreign_response = foreign.getresponse()
    foreign_response.read()
    foreign.close()
    if previous_seafile_origin is None:
        os.environ.pop("ARTCRAFT_SEAFILE_ORIGIN", None)
    else:
        os.environ["ARTCRAFT_SEAFILE_ORIGIN"] = previous_seafile_origin
    httpd.shutdown()
    thread.join(timeout=3)
    check("configured Seafile origin may only use the open handoff",
          allowed_response.status == 200 and '"ok": true' in allowed_body
          and foreign_response.status == 403,
          f"open HTTP {allowed_response.status}; dirty HTTP {foreign_response.status}")

    # ---- Save As/export and format mismatch are refused ------------------
    seafile = FakeSeafile()
    gw = make_gateway(seafile)
    session = open_user_session(gw)
    result, status = gw.save(session, valid_docx(), name="export.pdf")
    check("Save As cannot replace the original", status == 400 and not result["ok"])
    result, status = gw.save(session, b"%PDF-1.7", name="a.docx")
    check("PDF export cannot replace a DOCX", status == 400 and not result["ok"])

    large_types = io.BytesIO()
    with zipfile.ZipFile(large_types, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml",
                         "<Types>" + "x" * (MAX_CONTENT_TYPES_XML_BYTES + 1) + "</Types>")
    check("oversized OOXML type metadata is rejected before full decompression",
          not payload_matches_name("bomb.docx", large_types.getvalue()))
    with open(os.path.join(os.path.dirname(__file__), "fixtures", "synthetic.xlsx"), "rb") as f:
        sample_xlsx = f.read()
    check("ordinary XLSX MIME is accepted by the gateway",
          payload_matches_name("synthetic.xlsx", sample_xlsx))
    soundcraft_bundle = io.BytesIO()
    with zipfile.ZipFile(soundcraft_bundle, "w", zipfile.ZIP_STORED) as archive:
        archive.writestr("Synthetic Session.scraft", "{}")
        archive.writestr("Audio Files/clip.wav", b"synthetic audio")
    check("SoundCraft bundle with one root session is accepted",
          payload_matches_name("synthetic.scraftz", soundcraft_bundle.getvalue()))
    invalid_soundcraft = io.BytesIO()
    with zipfile.ZipFile(invalid_soundcraft, "w", zipfile.ZIP_STORED) as archive:
        archive.writestr("Audio Files/clip.wav", b"no session document")
    check("SoundCraft bundle without a root session is rejected",
          not payload_matches_name("synthetic.scraftz", invalid_soundcraft.getvalue()))

    # ---- Seafile capability URLs do not escape through browser errors -----
    upstream = ThreadingHTTPServer(("127.0.0.1", 0), UpstreamErrorHandler)
    upstream_thread = threading.Thread(target=upstream.serve_forever, daemon=True)
    upstream_thread.start()
    client = Seafile(f"http://127.0.0.1:{upstream.server_port}", "")
    gw = make_gateway(client)
    protected = gw.sessions.create(
        repo_id="repo", path="/a.docx", name="a.docx", file_id="aaaa", user="alice",
        can_edit=True, user_authorized=True, access_token="secret-capability-value",
        app="wordcraft", head_commit_id="head-a")
    browser_httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    browser_httpd.gateway = gw
    browser_thread = threading.Thread(target=browser_httpd.serve_forever, daemon=True)
    browser_thread.start()
    connection = http.client.HTTPConnection("127.0.0.1", browser_httpd.server_port, timeout=3)
    connection.request("GET", f"/session/{protected.sid}/document", headers={"Connection": "close"})
    response = connection.getresponse()
    error_body = response.read().decode()
    connection.close()
    browser_httpd.shutdown()
    browser_thread.join(timeout=3)
    browser_httpd.server_close()
    upstream.shutdown()
    upstream_thread.join(timeout=3)
    upstream.server_close()
    check("upstream failure does not leak a capability URL to the browser",
          response.status == 403 and "secret-capability-value" not in error_body
          and "access_token=" not in error_body,
          f"HTTP {response.status}: {error_body[:140]}")

    # A malformed successful save response may echo the capability URL too.
    upstream = ThreadingHTTPServer(("127.0.0.1", 0), EchoSaveErrorHandler)
    upstream_thread = threading.Thread(target=upstream.serve_forever, daemon=True)
    upstream_thread.start()
    client = Seafile(f"http://127.0.0.1:{upstream.server_port}", "")
    gw = make_gateway(client)
    protected = gw.sessions.create(
        repo_id="repo", path="/a.docx", name="a.docx", file_id="aaaa", user="alice",
        can_edit=True, user_authorized=True, access_token="secret-capability-value",
        app="wordcraft", head_commit_id="head-a")
    result, status = gw.save(protected, valid_docx(), name="a.docx")
    upstream.shutdown()
    upstream_thread.join(timeout=3)
    upstream.server_close()
    check("malformed save response cannot leak capability through browser JSON",
          status == 502 and "secret-capability-value" not in str(result)
          and "access_token" not in str(result)
          and result["error"] == "Seafile could not confirm the save",
          f"HTTP {status}: {result}")

    upstream = ThreadingHTTPServer(("127.0.0.1", 0), LargeContentHandler)
    upstream_thread = threading.Thread(target=upstream.serve_forever, daemon=True)
    upstream_thread.start()
    client = Seafile(f"http://127.0.0.1:{upstream.server_port}", "")
    try:
        client.thirdparty_file_content("synthetic-token", "file-id", max_bytes=16)
        bounded = False
    except SeafileError as exc:
        bounded = exc.status == 413
    upstream.shutdown()
    upstream_thread.join(timeout=3)
    upstream.server_close()
    check("Seafile document response is bounded before full buffering", bounded)

    # ---- deterministic CAS race -----------------------------------------
    seafile = FakeSeafile()
    gw = make_gateway(seafile)
    first = open_user_session(gw)
    second = open_user_session(gw)
    seafile.save_detail_barrier = threading.Barrier(2)
    results = []
    threads = [threading.Thread(target=lambda s, d: results.append(gw.save(s, d)),
                                args=(first, valid_docx())),
               threading.Thread(target=lambda s, d: results.append(gw.save(s, d)),
                                args=(second, valid_docx()))]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    statuses = sorted(status for _, status in results)
    check("concurrent saves have one winner", statuses == [200, 409], str(statuses))
    check("the losing concurrent save is explicitly a conflict",
          sum(1 for result, status in results if status == 409 and result.get("conflict")) == 1)
    check("the fake upstream CAS stored one version", len(seafile.written) == 1)

    # ---- the session store -------------------------------------------------
    store = SessionStore(ttl=60, idle_ttl=30, max_sessions=3)
    a = store.create(repo_id="r", path="/a", name="a", file_id="1", user="u", can_edit=True,
                     access_token="t", app="gridcraft", user_authorized=True)
    check("a session is created with an unguessable id", len(a.sid) >= 24, f"{len(a.sid)} chars")
    check("a session is found", store.get(a.sid) is not None)
    check("an unknown session is not found", store.get("nope") is None)
    for i in range(5):
        store.create(repo_id="r", path=f"/{i}", name="x", file_id="1", user="u", can_edit=True,
                         access_token="t", app="gridcraft", user_authorized=True)
    check("the session store is capped", len(store._sessions) <= 3, f"{len(store._sessions)} sessions")
    store.ttl = 0
    check("an expired session is not found", store.get(a.sid) is None)

    # ---- the dispatch table ------------------------------------------------
    dispatch = load_dispatch()
    check("the dispatch table is read from the file", isinstance(dispatch, dict) and dispatch)
    check("every dispatch entry names an app and a url",
          all("app" in v and "url" in v for v in dispatch.values()), str(dispatch)[:120])
    check("the dispatch keys carry no dot", all("." not in k for k in dispatch), str(list(dispatch)))
    # Only the applications that speak the ?host=parent bridge name it in their
    # URL. VectorCraft is driven by its own page API instead, so its URL does
    # not claim a contract it does not implement (REVIEW-04, G4).
    bridge_apps = {"pdfcraft", "gridcraft", "wordcraft"}
    for ext, entry in dispatch.items():
        if entry["app"] in bridge_apps:
            check(f"the {ext} url asks for the host mode", "host=parent" in entry["url"],
                  entry["url"])
        else:
            check(f"the {ext} url does not claim the host mode",
                  "host=parent" not in entry["url"], entry["url"])

    print()
    if FAILURES:
        print(f"FAILED: {len(FAILURES)} check(s): {', '.join(FAILURES)}")
        return 1
    print("ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
