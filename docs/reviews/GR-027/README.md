# GR-027 — SoundCraft Symphonia 0.6.1 WASM compatibility

**Status:** local compatibility patch; exact independent round-5 review is
PROVISIONAL PASS with no findings. The audio crate builds and tests on native
and WASM. Full SoundCraft Web WASM remains blocked after the CPAL fix by an
egui API/type mismatch between pinned `craft-ui` and SoundCraft. Browser and
Seafile save behavior are **NOT VERIFIED**.

| Item | Value |
|---|---|
| SoundCraft base | `d47abe484d4f9ef0cc9f8e872e0b3880a61a4588` |
| Dependency | Symphonia 0.6.1; Cargo manifests/lock unchanged |
| Patch | [`symphonia-0.6.1-compat.patch`](symphonia-0.6.1-compat.patch) |
| Patch SHA-256 | `e4a63489cfdfc0fd3cfc347a1998347bd92bb0b682ac9a25d1051f887e357e6b` |
| Reviews | [R1](REVIEW-INDEPENDENT-R1.md), [R2](REVIEW-INDEPENDENT-R2.md), [R3](REVIEW-INDEPENDENT-R3.md), [R4](REVIEW-INDEPENDENT-R4.md), [R5](REVIEW-INDEPENDENT-R5.md) |

The patch changes only `crates/audio-io/src/symph.rs`. It ports the decode path
to Symphonia 0.6.1 without changing dependencies. Preflight matches CAF, FLAC,
and WAV root signatures; it walks top-level MP4 atoms and validates `ftyp`
bounds. Markers inside payloads do not select unrelated parsers. Zero-padded
CAF and MP4 retain their correct root offsets. Audio track selection skips the
`CODEC_ID_NULL_AUDIO` sentinel.

## Checks

- `cargo +1.95.0 fmt --all -- --check` — PASS.
- `cargo +1.95.0 test --locked -p soundcraft-audio-io` — PASS, 57 tests.
- `cargo +1.95.0 check --locked -p soundcraft-audio-io --target wasm32-unknown-unknown` — PASS.
- The first run on `/tmp` hit the disk quota; reran using a target cache and temporary directory on the workspace volume.
- The GR-025 adapter applies and its two focused ledger tests pass (reported by the implementation lane). The full SoundCraft Web WASM build is not yet verified: CPAL errors were fixed in a separate GR-028 patch, after which the build reached 52 egui API/type errors from locked `craft-ui` 0.36 versus workspace egui/eframe 0.37.
- Browser, Seafile version creation, close/reopen, authorization, and production behavior are **NOT VERIFIED**.
