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

## Next (lab, no production, no upstream)

| # | Step | Done when |
| --- | --- | --- |
| 1 | Retain experimental host ports | Historical Rust ports and evidence retained outside the zero-patch candidate. |
| 2 | VectorCraft/FigCraft lab shims | Shim exists; durable-ACK/retry correction and semantic edit/reopen validation are in progress. |
| 3 | Real edits and semantic reopen for the zero-patch candidate | Current WordCraft/GridCraft/PdfCraft/CADCraft evidence exists; VectorCraft/FigCraft runtime validation and exact final-candidate replay remain pending. Rust host ports are experimental and excluded. GR-078 is legacy integration evidence. See [closure ledger](docs/PROJECT-CLOSURE.md). |
| 4 | Media scope | FilmCraft, EffectCraft and LightCraft are explicitly excluded from the candidate; no media route is shipped. |
| 5 | Human pass on HTTPS in a desktop browser (WebGPU, clipboard, fonts, unload guard) | checklist in `lab/real-seafile/README.md`, run by the owner |
| 6 | Bounded ONLYOFFICE vs WordCraft DOCX open/readback comparison | Corrected corpus opened in both editors (3 fixtures each), readback hashes unchanged, no downloads; limited screenshots retained. R2 source review passed; R3 archive findings were repaired and R4 returned a bounded PASS. No edit/save/version or full fidelity claim. Two WordCraft aborted requests remain unexplained; initial ONLYOFFICE 502 cause remains unverified ([GR-083](docs/GR-083-WORDCRAFT-ONLYOFFICE-DOCX-COMPARISON.md)) |
| 7 | Second independent review (R2) of the report and the bridge | findings incorporated |
| 8 | Candidate freeze → forensic review → project-level GPT gate | PASS |

## Owner-only

* Diagnose the ONLYOFFICE `api.js` 404 on the live instance.
* Roll back the GR-015 Seahub/`seaf-server` patches on the live instance (rollback archive recorded).
* Upgrade the live Seafile to 13 (the bridge needs Seahub ≥ 13 for non-office extensions).
* After the gate: approve (or not) each item in `docs/upstream-drafts/`.

## Out of scope

SeaDrive workflows. WebDAV clients. Nextcloud/ownCloud adapters (dropped by the report: WOPI
already exists there; the bridge is reusable as is). Re-implementing Seafile. Thirteen per-app
Seafile plugins.
