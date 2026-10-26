# GR-064 independent review — R1

**Verdict:** PROVISIONAL bounded PASS, with two MINOR findings. This was not a
project-level GPT verdict. The review did not repeat browser/service workflows.

## Findings and remediation

1. **Save confirmations were attributed to the wrong component.** The report
   and sanitized browser observations reversed the host message
   `Saved — new version …` and DeckCraft message `Saved to file host`. Both
   records now attribute them correctly.
2. **The candidate verifier did not bind each SRI to its referenced asset.**
   It accepted a digest if it matched any candidate file. The verifier now
   parses `href`/`integrity` pairs, rejects duplicate or mismatched
   associations, requires every manifested index reference to have its own
   SRI, and hashes each referenced file against that exact value. The manifest
   records the path/value pairs explicitly.

The reviewer also noted that active deployment identity, history, and the
post-change ONLYOFFICE edit/save behavior were not independently established
in that read-only review. Those limits remain disclosed; no new live-service
claims are made here.
