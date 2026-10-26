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
import re
import socket
import warnings
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import urllib.parse

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "integration"))

from gateway.server import (MAX_CONTENT_TYPES_XML_BYTES, Gateway, Handler,
                            OpenRateLimiter, load_dispatch,
                            payload_matches_name)  # noqa: E402
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
        self.save_calls = 0
        self.detail_calls = 0
        self.open_info_calls = 0
        self.user = "alice"
        self.head_id = "head-a"
        self.save_detail_barrier = None
        self.save_detail_calls = 0
        self._write_lock = threading.Lock()

    def file_detail(self, repo_id, path):
        self.detail_calls += 1
        return {"id": self.obj_id, "permission": self.permission, "size": len(self.content)}

    def thirdparty_file_info(self, access_token):
        self.open_info_calls += 1
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
        self.save_calls += 1
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


def zip_payload(entries):
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_STORED) as archive:
        for name, data in entries:
            archive.writestr(name, data)
    return out.getvalue()


def open_user_session(gw):
    session, error = gw.open_session("user-token")
    check("a user-bound token opens", session is not None, str(error))
    return session


def raw_http_request(port, request):
    connection = socket.create_connection(("127.0.0.1", port), timeout=3)
    connection.sendall(request)
    response = b""
    while True:
        chunk = connection.recv(4096)
        if not chunk:
            break
        response += chunk
    connection.close()
    return response


