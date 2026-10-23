# GPT-6.1 Sol Re-review — 0edbe52

Date: 2026-10-23  
Candidate: `0edbe524b4fa321b0f73f8601afef390e7f785e6`  
Verdict: **FAIL**

This independent re-review was run with GPT-6.1 Sol at medium reasoning effort
and default service tier. The annotated candidate tag resolved to the reviewed
SHA. Sol reported that no candidate files, production services, or upstream
artifacts were changed during review.

## Blockers

1. **The Seafile DOCX MVP remains NOT VERIFIED.** The accepted evidence does not
   show Seafile file-list click → WordCraft edit → serialized DOCX → durable
   Seafile version → editor confirmation → close/reopen with the edit preserved.
   `tests/test_browser.py` injects the host page and inspects fetched bytes;
   `tests/test_wordcraft_host_roundtrip.py` uses in-memory storage and checks
   backend XML after reload, not the reopened editor's document semantics.
2. **The dedicated conditional route rejects the intended update token.** Seahub
   mints an `op=update` token but uses `conditional-update-api`. The C route
   installs `upload_headers_cb`, which passes the URL's first component to
   `check_access_token`; that function checks that the route starts with the
   token operation. `conditional-update-api` does not start with `update`, so
   saves are rejected before reaching the handler. The source-level finding was
   confirmed against the pinned base and candidate patch; full runtime execution
   was not performed.

   Evidence: `docs/reviews/GR-015/seahub-12.0.14.patch` near the save URL;
   `docs/reviews/GR-015/seafile-server-12.0.14.patch` at route and hook setup;
   pinned source `server/upload-file.c` at `check_access_token` and
   `upload_headers_cb`.

## Major findings

* Conditional-save authorization, atomicity and runtime compatibility are not
  proven. The GR-015 test uses synthetic dependencies and source assertions;
  C compilation, Django routes, revocation, external-writer races, stale
  same-content saves, interrupted uploads and stock/Go rejection remain
  unverified.
* ONLYOFFICE edit/save/version/reopen preservation was not tested.
* GridCraft has no durable save-result handler or semantic formula recalculation
  and reopen proof. VectorCraft has no dirty/commit-ack protocol and its local
  editor test does not prove Seafile persistence.
* Public security controls remain incomplete: CSP and rate limits are absent;
  parser expansion limits, proxy request/resource limits, nested-frame origin
  handoff, cookie isolation, HTTPS and proxy-origin enforcement are untested.
* Distribution readiness is unresolved: provenance notices exist, but
  compatibility and packaging are not reviewed. Asset fetching remains
  unpinned and can replace patched WordCraft assets.

## Minor findings

* GR-006 still prominently claims “VERIFIED END-TO-END,” contradicting corrected
   status documents. RFC authentication wording does not account for the
   browser-mediated capability form.
* `git diff --check afec19e..0edbe52` reports whitespace in three report lines
  and two C-patch context lines.

## Evidence labels

| Area | Sol's reproduced evidence |
| --- | --- |
| Synthetic | Gateway unit suite, SVG assertion negatives, XLSX fixture, GR-015 AST/static harness passed |
| Local Chromium | Overlap rejection, dirty-state preservation, retry/failure checks passed with synthetic storage |
| Exact source | GR-015 patch applicability passed against recorded bases |
| Real Seafile | No runtime test or accepted E2E evidence found |

## Readiness

| Area | Assessment |
| --- | --- |
| Prototype | Operator-only local investigation; Seafile MVP not ready |
| Public deployment | Not ready |
| Upstream RFC | Internal draft only; publication locked |
| Upstream patch | Not ready; conditional route defective and server patches unbuilt |

## Required remediation

1. Fix route naming/token validation without weakening operation authorization;
   test the actual header hook.
2. Build and test the exact patches in an isolated synthetic Seafile deployment,
   including authorization, conflicts, unsupported-server rejection and durable
   commit acknowledgement.
3. Record the complete DOCX workflow and ONLYOFFICE edit/save/version/reopen
   regression.
4. Complete GridCraft/VectorCraft acknowledgement and semantic round trips,
   deployment controls, reproducible asset provenance and licensing packaging.
5. Correct contradictory evidence claims and submit a new immutable candidate.
