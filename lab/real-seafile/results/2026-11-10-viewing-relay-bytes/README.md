# Every routed legacy format reaches its editor with the fixture bytes (2026-11-10)

Source `337e4ea` plus the relay-capture probe changes (committed after this run);
stock synthetic Seafile CE **13.0.28**, rootless Podman, no Seafile or editor
patch. Focused run: `--viewing --editor wordcraft`, so the browser replay covers
the seven routed legacy formats and WordCraft's edit/save/reopen cycle only.

## Result

HTTP **59/59** and browser **67/67**, including **43** viewing checks, on the
`pptx-candidate-20261108/static` bundle set. Sanitized summaries: `slice.json`,
`browser.json`; integrity `SHA256SUMS`; runnable verifier `verify.py`.

The probe now captures the bridge's `/relay/file` response for each format and
compares it with the committed fixture. All seven routed formats pass both new
checks: the editor received the exact fixture bytes, and those bytes contain the
fixture marker.

| Fixture | Editor | Bytes | Marker found in |
| --- | --- | --- | --- |
| `doc.doc` | WordCraft | 9216 | OLE payload, UTF-16LE |
| `doc.odt` | WordCraft | 9325 | ODT `content.xml` |
| `sheet.xls` | GridCraft | 5632 | OLE payload, UTF-8 |
| `sheet.ods` | GridCraft | 8763 | ODT `content.xml` |
| `sheet.fods` | GridCraft | 15767 | plain text |
| `sheet.csv` | GridCraft | 42 | plain text |
| `slide.ppsx` | DeckCraft | 23994 | OPC `ppt/slides/slide1.xml` |

Routing and safety checks are unchanged: documented route, no download, no
version write on open.

## What this does NOT establish

* **Rendered pixels.** The screenshots this run captured are not retained as
  render evidence: they can fire before the editor has rendered (`doc.doc` still
  showed `Loading WordCraft…`). The fixture marker reached the editor, but no
  assertion covers what the editor painted.
* **A save of a legacy/OpenDocument format.** No legacy fixture is saved or
  turned into a version here.
* **The other five editors or the default six-editor candidate.** This run is
  filtered to WordCraft; their edit/save/reopen evidence is unchanged.
* Broad fidelity, production behaviour, or human HTTPS/hardware acceptance.
* Independent review of this run: NOT PERFORMED.

Run `python3 lab/real-seafile/results/2026-11-10-viewing-relay-bytes/verify.py`.
Project INCOMPLETE; upstream LOCKED.
