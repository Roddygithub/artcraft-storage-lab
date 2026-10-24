# GR-020 — DeckCraft host-save acknowledgement prototype

**Status: local prototype; not Seafile E2E and not ready for project-level GPT review.**

## Pinned source and artifact

| Item | Value |
|---|---|
| DeckCraft source | `storytold/deckcraft` `0f4fffcf6c71ffa16029d07ac23752fedd783547` |
| Shared transport | `artcraft-storage-lab` `90c261de22ef75c4c7c5c5cd1c712d483be0bbc8` (`craft-platform`) |
| Patch | [`deckcraft-host-save-ack.patch`](deckcraft-host-save-ack.patch) |
| Patch SHA-256 | `b00e36ecdc655b86205a8d1a87e8eb5ddf289d52320ecc19c8b130c22ab47186` |

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

The workspace test suite did not complete, so only the focused engine/UI tests are claimed. The checkout lacks the sibling `craft-fonts` repository; builds warn and continue without bundled project fonts. Luna high R1 reviewed the prior patch SHA `d6bdbc…ec11`; R2 reviewed the current exact patch SHA above and returned PASS with no findings. See `REVIEW-LUNA-HIGH-R2.md`.

## Evidence boundary

The native adapter test exercises host open → edit → serialized bytes → positive acknowledgement → reopen, plus stale-edit and rejected-save behavior. The WASM target compiles the actual browser transport. **A browser message run, Seafile version creation, a fresh Seafile-backed reopen, and production or ONLYOFFICE behavior are NOT VERIFIED.** This does not change the project-level GPT FAIL or upstream lock.
