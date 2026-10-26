# GR-071 evidence — dispatched app candidate provenance recheck

The read-only check validates the four source-pinned app candidate bundles
against one local static root and confirms the tracked dispatch JSON maps the
four supported extensions to those apps. It reuses the GR-055–058 verifiers;
there are no new dependencies or builds.

## Files

- [`checks.txt`](checks.txt) — command, output, and exact root.
- [`SHA256SUMS`](SHA256SUMS) — hashes of the retained GR-071 evidence files.
- [`INDEPENDENT-REVIEW-R1.md`](INDEPENDENT-REVIEW-R1.md),
  [`INDEPENDENT-REVIEW-R2.md`](INDEPENDENT-REVIEW-R2.md), and
  [`INDEPENDENT-REVIEW-R3.md`](INDEPENDENT-REVIEW-R3.md) — review results and
  remediation history.
- [`docs/GR-071-DISPATCHED-CANDIDATE-PROVENANCE.md`](../../GR-071-DISPATCHED-CANDIDATE-PROVENANCE.md) — finding and limits.
- [`scripts/verify-dispatched-candidates.sh`](../../../scripts/verify-dispatched-candidates.sh) — runnable read-only check.

## Review boundary

Review the script, command log, report, and referenced per-app manifests.
Do not access services, replay the browser, copy/promote assets, or change
dispatch. The test root is not claimed to be a production or currently running
service root. The old GR-054 `integration/static` observation is not replaced.
Independent R1–R2 reviews found and tracked bounded documentation findings; their
remediations are recorded in `INDEPENDENT-REVIEW-R1.md` and
`INDEPENDENT-REVIEW-R2.md`. R2 requested a final check of the GR-054 README
wording; R3 confirmed it corrected the contradiction and found no remaining
findings. All three reviews are bounded PROVISIONAL reviews, not project GPT
approval. Project GPT remains **INCOMPLETE** and upstream publication remains
**LOCKED**.
