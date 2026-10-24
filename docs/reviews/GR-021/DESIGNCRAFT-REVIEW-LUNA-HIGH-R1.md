# GR-021 DesignCraft host-save review — round 1

**Verdict: FAIL (bounded prototype patch).** One P2 remains.

## Finding

The 64 MiB limit in `HostEventBuffer::enqueue` runs after the shared browser
transport has copied the incoming `ArrayBuffer` or `Uint8Array` to a Rust
`Vec`. The transport also converts arbitrary message strings before applying
field-specific length checks. Consequently, the app queue bounds retained
events but not the peak allocation for one oversized message.

The finding is addressed in the shared transport package by checking byte
lengths before `to_vec()` and checking UTF-16 code-unit lengths before Rust
string conversion. The package remediation has its own independent PASS in
[`TRANSPORT-PRECOPY-REVIEW.md`](TRANSPORT-PRECOPY-REVIEW.md). The DesignCraft
patch must be repinned to that package revision and reviewed again before
acceptance.

## Other areas checked

- No host-mode bypass was found for recovery-open, document replacement,
  document close, or Save As in the inspected patch.
- Engine acknowledgement applies the captured saved baseline and leaves later
  edits dirty; the pending ticket is matched before it is consumed.
- Native `.designcraft` bytes are opened pathless and are serialized/reopened
  by the focused engine tests.
- The transport checks exact origin and parent `event.source`; its dependency
  was pinned to the stated immutable revision.
- Graphics-loss recovery can still offer a browser “Save a Copy” download. It
  is an emergency recovery download and is not represented as a host save.

## Checks reported/reproduced

The reviewer independently ran:

- `cargo test -p designcraft-engine host_save --locked` — 2 passed.
- `cargo fmt --all -- --check` — passed.
- `git diff --check 80d13911b2d20fbb5cd9398696627bb3a715417b` — passed.
- `cargo test -p designcraft-ui-egui host_save --locked` — incomplete because
  dependency compilation hit the `/tmp` quota; the UI test did not run.

The app WASM check was consequently not reached in the review. The author
subsequently reported five focused engine/UI tests and a locked WASM check
passing on the same source patch; these results do not override the reviewer’s
resource-boundary finding or constitute browser execution.

**Browser messaging, Seafile version persistence, and fresh editor reopen are
NOT VERIFIED.** No production service or upstream repository was changed.
