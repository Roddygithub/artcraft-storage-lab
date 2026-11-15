# Final-candidate review packet — 2026-11-15

This packet asks an independent reviewer to assess the exact repository SHA
provided with the review task. The route correction began at
`4a5ab576da0e0a0f227e672d8ea6258ea90c9acc`; labels were aligned with the retained
evidence at `be51c3b577fda9834de4364a35d0784d28f62492`, where the offline and
Seafile lab runs were repeated. Documentation and sanitized evidence updates
are layered on top. Do not treat a source-run PASS as a project-wide PASS.

## Owner intent and scope

ArtCraft is the intended personal office suite. ONLYOFFICE retirement was
authorized, and the active candidate must not depend on it. Do not recommend
LibreOffice or another converter as a product path: conversion is not the
chosen behavior. The review must distinguish the verified MVP subset from full
replacement coverage.

The candidate architecture is Seafile Web → Seahub WOPI → stateless ArtCraft
bridge → Craft Web editor → WOPI save → Seafile version. No production
deployment or upstream publication is authorized by this packet.

## Current evidence

* `lab/real-seafile/results/2026-11-15-offline-validation/`: 20/20 offline
  command groups at the exact source commit.
* `lab/real-seafile/results/2026-11-15-seafile-render-readonly/`: isolated
  Seafile CE 13.0.28; HTTP 56/56, browser 58/58; DOCX typed edits create
  versions and survive a fresh-session reopen; ODT, ODS, CSV and PPSX have
  visible synthetic markers and read-only UI checks.
* `lab/real-seafile/results/2026-11-15-legacy-render-probe/`: standalone bundle
  render screenshots; FODS displays raw XML. DOC/XLS host behavior was reported
  by earlier exploratory runs, but those failures are not retained as exact-
  source evidence and must be treated as NOT VERIFIED.
* `scripts/forensic-audit.py`: mechanical self-audit inventories 20 result
  directories/checksum manifests, runs 17 available verifiers, checks 16
  provenance files and scans 2 loose JSON files for known secret patterns.
  It is not a complete verifier/provenance chain for every directory and does
  not replace independent review.

## Independent review rounds

- `SOL-REVIEW-D263583.md`: PROVISIONAL PASS for the isolated sequential MVP
  subset only; production permission MAJOR and scope limitations remain.
- `SOL-REVIEW-A8E7149.md`: PROVISIONAL PASS for the documentation follow-up;
  three MINOR wording/link issues are addressed in the current follow-up. No
  runtime replay was performed for that documentation-only review; the current
  exact SHA was then reviewed at `546ce0d`.
- `SOL-REVIEW-546CE0D.md`: PROVISIONAL PASS for the documentation follow-up;
  no new MINOR findings. Production permission MAJOR and readiness limits
  remain open.

## Format claims

| Status | Formats | Boundary |
| --- | --- | --- |
| `EDIT_SUPPORTED` + `SAVE_SAME_FORMAT` | DOCX, XLSX, PPTX | Synthetic edit/save/version/reopen; broad compatibility NOT VERIFIED |
| `VIEW_SUPPORTED` | ODT, ODS, CSV, PPSX | Opt-in, read-only Seafile routes; no legacy save claim |
| `UNSUPPORTED` in candidate | DOC, XLS, FODS, FODT, FODP, PPT, ODP, PPS | No supported Seafile route or correct retained rendered result |

## Open risks and limits

1. The bridge checks version then performs a non-conditional host `PutFile`;
   a concurrent write can land between those operations. Readback does not
   make this atomic. The owner accepted this limit for the zero-patch MVP.
2. Seafile CE 13.0.28 accepts direct `PutFile` with a read-only WOPI token.
   The bridge rejects its own read-only relay, but cannot enforce host
   authorization. Do not call this production-safe.
3. The owner's live Seafile 12.0.14 responds over HTTPS and ping. The corrected
   owner account is active and has a verified direct read-write share to the
   existing synthetic library. Only that library permission changed; its files
   and server configuration were not changed. ArtCraft is not configured, and
   authenticated owner-server edit/save remains NOT VERIFIED. Do not request a
   production upgrade or deployment as part of this review. See
   `OWNER-SERVER-ACCESS-20261115.md`.
4. Physical browser acceptance (WebGPU, clipboard, fonts, popup behavior,
   dirty close, refused save and network recovery) remains NOT VERIFIED.
5. Some earlier free-review transcripts were private and are not retained.
   Their verdicts remain PROVISIONAL, not reviewable evidence.

## Required verdict

Review the exact SHA from the task prompt adversarially. Return explicit
`BLOCKER`, `MAJOR`, `MINOR`, `LIMITATION`, `ACCEPTED` or `NOT VERIFIED`
findings; inspect source, runnable evidence, security boundaries and the
candidate's readiness wording. State whether the subset MVP is ready for its
claimed lab scope, whether full ONLYOFFICE replacement is complete, and whether
any global GPT review gate can pass. Do not infer live-server or hardware
acceptance from the isolated lab.
