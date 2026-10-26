# GR-081 independent code/security review R4

**Verdict: PROVISIONAL FAIL.** Read-only review of the uncommitted remediation
over `70fa192`; no files changed, tests/builds run, browser used or services
accessed.

## Findings

1. **MAJOR — Save identity remains unresolved.** The host accepts a replacement
   carrying the original filename with `saveAs=false`, then submits its bytes
   under the selected storage filename. The check runs after serialization.
   WordCraft and GridCraft adapters still hardcode `false`. Bind the opened
   editor document identity and refuse replacement/Save As before serialization.
2. **MAJOR — ONLYOFFICE acceptance gate remains open.** The configured API script
   returned 404 and no editor initialized. Current-route edit/save/version/reopen
   remains **INCONCLUSIVE / NOT VERIFIED**. This review establishes no causal
   connection to ArtCraft.

## Prior findings

- R3 missing-name bypass: **CLOSED by source inspection**; missing or
  non-string names are rejected.
- R3 dirty-state MINOR: **CLOSED by source inspection**; rejection advances the
  revision and latches dirty state through clean events, and a successful retry
  can clear the latch.
- Static-index confinement: **CLOSED by source inspection** for the reported
  stationary symlink escape; runtime behavior remains unverified.
- Dispatcher mismatch: **CLOSED by source inspection**; expected map matches
  the five tracked routes and candidate checks are correctly scoped to GR-055–058.
- No additional code/security findings were identified.

The review noted that actual GridCraft behavior, same-name replacement,
pre-serialization refusal and rejection while another save is outstanding are
not established. No tests were run. The prior draft edit to the protocol-test
source was reverted; the test file is unchanged in the current candidate.
