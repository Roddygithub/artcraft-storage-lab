"""End-to-end tests: real HTTP between a browser-like client, the bridge and a fake Seahub WOPI host.

Run:  python3 tests/bridge/test_bridge.py
"""

from __future__ import annotations

import io
import json
import os
import sys
import threading
import unittest
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from wsgiref.simple_server import WSGIRequestHandler, make_server

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bridge.app import Bridge, Config, TransportError, content_matches_extension  # noqa: E402
from fake_seahub import FakeSeahub  # noqa: E402


class _Quiet(WSGIRequestHandler):
    def log_message(self, *a):
        pass


def _docx(text: bytes = b"hello") -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("[Content_Types].xml", "<Types/>")
        zf.writestr("word/document.xml", text)
    return buf.getvalue()


SVG = b'<?xml version="1.0"?><svg xmlns="http://www.w3.org/2000/svg"><rect/></svg>'


class _Http:
    """Minimal client that returns (status, headers, body) and never raises on HTTP errors."""

    @staticmethod
    def call(url, method="GET", headers=None, body=None):
        req = urllib.request.Request(url, data=body, method=method)
        for k, v in (headers or {}).items():
            req.add_header(k, v)
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                return r.status, dict(r.headers), r.read()
        except urllib.error.HTTPError as e:
            return e.code, dict(e.headers), e.read()


