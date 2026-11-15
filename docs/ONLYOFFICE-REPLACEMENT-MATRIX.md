# ONLYOFFICE replacement target

On 2026-11-08 the owner requested replacement coverage for **all formats**.
A read-only AST inspection of the current Seafile configuration found the
following declared routes. No settings were executed or changed, and no
credentials or private origins are retained. Configuration membership is not
proof that every current ONLYOFFICE path works in practice.

| Required format | Current mode | ArtCraft status | Verified behavior and limit |
| --- | --- | --- | --- |
| DOCX | View + edit | EDIT_SUPPORTED / SAVE_SAME_FORMAT | WordCraft synthetic typed edits, Seafile version and fresh reopen; broad arbitrary-document fidelity NOT VERIFIED |
| XLSX | View + edit | EDIT_SUPPORTED / SAVE_SAME_FORMAT | GridCraft synthetic typed-cell save, version and fresh reopen; broad workbook fidelity NOT VERIFIED |
| PPTX | View + edit | EDIT_SUPPORTED / SAVE_SAME_FORMAT | DeckCraft v0.16 synthetic title edit, same-format save, version and fresh reopen; broad fidelity NOT VERIFIED |
| DOC | View | UNSUPPORTED in current Seafile candidate | Standalone WordCraft bundle probe renders the synthetic marker; DOC is unrouted in the candidate and Seafile-host rendering is NOT VERIFIED by retained exact-source evidence |
| XLS | View | UNSUPPORTED in current Seafile candidate | Standalone GridCraft bundle probe renders the marker and value; XLS is unrouted in the candidate and Seafile-host rendering is NOT VERIFIED by retained exact-source evidence |
| ODT | View | VIEW_SUPPORTED | WordCraft displays the fixture marker; route/payload proved on Seafile; no in-place legacy save tested |
| ODS | View | VIEW_SUPPORTED | GridCraft displays marker/value cells, warns formulas become values and Save produces XLSX; no Seafile save tested |
| CSV | View | VIEW_SUPPORTED | GridCraft displays marker/value cells; its editor serializes XLSX, not a same-format CSV save |
| PPSX | View | VIEW_SUPPORTED | DeckCraft visibly renders the fixture marker on slide 1; route/payload proved on Seafile; no in-place legacy save tested |
| FODS | View | UNSUPPORTED | GridCraft screenshot displays raw `office:document` XML as cells; removed from the opt-in route |
| FODT | View | UNSUPPORTED | WordCraft rejects the fixture; no serialized import |
| PPT | View | UNSUPPORTED | DeckCraft opens a blank deck; no import |
| ODP | View | UNSUPPORTED | DeckCraft opens a blank deck; no import |
| FODP | View | UNSUPPORTED | DeckCraft opens a blank deck; no import |
| PPS | View | UNSUPPORTED | DeckCraft opens a blank deck; no import |

These are synthetic-fixture classifications, not broad format-fidelity claims.
No legacy row is evidence of an edit/save workflow. `CONVERT_AND_SAVE_AS` is
not part of the ArtCraft product path; the target is the Craft suite itself.

Current render evidence (isolated Craft bundles and Seafile-host screenshots for the four routed formats):
`lab/real-seafile/results/2026-11-15-legacy-render-probe/` and
`lab/real-seafile/results/2026-11-15-seafile-render-readonly/`. The six visible
bundle fixtures do not imply Seafile-host rendering works for DOC or XLS. Earlier
exploratory observations reported DOC unrelated content and an empty XLS frame,
but those failures are not retained as exact-source evidence and are not counted
as verified. Both formats are unrouted in the candidate. FODS is unrouted
because GridCraft displays raw XML. Current Seafile browser evidence verifies
visible content only for ODT, ODS, CSV and PPSX, and verifies no route for the
eight excluded formats; it makes no legacy save claim.

## Deterministic viewing fixtures — 2026-11-08

Every viewing format above now has one synthetic file that carries the marker
`GR-LEGACY-MARKER-20261108` in its real content, generated offline and
committed with checksums. Their provenance records the tool used at that time;
this is synthetic test-data provenance, not a product dependency or editor
recommendation. The owner has clarified that the intended office suite is
ArtCraft itself; no LibreOffice runtime or conversion workflow is in scope.

* fixtures + `PROVENANCE.txt` + `SHA256SUMS`: `lab/real-seafile/fixtures/legacy/`
* historical regeneration script: `scripts/make-legacy-fixtures.sh <tool-image> <outdir>`
* opt-in routing candidate: `lab/real-seafile/editors.viewing.json`
* offline check: `tests/test_legacy_fixtures.py` (fixture integrity, bridge
  signature guard, routing only)

