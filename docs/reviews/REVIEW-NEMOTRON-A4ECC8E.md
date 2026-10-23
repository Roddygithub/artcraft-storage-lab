# Independent Nemotron review of `a4ecc8e`

Date: 2026-10-23  
Reviewer: `nvidia/nvidia/nemotron-3-ultra-550b-a55b`, medium effort  
Candidate reviewed: `a4ecc8e1d0da44a12f7bd9c4e529ed4accdb4a0e`  
Result: **FAIL for GPT-candidate readiness**

This was a read-only adversarial review of the runtime evidence added after the
GPT-6.1 Sol FAIL on `0edbe524b4fa321b0f73f8601afef390e7f785e6`. It did not modify
the repository. Nemotron agreed that the isolated synthetic DOCX flow now
established a real Seahub click, WordCraft edit, committed Seafile version and
semantic editor reopen. It also agreed that the route-token mismatch had been
corrected and runtime-tested in the C fileserver hook.

## Findings

### Blocker

- **ONLYOFFICE regression remains unverified.** The test stack did not contain
  ONLYOFFICE. The per-library routing patch therefore has not shown that files
  outside the ArtCraft allowlist still open, edit, save, version and reopen in
  ONLYOFFICE.

### Major

- **Separate-origin security topology remains unverified.** The E2E used a
  same-origin loopback proxy, which does not exercise the intended Seahub to
  gateway origin boundary, cookies, CSP, CSRF or proxy trust.
- **Permission revocation, read-only access, expiry and replay were not exercised
  against the live patched Seahub endpoint.**
- **The simultaneous conditional-save test used direct synthetic Seahub calls,
  not two real editors saving at once.** The stale-session test was sequential.
- **External writer races and crash/network windows were not tested.**
- **GridCraft and VectorCraft durable semantic round trips remain unverified;**
  this DOCX evidence does not cover them.
- **Public deployment controls and licensing/distribution packaging remain
  incomplete or unverified.**

### Minor

- The reviewer considered the new isolated DOCX evidence a genuine advance and
  accepted the specific route-token correction, while keeping the broader
  candidate at FAIL.

## Follow-up after this review

After Nemotron reviewed the exact SHA above, two real WordCraft sessions were
opened from the synthetic Seahub route, edited independently, and sent Ctrl+S
concurrently. One committed a new version; the other received HTTP 409 and
remained dirty. A fresh click/reopen rendered the winner, and Seafile content
readback contained the winner's phrase but not the losing phrase. This addresses
the direct-call-only concurrency gap for two separate editor sessions. It does
not test overlapping save tickets within one editor or the other findings
above. Evidence: `docs/reviews/GR-015/ISOLATED-RUNTIME-E2E-20261023.md` and
`docs/reviews/GR-015/concurrent-editor-save-reopen.png`.

This review is not a GPT-6.1 Sol verdict and does not change the FAIL on the
reviewed Sol candidate. The current tip remains unfrozen and unreviewed by Sol;
public deployment is not ready and upstream publication remains locked.
