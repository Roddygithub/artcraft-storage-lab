# GR-040 independent evidence review — round 1

**Verdict: PROVISIONAL ACCEPT, bounded to the synthetic ONLYOFFICE evidence.**
No blocker or major finding. Three minor limitations remain. This is not a
project-level GPT verdict or production-readiness approval.

## Verified by the reviewer

- The five retained evidence-file checksums match `runtime/SHA256SUMS`.
- The report, README, status, matrix row 6.3, transcript and JSON agree on two
  browser edits, two HTTP-200 callbacks, history growth 3→5, final DOCX
  readback and fresh route/file-list reopen.
- The screenshots are consistent with the described saved state and reopen
  steps. The bundle correctly identifies the patched synthetic Seahub and
  C-fileserver revisions and the ONLYOFFICE image/version.
- The bounded claim is supported: the existing Seafile → ONLYOFFICE route
  preserved the two edits in this synthetic DOCX flow.

## Minor limitations

1. The synthetic Document Server container and its test-only environment
   configuration remain active. The runtime transcript discloses this; it is
   not a validity defect, but the test environment was not fully torn down.
2. The browser-to-callback DOCX payload was not separately hashed. This is
   explicitly recorded in the JSON and transcript, so exact byte provenance is
   not claimed.
3. The successful callback required a loopback host mapping and a `socat`
   relay in the synthetic test network. The initial failed callbacks and the
   workaround are recorded; this does not establish deployment topology.

## Not verified

Production/deployed ONLYOFFICE, TLS/proxy/CSP/CSRF and adversarial-frame
security, other file types or Document Server versions, callback-payload byte
identity, and project-wide GPT REVIEW PASS remain NOT VERIFIED.

Read-only review. The reviewer did not replay the historical browser run or
access services. This assessment applies to the retained evidence, not to
production or the overall project.
