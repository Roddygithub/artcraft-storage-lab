# Legacy fixture render probe — 2026-11-15

**Scope:** isolated ArtCraft bundles in the upstream `?host=parent` wrapper. No
Seafile, bridge save, production host, or legacy write was involved. It tests
whether a routed editor visibly renders the synthetic fixture marker after its
own save payload confirms import. These six positive cases are still a small
fixture probe, not broad fidelity or an in-Seafile render claim.

## Results

| Format | Editor | Render result | Visible semantic check |
| --- | --- | --- | --- |
| DOC | WordCraft | bundle: PASS; Seafile host: **FAIL** | Isolated bundle shows the marker, but the Seafile-host screenshot shows unrelated sample content; DOC stays unrouted |
| ODT | WordCraft | PASS | marker on the document page |
| XLS | GridCraft | bundle: PASS; Seafile route: **FAIL** | Standalone GridCraft displays marker and `value / 42`; stock Seafile opens an empty office frame and sends no WOPI file bytes; XLS stays unrouted |
| ODS | GridCraft | PASS | marker and `value / 42` in cells; editor warns it imports data only and saves XLSX |
| CSV | GridCraft | PASS | marker and `value / 42` in cells |
| PPSX | DeckCraft | PASS | marker visibly rendered on slide 1 |
| FODS | GridCraft | **FAIL** | workbook shows flat-ODF XML source (`office:document`) as cell text |

All seven pass the existing bundle-level serialization-marker probe. That
proves FODS bytes reach an import/save path, but the screenshot shows the wrong
content model. The DOC host screenshot also shows unrelated WordCraft sample
content despite exact fixture bytes reaching the editor. XLS can render in the
standalone GridCraft bundle, but stock Seafile CE 13.0.28 does not route it to
WOPI. Accordingly DOC, XLS and FODS are **UNSUPPORTED** in the Seafile product
candidate. No ArtCraft bundle or bridge code was changed.

The evidence is deliberately bundled as: screenshot + editor-emitted payload
summary + OCR verifier. Inspect the PNGs directly for layout. OCR verifies the
unique content marker and the FODS XML leak; it is not a substitute for broad
visual fidelity or hardware acceptance.

## Reproduce

```sh
uv run --with playwright --with pillow python scripts/probe-legacy-import.py \
  --static ~/.cache/artcraft-storage-lab/pptx-candidate-20261108/static \
  --output /absolute/private-dir
python3 lab/real-seafile/results/2026-11-15-legacy-render-probe/verify.py \
  /absolute/private-dir
```

Use the bundle hash in `provenance.json`; do not substitute a different
release. `tesseract` must be installed for the OCR assertions. The real Seafile
route and exact relay-byte checks are separate evidence at
`../2026-11-10-viewing-relay-bytes/`.

**Not tested:** editing or saving any legacy file into Seafile, exact layout
fidelity for arbitrary files, fonts on the owner's machine, clipboard, WebGPU,
or the combined Seafile-to-renderer screenshot flow.
