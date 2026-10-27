# Response to app-port review R1

Disposition of R1's five findings:

| Finding | Response |
|---|---|
| GridCraft patch omitted XLSX sniff/extension admission | Added the check before generic open. Host engine tests now pass 3/3, including invalid XLSX rejection. Regenerated patch includes the fix. |
| PhotoCraft patch omitted local transport snapshot | Added `integration/craft-platform` to the patch; app manifest and lockfile use the relative path. Package `SHA256SUMS` passes, the regenerated patch applies to the exact release index, and the locked offline WASM check passed after the path change. |
| WordCraft/GridCraft stale transport packaging checksums | Regenerated both patches from corrected source clones. The relocated checksum lists retain package files only and no `../../../Cargo.toml` or `../../../Cargo.lock` entries. |
| Validation not bound to final patches | Retained final patch hashes and clean-base apply checks in the GR-082 bundle. WordCraft locked WASM passes; engine host tests pass 2/2 and UI host tests 9/9. GridCraft locked WASM passes; engine host tests pass 3/3 and UI host tests pass 2/2. PhotoCraft's final local-path tree passes the locked WASM check and the standalone confirmation test (1/1); engine snapshot and Web/UI host suites were cancelled and remain NOT VERIFIED. Its earlier 19-test result predates the local-path packaging change. |
| PdfCraft qualification/dependency | Switched the transport dependency to the included local snapshot and regenerated the patch. Exact-base apply, package checksums and locked WASM pass. Final host ACK tests pass 8/8 and the UI `editing::` regression group passes 30/30; full-app/browser behavior remains open. |

These changes close only the artifact/source findings subject to independent R2
verification. No candidate has browser or Seafile version/readback/fresh-reopen
evidence. VectorCraft is a separate no-code-port assessment. Per-app R2 review
is pending. No route promotion, deployment, ONLYOFFICE change or publication
occurred.
