# GR-057 — PdfCraft reproducible candidate

Date: 2026-10-25. Result: **exact patched source built; actual-WASM Chromium
synthetic host roundtrip PASS**. Independent R1–R2 reviews: **PROVISIONAL PASS**;
R1's documentation MINOR is corrected. Work-item state: **GPT REVIEW PENDING**.
Project verdict remains **INCOMPLETE** and
upstream publication remains locked.

## Candidate and scope

PdfCraft Web was built from `storytold/pdfcraft` source
`57e531ccca0047597809748b5cb4276336d6051a`, with the exact GR-017 durable host
ack patch and `craft-platform` transport pinned to
`90c261de22ef75c4c7c5c5cd1c712d483be0bbc8`. The output is staged at
`/home/roddy/.cache/artcraft-storage-lab/gr057-pdfcraft-static/pdfcraft`,
outside dispatch. The candidate's three served assets are index, JS and WASM;
Trunk also leaves an empty `.trunk-lock` file. File sizes,
SHA-256 values and index references are pinned in [the inventory](reviews/GR-057/checks/hash-inventory.json)
and checked by [the verifier](reviews/GR-057/verify_candidate.py).

The actual built WASM passed a Chromium run with the synthetic AcroForm fixture
from the pinned PdfCraft checkout. A form value changed visibly, made the
document dirty, and Ctrl+S sent 2,403 bytes under ticket `pdfcraft:1`. The
synthetic same-origin parent retained the bytes in memory and returned a
positive matching acknowledgement. PdfCraft reported dirty false; a fresh
iframe reopened those saved bytes and rendered `GR-057 visible PDF form edit`.
The host harness, test script, browser JSON, transcript and screenshots are in
[the evidence bundle](reviews/GR-057/README.md).

This is **not** Seafile persistence: no Seafile endpoint was contacted, no file
version was created there, and no real server or production data was changed.
The parent-discovered read-only 404 for `/thirdparty-editor/file-save/` is
context only, not a test in this work item. Dispatch and `integration/static/`
were not changed. No credentials, personal data, ONLYOFFICE configuration or
upstream issue/PR/RFC were used. The candidate has not been promoted.

## Exact build inputs

| Input | Evidence |
|---|---|
| Base commit | Requested repository parent `247ae75753d4d22c7567b53271b3bf0c0d119f99` (`git rev-parse HEAD`) |
| PdfCraft source | `https://github.com/storytold/pdfcraft`, detached at `57e531ccca0047597809748b5cb4276336d6051a` |
| Stored patch | `docs/reviews/GR-017/patches/pdfcraft-durable-host-ack.patch`; SHA-256 `6d50eb1f45e81f2037948cd6160878feb2d87eb0881d167f0fc1d290e4450562`; `git apply --check` passed, then that file was applied once |
| Transport | `craft-platform` from `https://github.com/Roddygithub/artcraft-storage-lab.git`, exact revision `90c261de22ef75c4c7c5c5cd1c712d483be0bbc8`; app `Cargo.toml` and `Cargo.lock` pin the same revision, build log shows Cargo compiling `craft-platform` at `#90c261de` |
| Patched lockfile | SHA-256 `190c8a287c2010654192ecce2eb28b38aecb160a95fb5da62f9a6da774a88066` |
| Toolchain | Rust/Cargo 1.95.0 (`rustc 1.95.0 (59807616e 2026-04-14)`), Trunk 0.22.0, `wasm32-unknown-unknown` installed |
| Build overlay | `sed -i 's/data-wasm-opt="z"/data-wasm-opt="0"/' apps/pdfcraft-web/index.html`; resulting index SHA-256 `e1a34a29221432c5612c0b953f6c4cc7f5d5c6176c046b98ef728c78f0a58539` |
| Build command | `CARGO_TARGET_DIR=/home/roddy/.cache/cargo-target TMPDIR=/home/roddy/.cache/cargo-tmp CARGO_BUILD_JOBS=2 CARGO_PROFILE_RELEASE_DEBUG=0 CARGO_INCREMENTAL=0 RUSTUP_TOOLCHAIN=1.95.0 trunk build --release --locked --dist /home/roddy/.cache/artcraft-storage-lab/gr057-pdfcraft-static/pdfcraft --verbose` from `apps/pdfcraft-web`; exit 0 |
| Optimizer observation | Correct overlay was confirmed in source. Trunk 0.22.0 verbose log says `wasm-opt is turned off`; staged output is unoptimized by Binaryen. Chromium passed on this output. |

The complete literal command sequence and outcomes are in [commands](reviews/GR-057/commands.sh)
and [checks](reviews/GR-057/checks/). Cargo target and temporary output remained
under persistent `/home/roddy/.cache` paths; no Rust artifacts were directed to
`/tmp`.

## Browser result

Fixture: 1,744 bytes, SHA-256
`c6f8b656e225101129aa36bd5467adc8dba16730915f19caca17f6a546d0b040`. Saved
bytes: 2,403, SHA-256
`d99a53e45b423d664f97cf3f7f7873643a6dd4c73b6feca4b5f60db9e4faf2c2`. Dirty
sequence: `[false, true, false, false]`; ready count: 2; page errors: none.
Screenshots show the initial form, visible dirty edit and fresh reopened value.
The evidence details which parent behavior was synthetic. No result here
establishes a Seafile version, host integration against the discovered server,
dispatch behavior or production deployment.

## Review and remaining work

Independent review R1–R2 returned **PROVISIONAL PASS**; see
[`INDEPENDENT-REVIEW-R1.md`](reviews/GR-057/INDEPENDENT-REVIEW-R1.md). The GR-017 patch's older code/runtime reviews
are background evidence only; they do not review this exact source/transport/
build artifact. Exact candidate Seafile save/version/readback/reopen is
**NOT RUN**. The recorded build confirms Trunk disabled `wasm-opt` for the
`data-wasm-opt="0"` overlay; optimized-vs-functional output was not compared.
This candidate remains uncommitted, unpublished and outside dispatch pending
project GPT review.
