# GPT-6.1 Sol low — GR-018 bounded review, round 2

**Verdict:** changes requested for the bounded prototype. No blocker; one major
and two minor findings. This was not a project-level GPT verdict and grants no
upstream approval.

## Findings

1. **MAJOR — timeout cleanup could be extended by another five minutes.**
   `Bridge::expire_stale_saves` scheduled a fresh 300-second repaint instead of
   the remaining time to the earliest ticket deadline. A frame before expiry
   could schedule another full interval. The current patch computes the minimum
   remaining time from absolute request deadlines.
2. **MINOR — export success had no completion feedback.** Export tickets had no
   engine drawing entry, so the ACK was silently ignored. The current patch
   retains request filename/type metadata and reports successful export
   completion without changing drawing dirty state.
3. **MINOR — stale ACK followed by undo could remain falsely dirty.** The prior
   code created a new `Arc` baseline even when no version normalization was
   needed. The current patch preserves the acknowledged snapshot `Arc` and adds
   `undo_to_a_successfully_saved_snapshot_restores_clean_state`.

## Other reviewed areas

The reviewer found prior findings resolved by source inspection: wasm
`Instant::now()` use removed, stale SaveAs destination retained, expiry checked
at acknowledgement receipt, exports tracked, result queue admission restricted
to outstanding tickets, and startup failure sent through `cadcraft:failed`.
Same-origin and parent-source validation are delegated to GR-016 transport.

The absolute `/tmp/artcraft-gr016-craft-libs` dependency remains a
reproducibility and publication gate; the reviewer considered it compatible
with the explicitly local prototype scope, not a blocker for that scope.

## Reviewer-reproduced commands

- `cargo +1.95.0 fmt --all -- --check`: PASS
- `git diff --check`: PASS
- Rust 1.95 wasm32 `cadcraft-web` check: PASS, existing UI dead-code warnings
- Focused acknowledgement tests: 7 passed
- Full engine library suite: 343 passed

Browser timeout behavior, browser save/reopen, and Seafile persistence were not
verified. The working patch has since been updated to address all three
findings; round 3 re-review is recorded separately.
