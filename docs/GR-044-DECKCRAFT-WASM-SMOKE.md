# GR-044 — DeckCraft host-save runtime smoke

**Result: bounded synthetic browser PASS.** The local GR-020 DeckCraft Web
adapter was built and loaded as actual WASM in Chromium. A same-origin synthetic
parent opened a one-slide PPTX, a visible text edit made the editor dirty, the
host captured DeckCraft's serialized save bytes and returned the matching ACK,
the editor became clean, and a fresh iframe reopened the captured bytes with the
edit intact.

This is app-level host-transport coverage only. It does not exercise Seafile,
Seafile version creation, the file dispatcher, production, or ONLYOFFICE. Those
behaviors remain **NOT VERIFIED**. No upstream repository was changed.

## Pins and build

| Input | Value |
| --- | --- |
| DeckCraft | `0f4fffcf6c71ffa16029d07ac23752fedd783547` |
| `craft-platform` | `56c5e16d79b77751106173c13111ef4fe0a2c0ec` |
| GR-020 patch SHA-256 | `8d7f98468ce446add5357e10ed8e10e729eb3306fee359d320f09805acc3ee4a` |
| Trunk-built DeckCraft WASM | `deckcraft-web-17df9e6669a6dc99_bg.wasm`, 30 MB; SHA-256 `eebe27c9c42ee46be33e1285b37a9d8d51d5108ff70182fdea3110c5a9835ee9` |
| Rust | `1.95.0` |
| Trunk | `0.22.0` |

The local patched checkout in `/home/roddy/.cache/artcraft-deckcraft-gr020`
matched the DeckCraft pin, and its `Cargo.lock` matched the transport pin.
The patched WASM release build and the Trunk static bundle build both passed;
the latter ran the configured `wasm-opt -Oz` pass. The checkout had no adjacent
`craft-fonts` repository, so DeckCraft used its fallback font and Chromium
reported the expected missing Arial substitution notice. This did not prevent
opening, editing, saving, or reopening the synthetic deck.

## Browser run

`docs/reviews/GR-044/runtime/host.html` served as the only parent/host. It sent
the generated synthetic fixture over same-origin `postMessage`, kept the exact
received save bytes in the page, and returned `deckcraft:saveResult` with the
received ticket. The real DeckCraft app was loaded in an iframe from the
Trunk-built bundle with `?host=parent&webgl&blank`.

1. Chromium loaded the app WASM and the synthetic host opened
   `GR-044-synthetic.pptx` (7,297 bytes after the edited save; the original
   fixture is 4,700 bytes).
2. Double-clicked the slide text, selected it, and entered
   `gr044runtimeeditpassed`. DeckCraft showed the changed slide and reported
   `dirty=true` before save.
3. Pressed Ctrl+S. The host received `deckcraft:save` ticket `deckcraft:1` and
   7,297 serialized bytes, computed SHA-256
   `ce01fb7cd7819f5ee6e67c67d77aeda19829e431a2cf92bdfe396b7d76b09376`, kept
   those bytes in page memory, and returned `deckcraft:saveResult {ok:true}`
   with the same ticket. DeckCraft showed its saved status and `dirty=false`.
4. Clicked **Reopen saved bytes**. A fresh editor iframe loaded, received those
   captured bytes, became clean, and displayed `gr044runtimeeditpassed`.
5. The exact captured `saved.pptx` was retained in the evidence bundle; a ZIP
   inspection confirmed the slide XML contains `gr044runtimeeditpassed`, and
   its file SHA-256 matches the parent-computed hash above.

## Focused checks

| Check | Result |
| --- | --- |
| `python3 docs/reviews/GR-044/runtime/make_fixture.py` | PASS; deterministic 4,700-byte synthetic PPTX created |
| `cargo +1.95.0 build -p deckcraft-web --release --target wasm32-unknown-unknown --locked` | PASS |
| `RUSTUP_TOOLCHAIN=1.95.0 trunk build --release` from `apps/deckcraft-web` | PASS; optimized static browser bundle produced |
| Chromium synthetic open → visible edit → save bytes → matching ACK → clean state → fresh iframe reopen | PASS; exact hashes and screenshot in `docs/reviews/GR-044/` |

## Evidence boundary

The parent is synthetic and stores bytes only in its browser page. It is not a
file platform. No Seafile API, library, version history, dispatcher, or
ONLYOFFICE path was contacted. This therefore closes the GR-020 **browser
adapter runtime** gap only; the mandatory Seafile save/version/reopen workflow
for DeckCraft remains **NOT VERIFIED**. GR-044 is **GPT REVIEW PENDING**.

Evidence index and artifact hashes: [`docs/reviews/GR-044/README.md`](reviews/GR-044/README.md).

Follow-up checks independently matched the pinned source checkout, the GR-020
patch applied to a fresh base worktree, all changed source-file hashes, the
transport lock pin, and the cached WASM hash. The WASM was not rebuilt during
that follow-up; see the evidence README for exact values and commands.
