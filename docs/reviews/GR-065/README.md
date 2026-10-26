# GR-065 evidence — DesignCraft on synthetic Seafile

This bundle records DesignCraft opening `synthetic.designcraft` from the
synthetic Seafile file list, saving the edit through the host protocol, and
reopening it from the file list in a new editor session.

## Evidence

- [`runtime/save-confirmation.png`](runtime/save-confirmation.png) — edited
  text, clean editor status, and host `Saved — new version …` confirmation.
- [`runtime/fresh-session-reopen.png`](runtime/fresh-session-reopen.png) — the
  saved text in the editor opened from the Seafile list after leaving the first
  editor.
- [`runtime/seafile-file-list.png`](runtime/seafile-file-list.png) — the
  synthetic library listing the test document.
- [`runtime/browser-observations.txt`](runtime/browser-observations.txt) —
  sanitized observed sequence and HTTP statuses. Session capabilities,
  private origin, repository identifier, and account identity are omitted.
- [`hash-inventory.json`](hash-inventory.json) and
  [`verify_candidate.py`](verify_candidate.py) — exact candidate membership,
  file sizes/hashes, index references, and per-file SRI checks.
- [`SHA256SUMS`](SHA256SUMS) — digests for the retained screenshots and
  sanitized observations.

The exact GR-045 candidate was reused, not rebuilt. The verifier was run
against both the staged candidate and the active static root. Seafile history
was inspected in its UI; no screenshot of that panel is retained because it
displayed the account name. The browser save payload was not separately
captured and hashed against stored bytes.

The test-only same-tab popup adjustment, single-library scope, unchanged
ONLYOFFICE configuration, and unverified boundaries are described in the
[GR-065 report](../../GR-065-DESIGNCRAFT-REAL-SEAFILE-ROUNDTRIP.md). This is
not a project-level GPT PASS or upstream authorization.

Independent R1 returned a bounded PROVISIONAL PASS with no findings requiring
remediation. The reviewer did not access services or replay the browser; the
runtime sequence remains implementer-reported. See
[`INDEPENDENT-REVIEW-R1.md`](INDEPENDENT-REVIEW-R1.md).
