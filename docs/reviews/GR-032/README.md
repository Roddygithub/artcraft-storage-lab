# GR-032 evidence bundle — PhotoCraft host save

**Review state:** R1 findings were remediated. Independent R2/R3 returned **PROVISIONAL PASS** for this bounded source prototype. This is not a browser/Seafile MVP or a project GPT pass.

## Immutable inputs and patch

| Item | Value |
|---|---|
| Repository | `storytold/photocraft` |
| Exact base SHA | `a02f2ee41059d3312e7ff24a5af5edcac7b6435a` |
| Applied prerequisite | GR-026 `photocraft-core-slice-r2.patch` (SHA-256 `4ca7ea1e88bf215f80e6edc137417b8b21d0302e82b9a7a496ffd4e60b0cd3e4`) |
| Shared transport dependency | `craft-platform` exact rev `56c5e16d79b77751106173c13111ef4fe0a2c0ec` |
| Combined patch from the exact source SHA | [`photocraft-host-save.patch`](photocraft-host-save.patch) |
| Patch SHA-256 | `487935d8f6db33cf82c85f8d9c8aa0686016612510f15cf34f6b3f05a2c53fe7` |
| Scratch checkout | `/home/roddy/.cache/artcraft-storage-lab/photocraft-audit` (detached, no commit/push) |

The combined patch includes the accepted GR-026 core slice plus the GR-032 UI/Web adapter. To reproduce from the clean base, apply only this combined patch; do not apply the GR-026 prerequisite separately first.

## Independent review R1 and remediation

| Finding | Remediation | Evidence / remaining limit |
|---|---|---|
| The listener enqueued every parsed `SaveResult` into an unbounded `Vec` before the UI checked its ticket. Unknown/duplicate replies could grow memory and fill ahead of a valid ACK. | Replaced the vector with fixed `open` and `save_result` slots. Enqueue accepts only the first Open and a SaveResult matching the current outstanding ticket; a queued valid result cannot be overwritten. | `apps/photocraft-web/src/host_inbox.rs:4-29`; flood/duplicate regression passes. One Open payload remains bounded by the transport's existing 256 MiB admission cap; ACK error text is transport-bounded. |
| Listener registration errors were swallowed with `.ok()`, while startup still posted `ready`. | Listener errors propagate from the app creator as a startup error, so the `post_ready` call is reached only after listener success. | `apps/photocraft-web/src/web.rs:100-140`; helper propagation test passes. Actual browser startup-failure rendering was not exercised. |

Independent R2 confirmed the corrected exact patch includes the new module, applies to a clean checkout at the pinned base, and filters unknown/duplicate ACKs before enqueue. R3 confirmed the size/memory limitation below is accurately documented. Both verdicts are bounded and provisional; neither establishes browser or Seafile behavior.

## R2 implementation limit

The gateway defaults `ARTCRAFT_MAX_BYTES` to 50 MiB (`integration/gateway/server.py:98`). PhotoCraft serializes its snapshot before the transport handoff (`crates/ui-egui/src/lib.rs:1037-1044`), so a larger `.pcraft` can allocate its full serialized payload before rejection. Negative ACK keeps the document dirty, but there is no pre-serialization memory bound or verified size compatibility for large documents. This is documented as a limit; no implementation change was made in this remediation.

## Scope and review request

The patch adds the Rust-only `?host=parent` Web adapter for one pathless `.pcraft` document. Review the complete patch, paying particular attention to:

1. Whether all Web Save entry points reach `save_host_snapshot`, whether the transport sends the exact serialized snapshot under `craft-platform`'s same-origin/source checks, and whether only the matching durable positive ticket advances the saved baseline.
2. Negative, duplicate, unknown, late and missing ACK behavior, including the 30-second unknown-outcome lockout and retry/close refusal.
3. One-document enforcement through initial pathless Open, direct UI/app commands, action playback, menu and picker/drop routes, Save As/Save a Copy, Revert and close routes.
4. Whether standalone browser downloads and native filesystem writes remain unchanged outside `host_mode`.
5. Missing tests, route bypasses, data-loss or licensing concerns. The reviewer must not have authored this patch; record the independent report and remediation here.

## Source evidence

