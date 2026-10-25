# GR-028 — SoundCraft CPAL 0.18.2 playback compatibility

**Status:** local patch candidate; bounded independent review is INCOMPLETE.
The reviewer found no semantic CPAL API incompatibility in the inspected patch,
but could not access the base checkout. In this implementation session, the
patch was dry-run against the clean pinned base and the listed checks were
independently rerun. The patch changes three playback files only and adds no dependency changes. It makes the
`soundcraft-playback` crate compile on native and WASM with locked CPAL 0.18.2.
The full SoundCraft Web WASM build remains blocked after this patch by egui
0.36/0.37 API/type mismatches in `soundcraft-ui-egui` and the pinned `craft-ui`
dependency. Browser and Seafile behavior are **NOT VERIFIED**.

| Item | Value |
|---|---|
| SoundCraft base | `d47abe484d4f9ef0cc9f8e872e0b3880a61a4588` |
| CPAL | 0.18.2, locked; no Cargo changes |
| Patch | [`cpal-0.18.2-compat.patch`](cpal-0.18.2-compat.patch) |
| Patch SHA-256 | `ff1ced58251397b8077f92ee9b92c7cae1ada25a8a7fe9068c50ba7cdad5901c` |
| Review | [Independent R1](REVIEW-INDEPENDENT-R1.md): incomplete; no semantic issue found, applicability/builds not independently verified |

Changes use CPAL 0.18's unified `Error`, scalar `SampleRate`, `Device::description`, and by-value stream configs. Recording is explicitly unsupported on WASM (the browser CPAL backend has no input capture; recording also requires native file output). Native recording/playback code remains available.

## Checks run

- `patch --dry-run` applies to the clean checkout at the stated base.
- `cargo +1.95.0 check --locked -p soundcraft-playback --target wasm32-unknown-unknown` — PASS.
- `cargo +1.95.0 check --locked -p soundcraft-playback` — PASS.
- `cargo +1.95.0 test --locked -p soundcraft-playback --lib` — PASS, 36 tests.
- The full `soundcraft-web` WASM check gets past playback but fails in unchanged UI/dependency code: 52 egui errors, including `craft-ui` pinned to egui 0.36 while SoundCraft uses egui/eframe 0.37. This is a separate compatibility gap, not included in this patch.
- Browser save flow, Seafile versions, reopen persistence, and production behavior are **NOT VERIFIED**.
- The independent reviewer could not access the three SoundCraft source files
  or the stated base object from their review checkout. Patch applicability and
  commands above were checked separately in this implementation session; the
  review itself remains incomplete on those checks.
