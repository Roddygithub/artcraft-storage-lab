# Current project closure ledger

**Current override (2026-11-08):** the owner authorized ONLYOFFICE retirement;
see [retirement evidence](ONLYOFFICE-RETIREMENT-20261108.md). Its regression
and coexistence requirements below are historical and no longer block closure.
The active lab now targets Craft only. Missing office-format coverage, HTTPS
acceptance, exact-source evidence and independent final review remain open.

The owner requires replacement coverage for every currently configured
ONLYOFFICE format: 15 viewing routes and 3 editing routes. The six-Craft
candidate below is a verified subset, not the complete replacement scope.
See `docs/ONLYOFFICE-REPLACEMENT-MATRIX.md`.

## Current verified candidate subset

The candidate follows AGENTS.md rule 6: no Seafile patch and no editor patch.
It includes the released WordCraft, GridCraft, PdfCraft and CADCraft bundles,
plus VectorCraft/FigCraft with the explicitly declared lab JavaScript shim.
The default lab advertises only DOCX, XLSX, PDF, DXF, SVG and FIGCRAFT.
PPTX remains on ONLYOFFICE. Deployment defaults to DXF; office extensions
remain explicit operator opt-ins as documented in `deploy/bridge/README.md`.

DeckCraft, SoundCraft, PhotoCraft and DesignCraft require local Rust shell
ports. They remain experimental drafts and retained evidence, outside this
zero-patch candidate. Their former lab configuration is preserved in
`lab/real-seafile/editors.experimental.json` and
`seahub_settings.experimental.py`; it is not selected by the default launcher.
Media applications and the draw.io stub are also outside the candidate.
This is a scope correction required by rule 6, not validation of those ports.

## Evidence still required before freeze

The recovery audit of `2825f4c` invalidated the previous freeze/completion claim.
Private closure counts below are diagnostic until committed with exact source
identities and independently reviewed. See `FORENSIC-REVIEW-20261108.md`.

| Requirement | Current evidence/state |
| --- | --- |
| WordCraft real edits and semantic fresh reopen | GR-085; safety replay GR-086, HTTP 48/48 + browser 28/28 |
| GridCraft real edits and semantic fresh reopen | 2026-11-08 closure run, HTTP 46/46 + browser 27/27 |
| PdfCraft field edit/save/reopen | 2026-11-08 closure run, HTTP 46/46 + browser 18/18 |
| CADCraft circle edit/save/reopen | 2026-11-08 closure run, HTTP 46/46 + browser 20/20 |
| VectorCraft and FigCraft semantic edits/reopen | 2026-11-08 closure runs, HTTP 46/46 + browser 20/20 (VC), 21/21 (FC) |
| ONLYOFFICE browser edit/save/version regression | Earlier private run: 11 assertions, no final reopen after save two; corrected parser/reopen needs review and replay |
| Reproducible rootless launcher with exact asset identity | Implemented, five offline tests, bounded source review PASS; successful WordCraft real run retained in GR-086 |
| Human HTTPS desktop acceptance | Pending: `lab/real-seafile/README.md` checklist |
| Frozen clean candidate, exact SHA, forensic review | Pending |
| Fresh independent project GPT gate after forensic review | Pending |

GR-078 belongs to the retired `integration/` deployment and is not current
bridge runtime evidence. The historical results remain retained. Bounded
source/evidence reviews do not replace the final project gate.

## Accepted host limit and trust model

On 2026-11-08 the owner selected: **“Accepter cette limite documentée dans le
MVP zéro patch”** in response to the reproduced CheckFileInfo/PutFile race.
A version already changed at preflight is rejected, but a different writer
can commit after that check and before the unconditional host write. Readback
verification cannot reconstruct or prevent that intervening write. Atomic
protection requires a host-enforced conditional write; it is not guaranteed.
The regression in `tests/bridge/test_bridge.py` retains this counterexample.

Seahub also accepts writes with a directly extracted read-only WOPI token.
The bridge checks permissions on its own save path; it cannot fix the host's
direct endpoint. Same-origin editor bundles are trusted code with access to
the host frame, not a sandbox protecting that frame's token. These limits
must remain visible in the final verdict and deployment documentation.

Production upgrades/rollback, live ONLYOFFICE diagnosis and deployment are
separate owner-controlled work, not actions required to close the isolated
lab MVP. Upstream remains LOCKED until a project GPT PASS and separate owner
publication approval. Direct parent work is not Aptarchy completion.

## Blocking coexistence defect found in packaged Seahub 13.0.28

The default mixed WOPI/ONLYOFFICE configuration can leave an Office Online
error in an otherwise generated ONLYOFFICE page. APIJS is present but React
renders the error instead of the editor. Previous HTTP route checks only
looked for APIJS and therefore missed this defect; they now require an empty
Seahub error field. The isolated `--without-wopi` test is diagnostic only and
cannot establish coexistence. Do not deploy the current split configuration.

