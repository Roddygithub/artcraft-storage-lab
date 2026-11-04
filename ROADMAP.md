# ROADMAP

Reset on 2026-10-31 by the re-foundation (`docs/REFOUNDATION-REPORT.md`). The previous 14-phase
plan (gateway + Seahub/fileserver patches + per-app engine patches) is retired; its artifacts stay
under `docs/reviews/` and `integration/` as evidence.

## Done

| What | Evidence |
| --- | --- |
| Decision: zero-patch WOPI editor bridge, ONLYOFFICE kept for office | report §5 |
| Bridge prototype + fake-host tests | `bridge/`, `tests/bridge/` (21) |
| Real Seafile CE 13.0.28 + ONLYOFFICE 9.4 lab, HTTP slice | `lab/real-seafile/results/slice.json` (45/45) |
| Real browser path: 4 unpatched upstream bundles, VectorCraft via shim, DeckCraft/SoundCraft/PhotoCraft/DesignCraft via local ports built in the lab | `results/browser.json` (50/50), screenshots |
| Independent review R2 of the bridge, all HIGH/MEDIUM fixed | report §7, `tests/bridge/` (30) |
| Deployment kit | `deploy/bridge/` |
| Upstream drafts (unpublished) | `docs/upstream-drafts/` |

## Next (lab, no production, no upstream)

| # | Step | Done when |
| --- | --- | --- |
| 1 | ~~DeckCraft, SoundCraft, PhotoCraft, DesignCraft ports~~ done | diffs under `docs/upstream-drafts/`, lab 45/46 |
| 2 | ~~FigCraft through the shim~~ done | lab 50/50 |
| 3 | A real edit before Save in each browser scenario | WordCraft DOCX and GridCraft XLSX passed a fresh isolated replay: file-list clicks, trusted edits, two user-attributed versions, confirmation, old-editor closure and fresh-session semantic reopen; HTTP 48/48, browser 48/48 ([evidence](lab/real-seafile/results/2026-11-03-gridcraft-pilot/README.md)). DeckCraft native `.deckcraft` passed 26/26 ([GR-081](docs/GR-081-DECKCRAFT-REAL-SEAFILE-ROUNDTRIP.md)); CADCraft DXF passed an isolated visible circle edit, save/version, exact relay/readback equality and fresh-session reopen in the 95/95 sequential browser run ([GR-082](docs/GR-082-CADCRAFT-REAL-SEAFILE-ROUNDTRIP.md)). DeckCraft and CADCraft were direct parent work, not Aptarchy. Other editors' genuine edits remain pending; foreign `.pptx` and broad CADCraft DXF fidelity remain unverified |
| 4 | Media apps (FilmCraft, EffectCraft, LightCraft) as export-only (`saveAs: true`) | decision recorded; at most one proof |
| 5 | Human pass on HTTPS in a desktop browser (WebGPU, clipboard, fonts, unload guard) | checklist in `lab/real-seafile/README.md`, run by the owner |
| 6 | ONLYOFFICE vs WordCraft fidelity comparison on the same DOCX corpus | table in the report |
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
