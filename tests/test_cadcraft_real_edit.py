#!/usr/bin/env python3
"""Offline DXF, visible-circle, stable-frame and coordinate assertions for CADCraft's lab slice."""
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
    playwright = types.ModuleType("playwright")
    sync_api = types.ModuleType("playwright.sync_api")
    sync_api.sync_playwright = None
    playwright.sync_api = sync_api
    sys.modules["playwright"] = playwright
    sys.modules["playwright.sync_api"] = sync_api

import run_browser  # noqa: E402
import run_slice as rs  # noqa: E402


def dxf_circle(x="20", y="20", radius="10"):
    return ("0\nCIRCLE\n5\n2A\n100\nAcDbEntity\n8\n0\n100\nAcDbCircle\n"
            f"10\n{x}\n20\n{y}\n30\n0\n40\n{radius}\n").encode()


def dxf(body, section="ENTITIES", close=True):
    end = "0\nENDSEC\n" if close else ""
    return f"0\nSECTION\n2\n{section}\n".encode() + body + end.encode() + b"0\nEOF\n"


def png(image):
    output = BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()


class FakeCanvas:
    def __init__(self, frames):
        self.frames = frames
        self.calls = 0

    def screenshot(self, timeout):
        image = self.frames[min(self.calls, len(self.frames) - 1)]
        self.calls += 1
        return image


class FakeHost:
    def __init__(self, frames, bounds=None):
        self.canvas = FakeCanvas(frames)
        self.bounds = bounds

    def evaluate(self, _script):
        return self.bounds if self.bounds is not None else True

    def frame_locator(self, _selector):
        return self

    def locator(self, _selector):
        return self.canvas

    def wait_for_timeout(self, _milliseconds):
        pass


class FakePage:
    def __init__(self):
        self.clicks = []
        self.keys = []
        self.mouse = self
        self.keyboard = self

    def click(self, x, y):
        self.clicks.append((x, y))

    def type(self, value, delay):
        self.keys.append(("type", value, delay))

    def press(self, key):
        self.keys.append(("press", key))

    def wait_for_timeout(self, _milliseconds):
        pass


def canvas_fixture():
    image = Image.new("RGB", (640, 480), (30, 34, 40))
    draw = ImageDraw.Draw(image)
    for x in range(120, 500, 20):
        draw.line((x, 48, x, 420), fill=(42, 47, 55))
    for y in range(48, 421, 20):
        draw.line((120, y, 500, y), fill=(42, 47, 55))
    return image


