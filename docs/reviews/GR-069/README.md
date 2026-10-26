# GR-069 evidence bundle

This bundle records a real browser open/edit/save/new-version/fresh-session
reopen using the existing synthetic Seafile library and the exact GR-048
FigCraft WASM candidate. It is not a project-level GPT verdict.

## Contents

- `candidate-inventory.json` and `verify_candidate.py`: exact three-file
  candidate identity and a runnable build/stage/active-root verifier.
- `runtime/browser-observations.txt`: sanitized runtime chronology, including
  the failed first attempt and successful retry.
- `runtime/save-confirmation.png`: visible rectangle, clean editor, Seafile
  confirmation and returned version identifier.
- `runtime/fresh-reopen.png`: rectangle visible in the fresh Seafile-opened
  editor session.
- `INDEPENDENT-REVIEW-R1.md`: bounded read-only review result.
- `SHA256SUMS`: hashes of the retained bundle artifacts (excluding itself).

The setup fixture was uploaded through Seafile before editing. No edited output
was downloaded or manually uploaded. The Seafile route and allowlist were
temporary and restored after the run. The account/library identifiers and
session capabilities are omitted.

## Independent review boundary

Review the recorded evidence and candidate verifier only. Do not access the
Seafile service or replay the browser. Confirm the distinction between the
failed first save and the successful retry, the test-only same-tab popup shim,
the returned new-version identifier, and the fresh reopen. Exact save-message /
readback byte identity, explicit in-app close, and a post-change ONLYOFFICE
edit/save regression remain **NOT VERIFIED**. Project status must remain
**INCOMPLETE** and upstream publication **LOCKED**.

R1 returned a bounded PROVISIONAL PASS with no findings. This does not grant
project GPT PASS or upstream authorization.
