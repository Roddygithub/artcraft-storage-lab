# GR-076 — PhotoCraft bounded browser host adapter follow-up

**Status: GPT REVIEW PENDING — uncommitted implementation candidate for parent review.** No commit,
push, publication, deployment or dispatch. This is a bounded source slice, not a
project verdict or Seafile MVP.

## Scope and immutable inputs

Local main already retained GR-032's browser adapter. GR-076 reuses that adapter
on the exact GR-026 core and closes concrete guard and payload gaps; it does not
invent a newer PhotoCraft base. The parent checkout remains unchanged. No new external dependency was added;
the Web app declares its existing workspace format crate directly for bounded decoding.

| Input | Exact value |
|---|---|
| Isolated lab worktree | `/home/roddy/.t3/worktrees/artcraft-storage-lab/gr-076-photocraft` |
| Lab local-main base | `dc105220ae934f9779eb357a4cda901ee0aa0c0b` |
| Separate product worktree | `/home/roddy/.cache/artcraft-storage-lab/gr076-photocraft` |
| PhotoCraft base | `a02f2ee41059d3312e7ff24a5af5edcac7b6435a` |
| GR-026 core patch SHA-256 | `4ca7ea1e88bf215f80e6edc137417b8b21d0302e82b9a7a496ffd4e60b0cd3e4` |
| Reused GR-032 combined patch SHA-256 | `487935d8f6db33cf82c85f8d9c8aa0686016612510f15cf34f6b3f05a2c53fe7` |
| Required transport | `craft-platform` `56c5e16d79b77751106173c13111ef4fe0a2c0ec` |
| Complete candidate | [combined patch](reviews/GR-076/photocraft-host-save.patch); apply alone to exact PhotoCraft base |
| All Git dependency pins, compiler and lock digest | [pins.json](reviews/GR-076/pins.json) |

The retained GR-026 R2 and GR-032 patches declare `mod saved_snapshot_tests`
but omit its file. Their product code applies and the retained GR-032 WASM
check passes, but `cargo fmt` fails and engine tests are not reproducible from
those patches alone. GR-076 restores the three earlier tests from lab commit
`0557401d0ab275849e1ed36a94ead60f00941a12`,
`docs/reviews/GR-026/photocraft-core-slice.patch`, and adds a same-ID close/reopen
regression. No engine core behavior was replaced. Historical test claims have
not been silently reused as current evidence.

## Implemented behavior

| Requirement | Candidate behavior / source in product checkout |
|---|---|
| One host document | `open_file_pathless` accepts one nonempty `.pcraft`; synchronous host import bypasses preset loading, profile prompts, script events and background Open. No local path or Open Recent entry. `file_open.rs`; `host_inbox.rs` keeps a lifetime first-Open latch across drains |
| Async Save | Existing GR-032 `save_host_snapshot` captures immutable incarnation/revision, serializes, sends one opaque ticket and retains the snapshot. Menu and direct app `file.save` route here. `ui-egui/src/lib.rs` |
| ACK and later edits | Only current ticket consumes pending snapshot. Positive ACK advances captured revision; negative ACK preserves baseline; unknown/duplicate tickets do nothing. `host_save_result`; engine `acknowledge_saved_snapshot` |
| Unknown outcome | 30 seconds without result retains pending ticket/snapshot, reports unknown and blocks retry. Matching late positive/negative result can settle it. Listener requests repaint; pending ticket requests 100ms repaint so idle UI can process result/deadline. `web.rs` |
| Replacement and duplicate guards | Shared `host_document::authorize` installed on engine Session and checked before app/menu routes. Blocks file creation/open/batch/replacement/save-copy/close commands, action playback, Image Duplicate, history-to-document, Split/Merge Channels, smart-object child Open, and new-document outputs of layer/channel duplicate, Calculations and Select and Mask. Before initial host Open, Paste cannot synthesize a clipboard document |
| Direct bypass guards | Local `open_file`, `open_bytes`, `open_path`, `open_paths`, automation Open, picker Open, public Save As/automation Save and internal save-to routes refuse host mode. Web drops are discarded before file reads. Recovery service disabled only for host mode |
| Close/discard | In-app File Close/Close All/Close Others/Exit/Revert disabled even when clean (deliberate one-document slice). Dirty/pending/unresolved state also retains discard/window-close protection. Browser navigation uses existing best-effort beforeunload confirmation |
| Standalone/native | Host policy installed only for `host_mode`; standalone download remains `write_unconfirmed: true`; native file-path behavior retains its original branch |

Exact current file:line anchors for the source claims above are retained in
[source-evidence.txt](reviews/GR-076/source-evidence.txt); the complete source
is preserved by the hash-pinned patch.

## Bounds and limitations

| Boundary | Enforced bound / limitation |
|---|---|
| Parent message trust | Pinned transport requires exact same origin and actual parent `event.source`; explicit target origin on outgoing messages. Source inspected at exact transport pin; live browser security behavior **NOT VERIFIED** in GR-076 |
| Transport Open copy | Existing shared transport bounds message and cumulative runtime copied bytes to 256 MiB and 64 admissions before copying; metadata name 1024 UTF-16 units |
| Adapter document input/output | 1 byte through 50 MiB; Open rejected before import and Save rejected before transport handoff. Host-mode explicit export writes also cap payloads at 50 MiB. Output cap is after serialization: peak serialization allocation **NOT BOUNDED** by this check |
| Actual host `.pcraft` decode | Manifest 8 MiB, one blob 50 MiB, aggregate decoded tile/blob bytes 256 MiB, canvas 16,777,216 pixels; actual format decoder rather than extension-based generic import. These are admission limits, not a total process-memory guarantee |
| Inbox / outstanding write | One initial Open slot, one ACK slot matching expected ticket, one retained snapshot; duplicate/unknown floods cannot displace accepted ACK |
| ACK metadata | Pinned transport limits ticket (256 UTF-16 units plus Rust ticket 256-byte limit), error 4096 UTF-16 units and requires a boolean `ok` |
| Browser lifecycle | Real iframe Open/ACK/reopen, browser clock/unload behavior and idle repaint runtime **NOT VERIFIED** for this candidate; source compilation and focused tests only |
| External systems | Seafile authorization, version creation, persistence/reopen, ONLYOFFICE regression and production behavior **NOT VERIFIED** in this work; none accessed |
| Wider validation | Full PhotoCraft suite, native desktop UI/visual QA, clippy/layer gates and adversarial corpus **NOT VERIFIED** unless separately recorded in checks |

Host save ticket namespaces require successful browser `Crypto.getRandomValues`;
host startup fails visibly if it is unavailable. Standalone startup uses its
existing paths and does not need a host ticket namespace. Actual failure UI is
**NOT VERIFIED**.

## Checks and handoff

Rust 1.95 locked engine (4), host-filter UI (7), file-open UI (47), and inbox (2)
tests passed. Format, locked Web WASM check, clean-base patch application and
whitespace checks passed; independent R1/R2 source reviews returned only
**PROVISIONAL PASS**. Commands/results, patch digest and reviews are retained in
[the evidence bundle](reviews/GR-076/README.md). Runnable check:

```sh
./scripts/check-gr076-photocraft.sh /home/roddy/.cache/artcraft-storage-lab/gr076-photocraft
```

The script runs Rust 1.95 locked snapshot/host/file-open/inbox tests, formatting,
locked Web WASM check and whitespace checks. It neither starts a service nor
changes Cargo target/temp locations. All edits remain uncommitted for parent
review. Upstream and dispatch gates remain closed.
