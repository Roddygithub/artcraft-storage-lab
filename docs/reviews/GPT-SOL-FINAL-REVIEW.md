# GPT-6.1 Sol Final Review

Candidate: `c76a7594cc43ba2a6cf56de2232836f008a97863`
Branch: `main`
Date: 2026-10-22
Reviewer: GPT-6.1 Sol (independent delegated review)

## Verdict

**FAIL** — five BLOCKER findings remain. No GPT Review Pass is granted and upstream publication remains locked.

## BLOCKER

1. **Unauthenticated callers can obtain read/write sessions using the gateway account.** `Handler._open()` accepts arbitrary `repo_id/path` without authenticating the caller; `open_session_direct()` uses the configured Seafile credential. Sol reproduced an unauthenticated `/open/?format=json` response of 200 with `can_edit: true` and an empty user, then used the SID to write. Evidence: `integration/gateway/server.py` (`Handler._open`, `Gateway.open_session_direct`, `Handler.do_GET/do_POST`).

2. **Authorization checks use gateway permissions, not the editing user's.** Token-based opening records a username, but `_make_session()` and `save()` query file details through the gateway account token. Sol reproduced a read-only user obtaining an editable session and saving successfully when the gateway account had write access. Evidence: `integration/gateway/server.py` (`_make_session`, `Gateway.save`) and `integration/gateway/seafile.py` (`file_detail`).

3. **Concurrent saves silently overwrite.** With two sessions and a barrier after both read the same original content ID, both saves returned 200 / `ok: true`; writes landed B then A and final storage contained only A. `Gateway.save()` performs an unprotected check followed by an unconditional update. The existing sequential stale-save test does not cover this race. Evidence: `integration/gateway/server.py`, `integration/gateway/seafile.py`, `tests/test_gateway_unit.py`.

4. **WordCraft export can overwrite the original DOCX with another format.** The committed WordCraft patch forwards Save, Save As, and PDF export through `wordcraft:save`; host code ignores `data.name` and writes all bytes to the original session path. Sol reproduced PDF bytes replacing `/synthetic.docx` and a 200 / `ok: true` response. Live UI export was not verified. Evidence: `docs/reviews/GR-014/DIFF.patch`, its `Bridge.connect()`, `integration/gateway/hostpage.py`, and `Gateway.save()`.

5. **The mandatory Seafile Web DOCX MVP is not proven.** The browser test posts repository/path parameters directly and injects the returned host page; it does not click a DOCX in Seafile Web. Its reopen check fetches bytes and searches XML but does not reopen WordCraft and verify the rendered edit. GR-006 says DOCX is not registered in the live hook. Evidence: `tests/test_browser.py`, `docs/reviews/GR-006/README.md`; commit `fcc7d81` overstates this as the end-to-end MVP.

## MAJOR

- **SVG evidence does not establish intended stroke preservation.** Assertions accept any `<svg` and `<path>`; rectangle conversion could satisfy them. Byte equality proves transport fidelity, not edit correctness. Evidence: `tests/test_gr012_svg.py`.
- **Licensing analysis is incorrect.** `docs/LICENSING.md` identifies Seahub as GPLv2 and Seafile Server as an “LGPL-ish mix.” At the inspected upstream revisions Seahub declares Apache-2.0; Seafile Server declares AGPLv3 with an OpenSSL exception and has a separate Apache-2.0 Python subtree. `docs/DEPLOYMENT.md` and `docs/UPSTREAM-PLAN.md` also need correction. Sources: [Seahub LICENSE at c01d46bc](https://raw.githubusercontent.com/haiwen/seahub/c01d46bcaa0b2ce24c71561c6c61d15fea808d1a/LICENSE.txt), [Seafile Server LICENSE at a652460e](https://raw.githubusercontent.com/haiwen/seafile-server/a652460e9d4314d5e67c82e0ebe9aa48e8ea1212/LICENSE.txt).
- **ONLYOFFICE preservation is unproven.** GR-006 records a global XLSX third-party mapping. Leaving ONLYOFFICE settings unchanged does not prove dispatch remains unchanged because the Seahub third-party editor branch precedes normal office handling. Current production behavior is not verified; `docs/TEST-MATRIX.md` rows 6.3–6.4 remain unchecked.
- **The prepared Seafile save patch is not an established remedy.** It is not frozen or hashed in the candidate, and it was not run against Seahub. Supplemental inspection found a principal mismatch: permission checking uses `request.user`, while write-token creation uses cached `request_user`; the patch also retains read-then-write concurrency. External artifact is outside candidate SHA. Evidence: `docs/UPSTREAM-PLAN.md` and external `seahub.patch`.

## MINOR

- Browser test success assertions accept failure text (“Save failed” / “Could not”); later persisted-content checks reduce the risk of a complete false pass. Evidence: `tests/test_browser.py`, `tests/test_gr012_svg.py`.
- Gateway may acknowledge `ok: true` with `version: null` if post-write metadata lookup fails. Evidence: `integration/gateway/server.py`.
- Evidence matrix is inconsistent: SVG rows unchecked while DOCX Seafile-click and editor-reopen rows are checked despite weaker evidence. Evidence: `docs/TEST-MATRIX.md`.
- RFC should mention adjacent ArtCraft issue [#2420](https://github.com/storytold/artcraft/issues/2420), which addresses authoritative host sessions but is not proven equivalent to byte-storage integration.
- Luna report inaccurately attributes static path traversal coverage to the unit test; coverage exists in `tests/test_integration.py`.

## Readiness

- **Prototype:** restricted synthetic experimentation only; the real MVP is incomplete.
- **Public deployment:** not ready. Authentication, user authorization, concurrency, and export routing must be corrected. Missing CSP, Origin/Referer validation, and rate limiting remain separate pre-public-deployment gaps.
- **Upstream RFC/patch:** not ready. No upstream publication is authorized.
- **DeckCraft GR-011:** correctly deferred for an upstream capability gap; inspected browser source has picker/download behavior without a host bridge.

## Reproduction performed by Sol

- `python3 tests/test_gateway_unit.py`: passed.
- Python compilation and `git diff --check`: passed.
- Offline WordCraft WASM release build at patch commit `8707047` on parent `00bc6a4`: passed with five dead-code warnings.
- Live DOCX/XLSX/SVG E2E was not verified; credentials/configuration and Playwright were unavailable.

## Required before re-review

1. Authenticate session creation and enforce the actual user's current read/write permissions; close direct-open access.
2. Prevent silent overwrites across overlapping gateway saves and external Seafile writers; add deterministic regression coverage.
3. Separate overwrite, Save As, and export; reject mismatched output before it can replace the original.
4. Demonstrate the complete Seafile Web DOCX click → edit → save → new version → editor confirmation → close → editor reopen workflow in an isolated deployment while preserving ONLYOFFICE.
5. Strengthen SVG geometry/reopen checks and browser success/failure assertions; test refusal and network-failure acknowledgement.
6. Correct licensing, deployment claims, RFC context, and evidence matrix. Freeze and test the Seafile patch with correct principal binding and concurrency semantics.
7. Complete public-deployment protections before public exposure, then submit a new frozen candidate for fresh independent Sol review.
