# GR-035 evidence bundle — PhotoCraft optimized Web smoke

## Artifact

| File | SHA-256 | Purpose |
|---|---|---|
| [Optimized host reopen screenshot](runtime/photocraft-optimized-host-reopen-20261025.png) | `0cd7648a1921ad00199f8896e7a5264941f2fbd52e7838d30544b28097e5f2f4` | Fresh iframe shows the saved `Layer 1` and host state `dirty=false` |

## Recorded browser observations

- The optimized PhotoCraft WASM and JS files loaded with HTTP 200 in the T3
  Chromium preview.
- The GR-033 host harness opened the 4,000-byte synthetic fixture.
- UI-created `Layer 1` changed the app to dirty.
- Ctrl+S posted ticket `photocraft:73ca0f8a5ac6f87c3dd6fdc34c4a67c2:1` with
  4,984 bytes (SHA-256
  `92e93c2b993b7de073a2c870aba522d7f9112647d9d1181d2b8592df665936b3`).
- The parent echoed that ticket in a success `photocraft:saveResult`. The
  app reported clean, then the harness created a new iframe and reopened the
  captured bytes; `Layer 1` was visible and dirty state was false.

## Independent review

Nemotron 3 Ultra returned **PROVISIONAL ACCEPT** for this bounded smoke, with no
blocker or major finding. Minor qualification: the screenshot does not identify
the WASM resource hash Chromium loaded; the recorded optimized WASM exists and
its source build configuration enables `wasm-opt -Oz`, but the capture alone
does not bind the browser run to that exact file. The earlier phrase “durable-result”
was corrected in the test matrix to “matching positive ACK”; the parent ACK was
in-memory only.

## Boundary

The harness is an in-memory parent. It did not call the ArtCraft gateway or
Seafile. This bundle adds optimized-build runtime evidence only; it does not
establish durable storage, Seafile history/version creation, or storage-backed
reopen. Source, command, sizes and limitations: [GR-035 assessment](../../GR-035-PHOTOCRAFT-OPTIMIZED-BROWSER-SMOKE.md).
