"""Deterministic synthetic native FigCraft ZIP; no source or personal data."""
import json
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

doc = {"format":"figcraft", "version":1, "imageIndex":[],
       "name":"GR-048 synthetic", "pages":[1], "next_id":2,
       "current_page":1, "nodes":{"1":{"id":1,"name":"GR-048 page",
       "type":"page","width":0.0,"height":0.0}}}
path = Path(__file__).with_name('synthetic.figcraft')
with ZipFile(path, 'w') as z:
    entry = ZipInfo('document.json', (2026, 1, 1, 0, 0, 0))
    entry.compress_type = ZIP_DEFLATED
    z.writestr(entry, json.dumps(doc, separators=(',',':')))
with ZipFile(path) as z:
    assert json.loads(z.read('document.json')) == doc
print(path.name, path.stat().st_size)
