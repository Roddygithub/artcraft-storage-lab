#!/usr/bin/env python3
"""Ensure DeckCraft readiness waits for a known rendered document, not any stable canvas."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lab", "real-seafile"))
for _key, _value in (("SEAFILE_URL", "http://127.0.0.1:1/seahub"),
                     ("BRIDGE_URL", "http://127.0.0.1:1/bridge"),
                     ("ONLYOFFICE_URL", "http://127.0.0.1:1/onlyoffice"),
                     ("ADMIN_EMAIL", "synthetic@example.invalid"),
                     ("ADMIN_PASSWORD", "synthetic-not-a-real-password")):
    os.environ.setdefault(_key, _value)

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
    def __init__(self, frames):
        self.canvas = FakeCanvas(frames)

    def evaluate(self, _script):
        return True

    def frame_locator(self, _selector):
        return self

    def locator(self, _selector):
        return self.canvas

    def wait_for_timeout(self, _milliseconds):
        pass


def main():
    expected = b"rendered-native-deck"
    host = FakeHost([b"initial-empty-canvas"] * 6 + [expected] * 4)
    assert run_browser.wait_for_deckcraft_render(host, expected, timeout=2) == expected
    assert host.canvas.calls == 10

    blank = FakeHost([b"initial-empty-canvas"] * 20)
    assert run_browser.wait_for_deckcraft_render(blank, expected, timeout=0.02) is None

    capture = FakeHost([b"saved-render"] * 4)
    assert run_browser.wait_for_deckcraft_render(capture, timeout=2) == b"saved-render"
    print("DeckCraft document-render wait checks: 3/3 passed")


if __name__ == "__main__":
    main()
