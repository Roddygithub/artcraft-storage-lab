# GR-081 independent code/security review R3

**Verdict: PROVISIONAL FAIL for full remediation.** Read-only source review; no
files changed, tests/builds run, services accessed, or browser used.

## Findings

1. **MAJOR — Filename equality does not establish document identity.** A
   replacement or Save As that emits the selected filename with `saveAs=false`
   still reaches storage. Missing/non-string names also previously defaulted to
   the selected filename. The host checks after serialization, so it cannot
   enforce pre-serialization refusal. Editor-side protection remains **NOT
   VERIFIED**. Evidence: `integration/gateway/hostpage.py` save handler and the
   WordCraft/GridCraft adapter patches under `docs/reviews/GR-016/patches/`.
2. **MINOR — Rejection did not latch unsaved state.** A later editor
   `dirty=false` could clear the warning because rejection did not advance the
   revision. Actual editor event sequences are **NOT VERIFIED**.

The review judged the static-index final realpath check and five-route verifier
fix correct by inspection. Normal exact-name saves showed no apparent source
regression. ONLYOFFICE's 404 remains inconclusive.

## Response

The host now refuses WordCraft/GridCraft save events with missing or changed
names. Rejection increments `dirtyRevision`, sets `rejectedSaveRevision`, and
keeps host dirty state through later `dirty=false` events until a successful
retry at or beyond that revision. The existing protocol test was updated to
cover changed/missing names and the dirty latch, but **was not run**. This
addresses the review's missing-name and dirty-latch findings at source level.

The identity MAJOR remains open: a same-name replacement with `saveAs=false`
is still indistinguishable, and serialization has already happened before the
host sees the event. App-side pre-serialization refusal is **NOT VERIFIED**.
The change is therefore partial, not a full resolution.
