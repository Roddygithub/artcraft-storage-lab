#!/usr/bin/env python3
"""Exercise the GridCraft v0.12 Web bundle through the host save protocol.

The storage adapter is synthetic in-memory storage. This does not test Seafile
persistence, history, or production deployment.
"""

import argparse
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
from test_wordcraft_host_roundtrip import SyntheticSeafile, TOKEN  # noqa: E402


EDIT = "GR082_GRIDCRAFT_RELEASE_EDIT"


class SyntheticWorkbook(SyntheticSeafile):
    def __init__(self, initial_bytes):
        super().__init__(initial_bytes)
        self.read_count = 0

    def thirdparty_file_info(self, token):
        info = super().thirdparty_file_info(token)
        info.update(file_path="/synthetic.xlsx", file_name="synthetic.xlsx")
        return info

    def thirdparty_file_content(self, token, expected_file_id, max_bytes=None):
        self.read_count += 1
        return super().thirdparty_file_content(token, expected_file_id, max_bytes)

    def thirdparty_file_save(self, token, expected_id, expected_head, name, data):
        assert token == TOKEN and name == "synthetic.xlsx"
        if expected_id != self.file_id or expected_head != self.head:
            raise AssertionError("stale synthetic workbook save")
        self.content = data
        self.file_id = hashlib.sha1(data).hexdigest()
        self.head = f"synthetic-head-{len(self.versions) + 1}"
        self.versions.append(data)
        return {"file_id": self.file_id, "head_commit_id": self.head}


def workbook_text(data):
    text = []
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        for name in archive.namelist():
            if name == "xl/sharedStrings.xml" or (
                name.startswith("xl/worksheets/") and name.endswith(".xml")
            ):
                root = ET.fromstring(archive.read(name))
                text.extend(
                    node.text or ""
                    for node in root.iter()
                    if node.tag.endswith("}t") or node.tag.endswith("}v")
                )
    return " ".join(text)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--static-root", type=Path, default=ROOT / "integration/static")
    args = parser.parse_args()
    static_root = args.static_root.resolve()
    web_root = static_root / "gridcraft"
    if not (web_root / "index.html").is_file() or not list(web_root.glob("*_bg.wasm")):
        raise SystemExit("GridCraft Web bundle missing; stage a pinned build under gridcraft/")
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise SystemExit("Playwright is required; install Playwright and Chromium") from exc

    backend = SyntheticWorkbook((ROOT / "tests/fixtures/synthetic.xlsx").read_bytes())
    gateway = Gateway(backend, load_dispatch(), static_root=str(static_root))
    first, error = gateway.open_session(TOKEN)
    assert first is not None, error

    class TestHandler(Handler):
        def do_GET(self):
            if urllib.parse.urlsplit(self.path).path == "/open-test":
                sid = urllib.parse.parse_qs(urllib.parse.urlsplit(self.path).query).get(
                    "sid", [first.sid]
                )[0]
                session = self.server.gateway.sessions.get(sid)
                target = self.server.gateway.dispatch["xlsx"]
                page = hostpage.render(
                    session.sid, target["app"], target["url"], session.name, session.can_edit
                )
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
                page = browser.new_page(viewport={"width": 1280, "height": 800})
                page.add_init_script(
                    "window.__hostMessages=[]; addEventListener('message', e => "
                    "window.__hostMessages.push(e.data));"
                )
                diagnostics = {"console": [], "errors": []}
                page.on("console", lambda message: diagnostics["console"].append(
                    f"{message.type}: {message.text[:240]}"))
                page.on("pageerror", lambda error: diagnostics["errors"].append(str(error)[:400]))
                page.on("response", lambda response: diagnostics.setdefault("http_errors", []).append(
                    {"status": response.status, "path": urllib.parse.urlsplit(response.url).path})
                    if response.status >= 400 else None)
                page.goto(f"http://127.0.0.1:{server.server_port}/open-test", wait_until="load")
                page.wait_for_function(
                    "() => window.__hostMessages.some(m => m.type === 'gridcraft:opened')",
                    timeout=90_000,
                )
                canvas = page.frame_locator("#frame").locator("canvas").first
                canvas.click(position={"x": 105, "y": 288})
                page.wait_for_timeout(150)
                page.keyboard.press("F2")
                page.wait_for_timeout(150)
                page.keyboard.type(EDIT)
                # The cell editor may retain an uncommitted value while the host
                # still reports clean. Ctrl+S must commit that active edit before
                # serializing the workbook.
                page.keyboard.press("Control+s")
                page.wait_for_function(
                    "() => window.__hostMessages.some(m => m.type === 'gridcraft:save')",
                    timeout=30_000,
                )
                page.wait_for_function(
                    "() => /^Saved/.test(document.getElementById('state').textContent) && "
                    "window.__editorConfirmedSave === true",
                    timeout=60_000,
                )
                assert len(backend.versions) == 2
                assert EDIT in workbook_text(backend.content)
                saves = page.evaluate(
                    "() => window.__hostMessages.filter(m => m.type === 'gridcraft:save')"
                )
                assert len(saves) == 1 and saves[0]["intent"] == "save", saves
                identity = {key: saves[0][key] for key in ("openId", "documentId")}
                assert identity["openId"] and identity["documentId"]
                clean = page.evaluate(
                    "() => window.__hostMessages.filter(m => m.type === 'gridcraft:dirty' "
                    "&& m.dirty === false)"
                )
                assert any(
                    item.get("openId") == identity["openId"]
                    and item.get("documentId") == identity["documentId"]
                    and item.get("ticket") == saves[0]["ticket"]
                    for item in clean
                ), clean

                reopened, error = gateway.open_session(TOKEN)
                assert reopened is not None, error
                page.goto(
                    f"http://127.0.0.1:{server.server_port}/open-test?sid={reopened.sid}",
                    wait_until="load",
                )
                page.wait_for_function(
                    "() => window.__hostMessages.some(m => m.type === 'gridcraft:opened')",
                    timeout=90_000,
                )
                assert EDIT in workbook_text(backend.content)
                assert len(backend.versions) == 2
                assert backend.read_count >= 2
            finally:
                browser.close()
    finally:
        server.shutdown()
        thread.join(timeout=3)
        server.server_close()

    print("PASS: actual GridCraft Web edit serialized the synthetic workbook")
    print("PASS: one in-memory new version committed and durable ACK marked the editor clean")
    print("PASS: a fresh GridCraft session reopened the saved workbook")
    print("NOTE: synthetic in-memory storage; Seafile E2E and refused-action serializer counts remain unverified")


if __name__ == "__main__":
    main()