def main():
    # ---- bounded /open rate limit ----------------------------------------
    capacity_clock = [0.0]
    capacity_limiter = OpenRateLimiter(
        limit=2, window_seconds=60, max_peers=1, clock=lambda: capacity_clock[0])
    capacity_first = capacity_limiter.retry_after("192.0.2.1")
    capacity_full = capacity_limiter.retry_after("192.0.2.2")
    check("rate limiter rejects new peers when its bounded map is full",
          capacity_first is None and capacity_full == 60
          and len(capacity_limiter._windows) == 1)
    capacity_clock[0] = 60.0
    check("a full peer map admits a new peer after window expiry",
          capacity_limiter.retry_after("192.0.2.2") is None
          and len(capacity_limiter._windows) == 1)

    default_limiter = OpenRateLimiter(clock=lambda: 10.25)
    default_admissions = [default_limiter.retry_after("192.0.2.3")
                          for _ in range(60)]
    default_retry = default_limiter.retry_after("192.0.2.3")
    check("default limiter admits 60 requests and then rejects the 61st",
          all(delay is None for delay in default_admissions) and default_retry == 60)

    fractional_clock = [0.0]
    fractional_limiter = OpenRateLimiter(
        limit=1, window_seconds=60, clock=lambda: fractional_clock[0])
    fractional_limiter.retry_after("192.0.2.4")
    fractional_clock[0] = 59.25
    check("fractional Retry-After rounds up to a whole second",
          fractional_limiter.retry_after("192.0.2.4") == 1)

    sampled_under_lock = []
    lock_check_limiter = None

    def lock_check_clock():
        sampled_under_lock.append(lock_check_limiter._lock.locked())
        return 0.0

    lock_check_limiter = OpenRateLimiter(clock=lock_check_clock)
    lock_check_limiter.retry_after("192.0.2.5")
    check("rate-limit clock is sampled under its state lock",
          sampled_under_lock == [True])

    rate_clock = [0.0]
    rate_seafile = FakeSeafile()
    rate_gw = make_gateway(rate_seafile)
    rate_gw.open_rate_limiter = OpenRateLimiter(
        limit=1, window_seconds=60, max_peers=1, clock=lambda: rate_clock[0])
    rate_httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    rate_httpd.gateway = rate_gw
    rate_thread = threading.Thread(target=rate_httpd.serve_forever, daemon=True)
    rate_thread.start()
    rate_origin = f"http://127.0.0.1:{rate_httpd.server_port}"

    def open_request(extra_headers=None):
        conn = http.client.HTTPConnection("127.0.0.1", rate_httpd.server_port, timeout=3)
        headers = {"Content-Type": "application/x-www-form-urlencoded",
                   "Origin": rate_origin}
        headers.update(extra_headers or {})
        conn.request("POST", "/open/?format=json",
                     urllib.parse.urlencode({"access_token": "user-token"}), headers)
        response = conn.getresponse()
        body = response.read()
        result = (response.status, response.getheader("Retry-After"),
                  response.getheader("Connection"), body)
        conn.close()
        return result

    try:
        allowed_status, _, _, _ = open_request()
        limited_status, retry_after, close_header, _ = open_request(
            {"X-Forwarded-For": "198.51.100.8"})
        check("/open admits requests below the peer rate limit", allowed_status == 200,
              f"HTTP {allowed_status}")
        check("spoofed X-Forwarded-For cannot bypass /open rate limit",
              limited_status == 429 and retry_after == "60",
              f"HTTP {limited_status}, Retry-After={retry_after}")
        check("rate-limited /open closes the HTTP connection with its unread body",
              close_header == "close", f"Connection={close_header}")
        check("rate-limited /open is rejected before calling Seafile",
              rate_seafile.open_info_calls == 1,
              f"thirdparty_file_info calls={rate_seafile.open_info_calls}")
        check("rate-limit peer map stays bounded",
              len(rate_gw.open_rate_limiter._windows) <= 1,
              f"tracked peers={len(rate_gw.open_rate_limiter._windows)}")
        rate_clock[0] = 60.0
        expired_status, _, _, _ = open_request()
        check("/open rate limit resets after its window", expired_status == 200,
              f"HTTP {expired_status}")
    finally:
        rate_httpd.shutdown()
        rate_thread.join(timeout=3)
        rate_httpd.server_close()

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
    seafile = FakeSeafile()
    gw = make_gateway(seafile)
    gw.max_bytes = 10
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

    embedded_get = (f"GET /healthz HTTP/1.1\r\nHost: 127.0.0.1:{httpd.server_port}\r\n\r\n"
                    .encode())
    cross_origin_pipelined = raw_http_request(
        httpd.server_port,
        f"POST /session/missing/dirty HTTP/1.1\r\n".encode()
        + f"Host: 127.0.0.1:{httpd.server_port}\r\nOrigin: https://attacker.invalid\r\n".encode()
        + f"Content-Length: {len(embedded_get)}\r\n\r\n".encode()
        + embedded_get)
    check("cross-origin rejection closes instead of parsing its body as another request",
          cross_origin_pipelined.startswith(b"HTTP/1.1 403")
          and cross_origin_pipelined.count(b"HTTP/1.1 ") == 1
          and b"Connection: close" in cross_origin_pipelined,
          cross_origin_pipelined[:160].decode("latin-1", "replace"))

    expired_pipelined = raw_http_request(
        httpd.server_port,
        f"POST /session/not-a-session/dirty HTTP/1.1\r\n".encode()
        + f"Host: 127.0.0.1:{httpd.server_port}\r\nOrigin: {origin}\r\n".encode()
        + f"Content-Length: {len(embedded_get)}\r\n\r\n".encode()
        + embedded_get)
    check("expired-session rejection closes instead of parsing its body as another request",
          expired_pipelined.startswith(b"HTTP/1.1 404")
          and expired_pipelined.count(b"HTTP/1.1 ") == 1
          and b"Connection: close" in expired_pipelined,
          expired_pipelined[:160].decode("latin-1", "replace"))

    unknown_route_pipelined = raw_http_request(
        httpd.server_port,
        b"POST /unimplemented HTTP/1.1\r\n"
        + f"Host: 127.0.0.1:{httpd.server_port}\r\nOrigin: {origin}\r\n".encode()
        + f"Content-Length: {len(embedded_get)}\r\n\r\n".encode()
        + embedded_get)
    check("unknown POST route closes instead of parsing its body as another request",
          unknown_route_pipelined.startswith(b"HTTP/1.1 404")
          and unknown_route_pipelined.count(b"HTTP/1.1 ") == 1
          and b"Connection: close" in unknown_route_pipelined,
          unknown_route_pipelined[:160].decode("latin-1", "replace"))

    get_with_body = raw_http_request(
        httpd.server_port,
        f"GET /healthz HTTP/1.1\r\nHost: 127.0.0.1:{httpd.server_port}\r\n".encode()
        + f"Content-Length: {len(embedded_get)}\r\n\r\n".encode()
        + embedded_get)
    check("GET body is rejected without parsing pipelined bytes",
          get_with_body.startswith(b"HTTP/1.1 413")
          and get_with_body.count(b"HTTP/1.1 ") == 1
          and b"Connection: close" in get_with_body,
          get_with_body[:160].decode("latin-1", "replace"))

    legacy_get = raw_http_request(httpd.server_port, b"GET /healthz\r\n")
    check("HTTP/0.9 GET is closed before accessing its header map", legacy_get == b"",
          legacy_get[:120].decode("latin-1", "replace"))

    http_session, http_open_error = gw.open_session("user-token")
    check("HTTP body tests use a bound synthetic session", http_session is not None,
          str(http_open_error))
    seafile_calls_before_body_tests = seafile.open_info_calls
    oversized_open = http.client.HTTPConnection("127.0.0.1", httpd.server_port, timeout=3)
    oversized_open.request(
        "POST", "/open/?format=json", b"x" * (64 * 1024 + 1),
        {"Content-Type": "application/x-www-form-urlencoded", "Origin": origin})
    oversized_open_response = oversized_open.getresponse()
    oversized_open_response.read()
    check("oversized /open body is rejected and connection is closed",
          oversized_open_response.status == 413
          and oversized_open_response.getheader("Connection") == "close",
          f"HTTP {oversized_open_response.status}")
    check("oversized /open body never reaches Seafile",
          seafile.open_info_calls == seafile_calls_before_body_tests,
          f"thirdparty_file_info calls={seafile.open_info_calls}")
    oversized_open.close()

    http_session.unsaved = True
    oversized_dirty = http.client.HTTPConnection("127.0.0.1", httpd.server_port, timeout=3)
    oversized_dirty.request(
        "POST", f"/session/{http_session.sid}/dirty", b"false" + b" " * 60,
        {"Content-Type": "text/plain", "Origin": origin})
    oversized_dirty_response = oversized_dirty.getresponse()
    oversized_dirty_response.read()
    check("oversized dirty report is rejected with a closed connection",
          oversized_dirty_response.status == 413
          and oversized_dirty_response.getheader("Connection") == "close",
          f"HTTP {oversized_dirty_response.status}")
    check("oversized dirty report cannot clear unsaved state", http_session.unsaved is True)
    oversized_dirty.close()

    exact_dirty = http.client.HTTPConnection("127.0.0.1", httpd.server_port, timeout=3)
    exact_dirty.request(
        "POST", f"/session/{http_session.sid}/dirty", b"true" + b" " * 60,
        {"Content-Type": "text/plain", "Origin": origin})
    exact_dirty_response = exact_dirty.getresponse()
    exact_dirty_body = exact_dirty_response.read()
    check("exact 64-byte dirty report is accepted",
          exact_dirty_response.status == 200 and b'"unsaved": true' in exact_dirty_body,
          f"HTTP {exact_dirty_response.status}")
    exact_dirty.close()

    oversized_save = http.client.HTTPConnection("127.0.0.1", httpd.server_port, timeout=3)
    oversized_save.request(
        "POST", f"/session/{http_session.sid}/save", b"x" * 11,
        {"Content-Type": "application/octet-stream", "Origin": origin})
    oversized_save_response = oversized_save.getresponse()
    oversized_save_body = oversized_save_response.read().decode()
    check("oversized save body is rejected and connection is closed",
          oversized_save_response.status == 413
          and oversized_save_response.getheader("Connection") == "close",
          f"HTTP {oversized_save_response.status}: {oversized_save_body}")
    check("oversized save body does not write to Seafile", seafile.written == [])
    oversized_save.close()

    embedded_get = (f"GET /healthz HTTP/1.1\r\nHost: 127.0.0.1:{httpd.server_port}\r\n\r\n"
                    .encode())
    invalid_frames = (
        ("duplicate Content-Length", b"Content-Length: 0\r\nContent-Length: 0\r\n"),
        ("comma-separated Content-Length", b"Content-Length: 0, 0\r\n"),
        ("Transfer-Encoding with Content-Length",
         b"Content-Length: 0\r\nTransfer-Encoding: chunked\r\n"),
    )
    for label, framing in invalid_frames:
        invalid_frame_reply = raw_http_request(
            httpd.server_port,
            f"POST /session/{http_session.sid}/dirty HTTP/1.1\r\n".encode()
            + f"Host: 127.0.0.1:{httpd.server_port}\r\nOrigin: {origin}\r\n".encode()
            + framing + b"\r\n" + embedded_get)
        check(f"{label} is rejected with connection closure",
              invalid_frame_reply.startswith(b"HTTP/1.1 400")
              and invalid_frame_reply.count(b"HTTP/1.1 ") == 1
              and b"Connection: close" in invalid_frame_reply,
              invalid_frame_reply[:160].decode("latin-1", "replace"))
        check(f"{label} cannot clear unsaved state", http_session.unsaved is True)

    truncated = socket.create_connection(("127.0.0.1", httpd.server_port), timeout=3)
    truncated.sendall((
        f"POST /session/{http_session.sid}/dirty HTTP/1.1\r\n"
        f"Host: 127.0.0.1:{httpd.server_port}\r\nOrigin: {origin}\r\n"
        "Content-Length: 5\r\n\r\ntrue"
    ).encode())
    truncated.shutdown(socket.SHUT_WR)
    truncated_reply = b""
    while True:
        chunk = truncated.recv(4096)
        if not chunk:
            break
        truncated_reply += chunk
    truncated.close()
    check("truncated dirty report is rejected without clearing state",
          truncated_reply.startswith(b"HTTP/1.1 400")
          and b"Connection: close" in truncated_reply
          and http_session.unsaved is True,
          truncated_reply[:160].decode("latin-1", "replace"))

    truncated_save = socket.create_connection(("127.0.0.1", httpd.server_port), timeout=3)
    truncated_save.sendall((
        f"POST /session/{http_session.sid}/save HTTP/1.1\r\n"
        f"Host: 127.0.0.1:{httpd.server_port}\r\nOrigin: {origin}\r\n"
        "Content-Length: 10\r\n\r\n12345"
    ).encode())
    truncated_save.shutdown(socket.SHUT_WR)
    truncated_save_reply = b""
    while True:
        chunk = truncated_save.recv(4096)
        if not chunk:
            break
        truncated_save_reply += chunk
    truncated_save.close()
    check("truncated save body is rejected and connection is closed",
          truncated_save_reply.startswith(b"HTTP/1.1 400")
          and b"Connection: close" in truncated_save_reply
          and seafile.written == [],
          truncated_save_reply[:160].decode("latin-1", "replace"))

    malformed = socket.create_connection(("127.0.0.1", httpd.server_port), timeout=3)
    malformed.sendall((
        f"POST /session/{http_session.sid}/dirty HTTP/1.1\r\n"
        f"Host: 127.0.0.1:{httpd.server_port}\r\n"
        f"Origin: {origin}\r\nContent-Length: -1\r\n\r\n"
        f"GET /healthz HTTP/1.1\r\nHost: 127.0.0.1:{httpd.server_port}\r\n\r\n"
    ).encode())
    malformed_reply = b""
    while True:
        chunk = malformed.recv(4096)
        if not chunk:
            break
        malformed_reply += chunk
    malformed.close()
    check("negative Content-Length is rejected without parsing pipelined bytes",
          malformed_reply.startswith(b"HTTP/1.1 400")
          and malformed_reply.count(b"HTTP/1.1 ") == 1
          and b"Connection: close" in malformed_reply,
          malformed_reply[:160].decode("latin-1", "replace"))

    huge_length_socket = socket.create_connection(("127.0.0.1", httpd.server_port), timeout=3)
    huge_length_socket.sendall((
        f"POST /session/{http_session.sid}/dirty HTTP/1.1\r\n"
        f"Host: 127.0.0.1:{httpd.server_port}\r\n"
        f"Origin: {origin}\r\nContent-Length: {'9' * 5000}\r\n\r\n"
        f"GET /healthz HTTP/1.1\r\nHost: 127.0.0.1:{httpd.server_port}\r\n\r\n"
    ).encode())
    huge_length_reply = b""
    while True:
        chunk = huge_length_socket.recv(4096)
        if not chunk:
            break
        huge_length_reply += chunk
    huge_length_socket.close()
    check("unrepresentably long Content-Length is rejected and connection closed",
          huge_length_reply.startswith(b"HTTP/1.1 400")
          and huge_length_reply.count(b"HTTP/1.1 ") == 1
          and b"Connection: close" in huge_length_reply,
          huge_length_reply[:160].decode("latin-1", "replace"))

    empty_transfer_encoding = socket.create_connection(
        ("127.0.0.1", httpd.server_port), timeout=3)
    empty_transfer_encoding.sendall((
        f"POST /session/{http_session.sid}/dirty HTTP/1.1\r\n"
        f"Host: 127.0.0.1:{httpd.server_port}\r\nOrigin: {origin}\r\n"
        "Transfer-Encoding:\r\n\r\n0\r\n\r\n"
        f"GET /healthz HTTP/1.1\r\nHost: 127.0.0.1:{httpd.server_port}\r\n\r\n"
    ).encode())
    transfer_reply = b""
    while True:
        chunk = empty_transfer_encoding.recv(4096)
        if not chunk:
            break
        transfer_reply += chunk
    empty_transfer_encoding.close()
    check("empty Transfer-Encoding is rejected and connection closed",
          transfer_reply.startswith(b"HTTP/1.1 400")
          and transfer_reply.count(b"HTTP/1.1 ") == 1
          and b"Connection: close" in transfer_reply,
          transfer_reply[:160].decode("latin-1", "replace"))

    for label, raw_length in (("leading NBSP", b"\xa05"),
                              ("trailing NEL", b"5\x85")):
        http_session.unsaved = True
        bad_whitespace = socket.create_connection(
            ("127.0.0.1", httpd.server_port), timeout=3)
        bad_whitespace.sendall(
            f"POST /session/{http_session.sid}/dirty HTTP/1.1\r\n".encode()
            + f"Host: 127.0.0.1:{httpd.server_port}\r\nOrigin: {origin}\r\n".encode()
            + b"Content-Length: " + raw_length + b"\r\n\r\nfalse"
            + f"GET /healthz HTTP/1.1\r\nHost: 127.0.0.1:{httpd.server_port}\r\n\r\n".encode())
        whitespace_reply = b""
        while True:
            chunk = bad_whitespace.recv(4096)
            if not chunk:
                break
            whitespace_reply += chunk
        bad_whitespace.close()
        check(f"{label} in Content-Length is rejected without parsing pipelined bytes",
              whitespace_reply.startswith(b"HTTP/1.1 400")
              and whitespace_reply.count(b"HTTP/1.1 ") == 1
              and b"Connection: close" in whitespace_reply,
              whitespace_reply[:160].decode("latin-1", "replace"))
        check(f"{label} in Content-Length cannot clear unsaved state",
              http_session.unsaved is True)

    malformed_header_variants = (
        ("space before Content-Length colon",
         b"Content-Length : " + str(len(embedded_get)).encode() + b"\r\n"),
        ("tab before Content-Length colon",
         b"Content-Length\t: " + str(len(embedded_get)).encode() + b"\r\n"),
        ("malformed field before valid Content-Length",
         b"Malformed Header\r\nContent-Length: "
         + str(len(embedded_get)).encode() + b"\r\n"),
        ("stray carriage return before Content-Length",
         b"X-Review: x\r\rContent-Length: "
         + str(len(embedded_get)).encode() + b"\r\n"),
        ("line feed then carriage return before Content-Length",
         b"X-Review: x\n\rContent-Length: "
         + str(len(embedded_get)).encode() + b"\r\n"),
    )
    for label, malformed_header in malformed_header_variants:
        http_session.unsaved = True
        malformed_headers_reply = raw_http_request(
            httpd.server_port,
            f"POST /session/{http_session.sid}/dirty HTTP/1.1\r\n".encode()
            + f"Host: 127.0.0.1:{httpd.server_port}\r\nOrigin: {origin}\r\n".encode()
            + malformed_header + b"\r\n" + embedded_get)
        check(f"{label} is rejected without parsing pipelined bytes",
              malformed_headers_reply.startswith(b"HTTP/1.1 400")
              and malformed_headers_reply.count(b"HTTP/1.1 ") == 1
              and b"Connection: close" in malformed_headers_reply,
              malformed_headers_reply[:160].decode("latin-1", "replace"))
        check(f"{label} cannot clear unsaved state", http_session.unsaved is True)

    previous_seafile_origin = os.environ.get("ARTCRAFT_SEAFILE_ORIGIN")
    os.environ["ARTCRAFT_SEAFILE_ORIGIN"] = "https://seafile.example.test"
    host_page_connection = http.client.HTTPConnection(
        "127.0.0.1", httpd.server_port, timeout=3)
    host_page_connection.request(
        "POST", "/open/", urllib.parse.urlencode({"access_token": "user-token"}),
        {"Content-Type": "application/x-www-form-urlencoded", "Origin": origin,
         "Connection": "close"})
    host_page_response = host_page_connection.getresponse()
    host_page_body = host_page_response.read().decode()
    csp_header = host_page_response.getheader("Content-Security-Policy", "")
    host_page_connection.close()
    script_nonce = re.search(r'<script nonce="([^"]+)"', host_page_body)
    style_nonce = re.search(r'<style nonce="([^"]+)"', host_page_body)
    csp_nonce = re.search(r"script-src 'nonce-([^']+)'", csp_header)
    check("the capability host page uses a nonce-bound strict CSP",
          host_page_response.status == 200 and script_nonce and style_nonce and csp_nonce
          and script_nonce.group(1) == style_nonce.group(1) == csp_nonce.group(1)
          and "default-src 'none'" in csp_header
          and "frame-ancestors https://seafile.example.test" in csp_header,
          f"HTTP {host_page_response.status}; CSP nonce-bound={bool(csp_nonce)}")

    second_host_connection = http.client.HTTPConnection(
        "127.0.0.1", httpd.server_port, timeout=3)
    second_host_connection.request(
        "POST", "/open/", urllib.parse.urlencode({"access_token": "user-token"}),
        {"Content-Type": "application/x-www-form-urlencoded", "Origin": origin,
         "Connection": "close"})
    second_host_response = second_host_connection.getresponse()
    second_host_response.read()
    second_csp = second_host_response.getheader("Content-Security-Policy", "")
    second_host_connection.close()
    second_nonce = re.search(r"script-src 'nonce-([^']+)'", second_csp)
    check("the host-page CSP nonce is fresh per response",
          csp_nonce and second_nonce and csp_nonce.group(1) != second_nonce.group(1),
          f"distinct nonce={bool(csp_nonce and second_nonce and csp_nonce.group(1) != second_nonce.group(1))}")

    invalid_origin_values = (
        "https://seafile.example.test" + chr(13) + chr(10) + "X-Injected: yes",
        "https://seafile.example.test;img-src",
        "https://seafile.example.test%0aevil",
        "https://@seafile.example.test",
        "https://seafile.example.test?",
        "https://seafile.example.test#",
    )
    invalid_origin_responses = []
    for invalid_origin in invalid_origin_values:
        os.environ["ARTCRAFT_SEAFILE_ORIGIN"] = invalid_origin
        invalid_origin_connection = http.client.HTTPConnection(
            "127.0.0.1", httpd.server_port, timeout=3)
        invalid_origin_connection.request(
            "POST", "/open/", urllib.parse.urlencode({"access_token": "user-token"}),
            {"Content-Type": "application/x-www-form-urlencoded", "Origin": origin,
             "Connection": "close"})
        invalid_origin_response = invalid_origin_connection.getresponse()
        invalid_origin_response.read()
        invalid_origin_csp = invalid_origin_response.getheader("Content-Security-Policy", "")
        injected_header = invalid_origin_response.getheader("X-Injected")
        invalid_origin_connection.close()
        invalid_origin_responses.append((
            invalid_origin_response.status == 200
            and "frame-ancestors 'none'" in invalid_origin_csp
            and injected_header is None
        ))
    check("malformed configured Seafile origins fail closed without header injection",
          all(invalid_origin_responses),
          f"{sum(invalid_origin_responses)}/{len(invalid_origin_values)} rejected safely")

    os.environ["ARTCRAFT_SEAFILE_ORIGIN"] = "https://seafile.example.test:443"
    default_port_connection = http.client.HTTPConnection(
        "127.0.0.1", httpd.server_port, timeout=3)
    default_port_connection.request(
        "POST", "/open/?format=json",
        urllib.parse.urlencode({"access_token": "user-token"}),
        {"Content-Type": "application/x-www-form-urlencoded", "Origin": "https://seafile.example.test",
         "Connection": "close"})
    default_port_response = default_port_connection.getresponse()
    default_port_body = default_port_response.read().decode()
    default_port_connection.close()
    check("configured default HTTPS port matches the browser's normalized Origin",
          default_port_response.status == 200 and '"ok": true' in default_port_body,
          f"HTTP {default_port_response.status}")
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

    # ---- PhotoCraft native bundle shape ---------------------------------
    pcraft_fixture = os.path.join(os.path.dirname(__file__), "..", "docs", "reviews",
                                  "GR-033", "runtime", "photocraft-smoke.pcraft")
    with open(pcraft_fixture, "rb") as handle:
        native_pcraft = handle.read()
    check("the project-native PhotoCraft fixture has the expected ZIP manifest",
          payload_matches_name("synthetic.pcraft", native_pcraft))
    check("malformed .pcraft ZIP is rejected",
          not payload_matches_name("synthetic.pcraft", b"not a ZIP archive"))
    missing_manifest = zip_payload([("thumb.png", b"png")])
    check(".pcraft ZIP without a root manifest is rejected",
          not payload_matches_name("synthetic.pcraft", missing_manifest))
    nested_manifest = zip_payload([("nested/manifest.json", b"{}")])
    check("nested manifest is not accepted as the .pcraft root manifest",
          not payload_matches_name("synthetic.pcraft", nested_manifest))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        duplicate_manifest = zip_payload([("manifest.json", b"{}"),
                                          ("manifest.json", b"{}")])
    check("duplicate exact-root manifests are rejected",
          not payload_matches_name("synthetic.pcraft", duplicate_manifest))
    empty_manifest = zip_payload([("manifest.json", b"")])
    check("empty exact-root manifest is rejected",
          not payload_matches_name("synthetic.pcraft", empty_manifest))

    invalid_pcraft = nested_manifest
    seafile = FakeSeafile()
    gw = make_gateway(seafile)
    pcraft_session = gw.sessions.create(
        repo_id="repo", path="/a.pcraft", name="a.pcraft", file_id="aaaa",
        user="alice", can_edit=True, user_authorized=True, access_token="user-token",
        app="photocraft", head_commit_id="head-a")
    result, status = gw.save(pcraft_session, invalid_pcraft, name="a.pcraft")
    check("invalid .pcraft save is refused before calling Seafile",
          status == 400 and result["ok"] is False and seafile.save_calls == 0
          and seafile.written == [], f"HTTP {status}; save calls={seafile.save_calls}")

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
