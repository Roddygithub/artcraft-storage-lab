#!/usr/bin/env python3
"""Offline semantic checks only; browser/WOPI runtime is NOT RUN by this test.

Schemas checked against cached VectorCraft export.rs/path_d and FigCraft
format/src/large_tests.rs::files_with_every_field_spelled_out_still_open.
"""
import ast
from io import BytesIO
import json
from pathlib import Path
import re
import time
from types import SimpleNamespace
import xml.etree.ElementTree as ET
import zipfile

# Load only the pure helpers: no credentials, Playwright, services or network.
source = Path(__file__).resolve().parents[1] / 'lab/real-seafile/run_browser.py'
tree = ast.parse(source.read_text())
names = {'svg_has_rectangle', 'figcraft_has_frame', 'scene_has_geometry', 'page_api', 'select_active_browser_fixtures', 'open_from_seafile_list'}
namespace = dict(BytesIO=BytesIO, json=json, re=re, time=time, ET=ET, zipfile=zipfile)
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names],
                        type_ignores=[]), str(source), 'exec'), namespace)
svg_has_rectangle = namespace['svg_has_rectangle']
figcraft_has_frame = namespace['figcraft_has_frame']
scene_has_geometry = namespace['scene_has_geometry']
g = dict(x=0, y=0, width=137, height=91)
shape = '<path d="M0 0 L137 0 L137 91 L0 91 Z"/>'
def svg(body):
    return ('<svg xmlns="http://www.w3.org/2000/svg">' + body + '</svg>').encode()

assert svg_has_rectangle(svg(shape), g)
assert svg_has_rectangle(svg('<rect width="137" height="91"/>'), g)
for body in (f'<metadata>{shape}</metadata>', f'<defs>{shape}</defs>',
             shape.replace('137', '136'), shape.replace(' L137 91', ' C137 91'),
             shape.replace(' Z', ''), f'<g transform="translate(3 4)">{shape}</g>',
             f'<g display="none">{shape}</g>', f'<g opacity="0">{shape}</g>',
             f'<g fill-opacity="0">{shape}</g>', '<rect xmlns="urn:other" width="137" height="91"/>',
             '<rect width="137" height="91" fill="none" stroke="none"/>',
             f'<g fill="none" stroke="none">{shape}</g>',
             '<metadata>width=137 height=91</metadata>'):
    assert not svg_has_rectangle(svg(body), g), body
assert not svg_has_rectangle(b'not SVG', g)

def native(doc):
    out = BytesIO()
    with zipfile.ZipFile(out, 'w') as z:
        z.writestr('document.json', json.dumps(doc))
    return out.getvalue()

frame = dict(id=2, name='unique-frame', type='frame', parent=1, width=137, height=91)
doc = dict(format='figcraft', version=1, pages=[1], nodes={
    '1': dict(id=1, type='page', children=[2]), '2': frame})
assert figcraft_has_frame(native(doc), 'unique-frame', g)
for patch in (dict(type='rectangle'), dict(name='other'), dict(width=136),
              dict(transform=[1, 0, 0, 1, 3, 0]), dict(parent=7)):
    bad = dict(doc, nodes=dict(doc['nodes'], **{'2': dict(frame, **patch)}))
    assert not figcraft_has_frame(native(bad), 'unique-frame', g), patch
assert not figcraft_has_frame(native(dict(doc, nodes={'1': doc['nodes']['1']}, metadata=frame)), 'unique-frame', g)
assert not figcraft_has_frame(b'unique-frame width=137 height=91', 'unique-frame', g)
assert not figcraft_has_frame(native(dict(doc, version=2)), 'unique-frame', g)
assert scene_has_geometry({'layers': [{'id': 2, 'kind': 'Rectangle', 'bounds': g}]}, g)
assert not scene_has_geometry({'bounds': g}, g)
node = {'id': 2, 'type': 'FRAME', 'name': 'unique-frame', 'absoluteBounds': g}
assert scene_has_geometry({'pages': [{'id': 1, 'type': 'PAGE', 'children': [node]}]}, g, 'unique-frame')
assert not scene_has_geometry({'pages': [], 'metadata': node}, g, 'unique-frame')
assert not scene_has_geometry({'pages': [{'id': 1, 'type': 'PAGE', 'pluginData': node}]}, g, 'unique-frame')
assert not scene_has_geometry({'layers': [], 'metadata': {'id': 2, 'kind': 'Path', 'bounds': g}}, g)
assert not scene_has_geometry({'layers': [{'id': 2, 'kind': 'Path', 'bounds': g, 'visible': False}]}, g)
assert not scene_has_geometry({'id': 2, 'type': 'FRAME', 'name': 'wrong', 'absoluteBounds': g}, g, 'unique-frame')
fixtures = {'a.docx': ('wordcraft', b'x', ''), 'a.png': ('photocraft', b'x', '')}
assert namespace['select_active_browser_fixtures'](fixtures, {'wordcraft': {'extensions': ['docx']}}) == {'a.docx': fixtures['a.docx']}

class Host:
    def evaluate(self, script, args):
        assert "contentWindow[app]" in script
        assert "api.request(method, params)" in script
        assert args == ['vectorcraft', 'engine.execute', {'command': 'shape.rectangle', 'params': g}]
        return {'id': 2}
assert namespace['page_api'](Host(), 'vectorcraft', 'engine.execute', {'command': 'shape.rectangle', 'params': g}) == {'id': 2}

actions = []
class Element:
    def __init__(self, label, page): self.label, self.page = label, page
    def click(self, **kwargs):
        actions.append((self.label, 'click', kwargs.get('button', 'left')))
        if self.label == 'test.svg' and kwargs.get('button') == 'middle': self.page.context.pages.append(Popup())
class Popup:
    def wait_for_load_state(self, state, **_kwargs): assert state == 'domcontentloaded'
class Listing:
    def __init__(self): self.context, self.url = SimpleNamespace(pages=[self]), 'about:blank'
    def goto(self, url, **_kwargs): self.url = url
    def get_by_role(self, role, name, exact):
        assert (role, name, exact) == ('link', 'test.svg', True)
        return Element(name, self)
listing = Listing()
assert isinstance(namespace['open_from_seafile_list'](listing, 'https://synthetic.invalid', 'library', 'test.svg', middle_click=True), Popup)
assert actions == [('test.svg', 'click', 'middle')]
print('PASS offline VectorCraft/FigCraft geometry assertions; runtime NOT RUN')
