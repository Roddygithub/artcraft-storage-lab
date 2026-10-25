# GR-029 — SoundCraft Web egui 0.37 compatibility

## Goal

Remove the remaining compile blocker after GR-027 (Symphonia 0.6.1) and
GR-028 (CPAL 0.18.2), so the pinned SoundCraft Web app and GR-025 host-save
adapter can be checked for `wasm32-unknown-unknown` without changing the
upstream repositories.

## Bounded local compatibility patches

| Patch | Pinned base | Change | SHA-256 |
|---|---|---|---|
| [`craft-ui-egui-0.37-compat.patch`](reviews/GR-029/craft-ui-egui-0.37-compat.patch) | `storytold/craft-libs` `5c874d51eeb3de70e735c8ce87a59a7dedd47675` | Set workspace egui to 0.37 and map removed widget types to supported AccessKit roles | `5cf2728d20ed74d9fe0521543280d77ce9ef1a5efd3b6f3db3862b6363b06292` |
| [`soundcraft-egui-0.37-compat.patch`](reviews/GR-029/soundcraft-egui-0.37-compat.patch) | `storytold/soundcraft` `d47abe484d4f9ef0cc9f8e872e0b3880a61a4588`, after GR-025/027/028 | Screenshot callbacks, wheel source, selected-state accessibility, and egui 0.37 gutter scrolling | `af31ccc5d69ea1e9577e0a7f989077ccafd9e40cfe3643a2e8c8f934cc6fa098` |
| [`soundcraft-egui-0.37-build-lock.patch`](reviews/GR-029/soundcraft-egui-0.37-build-lock.patch) | SoundCraft lockfile immediately after GR-025 | Incremental lock update for local craft-ui path override; does not repeat the GR-025 transport entry | `d86d74198de55f7f98a4a381d1d18183013f9195c046dd0f56667cbc305f0743` |

Independent R3 review returned a bounded PROVISIONAL PASS with no remaining
findings. R1's accessibility issue and R2's lock-order issue are remediated.
The independent review and remediation history are recorded in
[`reviews/GR-029/`](reviews/GR-029/). Status: **GPT REVIEW PENDING**; this does
not establish the MVP or browser/Seafile runtime behavior.

These are local build-compatibility artifacts only. They are not applied to
production and have not been submitted upstream. The probe uses a local
`craft-ui` override pointing at the pinned craft-libs checkout after the first
patch. To reproduce it, add this local-only section to SoundCraft Cargo.toml,
substituting the other checkout path as needed:

```toml
[patch."https://github.com/storytold/craft-libs"]
craft-ui = { path = "/home/roddy/.cache/craft-libs-5c874d5-egui37/crates/ui" }
```

Apply the full GR-025 patch first (including its Cargo.lock hunk), then GR-027,
GR-028, and the GR-029 SoundCraft source patch. Add the local craft-ui path
override shown above, then apply the GR-029 lock patch to the Cargo.lock that is
already at the post-GR-025 state. This incremental patch updates that lock
without adding `craft-platform` a second time. The complete documented sequence
was replayed and the locked WASM check passed. This remains a local build
overlay, not an upstream dependency update.

## Checks

- `cargo +1.95.0 check --locked -p soundcraft-web --target wasm32-unknown-unknown` — PASS, with GR-025, GR-027, GR-028 and both GR-029 compatibility patches applied. Existing dead-code/deprecation warnings remain.
- `cargo +1.95.0 test --locked -p soundcraft-ui-egui --lib host_bound_session_routes_save_and_refuses_replacement_and_save_as` — PASS, 1 test.
- `rustfmt --edition 2024 --check crates/ui-egui/src/control.rs crates/ui-egui/src/panels.rs` — PASS.
- `git diff --check` on the SoundCraft source — PASS.
- The root unified Cargo config directs artifacts to `/home/roddy/.cache/cargo-target`; `/tmp` was 6% used after these checks.

## Limits

No clean-checkout automation script or browser test is included yet. The exact
host page, transferred bytes, durable Seafile version creation, editor-visible
save confirmation, and fresh-storage reopen remain **NOT VERIFIED**. This
compatibility result does not establish the ArtCraft MVP or a project GPT
review pass. Upstream publication remains locked.
