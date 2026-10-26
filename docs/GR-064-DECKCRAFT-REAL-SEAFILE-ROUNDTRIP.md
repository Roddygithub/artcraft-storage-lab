# GR-064 — DeckCraft on the synthetic Seafile library

Date: 2026-10-26
Status: **GPT REVIEW PENDING**

## Result

The exact DeckCraft host-save candidate completed the real synthetic Seafile
flow:

1. Added the 4,700-byte GR-044 synthetic PPTX fixture through Seafile's file
   list for setup.
2. Opened `synthetic.pptx` from that list in the patched DeckCraft Web WASM.
3. Replaced its visible slide text with `GR-064 DeckCraft Seafile edit`.
   DeckCraft showed unsaved state before Ctrl+S.
4. Pressed Ctrl+S. The host showed `Saved — new version …`; DeckCraft showed
   `Saved to file host`, and the editor returned to its clean state. The
   gateway `/open/`, document GET, and save POST returned HTTP 200.
5. Seafile history showed the setup `Added` event followed by `Modified
   "synthetic.pptx"` from the editor save.
6. Navigated away from the editor, returned through the Seafile file list, and
   opened the PPTX again. A fresh DeckCraft session displayed the edited text
   with no changes pending.

No browser download or manual upload of edited bytes was used. The retained
parent protocol handled save acknowledgement; unlike GR-063's VectorCraft
export route, DeckCraft returned to a clean native state after ACK.

## Candidate and scoped route

- Source: `storytold/deckcraft` `0f4fffcf6c71ffa16029d07ac23752fedd783547`.
- Host-save patch: GR-020 patch SHA-256
  `8d7f98468ce446add5357e10ed8e10e729eb3306fee359d320f09805acc3ee4a`.
- Shared transport pin: `56c5e16d79b77751106173c13111ef4fe0a2c0ec`.
- Candidate bundle SHA-256, size, and file membership are recorded in
  [`hash-inventory.json`](reviews/GR-064/hash-inventory.json). The same four
  bytes are staged in the active static root and in the review candidate cache.
- The `pptx` dispatcher and extension were added only to the existing
  one-library ArtCraft allowlist. DOCX, XLSX, PDF, and SVG routes were retained.
  A private rollback copy of the prior gateway dispatch and current Seahub
  settings is outside Git.
- `ENABLE_ONLYOFFICE=True` remained set. The ONLYOFFICE-prefixed settings were
  byte-for-byte equivalent at the parsed-assignment level before and after the
  change. A synthetic DOCX in the separate out-of-allowlist `OnlyOffice`
  library opened in ONLYOFFICE's read-only Community view. No edit or save was
  attempted there.

## Limits

- The T3 preview did not expose Seafile's `window.open` popup as a controllable
  tab. For the test file only, the preview page redirected that popup to the
  same tab; the actual Seafile file-list click and third-party-editor handoff
  still ran. This harness adjustment is recorded to avoid implying an
  unmodified popup lifecycle.
- This is one synthetic PPTX on one private Seafile instance. It does not prove
  broad PowerPoint compatibility, production readiness, or security under
  other deployment topologies.
- ONLYOFFICE received an open-only check after this route update. An
  ONLYOFFICE edit/save/version regression was not run.
- Build optimization evidence is inherited from the exact GR-044 candidate;
  this work item did not rebuild the 30.6 MB WASM.
- Independent reviews R1–R4 returned bounded PROVISIONAL PASS; all wording and
  verifier findings were corrected. Project GPT remains **INCOMPLETE** and
  upstream publication remains **LOCKED**.

See [`docs/reviews/GR-064/`](reviews/GR-064/README.md) for screenshots,
sanitized observations, hashes, and the candidate verifier.
