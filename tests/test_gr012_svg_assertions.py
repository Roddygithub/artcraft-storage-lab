#!/usr/bin/env python3
"""Unit checks for GR-012 SVG evidence assertions; no Seafile required."""

from test_gr012_svg import has_expected_stroke, has_serialized_stroke


rectangle_only = b'''<svg xmlns="http://www.w3.org/2000/svg">
<path d="M10 10 L190 10 L190 110 L10 110 Z" fill="#1a73e8"/>
</svg>'''
stroke = b'''<svg xmlns="http://www.w3.org/2000/svg">
<path d="M10 10 L190 10 L190 110 L10 110 Z" fill="#1a73e8"/>
<path d="M60 60 L180 120" fill="none" stroke="#000000"/>
</svg>'''

assert not has_serialized_stroke(rectangle_only)
assert has_serialized_stroke(stroke)
snapshot = {"layers": [{"children": [
    {"kind": "Path", "fill": "None", "stroke": "#000000",
     "bounds": {"x": 60, "y": 60, "width": 120, "height": 60}},
    {"kind": "Path", "fill": "#1a73e8", "stroke": "None",
     "bounds": {"x": 10, "y": 10, "width": 180, "height": 100}},
]}]}
assert has_expected_stroke(snapshot)
snapshot["layers"][0]["children"].pop(0)
assert not has_expected_stroke(snapshot)

print("PASS: rectangle-only SVG is not mistaken for the pencil stroke")
print("PASS: serialized SVG must contain the expected unfilled stroke path")
print("PASS: reopened VectorCraft snapshot must contain the expected path entity")
