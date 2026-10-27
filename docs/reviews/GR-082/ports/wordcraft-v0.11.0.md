# WordCraft v0.11.0 refresh candidate

**Status: PROVISIONAL candidate; synthetic in-memory host smoke PASS. Seafile E2E NOT VERIFIED.**

- Upstream release commit: `e31f2f06a5f8004ceaa88f68c00b47908e321aa4`.
- Port patch: `wordcraft-v0.11.0.patch`, SHA-256
  `5255bafd67ade004466218409c5d2ca320f190bbf5f08152b02b582997377e10`.
- Locked Rust 1.95 WASM check and focused engine/UI tests passed earlier; logs
  are `../checks/wordcraft-wasm-locked.txt`, `../checks/wordcraft-engine-host.txt`,
  and `../checks/wordcraft-ui-host.txt`.
- Release build used Rust 1.95, Trunk 0.22, `--release --locked`, and the
  documented build-only `data-wasm-opt=0` overlay. The cold build took 10m47s;
  an incremental build retained exit 0 in
  `../checks/wordcraft-release-build-r1.txt`.
- The four staged bundle files and SHA-256 values are recorded in
  `../checks/wordcraft-bundle-manifest.json`. The generated candidate remains
  under the cache path recorded in that manifest, outside Git and outside the
  active dispatcher.
- The actual-WASM host smoke passed: edited synthetic DOCX bytes were saved to
  the in-memory storage adapter, one new version was created, the host received
  the durable save result and editor clean acknowledgement, and a fresh session
  reopened the document; copying the rendered editor text confirmed the marker.
  See `../checks/wordcraft-browser-smoke-r9.txt`; the log includes the exact test-source SHA-256 and hashes of the actual served index/icon/JS/WASM files before and after the run. R8 is retained as historical evidence; R9 is final.

The harness records visible state history so the transient `opened` status is
not missed, and checks the marker in text copied from the reopened editor. The
message observer starts after initial open, so it asserts the post-save
`dirty=false` acknowledgement. Earlier failed diagnostic runs remain retained
under `../checks/wordcraft-browser-smoke-r*.txt`; the final provenance-complete pass is R9.

This does not establish synthetic Seafile persistence, History versioning,
readback from Seafile, production behavior, or ONLYOFFICE preservation. No
route, settings, service, or upstream repository was changed.
