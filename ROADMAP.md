# ROADMAP

Reset on 2026-10-31 by the re-foundation (`docs/REFOUNDATION-REPORT.md`). The previous 14-phase
plan (gateway + Seahub/fileserver patches + per-app engine patches) is retired; its artifacts stay
under `docs/reviews/` and `integration/` as evidence.

## Done

| What | Evidence |
| --- | --- |
| Decision: zero-patch WOPI editor bridge, ONLYOFFICE kept for office | report §5 |
| Bridge prototype + fake-host tests | `bridge/`, `tests/bridge/` (32) |
| Real Seafile CE 13.0.28 + ONLYOFFICE 9.4 lab, HTTP slice | `lab/real-seafile/results/slice.json` (45/45) |
| Real browser path: 4 unpatched upstream bundles, VectorCraft via shim, DeckCraft/SoundCraft/PhotoCraft/DesignCraft via local ports built in the lab | `results/browser.json` (50/50), screenshots |
| Independent review R2 of the bridge, all HIGH/MEDIUM fixed | report §7, `tests/bridge/` (30) |
| Deployment kit | `deploy/bridge/` |
| Upstream drafts (unpublished) | `docs/upstream-drafts/` |

## Active next steps — owner override, 2026-11-08

Compact validation/continuation entry point: `docs/VALIDATION-STATE.md`.

ONLYOFFICE is retired by owner instruction (`docs/ONLYOFFICE-RETIREMENT-20261108.md`).
Do not run the historical ONLYOFFICE campaigns below.

1. Done: ONLYOFFICE removed from active lab; fresh WordCraft replay HTTP 40/40,
   browser 28/28, exit 0 (`lab/real-seafile/results/2026-11-08-craft-only-wordcraft/`).
2. Done (opt-in `--pptx`): official DeckCraft v0.16.0 same-format edit/save/reopen,
   focused 15/15 and combined seven-editor 132/132 browser checks; see validation checkpoint.
3. Done: legacy/OpenDocument coverage evidence. Deterministic fixtures, offline
   signature/routing checks, an opt-in `--viewing` browser replay (HTTP 57/57,
   browser 140/140, 21 viewing checks) and a bundle import probe (5/5) are
   committed. Rendered legacy content in the combined run and the seven
   import-less formats remain NOT VERIFIED. Hardware WebGPU/clipboard/font/unload
   acceptance is still pending.
4. Freeze exact source/evidence, then obtain independent forensic and project GPT review.
   Evidence is frozen at `864fc77` (2026-11-10); the gate itself is pending.

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

## Owner-only

* Diagnose the ONLYOFFICE `api.js` 404 on the live instance.
* Roll back the GR-015 Seahub/`seaf-server` patches on the live instance (rollback archive recorded).
* Upgrade the live Seafile to 13 (the bridge needs Seahub ≥ 13 for non-office extensions).
* After the gate: approve (or not) each item in `docs/upstream-drafts/`.

## Out of scope

SeaDrive workflows. WebDAV clients. Nextcloud/ownCloud adapters (dropped by the report: WOPI
already exists there; the bridge is reusable as is). Re-implementing Seafile. Thirteen per-app
Seafile plugins.
