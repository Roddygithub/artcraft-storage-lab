# GR-020 — DeckCraft host-save acknowledgement prototype

**Status: local prototype; not Seafile E2E and not ready for project-level GPT review.**

## Pinned source and artifact

| Item | Value |
|---|---|
| DeckCraft source | `storytold/deckcraft` `0f4fffcf6c71ffa16029d07ac23752fedd783547` |
| Shared transport | `artcraft-storage-lab` `56c5e16d79b77751106173c13111ef4fe0a2c0ec` (`craft-platform`) |
| Patch | [`deckcraft-host-save-ack.patch`](deckcraft-host-save-ack.patch) |
| Patch SHA-256 | `8d7f98468ce446add5357e10ed8e10e729eb3306fee359d320f09805acc3ee4a` |

## Scope

This patch adds an opt-in `?host=parent` adapter to DeckCraft Web. It accepts a single parent-provided `.deckcraft`, `.pptx`, `.potx`, or `.ppsx` document, serializes edits through DeckCraft's existing Rust format writer, and leaves the presentation dirty until the parent returns a matching durable `saveResult`. The acknowledgement records the exact saved snapshot; edits made while a save is pending remain dirty. A host save timeout is reported as an unknown outcome and does not silently retry.

Host mode refuses additional document opens/creation, Save As, and path-based opens. Ordinary standalone browser downloads and native file saves retain their existing paths. The adapter is local to the lab patch; no DeckCraft upstream repository was changed and the Seafile dispatcher was not changed.

## Checks

| Check | Result |
|---|---|
| `cargo +1.95.0 test -p deckcraft-engine --lib external_save_tests --locked` | PASS, 2 tests |
| `cargo +1.95.0 test -p deckcraft-ui-egui --lib host_tests --locked` | PASS, 4 tests |
| `cargo +1.95.0 check -p deckcraft-web --target wasm32-unknown-unknown --locked` | PASS |
| `cargo +1.95.0 fmt --all -- --check` | PASS |
| `git diff --check` in pinned DeckCraft checkout | PASS |
| `cargo +1.95.0 xtask assets` | PASS; 47 asset files attributed |
| `cargo +1.95.0 xtask layers` | PASS; 28 crates, no layering violations |
| `cargo +1.95.0 xtask wasm` | PASS; all 23 listed WASM crates check |
| Targeted `cargo +1.95.0 clippy -p deckcraft-engine -p deckcraft-ui-egui -p deckcraft-web --all-targets --locked` | PASS with non-fatal existing workspace warnings; the one warning in changed UI code was simplified in the current patch |
| The same targeted Clippy command with `-- -D warnings` | BLOCKED by existing warnings in untouched `crates/isobmff/src/codec.rs:1406` and `crates/model/src/trendline.rs:468` |
| `cargo +1.95.0 xtask ci` | BLOCKED at workspace Clippy by existing `collapsible_match` in untouched `crates/matroska/src/demux.rs:726`; PDF dependency step passes |
| `cargo +1.95.0 test --workspace` | NOT COMPLETED; UI test binary remained waiting on several long-running tests for over five minutes and was stopped. An earlier run also encountered `/tmp` quota errors; retry used a dedicated `TMPDIR` |

The workspace test suite did not complete, so only the focused engine/UI tests are claimed. The checkout lacks the sibling `craft-fonts` repository; builds warn and continue without bundled project fonts. Luna high R1 reviewed the prior source patch SHA `d6bdbc…ec11`; R2 reviewed the app source before the transport re-pin. The re-pin changes only Cargo manifest/lock revisions and has an independent exact review; see `REVIEW-LUNA-HIGH-R2.md` and `REVIEW-TRANSPORT-REPIN.md`.

## Evidence boundary

The native adapter tests exercise host open → edit → serialized bytes → positive acknowledgement → reopen, plus stale-edit and rejected-save behavior. GR-044 now records an actual-WASM browser message run with a synthetic in-memory parent and fresh iframe reopen from captured bytes. **Seafile version creation, a fresh Seafile-backed reopen, dispatcher integration, and production or ONLYOFFICE behavior are NOT VERIFIED.** This does not change the project-level GPT FAIL or upstream lock.