The fixtures, the `content_matches_extension` signatures for DOC/XLS/PPT/PPS,
PPSX and FODT/FODS/FODP, and the routing map are testable offline. That is
**fixture and routing evidence**: the browser replay below adds a real Seafile
open/route/no-download/no-write check and the bundle probe adds editor import,
but no format replacement or rendered-content equivalence is claimed. Only DOC, ODT (WordCraft v0.16.0
README:99/128) and XLS, ODS, CSV (GridCraft v0.17.0 README:93/94/96) have a
documented upstream import path. GR-088 adds probe-proven imports for FODS
(GridCraft) and PPSX (DeckCraft); both are in the opt-in route and passed a real
browser routing replay (59/59 HTTP, 173/173 browser), though rendered content is
NOT VERIFIED. PPT, PPS, ODP and FODP only produce a blank deck and FODT produces
no save, so those five stay unrouted. The replacement baseline therefore remains
a partial, honest subset.

### Real Seafile routing replay — 2026-11-09 (opt-in `--viewing`)

At source `53c7e22` (commit `864fc77`), a fresh rootless lab with `--viewing`
passed HTTP **57/57** (17 of them legacy viewing-route checks) and browser
**140/140**, including **21** viewing checks, exit 0, on stock synthetic Seafile
CE 13.0.28. In one authenticated session each of DOC/ODT and XLS/ODS/CSV opens
from the Seafile file-list click, routes to the documented editor, downloads
nothing and writes no version; FODT, FODS, FODP, PPT, ODP, PPS and PPSX carried
**no WOPI route at that source** (the later GR-088 `fods` route is not part of
this replay). Sanitized retained evidence and a runnable verifier:
`lab/real-seafile/results/2026-11-09-legacy-viewing-browser/` (verifier PASS).
This supersedes the first routing replay at `4fe3fc4` (browser **119/119**,
`results/2026-11-08-legacy-viewing/`). It remains **routing and safety**
evidence; rendered content is not asserted.

### Bundle-level import probe — 2026-11-08 (offline)

The pinned WordCraft v0.16.0 and GridCraft v0.17.0 bundles import all five
routed legacy fixtures (DOC, ODT, XLS, ODS, CSV) and serialize the marker in
their native format: DOCX text runs, ODT `content.xml`, XLSX cells. Script
`scripts/probe-legacy-import.py`, exit 0 with **5/5 passed**. This is
editor-bundle import evidence, independent of host, bridge and Seafile.

The initial replacement baseline is **15 viewing formats and 3 editing
formats**. Adding editing support for the currently view-only formats would be
an additional capability, not something established by the existing settings.
Changing an extension, exporting another format or downloading a file cannot
satisfy same-file edit/save/new-version validation for the three editing routes.

The shipped zero-patch candidate currently validates DOCX/XLSX among the
required office formats; PPTX now has a validated opt-in `--pptx` lab candidate
(`lab/real-seafile/results/2026-11-08-pptx-official/`). PDF/DXF/SVG/FIGCRAFT are additional Craft routes, not
substitutes for the missing office coverage. Experimental DeckCraft Rust ports
remain outside the zero-patch default. The owner subsequently authorized ONLYOFFICE retirement independently of this
coverage; see `ONLYOFFICE-RETIREMENT-20261108.md`. Missing formats remain NOT VERIFIED.

Remaining: rendered-content capture for the five routed legacy formats inside a
combined host+browser session, an upstream import path for the seven unrouted
formats, human HTTPS/hardware acceptance and the independent project gate.
Production stays unchanged; upstream LOCKED; project INCOMPLETE.

## New upstream releases staged separately

Read-only GitHub release inspection identified DeckCraft **v0.16.0**, WordCraft
**v0.16.0** and GridCraft **v0.17.0**. Their official Web ZIPs were downloaded
and extracted through `scripts/craft_web_zip.py`; each archive matches its GitHub
asset SHA-256. Exact URLs, hashes, sizes and bundled-documentation hashes are
retained in `docs/reviews/PROJECT-CLOSURE-20261108/upstream-release-pins.json`.
These staged files do not replace the already validated bundles yet.

DeckCraft v0.16.0's bundled `HOSTING.md` now documents the upstream parent-host
protocol and preserving a host-opened PPTX's name/format on Save. Its pinned
`craft-web-host` protocol uses `saved {id}` acknowledgements; the bridge now
answers those only after verified storage (bounded source review PASS).
This is documentary capability evidence, **not a successful PPTX runtime**.

WordCraft v0.16.0 documents DOC import and ODT import/export; GridCraft v0.17.0
documents CSV/TSV and ODS data import using cached values rather than formulas.
No FODT/FODS support or faithful legacy/OpenDocument viewing is inferred from
those statements. All missing viewing routes still require actual tests.

PPTX update: the earlier documentary-only claim is superseded by the focused
2026-11-08 runtime above. One title-box fixture passed; Arial fallback was
visible, so exact font fidelity remains NOT VERIFIED. Combined replay passed HTTP 40/40 and browser 132/132 across seven editors
(`lab/real-seafile/results/2026-11-08-seven-craft-validation/`).
