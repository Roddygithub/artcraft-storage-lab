# Independent FilmCraft host-save patch review — round 2

**Result:** PROVISIONAL PASS for the bounded source patch; no blocker or major
finding. No overall project verdict or upstream approval.

| Check | Result |
|---|---|
| Upstream base | `fa550ce2d07bdfee6b1d7b6835e8abc8c6913d00` — matched |
| Exact binary diff SHA-256 | `16158f500b2ec12f93c8fcb14867e0b452030dbb338b2d4d7fa8612850a694d4` — matched |
| Manifest and lock transport pin | `56c5e16d79b77751106173c13111ef4fe0a2c0ec` — matched |
| Final guard delta | Engine host-mode `file.closeProject` refusal and its regression assertion only |
| Test/build rerun by reviewer | None; author-reported engine/UI tests, WASM check and fmt pass after final change |

Prior findings are closed in source: engine/UI guards refuse template project
creation, close-all, save-as-template and single-project close bypasses; Save
All, shortcut and control paths route through host save. Only the ticket-matched
ACK updates the saved baseline; unknown/duplicate results are ignored, negative
ACK retains dirty state, and timeout leaves the request pending as unknown. The
pinned transport validates exact origin and parent window source, and malformed
`ok` values do not become failed ACKs.

The reviewer confirmed patch identity, pin and source changes with `git diff
--check`; no build or test was rerun. Browser postMessage, durable Seafile
version creation, authorization and fresh-storage reopen remain **NOT
VERIFIED**.
