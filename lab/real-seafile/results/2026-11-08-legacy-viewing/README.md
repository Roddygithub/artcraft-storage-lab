# Legacy / OpenDocument viewing routes on real Seafile (opt-in `--viewing`)

Source `4fe3fc4`; stock synthetic Seafile CE **13.0.28**, rootless Podman,
launcher exit **0**. No editor or Seafile patch. Option `--viewing` swaps the
run's editors map for the opt-in candidate (`lab/real-seafile/editors.viewing.json`)
and adds only the documented-import extensions to both Seahub WOPI tuples.

## Result

HTTP **57/57** (including 17 legacy viewing-route checks), browser **119/119**
(the unchanged six-editor candidate replay). Sanitized checks: `slice.json`.
The private run directory, screenshots and full logs are **not** retained here.

## What the 17 viewing checks establish

Route evidence on a real Seahub, nothing more:

| Format | Check |
| --- | --- |
| DOC, ODT | Seahub mints a WOPI form to `/edit/wordcraft`; the bridge answers `editorId=wordcraft` |
| XLS, ODS, CSV | Seahub mints a WOPI form to `/edit/gridcraft`; the bridge answers `editorId=gridcraft` |
| FODT, FODS, FODP, PPT, ODP, PPS, PPSX | Seahub offers **no WOPI route** (no documented Craft import) |

The routed formats are the ones whose pinned upstream release documents an
import path (WordCraft v0.16.0 `README.md:99/128`, GridCraft v0.17.0
`README.md:93/94/96`); DeckCraft v0.16.0 documents only `.pptx`
(`README.md:22`).

## What this does NOT establish

* That any editor actually **imports or renders** these documents in a browser.
  No browser assertion covers a legacy fixture; the browser replay here is the
  standard six-editor candidate.
* That any legacy format is replaced, viewable or editable end to end.
* Human HTTPS desktop acceptance, broad fidelity, or production behaviour.
* The eight import-less formats remain without a candidate route.

Run `python3 lab/real-seafile/results/2026-11-08-legacy-viewing/verify.py`.
Independent review of this run NOT PERFORMED. Production unchanged; project
INCOMPLETE; upstream LOCKED.
