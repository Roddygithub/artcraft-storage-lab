# GR-044 evidence bundle

Scope: synthetic Chromium smoke for the GR-020 DeckCraft `?host=parent`
adapter. The actual patched app WASM opened, edited, emitted serialized save
bytes, received the matching positive acknowledgement, became clean, and
reopened the captured bytes in a fresh iframe.

| Artifact | SHA-256 | Purpose |
| --- | --- | --- |
| Trunk-built WASM (`deckcraft-web-17df9e6669a6dc99_bg.wasm`, kept in local build cache) | `eebe27c9c42ee46be33e1285b37a9d8d51d5108ff70182fdea3110c5a9835ee9` | Actual optimized WebAssembly module loaded in Chromium; 30 MB. The build output is not copied into this evidence bundle. |
| [`runtime/host.html`](runtime/host.html) | `a58f83d85e85cdab72b8340a0e04a0d5bb89a6a26dc7d529969dcf86e7337b6b` | Same-origin synthetic parent; it retains captured bytes in page memory, echoes the matching ticket, observes clean state and reopens those bytes in a fresh iframe |
| [`runtime/make_fixture.py`](runtime/make_fixture.py) | `b10e5c99acfd45c7b610bee21735a94c8a71e60c35ea2858d3580c439c2baf69` | Standard-library generator for the one-slide synthetic PPTX; fixed ZIP metadata makes the fixture reproducible |
| [`runtime/synthetic.pptx`](runtime/synthetic.pptx) | `c06d0e05220a380b595a5ca1cfe14d3f556c772102271b4656e5d308f32eea5c` | Original synthetic PPTX fixture, 4,700 bytes |
| [`runtime/saved.pptx`](runtime/saved.pptx) | `ce01fb7cd7819f5ee6e67c67d77aeda19829e431a2cf92bdfe396b7d76b09376` | Exact 7,297-byte payload captured from `deckcraft:save`; slide XML contains `gr044runtimeeditpassed` |
| [`runtime/deckcraft-host-reopen.png`](runtime/deckcraft-host-reopen.png) | `ad7f5bb23798b640fca0f266fd516f50586f739fc93d2e4ced86bcaa2987cdea` | Chromium screenshot after fresh iframe reopen; shows saved text, clean editor, matching ticket and payload hash |

## Independent reviews

- [R1 review](REVIEW-NEMOTRON.md): **PROVISIONAL PASS**, bounded browser smoke; its `sessionStorage` note was corrected after review.
- [R2 review](REVIEW-NEMOTRON-R2.md): **PROVISIONAL PASS**, revalidated the corrected host and evidence hashes, with no blockers or major findings.
- Both reviews leave Seafile persistence, source/build provenance, and production paths unverified. Final disposition remains **GPT REVIEW PENDING**; upstream publication remains locked.

## Follow-up provenance checks

After R2, the parent workspace independently checked the available local build
cache:

- DeckCraft checkout `HEAD` is `0f4fffcf6c71ffa16029d07ac23752fedd783547`;
  `Cargo.lock` pins `craft-platform` to
  `56c5e16d79b77751106173c13111ef4fe0a2c0ec`.
- The stored GR-020 patch hash is
  `8d7f98468ce446add5357e10ed8e10e729eb3306fee359d320f09805acc3ee4a`.
  It applies to a fresh worktree of that base using
  `git apply --unidiff-zero`; all 10 changed paths then hash identically to
  the locally patched build checkout.
- The cached Trunk WASM hashes to
  `eebe27c9c42ee46be33e1285b37a9d8d51d5108ff70182fdea3110c5a9835ee9`,
  matching the build artifact recorded above.

These checks connect the pinned base, stored patch, patched source tree and
cached WASM by content. The parent did not rebuild the WASM, and the original
build logs are not retained; a fresh reproducible build remains **NOT
VERIFIED**.

## Reproduction

The pinned, locally patched DeckCraft source was built from
`/home/roddy/.cache/artcraft-deckcraft-gr020`:

```sh
cargo +1.95.0 build -p deckcraft-web --release --target wasm32-unknown-unknown --locked
cd apps/deckcraft-web
RUSTUP_TOOLCHAIN=1.95.0 trunk build --release
```

Serve the generated `dist/web` as `deckcraft/` beside `runtime/host.html` and
`runtime/synthetic.pptx` on one local HTTP origin, then open `host.html` in
Chromium. Use the visible slide text editor to replace the text, press Ctrl+S,
and click **Reopen saved bytes**. The harness displays the payload size, SHA-256,
ticket and fresh-editor reopen status. The fixture can be recreated with:

```sh
python3 docs/reviews/GR-044/runtime/make_fixture.py
```

The recorded DeckCraft source pin is
`0f4fffcf6c71ffa16029d07ac23752fedd783547`; the Cargo lock transport pin is
`56c5e16d79b77751106173c13111ef4fe0a2c0ec`. The GR-020 patch SHA-256 is
`8d7f98468ce446add5357e10ed8e10e729eb3306fee359d320f09805acc3ee4a`.

The parent retains bytes only in browser page memory (`savedBytes`) and passes that buffer to the fresh iframe; no browser storage or platform persistence is involved. Seafile version creation,
Seafile-backed reopen, dispatcher behavior, production and ONLYOFFICE were not
part of this run and remain **NOT VERIFIED**. A synthetic host ACK is not a
durable storage write. No upstream changes were made.