class BridgeTestCase(unittest.TestCase):
    seahub: FakeSeahub
    bridge_origin: str

    @classmethod
    def setUpClass(cls):
        cls.seahub = FakeSeahub()
        cls.seahub.start()
        cls.lost_once = {"armed": False}
        real_urlopen = urllib.request.urlopen

        def urlopen(req, timeout=None):
            # Simulate a lost response on PutFile: the write reaches Seahub, the reply is lost.
            if cls.lost_once["armed"] and req.get_method() == "POST" and req.full_url.split("?")[0].endswith("/contents"):
                cls.lost_once["armed"] = False
                real_urlopen(req, timeout=timeout).close()
                raise urllib.error.URLError("connection reset by peer (simulated)")
            return real_urlopen(req, timeout=timeout)

        cls.server = make_server("127.0.0.1", 0, lambda e, s: cls.app(e, s), handler_class=_Quiet)
        cls.bridge_origin = f"http://127.0.0.1:{cls.server.server_port}"
        cls.cfg = Config(
            public_url=cls.bridge_origin,
            seahub_origin=cls.seahub.origin,
            editors={
                "wordcraft": {"app": "wordcraft", "url": "/editors/wordcraft/index.html?host=parent", "extensions": ["docx"], "label": "WordCraft"},
                "vectorcraft": {"app": "vectorcraft", "url": "/editors/vectorcraft/index.html?host=parent", "extensions": ["svg"]},
            },
            static_dir=cls._static_dir(),
            max_bytes=1024 * 1024,
            urlopen=urlopen,
        )
        cls.app = Bridge(cls.cfg)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def _static_dir(cls):
        import tempfile
        d = tempfile.mkdtemp(prefix="bridge-static-")
        os.makedirs(os.path.join(d, "wordcraft"))
        with open(os.path.join(d, "wordcraft", "index.html"), "w") as fh:
            fh.write("<!doctype html><title>stub</title>")
        with open(os.path.join(d, "wordcraft", "app.wasm"), "wb") as fh:
            fh.write(b"\0asm")
        cls._static = d
        return d

    @classmethod
    def tearDownClass(cls):
        import shutil
        shutil.rmtree(cls._static, ignore_errors=True)
        cls.server.shutdown()
        cls.server.server_close()
        cls.seahub.stop()

    # -- helpers -------------------------------------------------------------

    def _file(self, name="report.docx", content=None, can_edit=True, user="alice"):
        fid = f"repo1_{name}_{id(self)}_{len(self.seahub.files)}"
        self.seahub.add_file(fid, name, content if content is not None else _docx())
        token = self.seahub.mint_token(fid, user, can_edit)
        return fid, token, self.seahub.wopi_src(fid)

    def _open(self, editor, token, src, ttl="1893456000000"):
        url = f"{self.bridge_origin}/edit/{editor}?" + urllib.parse.urlencode({"WOPISrc": src, "ui": "en", "rs": "en", "lang": "en"})
        body = urllib.parse.urlencode({"access_token": token, "access_token_ttl": ttl}).encode()
        return _Http.call(url, "POST", {"Content-Type": "application/x-www-form-urlencoded"}, body)

    def _relay(self, op, token, src, headers=None, body=None, origin=None, bridge_header="1"):
        h = {"X-Wopi-Token": token, "X-Wopi-Src": src}
        if bridge_header is not None:
            h["X-Bridge-Request"] = bridge_header
        h["Origin"] = origin if origin is not None else self.bridge_origin
        h.update(headers or {})
        return _Http.call(f"{self.bridge_origin}/relay/{op}", "POST", h, body if body is not None else b"")

    def _save(self, token, src, data, expected, name=None, **kw):
        h = {"Content-Type": "application/octet-stream", "X-Expected-Version": expected}
        if name:
            h["X-File-Name"] = urllib.parse.quote(name)
        return self._relay("save", token, src, h, data, **kw)

    # -- discovery -----------------------------------------------------------

    def test_discovery_matches_seahub_parser_contract(self):
        status, headers, body = _Http.call(f"{self.bridge_origin}/wopi/discovery.xml")
        self.assertEqual(status, 200)
        self.assertIn("xml", headers["Content-Type"])
        root = ET.fromstring(body)
        # Exactly what seahub/wopi/utils.py does: root.iter('action') with ext/name/urlsrc
        actions = {(a.get("name"), a.get("ext")): a.get("urlsrc") for a in root.iter("action")}
        self.assertEqual(actions[("edit", "docx")], f"{self.bridge_origin}/edit/wordcraft")
        self.assertEqual(actions[("view", "docx")], f"{self.bridge_origin}/edit/wordcraft")
        self.assertEqual(actions[("edit", "svg")], f"{self.bridge_origin}/edit/vectorcraft")
        for (name, ext), urlsrc in actions.items():
            self.assertIn(name, ("view", "edit"))
            self.assertNotIn("?", urlsrc, "Seahub appends ?WOPISrc= itself")
            self.assertTrue(urlsrc.startswith(self.bridge_origin))

    # -- open flow -----------------------------------------------------------

    def test_open_renders_host_page_with_csp_and_no_token_in_urls(self):
        fid, token, src = self._file()
        status, headers, body = self._open("wordcraft", token, src)
        self.assertEqual(status, 200, body)
        page = body.decode()
        csp = headers["Content-Security-Policy"]
        self.assertIn(f"frame-ancestors {self.seahub.origin}", csp)
        self.assertIn("default-src 'none'", csp)
        self.assertIn("connect-src 'self'", csp)
        nonce = csp.split("script-src 'nonce-")[1].split("'")[0]
        self.assertIn(f'nonce="{nonce}"', page)
        self.assertIn('src="/host.js"', page)
        cfg = json.loads(page.split('id="bridge-config"')[1].split(">", 1)[1].split("</script>")[0])
        self.assertEqual(cfg["token"], token)
        self.assertEqual(cfg["name"], "report.docx")
        self.assertTrue(cfg["userCanWrite"])
        self.assertEqual(cfg["app"], "wordcraft")
        # The token must not appear in any URL attribute of the page.
        for attr in ("src=", "href=", "action="):
            for chunk in page.split(attr)[1:]:
                self.assertNotIn(token, chunk.split(">")[0])
        self.assertIn("<title>report.docx</title>", page)

    def test_open_refuses_foreign_wopisrc(self):
        fid, token, _ = self._file()
        status, _, body = self._open("wordcraft", token, "https://evil.example/api/v2.1/wopi/files/x")
        self.assertEqual(status, 400)
        self.assertIn("Seahub origin", body.decode())

    def test_open_refuses_wrong_editor_for_extension(self):
        fid, token, src = self._file(name="logo.svg", content=SVG)
        status, _, body = self._open("wordcraft", token, src)
        self.assertEqual(status, 400)
        self.assertIn("does not handle .svg", body.decode())
        status, _, _ = self._open("vectorcraft", token, src)
        self.assertEqual(status, 200)

    def test_open_with_unknown_token_is_401(self):
        fid, token, src = self._file()
        status, _, body = self._open("wordcraft", "deadbeef", src)
        self.assertEqual(status, 401)
        self.assertIn("expired or revoked", body.decode())

    def test_open_requires_form_post(self):
        status, _, _ = _Http.call(f"{self.bridge_origin}/edit/wordcraft?WOPISrc=x")
        self.assertEqual(status, 405)

    # -- relay: read ---------------------------------------------------------

    def test_relay_info_and_file(self):
        fid, token, src = self._file()
        status, _, body = self._relay("info", token, src)
        self.assertEqual(status, 200)
        info = json.loads(body)
        self.assertEqual(info["name"], "report.docx")
        self.assertEqual(info["version"], self.seahub.files[fid]["version"])
        self.assertNotIn("UserId", body.decode())
        status, headers, data = self._relay("file", token, src)
        self.assertEqual(status, 200)
        self.assertEqual(data, self.seahub.files[fid]["content"])
        self.assertEqual(headers["X-Wopi-Version"], info["version"])

    def test_relay_requires_bridge_header_and_same_origin(self):
        fid, token, src = self._file()
        status, _, _ = self._relay("info", token, src, bridge_header=None)
        self.assertEqual(status, 403)
        status, _, _ = self._relay("info", token, src, origin="https://evil.example")
        self.assertEqual(status, 403)
        status, _, _ = self._relay("info", token, src, origin=self.seahub.origin)
        self.assertEqual(status, 403, "even Seahub's origin may not call the relay cross-origin")

    # -- relay: save ---------------------------------------------------------

    def test_save_creates_new_version_attributed_to_user(self):
        fid, token, src = self._file(user="alice")
        v0 = self.seahub.files[fid]["version"]
        new = _docx(b"edited")
        status, _, body = self._save(token, src, new, v0, name="report.docx")
        self.assertEqual(status, 200, body)
        res = json.loads(body)
        f = self.seahub.files[fid]
        self.assertEqual(f["content"], new)
        self.assertEqual(res["version"], f["version"])
        self.assertNotEqual(res["version"], v0)
        self.assertEqual(f["commits"], 2)
        self.assertEqual(f["last_modifier"], "alice")
        self.assertFalse(res["reconciled"])

    def test_save_detects_external_change_and_does_not_overwrite(self):
        fid, token, src = self._file()
        v0 = self.seahub.files[fid]["version"]
        external = _docx(b"someone else")
        v1 = self.seahub.external_write(fid, external)
        status, _, body = self._save(token, src, _docx(b"mine"), v0)
        self.assertEqual(status, 409, body)
        res = json.loads(body)
        self.assertEqual(res["current"], v1)
        self.assertEqual(self.seahub.files[fid]["content"], external, "the newer version must survive")
        self.assertEqual(self.seahub.files[fid]["commits"], 2)

    def test_save_with_read_only_token_is_refused_by_bridge_not_seahub(self):
        fid, token, src = self._file(can_edit=False, user="bob")
        v0 = self.seahub.files[fid]["version"]
        before = len(self.seahub.put_log)
        status, _, body = self._save(token, src, _docx(b"sneaky"), v0)
        self.assertEqual(status, 403, body)
        self.assertEqual(self.seahub.files[fid]["version"], v0)
        self.assertEqual(len(self.seahub.put_log), before, "PutFile must never have been forwarded")
        # Demonstrate why the bridge check matters: Seahub itself would accept it.
        _Http.call(f"{src}/contents?access_token={token}", "POST", {"X-WOPI-Override": "PUT"}, _docx(b"direct"))
        self.assertEqual(self.seahub.files[fid]["content"], _docx(b"direct"), "fake reproduces Seahub's missing can_edit check")

    def test_save_refuses_rename_and_wrong_signature(self):
        fid, token, src = self._file()
        v0 = self.seahub.files[fid]["version"]
        status, _, body = self._save(token, src, _docx(b"x"), v0, name="other.docx")
        self.assertEqual(status, 400)
        self.assertIn("different name", body.decode())
        status, _, body = self._save(token, src, b"%PDF-1.7 not a docx", v0)
        self.assertEqual(status, 415)
        status, _, _ = self._save(token, src, b"", v0)
        self.assertEqual(status, 400)
        self.assertEqual(self.seahub.files[fid]["version"], v0)

    def test_save_is_idempotent_on_identical_bytes(self):
        fid, token, src = self._file()
        v0 = self.seahub.files[fid]["version"]
        new = _docx(b"same")
        s1, _, b1 = self._save(token, src, new, v0)
        v1 = json.loads(b1)["version"]
        s2, _, b2 = self._save(token, src, new, v1)
        self.assertEqual((s1, s2), (200, 200))
        self.assertEqual(json.loads(b2)["version"], v1)
        self.assertEqual(self.seahub.files[fid]["commits"], 2, "identical content creates no new version")

    def test_save_reconciles_lost_response(self):
        fid, token, src = self._file()
        v0 = self.seahub.files[fid]["version"]
        new = _docx(b"landed but reply lost")
        type(self).lost_once["armed"] = True
        status, _, body = self._save(token, src, new, v0)
        self.assertEqual(status, 200, body)
        res = json.loads(body)
        self.assertTrue(res["reconciled"])
        self.assertEqual(res["version"], self.seahub.files[fid]["version"])
        self.assertEqual(self.seahub.files[fid]["content"], new)
        self.assertEqual(self.seahub.files[fid]["commits"], 2)

    def test_save_with_revoked_token_is_401(self):
        fid, token, src = self._file()
        v0 = self.seahub.files[fid]["version"]
        self.seahub.revoke(token)
        status, _, body = self._save(token, src, _docx(b"late"), v0)
        self.assertEqual(status, 401)
        self.assertEqual(self.seahub.files[fid]["version"], v0)

    def test_save_too_large_is_413(self):
        fid, token, src = self._file()
        status, _, _ = self._save(token, src, b"P" * (1024 * 1024 + 1), self.seahub.files[fid]["version"])
        self.assertEqual(status, 413)

    # -- relay: locks --------------------------------------------------------

    def test_lock_roundtrip_and_conflict(self):
        fid, token, src = self._file()
        s, _, b = self._relay("lock", token, src, {"X-WOPI-Override": "LOCK", "X-WOPI-Lock": "L1"})
        self.assertEqual(s, 200, b)
        s, _, b = self._relay("lock", token, src, {"X-WOPI-Override": "LOCK", "X-WOPI-Lock": "L2"})
        self.assertEqual(s, 409)
        self.assertEqual(json.loads(b)["lock"], "L1")
        s, _, b = self._relay("lock", token, src, {"X-WOPI-Override": "GET_LOCK"})
        self.assertEqual(json.loads(b)["lock"], "L1")
        s, _, _ = self._relay("lock", token, src, {"X-WOPI-Override": "REFRESH_LOCK", "X-WOPI-Lock": "L1"})
        self.assertEqual(s, 200)
        s, _, _ = self._relay("lock", token, src, {"X-WOPI-Override": "UNLOCK", "X-WOPI-Lock": "L1"})
        self.assertEqual(s, 200)
        self.assertNotIn(fid, self.seahub.locks)
        s, _, _ = self._relay("lock", token, src, {"X-WOPI-Override": "PUT_RELATIVE", "X-WOPI-Lock": "L1"})
        self.assertEqual(s, 400)

    # -- misc ----------------------------------------------------------------

    def test_editor_page_may_be_framed_by_host_and_seahub(self):
        # The editor iframe sits inside the host page, which sits inside Seahub. frame-ancestors is
        # evaluated against every ancestor, so 'self' alone breaks in a real browser (lab finding).
        st, h, body = _Http.call(f"{self.bridge_origin}/editors/wordcraft/index.html")
        self.assertEqual(st, 200)
        self.assertEqual(h.get("Content-Security-Policy"), f"frame-ancestors 'self' {self.seahub.origin}")
        st, h, _ = _Http.call(f"{self.bridge_origin}/editors/wordcraft/app.wasm")
        self.assertEqual(st, 200)
        self.assertEqual(h.get("Content-Type"), "application/wasm")
        self.assertNotIn("Content-Security-Policy", h)
        st, _, _ = _Http.call(f"{self.bridge_origin}/editors/%2e%2e/host.html")
        self.assertIn(st, (400, 404))

    def test_host_js_is_served_and_speaks_upstream_protocol(self):
        status, headers, body = _Http.call(f"{self.bridge_origin}/host.js")
        self.assertEqual(status, 200)
        js = body.decode()
        self.assertIn("application/javascript", headers["Content-Type"])
        for needle in (
            "kind === 'ready'", "post('open'", "kind === 'save'", "kind === 'dirty'", "kind === 'failed'",
            "post('saveResult'", "e.origin !== location.origin", "e.source !== frame.contentWindow",
            "'X-Expected-Version'", "'X-Bridge-Request': '1'", "beforeunload",
        ):
            self.assertIn(needle, js, needle)
        self.assertNotIn("access_token=", js, "the token must never be put in a URL by the host page")

    def test_signature_guard_table(self):
        self.assertTrue(content_matches_extension("docx", _docx()))
        self.assertFalse(content_matches_extension("docx", b"PK\x03\x04garbage"))
        self.assertTrue(content_matches_extension("svg", SVG))
        self.assertFalse(content_matches_extension("svg", b"<html></html>"))
        self.assertTrue(content_matches_extension("pdf", b"%PDF-1.4"))
        self.assertTrue(content_matches_extension("pcraft", b"anything"), "unknown extensions pass through")

    def test_config_rejects_duplicate_extensions_and_foreign_editor_urls(self):
        with self.assertRaises(ValueError):
            Config(public_url="https://b", seahub_origin="https://s", editors={"a": {"app": "a", "url": "/x", "extensions": ["docx"]}, "b": {"app": "b", "url": "/y", "extensions": ["docx"]}})
        with self.assertRaises(ValueError):
            Config(public_url="https://b", seahub_origin="https://s", editors={"a": {"app": "a", "url": "https://cdn.example/x", "extensions": ["docx"]}})


if __name__ == "__main__":
    unittest.main(verbosity=2)
