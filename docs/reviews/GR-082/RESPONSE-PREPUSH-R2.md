# Response to GR-082 pre-push review R2

**Disposition: the MEDIUM and both LOW findings are addressed locally; R3
independent recheck pending. No commit or push yet.**

1. **Run provenance (MEDIUM):** after adding clipboard clearing before copy, the
   WordCraft actual-WASM smoke passed as R8 (historical). Its retained log records the exact
   test-source SHA-256 (`0a532c59da6d73baf839996c5c3fef955f21d8989e650d6a13df005f70536e09`)
   and the four JS/WASM/index/icon asset SHA-256 values before and after the
   run; each pair is unchanged and matches the bundle manifest. The assertion
   confirms copied text from the freshly reopened editor contains the marker.
2. **Publication wording (LOW):** the main report and port manifest now scope
   the lock to upstream publication/promotion; candidate branch pushes to this
   project's own origin are allowed after checks and independent review, without
   a PR or merge.
3. **Stale evidence link (LOW):** the WordCraft port manifest and bundle
   manifest initially pointed to R8; after R3, R9 supersedes it as the final
evidence. Earlier runs remain available as
   historical diagnostics and are not labelled as final evidence.

No Seafile history/readback/reopen evidence is claimed. Route promotion, merge,
upstream issues/PRs/RFCs, and project GPT PASS remain gated.
