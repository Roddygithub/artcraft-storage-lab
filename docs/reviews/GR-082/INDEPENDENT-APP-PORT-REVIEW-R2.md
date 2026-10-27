# GR-082 Wave 1 app-port review R2

**Verdict: PROVISIONAL — R1 packaging corrections verified; two MEDIUM findings remain.** Read-only review; no files edited, builds/tests run, browser/services accessed, deployment performed, or publication made.

## Remaining findings

1. **MEDIUM — final validation evidence incomplete.** The retained WordCraft and
   GridCraft WASM logs ended during compilation without completion records.
   Their retained focused host-test logs show WordCraft 2 engine / 9 UI passes
   and GridCraft 3 engine / 2 UI passes. PhotoCraft's report referred to final
   `*-r2.log` files outside the reviewed artifact bundle; the retained JSON
   still records its first web-test attempt failing with exit 101. Final WASM
   completion and PhotoCraft's corrected 19-test result were not independently
   verifiable from the retained files.
2. **MEDIUM — PdfCraft native qualification remains open.** The port report
   records host ACK tests as unverified after timeout and does not cover the
   upstream save/edit/prompt regressions.

## Verified corrections

- All five release clone HEADs match the requested exact commits; VectorCraft is
  clean and report-only.
- Four final patch files apply against their exact release indexes and match
  the source-clone patch content.
- GridCraft patch includes `.xlsx` name and content-sniff rejection before
  generic open.
- PhotoCraft and PdfCraft include the local transport snapshot and relative
  path dependency.
- Each transport checksum manifest verifies 17/17 entries; no stale lab-root
  Cargo entries remain. Each packaged `browser/host.rs` hashes to
  `dfd3d3e2d2dde7d9a630e487ea79d6b3adf0085266d7480825900e912d0a9dda`.

Final patch digests are recorded in
[`port-manifest.json`](port-manifest.json). Browser/Seafile acceptance and
project GPT approval remain **NOT VERIFIED**.
