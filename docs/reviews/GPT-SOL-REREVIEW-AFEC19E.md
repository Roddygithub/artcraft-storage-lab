# GPT-6.1 Sol Final Re-review

Candidate: `afec19e63a6a4faec8a94f93651363dbe007e526`  
Reviewer: GPT-6.1 Sol (`codex`, `gpt-6.1-sol`, max reasoning, priority)  
Date: 2026-10-23  
Delegated task: `node:delegated-task:command%3Amcp%3Ae88d48d8-e62d-44d6-a39b-f433b7eaa818%3Adelegate-task%3Aartcraft-sol-final-rereview-afec19e63-20261023`

## Verdict

**FAIL.** Sol reviewed the exact candidate in an isolated, clean worktree. No
deployed service or upstream artifact was changed. This report preserves the
independent review; findings remain open until reproduced, fixed, tested, and
re-reviewed.

## Blockers

1. The required Seafile Web → WordCraft DOCX edit → durable version → close →
   reopen flow is not proven. `tests/test_browser.py` injects a gateway page and
   checks downloaded XML; the WordCraft round-trip uses in-memory storage and
   does not show the saved edit rendered by a reopened editor.
2. Conditional save is not fail-closed across server implementations. Seahub
   accepts ordinary `update-api` HTTP 200 even if the fileserver ignores the
   conditional parameters. The Go route ignores `expected_file_id`; actual
   server race behavior remains **NOT VERIFIED**.

## Major findings

1. Overlapping saves can falsely set the host clean and show “Saved” while the
   later edit is absent from storage. Sol reproduced this with local WordCraft,
   Chromium, and delayed synthetic storage. The single-save test misses it.
2. The proposed save view can turn generic preview capabilities into write
   authority. It ignores cached `permission.can_edit` and does not enforce the
   ArtCraft repository allowlist or capability audience.
3. Malformed successful save responses can expose their first 200 bytes,
   including an `access_token`, through the gateway error response.
4. The proposed single-origin topology exposes the hidden Seahub capability form
   and Seahub cookies to the unsandboxed Craft frame.
5. GridCraft has no ticket/save-result handler and marks the workbook saved when
   bytes are handed to the parent. Its fixture stores formula text in `<v>`
   without a formula `<f>`; semantic reopen is unproven.
6. GR-012 omits required `Origin` headers, accepts rectangle-only SVG geometry,
   checks byte equality instead of reopening VectorCraft, and lacks a
   dirty/commit-ack protocol.
7. ONLYOFFICE edit/save/version/reopen preservation is unverified.
8. CSP, rate limiting, streaming response bounds, expanded document limits, and
   proxy-origin behavior remain incomplete or unverified.
9. GR-015 licensing/provenance packaging is incomplete and other documents have
   stale claims about Seafile source inclusion.

## Minor findings

- RFC, upstream plan, and file-dispatch documentation contain stale readiness or
  behavior claims.
- `git diff --check d9ef476e..afec19e` reports whitespace in six Seahub patch
  context lines; patch applicability passes.
- `scripts/fetch-craft-web.sh` fetches unpinned latest assets and can overwrite
  patched WordCraft; build provenance needs pinning and documentation.

## Readiness

- Prototype: operator-only local investigation; Seafile MVP not ready.
- LAN/Tailscale: not ready.
- Public deployment: not ready.
- Upstream RFC and patch: not ready; publication remains locked.

Sol independently reproduced gateway unit checks, host protocol simulation,
GR-015 synthetic authorization/type checks, WordCraft with in-memory storage,
syntax/format checks, and patch applicability. Sol also reproduced the
overlapping-save failure in a real local editor/browser. Real Seafile runtime
authorization, persistence/history, server atomicity, semantic reopen, and
ONLYOFFICE save regression remain **NOT VERIFIED**.

## Required remediation

Track and test overlapping save tickets; reject unsupported conditional-save
servers before writes; scope write capabilities by audience, repository,
document, and granted operation; remove error-body credential leakage; isolate
Seahub from the editor origin; complete public-facing resource/security bounds;
prove DOCX/ONLYOFFICE in an isolated synthetic Seafile deployment; repair XLSX
and SVG semantic tests; reconcile licensing, provenance, and documentation; and
submit a new immutable candidate for independent Sol review.
