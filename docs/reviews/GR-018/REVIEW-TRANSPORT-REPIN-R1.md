# CADCraft GR-018 shared-transport re-pin review

**Result:** PROVISIONAL PASS for the exact repinned patch. No blocker or major
regression found. This is not a new overall project verdict.

| Check | Result |
|---|---|
| CADCraft base | `7bf5905ac97316a7896de8cbc12d243f57b09bd8` — matched |
| Exact binary patch SHA-256 | `38d1e6943107a68d2a0fb20e82fbab14297b2c50487de9387cc03fdb7ed066d7` — matched |
| `craft-platform` pin | `56c5e16d79b77751106173c13111ef4fe0a2c0ec` in manifest and lockfile |
| Patch/worktree identity | generated diff matched stored patch byte-for-byte |
| Independent rebuild/tests | not rerun |

The repin review found no change to the host-save correctness paths: browser
monotonic timing, late/duplicate ACK rejection, earliest-deadline repaint,
SaveAs destination handling, export completion feedback, and request-specific
timeout messages remain. The pinned transport retains same-origin/parent-source
checks and listener cleanup.

Implementer-reported after the repin: 3 focused engine acknowledgement tests,
Rust 1.95 locked WASM check, formatting, diff and reverse-apply checks pass.
The pre-existing Sol low round-4 review and runtime reports remain referenced in
[`README.md`](README.md). Browser and Seafile behavior are not newly covered by
this dependency-only re-pin review.