| Claim | Evidence in the patched PhotoCraft source |
|---|---|
| Pathless open does not set a save path or recent entry | `crates/ui-egui/src/file_open.rs:95-103`; GR-026 core regression in `crates/ui-egui/src/file_open/tests.rs` |
| Exact open-incarnation snapshot ACK primitive | `crates/engine/src/lib.rs:261-284, 618-629` |
| Host Save captures and retains the snapshot until ticket result | `crates/ui-egui/src/lib.rs:1026-1082` |
| Browser transport setup, bounded listener inbox, ready, save handoff and timeout | `apps/photocraft-web/src/web.rs:95-140, 400-414, 488-508, 549-558`; queue policy in `apps/photocraft-web/src/host_inbox.rs:4-36`; dependency and exact rev in Web `Cargo.toml` and `Cargo.lock` |
| Host route restrictions | `crates/ui-egui/src/menus.rs:67-80`, `lib.rs:1334-1337, 1742-1744`, `file_open.rs:95-110, 170-172`, `file_dialog.rs:262-264`, `discard_ui.rs:70-77` |
| Shared transport checks message origin/source and documents that `post_save` delivery is not durable confirmation | `craft-platform` exact rev `56c5e16d79b77751106173c13111ef4fe0a2c0ec`, `integration/rust/craft-platform/src/browser/host.rs:84-93, 158-175` |

## Commands and results

Run the patch check from a clean detached checkout at the exact base. Post-R2 test and WASM commands were run in the resulting applied-patch checkout using the configured global Cargo cache (no `/tmp` target or temp overrides):

```sh
git rev-parse HEAD
git -C /home/roddy/.cache/artcraft-storage-lab/photocraft-patch-check apply --check /home/roddy/Projects/artcraft-storage-lab/docs/reviews/GR-032/photocraft-host-save.patch
git -C /home/roddy/.cache/artcraft-storage-lab/photocraft-patch-check apply /home/roddy/Projects/artcraft-storage-lab/docs/reviews/GR-032/photocraft-host-save.patch
cargo +1.95.0 metadata --locked --no-deps --format-version 1
cargo +1.95.0 test --locked -p photocraft-ui-egui host_save_dispatch_waits_for_matching_durable_ack_and_guards_bypass_routes
cargo +1.95.0 test --locked -p photocraft-web host_inbox::tests::
cargo +1.95.0 check --locked -p photocraft-web --target wasm32-unknown-unknown
git diff --check
```

| Command | Result |
|---|---|
| `git rev-parse HEAD` | `a02f2ee41059d3312e7ff24a5af5edcac7b6435a` |
| Initial `cargo +1.95.0 check --locked -p photocraft-web --target wasm32-unknown-unknown` | Failed as expected before lockfile update: dependency required exact pinned `craft-platform` source entry |
| Unlocked locked-source resolution, `cargo +1.95.0 check -p photocraft-web --target wasm32-unknown-unknown` | Passed dependency resolution, compiled `craft-platform` at exact pinned rev and compiled the then-current adapter; later compile errors in that first run were fixed |
| `cargo +1.95.0 metadata --locked --no-deps --format-version 1` | PASS; metadata reports the pinned `craft-platform` Git rev and browser feature |
| `cargo +1.95.0 check --locked -p photocraft-web --target wasm32-unknown-unknown` | PASS in the extracted patch checkout; exact pinned `craft-platform` and included `host_inbox.rs` compiled |
| `cargo +1.95.0 test --locked -p photocraft-ui-egui host_save_dispatch_waits_for_matching_durable_ack_and_guards_bypass_routes` | PASS, 1 passed; 3,815 filtered from the UI unit test binary, 133 filtered integration tests |
| `cargo +1.95.0 test --locked -p photocraft-web host_inbox::tests::` | PASS in the extracted patch checkout, 2 passed; bounded unknown/duplicate inbox and listener-error propagation |
| `git apply --check` on clean exact-base checkout | PASS |
| `git diff --check` | PASS |

The UI test exercises pathless one-open binding, File › Save dispatch, serialized payload handoff, wrong/late ticket rejection, negative ACK dirty preservation, unique retry ticket, unknown-outcome timeout, retry/close refusal, matching positive ACK, and New/Save As guards. Separate picker/drop route tests and live browser messaging remain a review/test gap.

## Not verified

- No running browser iframe host or browser message lifecycle was exercised.
- No Seafile login, library, version creation, readback or fresh-editor reopen was tested.
- No production Seafile instance or ONLYOFFICE configuration was accessed.
- No upstream issue, PR, RFC, commit or push was made.
