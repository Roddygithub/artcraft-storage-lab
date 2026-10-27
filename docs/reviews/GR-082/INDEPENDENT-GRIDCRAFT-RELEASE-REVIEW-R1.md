# GridCraft v0.12.1 release evidence review R1

**Verdict: bounded PROVISIONAL PASS with one LOW documentation finding.** The
review was read-only; no tests, builds, browser, network, or service operations
were performed.

- Exact source HEAD and tag are `f86aec12dabc744b5f75e1033f87bfe685e78481`;
  the source diff matches the archived patch and its SHA-256.
- The release log records the corrected Cargo PATH, Rust 1.95, Trunk 0.22,
  locked release build and exit 0. The bundle and actual served static files
  match all four recorded sizes and hashes. R4's pre/post hashes cover the
  served directory and its test-source hash matches the current harness.
- The harness supports active-cell Ctrl+S serialization containing the marker,
  one synthetic memory version, matching identity/ticket clean acknowledgement,
  and fresh-session open with a second backend read. It does not establish
  rendered marker text after reopen.
- Synthetic storage boundaries and the unverified Seafile, replacement/Save As,
  refused-action serializer-count, production and ONLYOFFICE gates remain
  explicit.

**LOW finding:** the queue said “final pre-push review is pending” next to R4's
completed branch-only pre-push PASS. Clarify which remaining review was pending.

The GridCraft smoke does not establish Seafile persistence, replacement refusal,
production acceptance, or live ONLYOFFICE health.
