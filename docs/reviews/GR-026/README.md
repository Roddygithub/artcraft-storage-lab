# GR-026 evidence — PhotoCraft host integration

**Result:** bounded core stage implemented locally; the full browser host adapter
is still not implemented. The pathless-open/snapshot-ACK patch is a provisional
PASS after remediation of stale acknowledgements across close/reopen and patch
format. Browser transport, Seafile durability and project-level readiness are
**NOT VERIFIED**.

## Core stage patch

| Item | Value |
|---|---|
| Base | `a02f2ee41059d3312e7ff24a5af5edcac7b6435a` |
| Patch | [`photocraft-core-slice-r2.patch`](photocraft-core-slice-r2.patch) |
| SHA-256 | `4ca7ea1e88bf215f80e6edc137417b8b21d0302e82b9a7a496ffd4e60b0cd3e4` |
| Review | [Independent R2](REVIEW-INDEPENDENT-R2.md): PROVISIONAL PASS |
| Tests | Engine snapshot tests 4/4, pathless UI test 1/1 and locked Web WASM check pass in this session |

The patch adds a pathless byte-open API and captures the document revision plus
a unique open-incarnation token in `SavedSnapshot`. A durable ACK advances only
the saved revision of that exact open document. Closing and reopening a document
with a reused ID creates a different incarnation, so an old ACK is rejected.
The standard `git apply --check` succeeds against the clean pinned base.

This is only an engine/UI core seam; it adds no browser message listener or
Seafile write path. No production access or upstream action was performed.

## Exact source and shared transport

| Claim | Evidence |
|---|---|
| PhotoCraft source checkout is the requested immutable revision | `git -C .scratch-photocraft rev-parse HEAD` returned `a02f2ee41059d3312e7ff24a5af5edcac7b6435a` after fetching that exact object from `https://github.com/storytold/photocraft.git` |
| The browser app currently has no `craft-platform` dependency | audited `apps/photocraft-web/Cargo.toml:21-37`; the wasm target lists eframe, rfd, wasm-bindgen, js-sys and web-sys |
| The existing web writer is a browser download and unconfirmed | audited `apps/photocraft-web/src/web.rs:431-439`: Save dialog returns a name, `write` calls `download`, and `write_unconfirmed` is true |
| The editor has an export-to-bytes implementation | audited `apps/photocraft-web/src/web.rs:395-400`; it calls `photocraft_io::export` and returns `r.bytes` |
| Public `open_file` makes the incoming string a file path | audited `crates/ui-egui/src/file_open.rs:91-105`; it passes `Some(path)` to the opening path and documents that Save writes back to that path |
| Open picker is multi-file and creates multiple tabs | audited `apps/photocraft-web/src/web.rs:401-427` and `crates/ui-egui/src/file_dialog.rs:243-267` |
| Save cleanliness is decided synchronously after the write callback | audited `crates/ui-egui/src/lib.rs:1960-1977`; `saved_revision_after_write(!write_unconfirmed, ...)` only advances when write is confirmed |
| App has multiple ways to create/route document state | audited `crates/ui-egui/src/menus.rs:224-302` (Open/New/Save/Save As) plus app command/UI routes; host mode must guard replacement and copy operations, not only add a transport listener |
| Shared transport implements same-origin parent checks, bounded Open input, tickets, SaveResult, and timeout-capable app events | `integration/rust/craft-platform/src/browser/host.rs`, `integration/rust/craft-platform/src/host_protocol.rs`; package is already local and checksum-protected |
| Required app dependency pin must remain immutable | use exactly `git = "https://github.com/Roddygithub/artcraft-storage-lab", rev = "56c5e16d79b77751106173c13111ef4fe0a2c0ec"`; never use a branch or tag |

The PhotoCraft repository `AGENTS.md` was also read. It requires Rust-only
product code, no JS/TS or webview shell, and wasm compilation for app changes.
No PhotoCraft files were edited.

## Checks run

| Check | Result |
|---|---|
| Exact source SHA | PASS: patch applies to clean `a02f2ee41059d3312e7ff24a5af5edcac7b6435a` checkout |
| Engine snapshot ACK tests | PASS: 4 tests, including same-ID close/reopen stale ACK rejection |
| UI pathless-open regression | PASS: `cargo +1.95.0 test --locked -p photocraft-ui-egui pathless_host_open_uses_name_without_binding_or_recent_entry`; 1 test |
| Rust 1.95 locked WASM PhotoCraft app check | PASS after incarnation-token addition: `cargo +1.95.0 check --locked -p photocraft-web --target wasm32-unknown-unknown` |
| Format and diff whitespace checks | PASS for the current checkout |
| Independent exact review | R2 PROVISIONAL PASS; reviewer could not run tests due `/tmp` quota |
| Browser host / Seafile version / reopen | NOT VERIFIED |

See `docs/GR-026-PHOTOCRAFT-HOST-SAVE.md` for the remaining implementation design.
