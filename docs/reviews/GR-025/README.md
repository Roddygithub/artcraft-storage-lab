# GR-025 evidence — SoundCraft host-save prototype

**Status:** PROVISIONAL source review; no blocker/major found after the local
Open bypass fix. **The `soundcraft-web` WASM build is blocked**, and its browser
and Seafile workflow are not verified. No upstream or production action.

| Item | Value |
|---|---|
| SoundCraft base | `storytold/soundcraft` `d47abe484d4f9ef0cc9f8e872e0b3880a61a4588` |
| Shared transport | `craft-platform` `56c5e16d79b77751106173c13111ef4fe0a2c0ec` |
| Patch | [`soundcraft-host-save.patch`](soundcraft-host-save.patch) |
| Patch SHA-256 | `f8f9da024b80b3292cca1a60ee69eaf4e19c450d7582fac582596fd11aebc331` |
| Independent review | [`REVIEW-INDEPENDENT-R2.md`](REVIEW-INDEPENDENT-R2.md) |

The patch adds a one-session `?host=parent` path for `.scraftz`, ticketed
snapshot ACK, failure/timeout behavior, and host-mode Save As/replacement/Open
guards. Local picker/drop session bytes are refused through the shared
`dialogs::open_session_bytes` entry point. The parent’s initial Open is separate.

## Checks

- Two host-save ledger tests pass.
- Formatting, `git diff --check`, and clean-base `git apply --check` pass.
- The UI regression and standalone browser-open tests **did not run** because
the upstream base fails to compile with Symphonia 0.6.1 API mismatches.
- The `soundcraft-web` WASM check is **BLOCKED** by the same base audio-io
  errors. GR-027 locally ports that API and has a follow-up marker-scope review pending; after that, a CPAL 0.18.2 mismatch in
  `soundcraft-playback` remains, tracked as GR-028. Neither compatibility fix
  has yet been independently reviewed or merged.
- 64 MiB output cap is after serializer allocation; peak serialization memory
  is not bounded by that cap.

Browser host messaging, durable Seafile writes, version creation, close/reopen,
authorization, and deployment are **NOT VERIFIED**. Do not add SoundCraft to
Seafile dispatch on this evidence.
