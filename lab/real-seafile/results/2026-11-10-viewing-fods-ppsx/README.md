# FODS and PPSX viewing routes on real Seafile (opt-in `--viewing`)

Source: commit `91d8c7f` plus the GR-088 routing changes that add FODS and PPSX
to the opt-in candidate (committed after this run). Stock synthetic Seafile CE
**13.0.28**, rootless Podman, no Seafile or editor patch. The launcher process
was interrupted after the browser container finished (session ended), so its
final exit code was **not captured**; the browser wrote a complete 173/173
result and the project containers were removed manually afterwards.

## Result

HTTP **59/59** and browser **173/173**, including **29** viewing checks, on the
`pptx-candidate-20261108/static` bundle set (WordCraft v0.16.0, GridCraft
v0.17.0, official DeckCraft v0.16.0, plus the other pinned editors).

Sanitized checks: `slice.json` and `browser.json` (integrity: `SHA256SUMS`,
runnable verifier: `verify.py`). The private run directory and screenshots are
not retained.

## What the new checks establish

| Route | HTTP | Browser |
| --- | --- | --- |
| `fods` → GridCraft | `seahub_fods_routes_to_wopi_gridcraft`, `bridge_open_fods_gridcraft` | file-list open, documented route, no download, no version write |
| `ppsx` → DeckCraft | `seahub_ppsx_routes_to_wopi_deckcraft`, `bridge_open_ppsx_deckcraft` | file-list open, documented route, no download, no version write |
| native `.deckcraft` | route retained | DeckCraft native workflow passes again |

The documented five (DOC/ODT, XLS/ODS/CSV) still pass, and FODT/FODP/PPT/ODP/PPS
still carry **no WOPI route**. The six editors' edit/save/version/reopen checks
also pass in the same run.

## What this does NOT establish

* Rendered legacy content: this is routing and safety evidence only. The marker
  import is proven separately by `scripts/probe-legacy-import.py` (7/7).
* Saves of a legacy/OpenDocument fixture, broad fidelity, production behavior or
  human HTTPS/hardware acceptance.
* Independent review of this run: NOT PERFORMED.
