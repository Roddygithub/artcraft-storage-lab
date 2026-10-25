# GR-032 — PhotoCraft `?host=parent` host-save adapter

**Status:** **GPT REVIEW PENDING** for this bounded local Rust-only source prototype. It is not a browser/Seafile MVP or a project PASS. R1 findings (unbounded ACK inbox, silent listener-registration failure) were remediated; independent R2/R3 reviews returned **PROVISIONAL PASS**.

| Field | Value |
|---|---|
| Source | `storytold/photocraft` `a02f2ee41059d3312e7ff24a5af5edcac7b6435a` |
| Applied prerequisite | GR-026 core patch `docs/reviews/GR-026/photocraft-core-slice-r2.patch`, SHA-256 `4ca7ea1e88bf215f80e6edc137417b8b21d0302e82b9a7a496ffd4e60b0cd3e4` |
| Shared transport | `craft-platform` `56c5e16d79b77751106173c13111ef4fe0a2c0ec` |
| Combined patch | [`photocraft-host-save.patch`](reviews/GR-032/photocraft-host-save.patch), SHA-256 `487935d8f6db33cf82c85f8d9c8aa0686016612510f15cf34f6b3f05a2c53fe7` |
| Checkout | `/home/roddy/.cache/artcraft-storage-lab/photocraft-audit`, detached at the exact base above; no commit or push |

## Implemented slice

The Web app accepts `?host=parent` only when the pinned `craft-platform` same-origin parent transport can be created. It announces readiness, consumes parent Open via `open_file_pathless`, and exports the active `.pcraft` document as serialized bytes on File › Save. The callback sends a ticketed `save` message (`saveAs=false`); the editor keeps the immutable `SavedSnapshot` until a matching result arrives. Only a matching positive result calls `Session::acknowledge_saved_snapshot`; negative results preserve the previous saved baseline. A 30-second missing result marks the write outcome unknown, retains the ticket/snapshot and prevents retry or dirty/unresolved close. A later matching result can settle that ticket. Duplicate and unknown tickets are filtered before enqueue; the inbox holds at most the first Open and one currently expected ACK, so floods cannot grow it or crowd out the valid result. Listener-registration failure aborts startup before `ready` is posted.

Host mode refuses local file/path opens, picker/drop opens, second pathless opens, New/New from Clipboard, Open/Open As/Open Recent, action playback, Save As, Save a Copy, Revert, and close/exit while dirty or a host write is pending/unresolved. Standalone web download and native save code paths retain their existing behavior. Product changes are Rust-only; no JavaScript/TypeScript product code was added.

**Payload-size limit:** the gateway defaults `ARTCRAFT_MAX_BYTES` to 50 MiB (`integration/gateway/server.py:98`). PhotoCraft serializes the snapshot before calling the host transport (`crates/ui-egui/src/lib.rs:1037-1044`), so an oversized document can allocate its serialized bytes before the host/gateway rejects the request. A negative ACK leaves the document dirty, but this does not bound peak serialization memory or establish gateway compatibility for large `.pcraft` documents.

Key source evidence in the patch checkout: `apps/photocraft-web/src/web.rs:95-140` registers the listener, fails startup on error, and posts ready only afterward; `web.rs:400-414` drains the inbox and handles ACK/timeout; `web.rs:488-508` filters ACKs against the current ticket; `apps/photocraft-web/src/host_inbox.rs:4-36` bounds the inbox to one Open and one matching ACK; `host_inbox.rs:39-62` tests flood resistance and listener errors. `crates/ui-egui/src/lib.rs:1026-1082, 1334-1337, 1742-1744` holds the exact snapshot, ACK, timeout and command guards; `crates/ui-egui/src/menus.rs:67-80`, `file_open.rs:95-110, 170-172`, `file_dialog.rs:262-264`, and `discard_ui.rs:70-77` guard menu, open/picker/drop and close routes; `crates/engine/src/lib.rs:261-284, 618-629` contains the GR-026 incarnation-bound snapshot primitive. Standalone download remains marked unconfirmed at `apps/photocraft-web/src/web.rs:532-535` and the existing write baseline logic is unchanged at `crates/ui-egui/src/lib.rs:2046`.

## Evidence and limits

| Check / claim | Result |
|---|---|
| Base and patch | Patch generated as a combined diff against exact `a02f2ee41059d3312e7ff24a5af5edcac7b6435a`; accepted GR-026 core patch is included in the diff |
| Transport pin | `Cargo.lock` resolves `craft-platform` to exact rev `56c5e16d79b77751106173c13111ef4fe0a2c0ec`; locked WASM check resolved that package |
| Rust 1.95 locked PhotoCraft Web WASM check | **PASS**: `cargo +1.95.0 check --locked -p photocraft-web --target wasm32-unknown-unknown` |
| Focused UI lifecycle test | **PASS**, 1/1: `cargo +1.95.0 test --locked -p photocraft-ui-egui host_save_dispatch_waits_for_matching_durable_ack_and_guards_bypass_routes`; covers negative ACK, retry ticket uniqueness, stale ACK, timeout/retry/close guard, and matching success |
| Independent R1 finding remediation tests | **PASS**, 2/2: `cargo +1.95.0 test --locked -p photocraft-web host_inbox::tests::`; unknown/duplicate floods cannot displace a valid ACK, and listener errors propagate |
| Final locked Web WASM check | **PASS** after R1 changes: `cargo +1.95.0 check --locked -p photocraft-web --target wasm32-unknown-unknown` |
| Patch apply and whitespace | **PASS**: `git apply --check` in a second clean detached checkout at the exact source SHA; `git diff --check` |
| Source route guard coverage | Open APIs, direct app commands, menu routes, local picker/drop and discard/close paths are guarded in source; exact runtime behavior needs independent review and tests |
| Browser host messaging | **NOT VERIFIED** in a running browser; no host page exercised the listener or ACK lifecycle. Listener failure behavior is covered by a Rust helper test/source ordering, not browser runtime |
| Seafile authorization/version creation/readback/fresh reopen | **NOT VERIFIED**; no Seafile was accessed |
| Gateway payload-size compatibility and pre-serialization memory bound | **NOT VERIFIED**; default gateway ceiling is 50 MiB; PhotoCraft serializes before submission, and oversized-save ACK behavior has no runtime evidence |
| ONLYOFFICE regression | **NOT VERIFIED**; no Seafile or ONLYOFFICE configuration was touched |
| Production or upstream actions | None; no production access, issue, PR, RFC, commit or push |

The exact patch and its runnable commands are preserved in [`reviews/GR-032/README.md`](reviews/GR-032/README.md). Do not dispatch this adapter through Seafile before independent review, browser lifecycle evidence and required GPT review.
