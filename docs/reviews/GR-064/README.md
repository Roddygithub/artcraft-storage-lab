# GR-064 evidence — DeckCraft on synthetic Seafile

This bundle records the actual DeckCraft Web host-save flow on one synthetic
PPTX in the existing synthetic Seafile library. It supports file-list open,
visible edit, acknowledged save/new history event, and fresh file-list reopen.

## Evidence

- [`runtime/deckcraft-save-confirmed.png`](runtime/deckcraft-save-confirmed.png) — edited slide, clean state, and the host's `Saved — new version …` confirmation. DeckCraft's `Saved to file host` message is recorded in `runtime/browser-observations.txt`.
- [`runtime/deckcraft-fresh-reopen.png`](runtime/deckcraft-fresh-reopen.png) — new editor session showing the saved text and no pending changes.
- [`runtime/onlyoffice-open-only.png`](runtime/onlyoffice-open-only.png) — out-of-allowlist synthetic DOCX open in ONLYOFFICE; no edit/save.
- [`runtime/browser-observations.txt`](runtime/browser-observations.txt) — sanitized event sequence, routes/statuses, history, and boundaries.
- [`hash-inventory.json`](hash-inventory.json) and [`verify_candidate.py`](verify_candidate.py) — candidate file membership, size, digest, index references, and per-`href` SRI verification (each integrity value is checked against its specifically referenced file).
- [`SHA256SUMS`](SHA256SUMS) — retained screenshot digests.

The four candidate files were also checked against the exact GR-044 inventory
and static-root deployment copy. The reusable candidate was not rebuilt in
GR-064. Source and transport provenance: DeckCraft base
`0f4fffcf6c71ffa16029d07ac23752fedd783547`, GR-020 patch SHA-256
`8d7f98468ce446add5357e10ed8e10e729eb3306fee359d320f09805acc3ee4a`, and
`craft-platform` revision `56c5e16d79b77751106173c13111ef4fe0a2c0ec`.

The test-only `window.open` same-tab adjustment is disclosed in the report.
The test stayed within the synthetic library. No production files were opened
or changed. ONLYOFFICE settings were preserved; only open behavior, not
edit/save, was checked after this route change. Seafile behavior outside this
synthetic instance and deployment/security readiness remain **NOT VERIFIED**.

Independent R1–R4 returned bounded PROVISIONAL PASS. All review findings were
remediated; see `INDEPENDENT-REVIEW-R1.md` through `R4.md`. The screenshot
caption describes only visible content; DeckCraft's toast is attributed in
the sanitized observation transcript.
This evidence is not a project-level GPT PASS or upstream publication
authorization.
