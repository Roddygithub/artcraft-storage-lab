# Independent SoundCraft GR-025 follow-up review

**Result:** PROVISIONAL source review; R1's major replacement bypass is closed.
No new blocker or major found by inspection. This is not a full PASS because the
changed UI regression and WASM build could not compile.

| Check | Result |
|---|---|
| Source base | `d47abe484d4f9ef0cc9f8e872e0b3880a61a4588` confirmed |
| Patch SHA-256 | `f8f9da024b80b3292cca1a60ee69eaf4e19c450d7582fac582596fd11aebc331` matched |
| craft-platform pin | `56c5e16d79b77751106173c13111ef4fe0a2c0ec` in manifest and lock |
| UI/WASM tests by reviewer | Not run; author reports they fail before changed code builds on Symphonia base errors |

The common `dialogs::open_session_bytes` now refuses local picker/drop
replacement in host mode before storing bytes; the dirty-session regression
checks content, dirty state and undo history. Host initial Open remains separate.
The engine/menu/shortcut SaveAs and replacement guards, ticket ledger, exact
snapshot ACK behavior, negative ACK retry and timeout lockout show no new issue
on source inspection. Standalone behavior remains the default with host mode off.

Known remaining minor: the 64 MiB serialization limit is checked after the
serializer allocates output. Full WebAssembly, browser messaging and Seafile
version/reopen remain **NOT VERIFIED**. GR-027 and GR-028 track source-build
compatibility blockers separately. Reviewer did not rerun tests or apply check.
