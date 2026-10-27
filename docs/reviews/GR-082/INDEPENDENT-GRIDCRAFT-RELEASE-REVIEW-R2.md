# GridCraft v0.12.1 release evidence review R2

**Verdict: bounded PROVISIONAL PASS. No new findings.** Read-only review; no
edits, tests, builds, browser, network, or service operations.

- R1 LOW is closed: the queue distinguishes completed pre-push R4 from the
  separate GridCraft release-evidence R1.
- Optimizer wording is bounded: source enables `data-wasm-opt="z"`; the build
  log records wasm-opt version 131 and exit 0, while the exact invocation is
  not retained.
- Exact HEAD/tag, patch digest, test-source digest, and all release/served asset
  hashes match their recorded values.
- The smoke supports active-cell Ctrl+S, one synthetic memory version,
  matching identity/ticket clean acknowledgement, and fresh-session open. It
  does not establish rendered marker text after reopen.

Seafile persistence, replacement/Save As serializer counts, production
acceptance, and live ONLYOFFICE health remain outside this verdict.
