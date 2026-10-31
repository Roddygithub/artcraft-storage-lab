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
| Real browser path with 4 unpatched upstream bundles + VectorCraft via shim | `results/browser.json` (21/21), screenshots |
| Deployment kit | `deploy/bridge/` |
| Upstream drafts (unpublished) | `docs/upstream-drafts/` |

## Next (lab, no production, no upstream)

| # | Step | Done when |
| --- | --- | --- |
| 1 | DeckCraft `host.rs` port built and exercised in the lab (`.pptx`) | browser slice passes for DeckCraft with the patched bundle, patch under `docs/upstream-drafts/` |
| 2 | FigCraft through the shim | browser slice makes a fixture with the app and round-trips it |
| 3 | PhotoCraft, DesignCraft, SoundCraft ports (rebase the lab's GR patches on upstream heads) | same criterion as 1, one app at a time |
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
