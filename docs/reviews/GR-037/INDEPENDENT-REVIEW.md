# GR-037 independent review record

## Round 1 — changes requested

**Reviewer:** GPT-6.1 Sol, low effort, 2026-10-25.
**Scope:** read-only review of the GR-037 save-byte evidence, browser test
capture, local build-storage check, and tracking updates.

Findings:

1. **MAJOR:** the JSON assertions did not retain enough supporting runtime
   output to substantiate counts, server receipt, history/detail identity, and
   fresh-session evidence.
2. **MINOR:** the browser route hook captures an outgoing request body before
   `route.continue_()`, not bytes received by the gateway.
3. **MINOR:** the build-storage documentation verified target directory but
   not effective Cargo child `TMPDIR`.

## Round 2 — provisional accept

The reviewer assessed all three items closed:

- Retained a sanitized transcript of the browser observer, gateway server
  digest, HTTP response, Seafile history, and fresh-route observations; JSON
  now separates prior/current commit and file IDs, event counts, and hashes
  of session capabilities rather than retaining the raw capabilities.
- Renamed the test capture to `browser_request`, labels it as outgoing, and
  checks exact size as well as SHA-256. Server receipt is independently
  represented by the retained gateway output.
- Added `scripts/check-build-storage.sh`, which checks Cargo metadata,
  configured `TMPDIR`, and the environment seen by a Cargo-run probe. The
  script was run locally and verified both persistent paths under `/home`.

**Review result:** PROVISIONAL ACCEPT for this bounded evidence update; no
BLOCKER or MAJOR. One MINOR asked that the test module docstring say “outgoing
browser request” instead of “gateway edge.” That wording was corrected after
the review; the correction was not separately reviewed.

The reviewer checked Python/shell syntax, JSON consistency, artifact hashes,
the screenshot, and `git diff --check`. The reviewer did not replay the
historical browser/Seafile run; the transcript is sanitized retained evidence,
not raw logs. Production readiness, optimized output, deployment security,
ONLYOFFICE regression, and project-level GPT verdict remain unestablished.
