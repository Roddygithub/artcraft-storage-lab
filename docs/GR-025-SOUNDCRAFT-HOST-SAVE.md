# GR-025 — SoundCraft host-save acknowledgement prototype

**Status:** bounded source prototype; local-open replacement finding fixed by
source review. The WebAssembly build remains blocked by upstream SoundCraft API
mismatches; this is not an app-runtime, Seafile, or project-level PASS.

At `storytold/soundcraft` base
`d47abe484d4f9ef0cc9f8e872e0b3880a61a4588`, host mode opens one pathless
`.scraftz` session. Save serializes the existing bundle and sends a bounded
ticket; only the matching success ACK for the exact current snapshot clears
dirty. Negative ACK permits explicit retry; unknown/duplicate ACKs are ignored;
timeout locks saving as an unknown outcome. Host Save As, session replacement,
and local picker/drop session opens are refused. Standalone downloads and native
saves remain separate.

The independent review caught a local picker/drop path that bypassed the
replacement guard; the follow-up adds the refusal in the common UI entry point.
The parent’s initial Open remains a distinct code path. Source review found the
fix correct, but its UI regression has not run because the pinned base does not
compile against the locked Symphonia API. The Symphonia API port is recorded in GR-027 and has a bounded exact provisional
PASS after five review rounds. The CPAL 0.18.2 playback port is recorded in
GR-028 and under independent review. Full Web WASM then fails in unchanged UI
code from the egui 0.36/0.37 dependency mismatch.

Patch, exact checks, review, and limits: [`docs/reviews/GR-025/`](reviews/GR-025/).
The patch is not in Seafile dispatch.
