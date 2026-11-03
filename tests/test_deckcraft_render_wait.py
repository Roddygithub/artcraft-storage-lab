#!/usr/bin/env python3
"""Ensure DeckCraft readiness requires the expected slide render, not a stable blank canvas."""
from io import BytesIO
import os
import sys
import types

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lab", "real-seafile"))
for _key, _value in (("SEAFILE_URL", "http://127.0.0.1:1/seahub"),
                     ("BRIDGE_URL", "http://127.0.0.1:1/bridge"),
                     ("ONLYOFFICE_URL", "http://127.0.0.1:1/onlyoffice"),
                     ("ADMIN_EMAIL", "synthetic@example.invalid"),
                     ("ADMIN_PASSWORD", "synthetic-not-a-real-password")):
    os.environ.setdefault(_key, _value)

try:
    import playwright.sync_api  # noqa: F401
except ModuleNotFoundError:
    # These tests exercise only pure readiness logic, not a browser session.
    playwright = types.ModuleType("playwright")
    sync_api = types.ModuleType("playwright.sync_api")
    sync_api.sync_playwright = None
    playwright.sync_api = sync_api
    sys.modules["playwright"] = playwright
    sys.modules["playwright.sync_api"] = sync_api

import run_browser  # noqa: E402


class FakeCanvas:
    def __init__(self, frames):
        self.frames = frames
        self.calls = 0

    def screenshot(self, timeout):
        image = self.frames[min(self.calls, len(self.frames) - 1)]
        self.calls += 1
        return image


class FakeHost:
    def __init__(self, frames, loaded=True):
        self.canvas = FakeCanvas(frames)
        self.loaded = loaded if isinstance(loaded, list) else [loaded]
        self.evaluations = 0

    def evaluate(self, _script):
        value = self.loaded[min(self.evaluations, len(self.loaded) - 1)]
        self.evaluations += 1
        return value

    def frame_locator(self, _selector):
        return self

    def locator(self, _selector):
        return self.canvas

    def wait_for_timeout(self, _milliseconds):
        pass


def main():
    # Retained screenshot from a real synthetic-Seafile DeckCraft open, cropped to remove
    # Seahub chrome. It provides a representative WASM canvas, not a hand-drawn golden image.
    reference_path = os.path.join(HERE, "fixtures", "deckcraft-rendered-reference.png")
    reference = open(reference_path, "rb").read()
    reference_image = Image.open(BytesIO(reference)).convert("RGB")
    changed_image = reference_image.resize((1350, 815), Image.Resampling.BILINEAR)
    ImageDraw.Draw(changed_image).text((740, 430), "decktyped123", fill="black")
    changed_buffer = BytesIO()
    changed_image.save(changed_buffer, format="PNG")
    changed = changed_buffer.getvalue()

    blank_image = reference_image.copy()
    width, height = blank_image.size
    ImageDraw.Draw(blank_image).rectangle((int(width * 0.268), int(height * 0.254),
                                           int(width * 0.90), int(height * 0.845)), fill="white")
    blank_buffer = BytesIO()
    blank_image.save(blank_buffer, format="PNG")
    blank = blank_buffer.getvalue()

    assert run_browser.deckcraft_canvas_has_document_visuals(reference)
    assert not run_browser.deckcraft_canvas_has_document_visuals(blank)
    assert run_browser.deckcraft_canvas_matches_reference(reference, reference)
    assert run_browser.deckcraft_canvas_matches_reference(changed, reference)
    assert not run_browser.deckcraft_canvas_matches_reference(blank, reference)
    assert not run_browser.deckcraft_canvas_matches_reference(blank, blank)

    host = FakeHost([reference] * 4, loaded=[False] * 6 + [True] * 4)
    assert run_browser.wait_for_deckcraft_render(host, reference, timeout=2) == reference
    assert host.evaluations == 10 and host.canvas.calls == 4

    not_opened = FakeHost([b"stable-but-not-opened"] * 20, loaded=False)
    assert run_browser.wait_for_deckcraft_render(not_opened, reference, timeout=0.02) is None
    assert not_opened.canvas.calls == 0

    blank_canvas = FakeHost([blank] * 12)
    assert run_browser.wait_for_deckcraft_render(blank_canvas, reference, timeout=0.02) is None
    reopened = FakeHost([changed] * 4)
    assert run_browser.wait_for_deckcraft_render(reopened, reference, timeout=2) == changed
    print("DeckCraft document-render wait checks: 7/7 passed")


if __name__ == "__main__":
    main()
