#!/usr/bin/env python3
"""Exercise the installed WordCraft Web build through the real host page.

This verifies WordCraft serialization, the postMessage save/ack protocol and
editor reopen. Storage is a synthetic in-memory Seafile adapter, so this is not
a Seafile integration or persistence test.

Prerequisites: fetch/build the WordCraft Web files into integration/static/
wordcraft and install Playwright with Chromium. Run:

    python3 tests/test_wordcraft_host_roundtrip.py
"""

import hashlib
import io
import sys
import threading
import urllib.parse
import xml.etree.ElementTree as ET
import zipfile
from http.server import ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from integration.gateway import hostpage  # noqa: E402
from integration.gateway.server import Gateway, Handler, load_dispatch  # noqa: E402


TOKEN = "synthetic-editor-capability"
EDIT = "GPT_FINAL_REAL_WORDCRAFT_EDIT"


class SyntheticSeafile:
    def __init__(self, initial_bytes):
        self.content = initial_bytes
        self.file_id = hashlib.sha1(initial_bytes).hexdigest()
        self.head = "synthetic-head-1"
        self.initial_file_id = self.file_id
        self.versions = [initial_bytes]

    def thirdparty_file_info(self, token):
        assert token == TOKEN
        return {
            "repo_id": "synthetic-repo",
            "file_path": "/synthetic.docx",
            "file_name": "synthetic.docx",
            "username": "reviewer@example.test",
            "permission": "rw",
            "can_edit": True,
            "file_id": self.file_id,
            "head_commit_id": self.head,
        }

    def thirdparty_file_content(self, token, expected_file_id):
        assert token == TOKEN
        if expected_file_id != self.file_id:
            raise AssertionError("stale synthetic read")
        return self.content

    def thirdparty_file_save(self, token, expected_id, expected_head, name, data):
        assert token == TOKEN and name == "synthetic.docx"
        if expected_id != self.file_id or expected_head != self.head:
            raise AssertionError("stale synthetic save")
        self.content = data
        self.file_id = hashlib.sha1(data).hexdigest()
        self.head = f"synthetic-head-{len(self.versions) + 1}"
        self.versions.append(data)
        return {"file_id": self.file_id, "head_commit_id": self.head}


def docx_text(data):
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        root = ET.fromstring(archive.read("word/document.xml"))
    return "".join(node.text or "" for node in root.iter() if node.tag.endswith("}t"))


def main():
    web_root = ROOT / "integration/static/wordcraft"
    fixture = ROOT / "tests/fixtures/synthetic.docx"
    if not (web_root / "index.html").is_file() or not list(web_root.glob("*_bg.wasm")):
        raise SystemExit("WordCraft Web bundle missing; run scripts/fetch-craft-web.sh wordcraft first")
    if not fixture.is_file():
        raise SystemExit("synthetic DOCX fixture is missing")

    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise SystemExit("Playwright is required; install Playwright and Chromium") from exc

    backend = SyntheticSeafile(fixture.read_bytes())
    gateway = Gateway(backend, load_dispatch(), static_root=str(ROOT / "integration/static"))
    first, error = gateway.open_session(TOKEN)
    assert first is not None, error

    class TestHandler(Handler):
        def do_GET(self):
            if urllib.parse.urlsplit(self.path).path == "/open-test":
                sid = urllib.parse.parse_qs(urllib.parse.urlsplit(self.path).query).get(
                    "sid", [first.sid])[0]
                session = self.server.gateway.sessions.get(sid)
                target = self.server.gateway.dispatch["docx"]
                page = hostpage.render(session.sid, target["app"], target["url"],
                                       session.name, session.can_edit)
                return self._send(200, page, "text/html; charset=utf-8")
            return super().do_GET()

    server = ThreadingHTTPServer(("127.0.0.1", 0), TestHandler)
    server.gateway = gateway
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(
                headless=True,
                args=["--enable-unsafe-swiftshader", "--use-gl=angle", "--use-angle=swiftshader"],
            )
            try:
                page = browser.new_page()
                page.goto(f"http://127.0.0.1:{server.server_port}/open-test", wait_until="load")
                page.wait_for_function(
                    "() => /opened/.test(document.getElementById('state').textContent)",
                    timeout=120_000,
                )
                page.evaluate(
                    "() => { window.__hostMessages=[]; "
                    "addEventListener('message', e => window.__hostMessages.push(e.data)); }"
                )
                canvas = page.frame_locator("#frame").locator("canvas").first
                canvas.click(position={"x": 360, "y": 300})
                page.keyboard.press("Control+End")
                page.keyboard.type(" " + EDIT)
                page.wait_for_function("() => window.__lastDirty === true", timeout=30_000)
                page.keyboard.press("Control+s")
                page.wait_for_function(
                    "() => /^Saved/.test(document.getElementById('state').textContent)",
                    timeout=60_000,
                )
                page.wait_for_function("() => window.__editorConfirmedSave === true",
                                       timeout=30_000)

                assert backend.file_id != backend.initial_file_id
                assert len(backend.versions) == 2
                assert EDIT in docx_text(backend.content)
                messages = page.evaluate(
                    "() => window.__hostMessages.map(m => ({type:m.type,dirty:m.dirty}))"
                )
                assert sum(m == {"type": "wordcraft:dirty", "dirty": False}
                           for m in messages) >= 2, messages

                reopened, error = gateway.open_session(TOKEN)
                assert reopened is not None, error
                page.goto(
                    f"http://127.0.0.1:{server.server_port}/open-test?sid={reopened.sid}",
                    wait_until="load",
                )
                page.wait_for_function(
                    "() => /opened/.test(document.getElementById('state').textContent)",
                    timeout=120_000,
                )
                assert EDIT in docx_text(backend.content)
            finally:
                browser.close()
    finally:
        server.shutdown()
        thread.join(timeout=3)
        server.server_close()

    print("PASS: real WordCraft Web edit changed and serialized the DOCX")
    print("PASS: synthetic storage acknowledged one new version")
    print("PASS: host observed WordCraft's post-save dirty=false acknowledgement")
    print("PASS: WordCraft reopened the saved document")
    print("NOTE: synthetic in-memory storage; real Seafile E2E remains unverified")


if __name__ == "__main__":
    main()