def main():
    assert run_browser.dxf_circles(rs.MINIMAL_DXF) == []
    one = dxf(dxf_circle())
    assert run_browser.dxf_circles(one) == [(20.0, 20.0, 10.0)]
    assert run_browser.dxf_has_circle(one)
    assert not run_browser.dxf_has_circle(one, center=(10, 10))
    assert not run_browser.dxf_has_circle(one, radius=5)
    padded = b"".join(f"{line:>3}\r\n".encode() for line in one.decode("ascii").splitlines())
    assert run_browser.dxf_circles(padded) == [(20.0, 20.0, 10.0)]
    assert run_browser.dxf_circle_count(dxf(dxf_circle() + dxf_circle(x="40"))) == 2
    assert run_browser.dxf_circles(dxf(dxf_circle().replace(b"CIRCLE", b"LINE", 1))) == []
    assert run_browser.dxf_circles(dxf(dxf_circle(), close=False)) is None
    non_entity_circle = (b"0\nSECTION\n2\nBLOCKS\n" + dxf_circle() +
                         b"0\nENDSEC\n0\nSECTION\n2\nENTITIES\n0\nENDSEC\n0\nEOF\n")
    assert run_browser.dxf_circles(non_entity_circle) == []
    assert run_browser.dxf_circles(dxf(dxf_circle().replace(b"100\nAcDbEntity\n", b""))) == [(20.0, 20.0, 10.0)]
    for bad in (dxf_circle(radius="0"), dxf_circle(radius="-1"), dxf_circle(radius="nan"),
                dxf_circle(radius="inf"), dxf_circle().replace(b"10\n20\n", b""),
                dxf_circle().replace(b"10\n20\n", b"10\n20\n10\n30\n")):
        assert run_browser.dxf_circles(dxf(bad)) is None
    assert run_browser.dxf_circles(one[:-6]) is None
    assert run_browser.dxf_circles(b"\xff") is None
    no_geometry = b"0\nSECTION\n2\nENTITIES\n0\nCIRCLE\n0\nENDSEC\n0\nEOF\n"
    assert run_browser.dxf_circles(no_geometry) is None
    nested = b"0\nSECTION\n2\nENTITIES\n0\nSECTION\n2\nBLOCKS\n0\nENDSEC\n0\nENDSEC\n0\nEOF\n"
    assert run_browser.dxf_circles(nested) is None

    original = canvas_fixture()
    edited = original.copy()
    ImageDraw.Draw(edited).ellipse((260, 180, 380, 300), outline=(220, 225, 232), width=2)
    circle_metrics = run_browser.cadcraft_rendered_circle_metrics(png(edited), png(original))
    assert circle_metrics is not None and circle_metrics[0] >= 250 and 0.9 <= circle_metrics[1] <= 1.1 and circle_metrics[2] >= 0.8
    rectangle = original.copy()
    ImageDraw.Draw(rectangle).rectangle((260, 180, 380, 300), outline=(220, 225, 232), width=2)
    rectangle_metrics = run_browser.cadcraft_rendered_circle_metrics(png(rectangle), png(original))
    assert rectangle_metrics is not None and rectangle_metrics[2] < 0.8
    chrome = original.copy()
    ImageDraw.Draw(chrome).rectangle((5, 5, 40, 30), fill=(250, 250, 250))
    assert run_browser.cadcraft_canvas_edit_pixels(png(chrome), png(original)) == 0

    # Changing toolbar chrome must not prevent stable-frame detection of the drawing itself.
    chrome2 = edited.copy()
    ImageDraw.Draw(chrome2).rectangle((5, 5, 40, 30), fill=(250, 30, 30))
    assert run_browser.wait_for_cadcraft_original_canvas(FakeHost([png(original), png(chrome), png(original)])) is not None
    assert run_browser.wait_for_cadcraft_canvas_change(
        FakeHost([png(edited), png(chrome2), png(edited)]), png(original), timeout=1) is not None
    unstable_drawing = original.copy()
    ImageDraw.Draw(unstable_drawing).point((200, 100), fill=(250, 250, 250))
    stable_host = FakeHost([png(original), png(unstable_drawing), png(original), png(original), png(original)])
    assert run_browser.wait_for_cadcraft_original_canvas(stable_host) is not None
    assert stable_host.canvas.calls == 5

    page = FakePage()
    host = FakeHost([], bounds={"frameX": 10, "frameY": 20, "x": 50, "y": 30, "width": 1000, "height": 600,
                                "viewportWidth": 1200, "viewportHeight": 800})
    assert run_browser.cadcraft_add_circle(page, host,
        {"x": 200, "y": 100, "width": 1200, "height": 800}, "20,20", "10",
        lambda: "unsaved changes")
    assert page.clicks == [(740.0, 690.0)]
    assert page.keys == [("type", "CIRCLE", 50), ("press", "Enter"),
                         ("type", "20,20", 50), ("press", "Enter"),
                         ("type", "10", 50), ("press", "Enter")]
    delayed_page = FakePage()
    delayed_host = FakeHost([], bounds={"frameX": 10, "frameY": 20, "x": 50, "y": 30, "width": 1000, "height": 600,
                                        "viewportWidth": 1200, "viewportHeight": 800})
    delayed_status = iter(("ready", "ready", "unsaved changes"))
    assert run_browser.cadcraft_add_circle(delayed_page, delayed_host,
        {"x": 200, "y": 100, "width": 1200, "height": 800}, "5,5", "3",
        lambda: next(delayed_status, "unsaved changes"), timeout=0.2)
    assert delayed_page.keys[-2:] == [("type", "3", 50), ("press", "Enter")]
    timeout_page = FakePage()
    assert not run_browser.cadcraft_add_circle(timeout_page, delayed_host,
        {"x": 200, "y": 100, "width": 1200, "height": 800}, "5,5", "3",
        lambda: "ready", timeout=0.01)
    scaled_page = FakePage()
    scaled_host = FakeHost([], bounds={"frameX": 10, "frameY": 20, "x": 50, "y": 30, "width": 1000, "height": 600,
                                       "viewportWidth": 1000, "viewportHeight": 600})
    assert run_browser.cadcraft_add_circle(scaled_page, scaled_host,
        {"x": 200, "y": 100, "width": 1200, "height": 800}, "20,20", "10",
        lambda: "unsaved changes")
    assert scaled_page.clicks == [(848.0, 886.6666666666666)]
    print("PASS: CADCraft DXF/render/input assertions")


if __name__ == "__main__":
    main()
