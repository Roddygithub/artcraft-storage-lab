# GPT-6.1 Sol Low — bounded GR-016 remediation review

Date: 2026-10-24
Scope: GridCraft in-app Open, Rust MSRV correction, and adjacent shared
transport acknowledgement handling.
Result: **PROVISIONAL PASS**, limited to this remediation; not a project GPT
verdict.

## Review result

**PASS**

### Blocker

- None.

### Major

- None. Sol confirmed both prior GridCraft MAJOR findings were fixed.

### Minor

- GridCraft open-request send failures remain log-only in
  `apps/gridcraft-web/src/host.rs:44–48`; WordCraft ignores them at
  `apps/wordcraft-web/src/host.rs:56–58`.
- GridCraft reports pending-table exhaustion as “duplicate save ticket” at
  `apps/gridcraft-web/src/host.rs:101–104`.
- WordCraft's parent-facing dirty flag excludes unconfirmed saves at
  `crates/ui-egui/src/lib.rs:2263–2266`. Existing save/close guards track
  pending saves separately; Sol considered this retained behavior, not a
  regression from the transport refactor.

## Evidence reviewed

- Confirmed all three scratch checkout SHAs match the GR-016 README pins and
  each preserved patch matches the current scratch `git diff`.
- Traced GridCraft File > Open through `backstage.rs:565–567`,
  `SheetApp::open_dialog` at `lib.rs:782–784`, the overridden `open_async` at
  `host.rs:44–45`, shared `post_open_request` at
  `crates/platform/src/browser/host.rs:97–98`, then the parent response through
  GridCraft's inbox at `host.rs:116–118` and `lib.rs:1234–1255`.
- Verified `PendingSaves` limits outstanding entries to 64 and removes each
  ticket once (`crates/platform/src/host_protocol.rs:33–44`). GridCraft consumes
  only matching tickets before queueing results (`host.rs:120–124`), so unknown
  or duplicate acknowledgements cannot grow its result queue.
- Verified save-post failure removes pending state and reaches the app message
  (`host.rs:54–57, 87–88, 105–107`). Successful acknowledgement retains the
  document UID/snapshot association (`host.rs:78–81`; engine `lib.rs:344–352`),
  so edits made after a save snapshot stay dirty.
- Verified the shared transport checks exact origin and parent source
  (`browser/host.rs:45–48`) and removes listeners on drop (`142–146`).
- `cargo test -p craft-platform --offline`: PASS, 6 tests.
- `cargo +1.95.0 check -p gridcraft-web --target wasm32-unknown-unknown
  --locked --offline`: PASS, with the existing `Modified` dead-code warning.
  GridCraft and craft-libs both declare Rust 1.95.
- The reviewer did not independently rerun the browser test. It inspected the
  supplied browser evidence. No Seafile E2E, cross-origin deployment, or
  remaining-app completion is claimed.

## Test gaps

- A focused GridCraft snapshot test was started but stopped during compilation
  to bound review time; no result is claimed.
- Wrong-source messages, listener teardown, concurrent/out-of-order saves,
  response loss, and injected send failures lack runtime verification.
- Rust 1.95 verification covers the WASM target, not every workspace target.

## Review task

T3 delegated review `artcraft-gr016-gridcraft-sol-low-review-20261024-r3`,
model `gpt-6.1-sol`, reasoning effort `low`. The separate Nemotron review lane
was interrupted without a result to control delay and token use; its
interruption is recorded in `docs/AI-ROUTING.md`.
