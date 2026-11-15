# ROADMAP

Reset on 2026-10-31 by the re-foundation (`docs/REFOUNDATION-REPORT.md`). The previous 14-phase
plan (gateway + Seahub/fileserver patches + per-app engine patches) is retired; its artifacts stay
under `docs/reviews/` and `integration/` as evidence.

## Done

| What | Evidence |
| --- | --- |
| Decision: zero-patch WOPI editor bridge; owner later authorized ONLYOFFICE retirement and selected ArtCraft as the target suite | report §5; `docs/ONLYOFFICE-RETIREMENT-20261108.md` |
| Bridge prototype + fake-host tests | `bridge/`, `tests/bridge/` (33) |
| Historical Seafile CE 13.0.28 + ONLYOFFICE 9.4 lab, HTTP slice | `lab/real-seafile/results/slice.json` (45/45); not the active candidate |
| Real browser path: 4 unpatched upstream bundles, VectorCraft via shim, DeckCraft/SoundCraft/PhotoCraft/DesignCraft via local ports built in the lab | `results/browser.json` (50/50), screenshots |
| Independent review R2 of the bridge, all HIGH/MEDIUM fixed | report §7, historical suite at review time (30); current suite has 33 |
| Deployment kit | `deploy/bridge/` |
| Upstream drafts (unpublished) | `docs/upstream-drafts/` |

## Active status — owner override, updated 2026-11-15

Compact validation/continuation entry point: `docs/VALIDATION-STATE.md`.

ONLYOFFICE is retired by owner instruction (`docs/ONLYOFFICE-RETIREMENT-20261108.md`).
Do not run the historical ONLYOFFICE campaigns below.

1. Automated isolated candidate: 20/20 offline command groups and the fresh
   Seafile CE 13.0.28 lab pass at source `be51c3b577fda9834de4364a35d0784d28f62492`;
   HTTP 56/56 and browser 58/58. Core DOCX typed edits create Seafile versions
   and survive a fresh-session reopen.
2. Opt-in read-only legacy routes: ODT→WordCraft, ODS/CSV→GridCraft and
   PPSX→DeckCraft have exact-byte, visible-marker and read-only-state checks.
   DOC/XLS are unrouted; their standalone fixture render works, but retained
   Seafile-host behavior is NOT VERIFIED. FODS displays raw XML; FODT/FODP/PPT/
   ODP/PPS remain unrouted. No legacy edit/save or conversion is claimed.
3. Owner-server test access is prepared: the corrected account is active and
   the existing synthetic library is shared read-write. No file content or
   server configuration changed. The live Seafile is 12.0.14 with no ArtCraft
   bridge configured, so authenticated browser edit/save/reopen remains NOT
   VERIFIED. See `docs/reviews/PROJECT-CLOSURE-20261115/OWNER-SERVER-ACCESS-20261115.md`.
4. Remaining: hardware WebGPU/clipboard/fonts/unload acceptance and authenticated
   owner-server validation. GPT-6 Sol reviewed `d263583` and returned PROVISIONAL
   PASS for the isolated subset only; this is not the project-wide gate. No
   converter or LibreOffice product path is planned.

## Historical next steps (superseded where they require ONLYOFFICE)

| # | Step | Done when |
| --- | --- | --- |
| 1 | Retain experimental host ports | Historical Rust ports and evidence retained outside the zero-patch candidate. |
| 2 | VectorCraft/FigCraft lab shims | Private earlier-source results: 20/20 VC, 21/21 FC; sanitized retained evidence and final-source review/replay pending. |
| 3 | Real edits and semantic reopen for the zero-patch candidate | Six Craft private runs recorded passing assertions. ONLYOFFICE needs corrected semantic predicates and final fresh reopen. Exact-source retained evidence remains pending. |
| 4 | Media scope | FilmCraft, EffectCraft and LightCraft are explicitly excluded from the candidate; no media route is shipped. |
| 5 | Human pass on HTTPS in a desktop browser (WebGPU, clipboard, fonts, unload guard) | checklist in `lab/real-seafile/README.md`, run by the owner |
| 6 | Bounded ONLYOFFICE vs WordCraft DOCX open/readback comparison | Corrected corpus opened in both editors (3 fixtures each), readback hashes unchanged, no downloads; limited screenshots retained. R2 source review passed; R3 archive findings were repaired and R4 returned a bounded PASS. No edit/save/version or full fidelity claim. Two WordCraft aborted requests remain unexplained; initial ONLYOFFICE 502 cause remains unverified ([GR-083](docs/GR-083-WORDCRAFT-ONLYOFFICE-DOCX-COMPARISON.md)) |
| 7 | Second independent review (R2) of the report and the bridge | findings incorporated |
| 8 | Candidate freeze → forensic review → project-level GPT gate | PENDING; previous PASS wording was incorrect |

## Owner-controlled actions — separate authorization required

* If historical GR-015 Seahub/`seaf-server` patches remain deployed, assess a rollback plan separately; do not change production in this validation task.
* For a live ArtCraft test, use an isolated Seafile CE 13+ test instance or obtain separate authorization for any production compatibility change and bridge deployment.
* Consider upstream drafts only after the project GPT gate passes and the owner explicitly authorizes publication.

## Out of scope

SeaDrive workflows. WebDAV clients. Nextcloud/ownCloud adapters (dropped by the report: WOPI
already exists there; the bridge is reusable as is). Re-implementing Seafile. Thirteen per-app
Seafile plugins.
