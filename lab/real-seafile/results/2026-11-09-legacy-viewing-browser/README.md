# Legacy / OpenDocument browser routing on real Seafile (opt-in `--viewing`)

Source `53c7e22` (branch `work/project-closure-20261108`); stock synthetic
Seafile CE **13.0.28**, rootless Podman, launcher exit **0**, project containers
removed. No editor or Seafile patch. Option `--viewing` swaps the run's editors
map for the opt-in candidate (`lab/real-seafile/editors.viewing.json`) and adds
only the documented-import extensions to both Seahub WOPI tuples.

## Result

HTTP **57/57** (17 legacy viewing-route checks) and browser **140/140**
(including **21** viewing browser checks), exit 0. Sanitized checks:
`slice.json` and `browser.json` (integrity: `SHA256SUMS`, runnable verifier:
`verify.py`). The private run directory and screenshots are **not** retained.

## What the 21 viewing browser checks establish

Route and safety evidence in a real authenticated browser session, nothing more:

| Check (×5 fixtures: DOC, ODT → WordCraft; XLS, ODS, CSV → GridCraft) | Meaning |
| --- | --- |
| `viewing_<f>_opened_from_seafile_file_list` | the file-list click opens the document |
| `viewing_<f>_routes_to_<editor>` | the office frame URL is the documented editor |
| `viewing_<f>_open_did_not_download` | no browser download occurred |
| `viewing_<f>_open_wrote_no_version` | opening wrote no Seafile version (history stays at the upload) |
| `viewing_probe_authenticated_session` | one authenticated session, retried while Seahub warms up |

The unrouted formats (FODT, FODS, FODP, PPT, ODP, PPS, PPSX) keep **no WOPI
route**; the HTTP slice asserts each with `seahub_<ext>_has_no_wopi_route`.

## What this does NOT establish

* The exact legacy bytes handed to the editor (`/relay/file`) and the editor's
  imported model are **not captured in this combined run**: the request fires
  before any listener can attach (nested same-origin iframe load order).
* Those two assertions are covered by the **bundle-level import probe**
  (`scripts/probe-legacy-import.py`): the same pinned bundles import the same
  fixtures and serialize the marker in native formats — **5/5 PASS**, offline,
  independent of host/bridge/Seafile.
* No browser assertion covers a legacy fixture's rendered content; no save of a
  legacy fixture is attempted here.
* Human HTTPS desktop acceptance, broad fidelity, or production behaviour.

Run `python3 lab/real-seafile/results/2026-11-09-legacy-viewing-browser/verify.py`.
Independent review of this run NOT PERFORMED. Production unchanged; project
INCOMPLETE; upstream LOCKED.
