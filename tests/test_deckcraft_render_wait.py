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
    host_path = os.path.join(HERE, "fixtures", "deckcraft-host-opened.png")
    host_opened = open(host_path, "rb").read()
    assert run_browser.deckcraft_canvas_has_document_visuals(host_opened)
    assert run_browser.deckcraft_canvas_matches_reference(host_opened, reference)

    edited_image = reference_image.copy()
    draw = ImageDraw.Draw(edited_image)
    width, height = edited_image.size
    # Simulate an edit that changes the rendered title enough to fail the old unedited-image gate.
    for index in range(8):
        y = int(height * (0.37 + index * 0.034))
        draw.rectangle((int(width * 0.45), y, int(width * 0.72), y + int(height * 0.018)),
                       fill=(255, 0, 0))
    edited_buffer = BytesIO()
    edited_image.save(edited_buffer, format="PNG")
    edited = edited_buffer.getvalue()

    small_edit_image = reference_image.copy()
    width, height = small_edit_image.size
    x, y = int(width * 0.50), int(height * 0.48)
    ImageDraw.Draw(small_edit_image).rectangle((x, y, x + 30, y + 20), fill=(0, 0, 0))
    small_edit_buffer = BytesIO()
    small_edit_image.save(small_edit_buffer, format="PNG")
    small_edit = small_edit_buffer.getvalue()

    blank_image = reference_image.copy()
    width, height = blank_image.size
    ImageDraw.Draw(blank_image).rectangle((int(width * 0.23), int(height * 0.20),
                                           int(width * 0.94), int(height * 0.85)), fill="white")
    blank_buffer = BytesIO()
    blank_image.save(blank_buffer, format="PNG")
    blank = blank_buffer.getvalue()

    assert run_browser.deckcraft_canvas_has_document_visuals(reference)
    assert not run_browser.deckcraft_canvas_has_document_visuals(blank)
    assert run_browser.deckcraft_canvas_matches_reference(reference, reference)
    # The visible edit must fail the old unedited-fixture comparison and pass the edit gate.
    assert not run_browser.deckcraft_canvas_matches_reference(edited, reference)
    assert run_browser.deckcraft_canvas_shows_title_edit(edited, reference)
    assert not run_browser.deckcraft_canvas_shows_title_edit(reference, reference)
    assert run_browser.deckcraft_canvas_matches_reference(edited, edited)
    assert not run_browser.deckcraft_canvas_matches_reference(blank, reference)
    assert not run_browser.deckcraft_canvas_matches_reference(blank, blank)
    assert run_browser.wait_for_deckcraft_render(FakeHost([reference] * 4), None, timeout=0.02) is None
    # A small title edit still matches the old tolerant comparator, so the sensitive gate must
    # independently reject losing it in either the saved page or the fresh session.
    assert run_browser.deckcraft_canvas_matches_reference(small_edit, reference)
    assert run_browser.deckcraft_canvas_shows_title_edit(small_edit, reference)
    assert run_browser.wait_for_deckcraft_title_edit(FakeHost([reference] * 20), reference, timeout=0.02) is None
    assert run_browser.wait_for_deckcraft_title_edit(FakeHost([reference] * 20), reference, timeout=0.02) is None
    assert run_browser.wait_for_deckcraft_title_edit(FakeHost([small_edit] * 4), reference, timeout=2) == small_edit
    assert run_browser.wait_for_deckcraft_title_edit(FakeHost([small_edit] * 4), reference, timeout=2) == small_edit

    host = FakeHost([reference] * 4, loaded=[False] * 6 + [True] * 4)
    assert run_browser.wait_for_deckcraft_render(host, reference, timeout=2) == reference
    assert host.evaluations == 10 and host.canvas.calls == 4

    visible_edit = FakeHost([edited] * 4)
    assert run_browser.wait_for_deckcraft_title_edit(visible_edit, reference, timeout=2) == edited
    saved = FakeHost([edited] * 4)
    assert run_browser.wait_for_deckcraft_render(saved, edited, timeout=2) == edited

    not_opened = FakeHost([b"stable-but-not-opened"] * 20, loaded=False)
    assert run_browser.wait_for_deckcraft_render(not_opened, reference, timeout=0.02) is None
    assert not_opened.canvas.calls == 0

    blank_canvas = FakeHost([blank] * 12)
    assert run_browser.wait_for_deckcraft_render(blank_canvas, reference, timeout=0.02) is None
    reopened = FakeHost([edited] * 4)
    assert run_browser.wait_for_deckcraft_render(reopened, edited, timeout=2) == edited
    print("DeckCraft document-render wait checks: 26/26 passed")


if __name__ == "__main__":
    main()