Local packaged-source audit: `seahub/views/file.py:824–878` attempts WOPI even
for an extension absent from its tuples, sets `return_dict['err']`, and then
passes it to ONLYOFFICE. `frontend/src/view-file-onlyoffice.js:49–50` renders
an error instead of the editor. No standard per-extension configuration fix
was found. The multiple-suite API is Pro-gated and chooses per library rather
than per extension. A compatible unmodified host or another verified native
configuration is required before closure; no host patch or production change
is authorized by this finding.

## Replacement objective clarified by the owner

The owner intends to retire ONLYOFFICE if WordCraft meets the required needs.
It remains the fallback during validation; no removal has been performed.
Priority is now WordCraft durability and document fidelity, then a reviewable
migration/rollback plan. Mixed-suite coexistence is a limitation of the current
host configuration, not evidence that WordCraft's own edit/save chain fails.
It must remain disclosed while ONLYOFFICE is retained.

The new combined six-Craft recovery replay records 119/119 browser assertions
at source `664898f`. Its historical HTTP 46/46 includes two insufficient APIJS
checks; both generated ONLYOFFICE pages fail the subsequently corrected gate.
See `lab/real-seafile/results/2026-11-08-combined-core-recovery/`.

The corrected ONLYOFFICE-only diagnostic completed both real typed saves with
new attributed versions and current-body API readback. It then failed waiting
for the native Find input in the final fresh editor (hidden UI control).
Final fresh semantic reopen remains NOT VERIFIED; this is not a PASS.
The launcher exited 1 and removed its lab containers. No further ONLYOFFICE
replay is planned while priority shifts to WordCraft fidelity. Sanitized checks:
`docs/reviews/PROJECT-CLOSURE-20261108/ONLYOFFICE-DIAGNOSTIC.json`.

## WordCraft replacement readiness follow-up

The focused layout-fixture recovery run records browser **28/28** with actual
DOCX original, first relay/readback and second readback retained. The first
relay equals Seafile readback. Both readbacks preserve referenced header/footer
text, PAGE instructions, table-cell text, explicit page breaks, page geometry
and paragraph style references. The runnable structural verifier and three
parent-inspected screenshots are in
`lab/real-seafile/results/2026-11-08-wordcraft-structure-recovery/`.

This is one synthetic document, not full visual or general DOCX compatibility.
HTTP correctly reports 44 passes and 2 ONLYOFFICE failures; diagnostic collection
does not hide that failure and the runner exits 1 after cleanup. Replacement
readiness still requires the prose/list-format corpus, broader document features,
HTTPS desktop acceptance and final independent gate. No ONLYOFFICE removal or
production change has been performed.

The prose and list/table corpus recovery cases each passed **28/28** browser
assertions at captured source `9a71dff`, while retaining HTTP 44/2 and exit 1.
Both first relay/readback pairs are byte-identical. Their original direct
formatted runs and resolved bullet/decimal list semantics survive both saves,
alongside the earlier bounded structural invariants. Four parent-inspected
screenshots and synthetic DOCX payloads are retained with a runnable verifier:
`lab/real-seafile/results/2026-11-08-wordcraft-corpus-recovery/`.
This extends tested synthetic coverage; it does not prove arbitrary-document
fidelity or authorize retiring ONLYOFFICE. Required real-use formats are being
clarified before a replacement/migration plan is finalized.


## Craft-only recovery replay — 2026-11-08

At exact source `2fb30cd`, a fresh rootless lab passed HTTP **40/40** and
WordCraft Chromium **28/28**, exited 0 and removed its containers. The six
ONLYOFFICE HTTP checks were retired, not repaired or counted as passes.
Two typed saves created attributed Seafile versions; a fresh file-list reopen
between the saves loaded the first persisted bytes. Retained synthetic DOCX
payloads, sanitized checks, screenshots and exact-source hashes are in
[`2026-11-08-craft-only-wordcraft`](../lab/real-seafile/results/2026-11-08-craft-only-wordcraft/README.md).
The structural verifier passes for both saved DOCX files. This is automated
internal HTTP evidence, not HTTPS acceptance or an independent review.
Next implementation priority: upstream DeckCraft PPTX same-format persistence.
Project INCOMPLETE; upstream LOCKED.

## Full default-candidate replay — 2026-11-08

Exact source `8369e8f`: all six default editors passed **119/119** browser
assertions after **40/40** HTTP checks; launcher exit 0, project containers
removed. Compact offline validation passed **18/18 command groups**. Retained
sanitary summaries, synthetic payloads, provenance and integrity verifier:
`lab/real-seafile/results/2026-11-08-all-craft-validation/`. This closes the
combined current-source six-editor replay, not missing formats, HTTPS acceptance
or independent review. Continue from `docs/VALIDATION-STATE.md`.


