# GR-017 PdfCraft runtime smoke — current patch

**Date:** 2026-10-24
**PdfCraft base:** `57e531ccca0047597809748b5cb4276336d6051a`
**Current patch SHA-256:** `de30f47e823536c8b99d4d718a0731f8afdc1f56537deceec3d77f9ffda7fbf5`

## Build

From `/tmp/artcraft-gr017-pdfcraft/apps/pdfcraft-web`:

```sh
CARGO_BUILD_JOBS=2 CARGO_PROFILE_RELEASE_DEBUG=0 CARGO_INCREMENTAL=0 trunk build --release
```

Result: exit 0; Trunk 0.22.0; Rust 1.97; release build completed and Trunk
finished `wasm-opt -Oz`. Existing unused/dead-code warnings were emitted.

Built WASM: `pdfcraft-web-7c8b38b8f742e1b5_bg.wasm`, SHA-256
`2dda4ff36e8259a687f30827ca2fe7fe1fefc76b3958ec3beb9c4daccf97567c`.

## Chromium flow

Served the built app and [`runtime/host-test.html`](runtime/host-test.html) from
a local HTTP server on port 8766. The harness uses the app's real release WASM
and the pinned source fixture `crates/ui-egui/tests/data/form.pdf` (copied into
the served directory as `form.pdf`). It is an in-memory `sessionStorage` host,
not Seafile.

1. The host received `pdfcraft:ready` and sent `form.pdf` to the iframe.
2. Typed `r4-exact-host-ack` into a PDF form field. The dirty sequence was
   `[false, true]` before saving.
3. Ctrl+S emitted ticket `pdfcraft:1` with 2,385 serialized bytes. The synthetic
   host stored them in `sessionStorage` and sent a successful matching
   `pdfcraft:saveResult`; dirty became false, yielding `[false, true, false]`.
4. Reloaded the iframe from the stored bytes. Fresh PdfCraft rendered
   `r4-exact-host-ack`; see [`pdfcraft-host-reopen-r4.png`](pdfcraft-host-reopen-r4.png).

Stored-byte evidence: 2,385 bytes; SHA-256
`1912e0529d9b051828c895e25865f4392fa0554bab1d00f636b4641aff325b84`.
Browser network log showed HTTP 200 for the host page, editor index, JS, WASM,
and fixture. This verifies the current patch's browser delivery/ACK/reopen path
against the synthetic host. It does **not** verify a Seafile API write, new
Seafile version, failure/retry, timeout, or production deployment.
