# GridCraft v0.12.1 refresh candidate

**Status: PROVISIONAL candidate; actual-WASM synthetic in-memory host roundtrip PASS. Seafile E2E NOT VERIFIED.**

- Exact upstream source: `f86aec12dabc744b5f75e1033f87bfe685e78481`; release patch SHA-256: `bfe4a5ee134b204242b73356376797f225ecc376889290681a38824a87ffa8f0`.
- Exact-base patch application, locked Rust 1.95 WASM check, focused engine (3) and UI (2) tests passed. Logs are in `../checks/gridcraft-apply.txt`, `gridcraft-wasm-locked.txt`, `gridcraft-engine-host.txt`, and `gridcraft-ui-host.txt`.
- Release build used Rust 1.95, Trunk 0.22, `--release --locked`, and Trunk wasm-opt version 131 enabled by the source `data-wasm-opt="z"` setting; the exact optimizer invocation was not retained. The complete command/output and asset digests are in `../checks/gridcraft-release-build-r2.txt`; bundle hashes and byte sizes are in `../checks/gridcraft-bundle-manifest.json`.
- The actual-WASM browser smoke edits an active cell, presses ordinary Ctrl+S, observes one synthetic in-memory version and durable ACK/clean state, then opens the saved workbook in a fresh GridCraft session. The current test-source SHA-256 is `fcdec05456b6203f4220bff50ca61b680b240944ee3ff09ddbcc5dcdb1d5277c`. Its retained log hashes index, icon, JS, and WASM in the actual served static directory before and after; all four pairs are unchanged and match the bundle manifest. See `../checks/gridcraft-browser-smoke-r4.txt`.
- The smoke uses a synthetic in-memory storage adapter. It does not establish Seafile history, durable readback, or Seafile fresh reopen. Replacement/Save As serializer-entry counts are also **NOT VERIFIED** for this release smoke.

No dispatcher promotion, deployment, Seafile settings change, or ONLYOFFICE change occurred.
