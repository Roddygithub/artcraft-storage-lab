#!/usr/bin/env python3
"""Ensure DeckCraft readiness waits for host open status and an in-session stable canvas."""
import os
import sys
import types

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
    rendered = b"rendered-native-deck"
    host = FakeHost([rendered] * 4,
                    loaded=[False] * 6 + [True] * 4)
    assert run_browser.wait_for_deckcraft_render(host, timeout=2) == rendered
    assert host.evaluations == 10 and host.canvas.calls == 4

    not_opened = FakeHost([b"stable-but-not-opened"] * 20, loaded=False)
    assert run_browser.wait_for_deckcraft_render(not_opened, timeout=0.02) is None
    assert not_opened.canvas.calls == 0

    reopened_capture = b"rendered-in-fresh-session"
    reopened = FakeHost([reopened_capture] * 4)
    assert run_browser.wait_for_deckcraft_render(reopened, timeout=2) == reopened_capture
    print("DeckCraft document-render wait checks: 3/3 passed")


if __name__ == "__main__":
    main()
