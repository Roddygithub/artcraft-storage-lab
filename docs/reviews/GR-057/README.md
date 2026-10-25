# GR-057 evidence — PdfCraft reproducible candidate

Implementation worktree base: `247ae75753d4d22c7567b53271b3bf0c0d119f99`.
Candidate: `/home/roddy/.cache/artcraft-storage-lab/gr057-pdfcraft-static/pdfcraft`
(outside `integration/static/` and dispatch).

## Exact source, patch and transport

```text
git clone https://github.com/storytold/pdfcraft.git /home/roddy/.cache/artcraft-storage-lab/gr057-source/pdfcraft
git -C /home/roddy/.cache/artcraft-storage-lab/gr057-source/pdfcraft fetch origin 57e531ccca0047597809748b5cb4276336d6051a
git -C /home/roddy/.cache/artcraft-storage-lab/gr057-source/pdfcraft checkout --detach 57e531ccca0047597809748b5cb4276336d6051a
git -C /home/roddy/.cache/artcraft-storage-lab/gr057-source/pdfcraft rev-parse HEAD
```

Observed HEAD: `57e531ccca0047597809748b5cb4276336d6051a`.

```text
sha256sum docs/reviews/GR-017/patches/pdfcraft-durable-host-ack.patch
git -C /home/roddy/.cache/artcraft-storage-lab/gr057-source/pdfcraft apply --check docs/reviews/GR-017/patches/pdfcraft-durable-host-ack.patch
git -C /home/roddy/.cache/artcraft-storage-lab/gr057-source/pdfcraft apply docs/reviews/GR-017/patches/pdfcraft-durable-host-ack.patch
```

Patch SHA-256: `6d50eb1f45e81f2037948cd6160878feb2d87eb0881d167f0fc1d290e4450562`.
The patch was applied once to the clean pinned source. It pins
`craft-platform` to immutable commit `90c261de22ef75c4c7c5c5cd1c712d483be0bbc8`;
the resulting Cargo lockfile SHA-256 is
`190c8a287c2010654192ecce2eb28b38aecb160a95fb5da62f9a6da774a88066`.
The lock source and successful build's `Compiling craft-platform ...#90c261de`
line confirm the transport resolution.

## Toolchain and build

Versions used: Rust 1.95.0, Cargo 1.95.0, Trunk 0.22.0,
`wasm32-unknown-unknown`. The checkout's `index.html` originally used
`data-wasm-opt="z"`. The documented build-only overlay was applied:

```sh
sed -i 's/data-wasm-opt="z"/data-wasm-opt="0"/' apps/pdfcraft-web/index.html
sha256sum apps/pdfcraft-web/index.html
```

Overlay index SHA-256:
`e1a34a29221432c5612c0b953f6c4cc7f5d5c6176c046b98ef728c78f0a58539`.
The stored patch was not modified by this overlay.

```sh
cd /home/roddy/.cache/artcraft-storage-lab/gr057-source/pdfcraft/apps/pdfcraft-web
CARGO_TARGET_DIR=/home/roddy/.cache/cargo-target \
TMPDIR=/home/roddy/.cache/cargo-tmp \
CARGO_BUILD_JOBS=2 \
CARGO_PROFILE_RELEASE_DEBUG=0 \
CARGO_INCREMENTAL=0 \
RUSTUP_TOOLCHAIN=1.95.0 \
trunk build --release --locked \
  --dist /home/roddy/.cache/artcraft-storage-lab/gr057-pdfcraft-static/pdfcraft --verbose
```

Exit 0. The corrected Trunk build completed successfully; warnings were existing
dead/unused code in PdfCraft crates. Verbose output explicitly says
`wasm-opt is turned off` for `data-wasm-opt="0"`. The staged WASM is unoptimized
by Trunk's Binaryen step. Build paths and temporary output were under
`/home/roddy/.cache`, never `/tmp`. See [`commands.sh`](commands.sh) for the full
rerunnable sequence.

## Candidate file inventory

The exact staged file set, sizes, SHA-256 values and explicit index references
are in [`checks/hash-inventory.json`](checks/hash-inventory.json). Run:

```sh
python3 docs/reviews/GR-057/verify_candidate.py
```

The verifier checks exact file membership, byte counts, hashes and that index
references are manifested. It ignores Trunk's empty `.trunk-lock` metadata
file; the three served candidate assets are:

| File | Bytes | SHA-256 |
|---|---:|---|
| `index.html` | 1,210 | `3a6e2ec1bad7f1f495256502bcfb525646267681c7b66577d689475ace33264c` |
| `pdfcraft-web-a30dc4dd8a148def_bg.wasm` | 49,909,107 | `fcf3e3721c399fd695d3e431689f35b83e81b94960bd5d1eb57e1614ba5dcec4` |
| `pdfcraft-web-d3ba543cb17a7f63.js` | 165,584 | `84eea07a552e7c98b12c837f086c4da2364a285a5d468ad8ffc0f082fda0e042` |

## Chromium smoke

Run the actual built WASM with the repository's Playwright Chromium installation:

```sh
uv run --with playwright --python 3.14 -- python -u docs/reviews/GR-057/runtime/test_pdfcraft_host_roundtrip.py \
  --candidate /home/roddy/.cache/artcraft-storage-lab/gr057-pdfcraft-static/pdfcraft \
  --fixture /home/roddy/.cache/artcraft-storage-lab/gr057-source/pdfcraft/crates/ui-egui/tests/data/form.pdf \
  --evidence-dir docs/reviews/GR-057/runtime
```

Result: **PASS**. The 1,744-byte synthetic AcroForm fixture
(`c6f8b656e225101129aa36bd5467adc8dba16730915f19caca17f6a546d0b040`) opened;
the in-editor form field visibly changed to `GR-057 visible PDF form edit` and
dirty became true. Ctrl+S delivered 2,403 bytes with SHA-256
`d99a53e45b423d664f97cf3f7f7873643a6dd4c73b6feca4b5f60db9e4faf2c2` and ticket
`pdfcraft:1`. The host retained these bytes in browser memory, sent the matching
positive `pdfcraft:saveResult`, and PdfCraft reported dirty false. The harness
then created a fresh iframe and supplied the captured bytes; the edit was
visibly rendered again. `browser-evidence.json` records dirty sequence
`false → true → false → false`, two ready events, and no page errors. The raw
HTTP transcript is in [`runtime/browser-smoke.txt`](runtime/browser-smoke.txt);
screenshots are `opened.png`, `edited.png`, and `reopened.png`.

This is an in-memory parent ACK, **not** a Seafile write/version. No Seafile,
Proxmox, ONLYOFFICE, production server, credential, or upstream repository write
was used. Independent review remains pending; GR-017's previous patch reviews
do not constitute review of this exact candidate.
