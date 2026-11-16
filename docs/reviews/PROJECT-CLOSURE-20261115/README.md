# Final-candidate review packet — 2026-11-15

This packet asks an independent reviewer to assess the exact repository SHA
provided with the review task. The current technical candidate is
`123d2a0ca8435e93e37b6d2f31fb73ac016fc5fb`; the commits layered on top are
documentation and sanitized evidence only (`git diff --stat 123d2a0 <SHA>`
should show no change under `bridge/`). The route correction began at
`4a5ab576da0e0a0f227e672d8ea6258ea90c9acc`, and labels were aligned with the
retained evidence at `be51c3b577fda9834de4364a35d0784d28f62492`. Do not treat a
source-run PASS as a project-wide PASS.

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

* `lab/real-seafile/results/2026-11-15-offline-validation-123d2a0/`: 21/21
  offline command groups at the exact candidate `123d2a0`, with every log
  retained and manifest-verified.
* `lab/real-seafile/results/2026-11-15-seafile-render-readonly/`: isolated
  Seafile CE 13.0.28; HTTP 56/56, browser 58/58; DOCX typed edits create
  versions and survive a fresh-session reopen; ODT, ODS, CSV and PPSX have
  visible synthetic markers and read-only UI checks.
* `lab/real-seafile/results/2026-11-15-seafile12-replay/`: pinned Seafile CE
  12.0.14; WordCraft DOCX 24/24, GridCraft XLSX 27/27, DeckCraft PPTX 15/15
  browser assertions, each with a new Seafile version and a fresh-session
  reopen. DOCX and PPTX relay/readback bytes are retained; GridCraft's runner
  does not retain XLSX relay bytes, so its claim is limited to the recorded
  assertions. Its summaries retained the central claims as bare booleans —
  superseded by the re-run below.
* `lab/real-seafile/results/2026-11-15-seafile12-detail/`: the remediated
  re-run (same pinned image and launcher): 66/66, and its `verify.py` rejects
  bare booleans — every version check retains
  `history N->M grew=True creator_is_opener=True`, every fresh-session and
  file-list check retains `url_has_login_redirect=False`; the nine
  `check(name, True)` tautologies are gone; the sanitizer is committed and
  unit-tested. Produced from the review
  `CE12-REVIEW-5FE30C6.md`.
* `lab/real-seafile/results/2026-11-16-seafile12-byteproof/`: the current
  CE12 evidence: 66/66, same proof requirements as the detail run, plus
  retained XLSX bytes (relay==readback byte-identical, original differs) and
  `new_browser_context=True` in fresh-session details.
* `docs/security/HOST_PERMISSION_BOUNDARY.md`: the host write boundary
  analysis (PutFile ignores `can_edit` on CE 12 and 13; zero-patch fix NOT
  possible; host change required for untrusted viewers).
* `lab/real-seafile/results/2026-11-15-seafile12-isolated-edit-save/`: the same
  CE12 three-editor replay (24 DOCX + 27 XLSX + 15 PPTX = 66) at the earlier
  source `11b75a2`, superseded by the replay above at the current candidate.
* `lab/real-seafile/results/2026-11-15-legacy-render-probe/`: standalone bundle
  render screenshots; FODS displays raw XML. DOC/XLS host behavior was reported
  by earlier exploratory runs, but those failures are not retained as exact-
  source evidence and must be treated as NOT VERIFIED.
* `scripts/forensic-audit.py`: mechanical self-audit inventories 24 result
  directories/checksum manifests, runs 21 available verifiers, checks 19
  provenance files and scans 87 JSON files plus 2 loose root JSON files for
  known secret patterns. It is not a complete verifier/provenance chain for
  every directory and does not replace independent review.

## Independent review rounds

- `SOL-REVIEW-D263583.md`: PROVISIONAL PASS for the isolated sequential MVP
  subset only; production permission MAJOR and scope limitations remain.
- `SOL-REVIEW-A8E7149.md`: PROVISIONAL PASS for the documentation follow-up;
  three MINOR wording/link issues are addressed in the current follow-up. No
  runtime replay was performed for that documentation-only review; the current
  exact SHA was then reviewed at `546ce0d`.
- `SOL-REVIEW-546CE0D.md`: PROVISIONAL PASS for the documentation follow-up;
  no new MINOR findings. Production permission MAJOR and readiness limits
  remain open. A later read-only owner-server check found pre-existing legacy
  Seahub routing and an active gateway; this discovery is not part of that
  review and is being documented separately.
- `SOL-REVIEW-6E496BA.md`: PROVISIONAL PASS with two MINOR wording findings
  about gateway linkage and the lab checklist entry point.
- `SOL-REVIEW-230A47C.md`: PROVISIONAL PASS for the correction; both MINOR
  findings closed, none new. This does not verify the live WOPI workflow.
- `CE12-REVIEW-5FE30C6.md`: targeted free-model review of the CE12 runner and
  both replay directories, run in an isolated worktree at `5fe30c6`
  (byte-identical CE12 artefacts to the `a1984d5` review head). PROVISIONAL
  PASS; no BLOCKER/MAJOR; two MINOR evidence-quality findings (version and
  fresh-session claims retained as bare booleans), all six fault-injection
  mutations rejected by both verifiers. Remediated by the
  `2026-11-15-seafile12-detail` re-run with retained proof details; the
  remediation also found and removed nine `check(name, True)` tautologies,
  three of which counted in the advertised 66/66.

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
   account has a verified read-write share to the synthetic library. Read-only
   inspection found a pre-existing patched repo-scoped ArtCraft route and
   active legacy gateway; current WOPI is disabled. The route is not the
   candidate. GR-059 has historical real save/version/reopen evidence through
   that route; current WOPI was not tested. No file content or server
   configuration was changed during this task. See
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
