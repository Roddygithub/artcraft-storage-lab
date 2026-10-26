# GR-081 independent docs/evidence review R3

**Verdict: PROVISIONAL FAIL — documentation/evidence remediation required.**
Read-only review; no edits, tests, builds, browser or service access.

## Findings and responses

1. **MAJOR — Origin guidance conflicted.** `docs/ARTCRAFT-GLOBAL-INTEGRATION.md`
   described `/open/` as a same-origin POST. The diagram now calls it a
   cross-origin form POST from Seahub, with gateway and Craft sharing an origin
   distinct from Seahub.
2. **MINOR — GR-069 checksum was stale.** After the inventory was finalized,
   `docs/reviews/GR-069/SHA256SUMS` was updated. Current inventory digest:
   `75f150232d5b1720bbfb7045e83dfb5ed4e3fa80235fb16ab954e877f9ca213d`.
3. **MINOR — Screenshot qualifications were missing from summaries.** The
   global overview now labels GR-078 PhotoCraft save/reopen operator-recorded
   and says the retained images are reused GR-076 captures showing Layer 1/2.
   The combined replay matrix result is `[~]` because that portion is
   evidence-limited.

The reviewer confirmed all ten GR-078 screenshot hashes match the manifest,
including the disclosed reuse. Save As/replacement identity and ONLYOFFICE
remain open. No new secrets or PII were identified; reviewed local links
resolved.