## Official PPTX and HTTPS recovery — 2026-11-08

At application source `4f4b2dc`, official unmodified DeckCraft v0.16.0 passed
one synthetic title edit → same-file PPTX save → attributed new version →
close → fresh authenticated file-list reopen: **15/15** focused browser checks.
The opt-in `--pptx` combined seven-editor replay passed **132/132** browser
checks after **40/40** HTTP checks. Default routing remains the six-editor
candidate; experimental Rust ports are not involved. The title/marker payloads
and relay/readback equality are retained with provenance and an integrity check.
An Arial fallback warning remains visible; full PPTX fidelity is not claimed.

Current Craft-only WordCraft HTTPS passed HTTP **40/40** and browser **28/28**,
including two attributed saves with a fresh reopen between them. Temporary TLS
routes on desktop/Proxmox were restored by exact before/after comparison. No
production Seafile settings or user documents were changed. The saved screenshot
was inspected and the DOCX structural verifier passed. HTTPS automation does not
replace hardware WebGPU/clipboard/font/unload acceptance. No final reopen after
the second WordCraft save is claimed.

Retained evidence under `lab/real-seafile/results/`: `2026-11-08-pptx-official/`,
`2026-11-08-seven-craft-validation/`, `2026-11-08-wordcraft-https-current/`.
All three launchers exited 0; their project containers are absent. Offline
validation passed **19/19 command groups**. Earlier failed PPTX attempts remain
recorded as failures, with their filter/click-target corrections. Independent
review has not been performed. Continue from `docs/VALIDATION-STATE.md`.
Project INCOMPLETE; upstream LOCKED.

## Legacy/OpenDocument viewing fixtures — 2026-11-08

Deterministic synthetic fixtures now exist for every remaining viewing format
(DOC, ODT, FODT, XLS, ODS, FODS, CSV, PPT, ODP, FODP, PPS, PPSX), each
carrying the marker `GR-LEGACY-MARKER-20261108` in its real content. They were
produced offline with LibreOffice in a disposable rootless-Podman container and
committed with `PROVENANCE.txt`, `SHA256SUMS` and
`scripts/make-legacy-fixtures.sh`. The bridge's name-to-bytes signature guard
now also covers DOC/XLS/PPT/PPS (OLE), PPSX (OPC) and FODT/FODS/FODP (flat ODF);
an opt-in routing candidate (`lab/real-seafile/editors.viewing.json`) maps only
the formats with a documented upstream import (DOC/ODT to WordCraft, ODS/CSV to
GridCraft). All of this is covered offline by `tests/test_legacy_fixtures.py`
and the bridge suite.

This is fixture and routing evidence. A real browser replay later added the
Seafile file-list open, documented route, no-download and no-version-write
checks; the seven formats without a documented Craft import stay unrouted. The
default six/seven-editor candidate is unchanged. Offline checks now number 20
command groups.

## Final evidence freeze — 2026-11-10

Source: `main` at `40a2f1b`, fast-forwarded from `work/project-closure-20261108`
(previously 80 commits ahead of `ae903ac`). The frozen evidence commit is
`864fc77`; no runtime code changed after the `--viewing` replay source
`53c7e22`, and the later commits add the retained run, its verifier and this
documentation.

| Check (re-run 2026-11-10 at `864fc77`) | Result |
| --- | --- |
| `scripts/validate-candidate.py` (documented `uv` Playwright environment) | 20/20 command groups PASS |
| `tests/bridge/test_bridge.py` | 33 tests OK |
| `tests/test_legacy_fixtures.py` | 9 tests OK (1 skipped) |
| `tests/lab/test_local.py` | 13 tests OK |
| `results/2026-11-09-legacy-viewing-browser/verify.py` | PASS: HTTP 57/57, browser 140/140, 21 viewing checks |
| `scripts/probe-legacy-import.py` | 5/5 routed legacy fixtures imported |
| Default, `--pptx` and six-editor replays (earlier, retained) | 119/119; seven-editor 132/132; PPTX focused 15/15 |

Scope frozen: the default six unmodified Craft bundles, the opt-in DeckCraft
PPTX candidate, and the opt-in documented-import legacy routes (DOC/ODT to
WordCraft, XLS/ODS/CSV to GridCraft).

Still NOT VERIFIED: rendered legacy content inside one combined host+browser
session, the seven formats with no documented Craft import, broad document
fidelity, human HTTPS/hardware acceptance, production behavior and any
independent or project-level PASS.

Verdict: implementation and evidence are **frozen** at `864fc77`, integrated on
`main` at `40a2f1b`. Project **INCOMPLETE** until the owner-controlled gates
close (independent forensic and project GPT gate, human HTTPS desktop
acceptance). Upstream publication remains **LOCKED**. This freeze is not a
global PASS and must not be presented as one.
