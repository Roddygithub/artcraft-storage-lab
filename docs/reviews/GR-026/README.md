# GR-026 evidence — PhotoCraft host integration

**Result:** bounded implementation not attempted. Source inspection found that
safe durable semantics require app-level changes beyond an isolated browser
adapter. No downloaded source, app patch, production access, upstream action or
project-level PASS is part of this result.

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
| Exact source SHA | PASS, command and output recorded above |
| Rust 1.95 locked shared-transport tests | PASS: `cargo +1.95.0 test --manifest-path integration/rust/craft-platform/Cargo.toml --locked`; 7 unit tests passed |
| Rust 1.95 locked WASM check | PASS for the shared transport only: `cargo +1.95.0 check --manifest-path integration/rust/craft-platform/Cargo.toml --locked --features browser --target wasm32-unknown-unknown --tests` |
| Rust 1.95 format check | FAIL on unchanged shared-transport files: `cargo +1.95.0 fmt --manifest-path integration/rust/craft-platform/Cargo.toml -- --check` reports pre-existing formatting differences across the package; no formatter changes were applied |
| Rust 1.95 locked WASM PhotoCraft app check | NOT RUN: no patch/app integration was produced, so an app build would not verify an implementation |
| Diff whitespace check | PASS: `git diff --check` |
| Focused PhotoCraft host lifecycle tests | NOT RUN: there is no implementation to test |
| Browser host / Seafile version / reopen | NOT VERIFIED |
| Independent code review | NOT APPLICABLE: no code patch; review of this design remains open |

See `docs/GR-026-PHOTOCRAFT-HOST-SAVE.md` for the minimal implementation design.
