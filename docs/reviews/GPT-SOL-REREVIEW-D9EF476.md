# GPT-6.1 Sol Independent Re-review

Candidate: `d9ef476e6fbcb04c9a9e23cfe235812167d1f27c`
Base candidate: `c76a7594cc43ba2a6cf56de2232836f008a97863`
Date: 2026-10-23
Reviewer: GPT-6.1 Sol

## Verdict

**FAIL** — no GPT review pass. Upstream remains locked.

## Blockers

1. **The required DOCX MVP is unproven.** No evidence demonstrates Seafile Web click → WordCraft edit → save → Seafile version → editor confirmation → close/reopen with the edit preserved. `tests/test_browser.py:89–123` injects a gateway-generated page; `:238–259` checks downloaded XML rather than reopening the editor. GR-015 says patched-server integration and browser tests were not run (`docs/reviews/GR-015/README.md:47–50`).
2. **Conditional save can still accept stale state.** The Seafile C patch returns early for identical content before the branch compare-and-swap, so a concurrent update can bypass the current-branch check (`docs/reviews/GR-015/seafile-server-12.0.14.patch:37–58`; source locations `repo-op.c:4337–4339,4403–4435`). The Go fileserver path does not consume `expected_file_id` and calls `genNewCommit(..., true, ...)` (`fileserver/fileop.go:3123–3129,3224–3254`). The deployed route is not verified. The gateway fake-CAS race does not prove either server route.

## Major findings

1. Read access is not reauthorized after revocation. The content view still mints a view token with an empty username and checks existence rather than current permission (`seahub-12.0.14.patch:93–108`). Sol reproduced a private-byte response after simulated revocation with no permission check.
2. Capability-bearing upstream URLs can reach browser errors. `Seafile._request()` includes full URLs in exceptions (`integration/gateway/seafile.py:53–58`), which `Gateway.save()` and document handlers return (`server.py:184,247`). Synthetic reproduction exposed `access_token` in error output.
3. Save acknowledgement and dirty state are not trustworthy. The host clears `window.__lastDirty` before the editor receives `saveResult` (`hostpage.py:238–254`); `test_browser.py:192–199` can pass without editor confirmation. A later edit during save can be lost from the host dirty indicator, and network-error catches do not set it.
4. GridCraft/SVG fixes remain incomplete: Seahub checks `spreadsheet.sheet` instead of the normal `spreadsheetml.sheet` (`seahub-12.0.14.patch:64–73`); SVG open tests omit `Origin` (`tests/test_gr012_svg.py:105–107,255–257`); the SVG assertion accepts rectangle-only geometry converted to a path without the intended stroke (`:211–219`); reopen is byte equality, not editor semantic verification.
5. ONLYOFFICE preservation is not demonstrated; unchanged settings and extension routing do not prove open/edit/save regression behavior (`GR-015/README.md:50`, `docs/TEST-MATRIX.md` row 6.3).
6. Licensing is only partially corrected. GR-015 contains upstream source context while `docs/LICENSING.md:35–36,87–92` says no such source is present. The cited target repositories declare Seahub Apache-2.0 and Seafile Server AGPLv3 with an OpenSSL exception; patch provenance and notices need explicit treatment.
7. Public-deployment controls and docs are incomplete: CSP/rate limiting absent; `[Content_Types].xml` decompression is unbounded (`server.py:52–55`) despite the security doc saying OOXML is not unpacked; the security doc describes a different-origin/no-Seahub-cookie model inconsistent with proposed same-origin deployment.

## Minor findings

- `git diff --check c76a7594 d9ef476e` exits 2 for trailing whitespace in the remediation report and two GR-015 patch files.
- `docs/SAVE-PROTOCOL.md:201–217` and `docs/TEST-MATRIX.md` contain stale PASS/race/reopen/editor-confirmation claims.
- `docs/RFC-DRAFT.md` omits adjacent ArtCraft Host Mode proposal [#2420](https://github.com/storytold/artcraft/issues/2420); its native authoritative-session scope differs from this browser byte-storage integration.

## Reproduced checks

- `python3 tests/test_gateway_unit.py`: PASS (synthetic gateway tests, including fake CAS).
- `python3 -m py_compile integration/gateway/*.py tests/*.py`: PASS.
- Clean-worktree `git diff --check`: PASS; exact candidate range whitespace check: FAIL, exit 2.
- Local synthetic reproductions: XLSX MIME rejection, access-token leakage, revoked-reader access, rectangle-only SVG false positive, host dirty-state/confirmation weakness.

## Readiness

- Prototype: restricted synthetic development only; accepted Seafile MVP not ready.
- Public deployment: not ready.
- Upstream RFC: not ready for publication.
- Upstream patch: not ready.

## Required remediation

1. Fix the C identical-content precondition bypass; identify the deployed fileserver route and make unsupported routes reject conditional saves.
2. Enforce current read/write authorization and redact capability URLs from browser-facing errors.
3. Keep editor dirty state separate from durable persistence acknowledgement; test edits during save, rejection, network failure, and actual editor confirmation.
4. Fix XLSX validation and SVG headers/assertions; verify SVG semantics after reopening in VectorCraft.
5. Demonstrate the complete DOCX workflow and ONLYOFFICE preservation in an isolated synthetic deployment.
6. Reconcile licensing, deployment instructions, evidence, and RFC claims; create and independently review a new candidate.

## Not verified

Real Seafile persistence/history; deployed fileserver route; patched Seahub deployment; fresh C/WordCraft builds; authenticated Seafile Web click-through; WordCraft durable confirmation/reopen; external-writer races; live permission revocation; GridCraft/VectorCraft semantic round trips; ONLYOFFICE behavior; proxy `Origin` handling; deployed ONLYOFFICE edition/license; other Craft app integrations.

No production access, implementation edits, or upstream publication were performed during this review.
