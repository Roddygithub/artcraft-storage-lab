# GR-082 Wave 1 — VectorCraft source qualification

Status: **PROVISIONAL; exact-release synthetic memory-host smoke passed; GPT REVIEW PENDING**. 2026-10-27.

**Decision: no integration code port identified. Rebuild/requalify v0.17.0 using the existing gateway page API/polling adapter. The follow-up below qualifies only the synthetic memory-host page-API workflow; it is not a Seafile or release-acceptance PASS.** No durable VectorCraft host-save patch is present in the retained integration or required to port for this release comparison.

## Exact inputs and method

- Old base: `v0.14.0`, `ad0566943ab9741e6356bbc9b53c3cc09895068d` (GR-058 inventory source identity).
- Target: `v0.17.0`, `43313f9451de7ab5b909801006b8881458f2bf04`. `git rev-parse HEAD v0.17.0` in `/home/roddy/.cache/artcraft-storage-lab/upstream-refresh-sources/vectorcraft` returned this SHA twice; `git status --short` returned no changes.
- The supplied target clone is shallow and lacks the old object (`git diff OLD NEW` returned `fatal: bad object ad056...`). To avoid changing that clone, retrieved the exact old source archive from https://codeload.github.com/storytold/vectorcraft/tar.gz/ad0566943ab9741e6356bbc9b53c3cc09895068d into the external output directory. Archive source is commit-addressed; old tag identity comes from retained GR-058 evidence, not a newly resolved tag.
- Compared file bytes and source diffs against target checkout. Retained evidence: [`vectorcraft-evidence/surface-comparison.json`](vectorcraft-evidence/surface-comparison.json), [`changed-paths.txt`](vectorcraft-evidence/changed-paths.txt), and focused `*.diff` files in that directory. The changed-path list inventories target files changed/added relative to old, not removed files. The exact old-source archive remains in the external research output cache.
- Read retained `integration/gateway/hostpage.py`, `tests/test_vectorcraft_candidate_host.py`, `docs/GR-058-VECTORCRAFT-REPRODUCIBLE-CANDIDATE.md`, its inventory, and `docs/GR-063-VECTORCRAFT-REAL-SEAFILE-ROUNDTRIP.md`.

## Adapter compatibility

| Surface | Exact source evidence | Assessment |
| --- | --- | --- |
| Page API | Target `apps/vectorcraft-web/src/api.rs:59-67,146-191`; entire file byte-identical to old | `openFile(name, Uint8Array)` still synchronously returns queued boolean; capture toggle remains synchronous; `files()` returns `{path,size}[]`; `readFile(name)` returns Uint8Array or throws. Gateway's await on synchronous results remains valid. |
| Captured save storage | `apps/vectorcraft-web/src/saved_files.rs:3-39`, byte-identical | Basename keyed, latest save replaces same basename; maximum 16 entries. No new save/dirty/host-ACK event. |
| Web save/download path | Entire `apps/vectorcraft-web/src/web.rs`, byte-identical; `download` at 557 onward | Capture remains the gateway's bridge. Successful local capture is not remote Seafile persistence or native host confirmation. |
| Bootstrap/assets | `src/main.rs`, `index.html`, `Trunk.toml`, `src/fonts.rs`, `crates/text/build.rs` byte-identical (SHA-256 manifest) | No identified API/bootstrap port. New compiled JS/WASM and manifest hashes must be recorded. |
| Retained gateway | `integration/gateway/hostpage.py:138-231` | Same-origin API access, capture before open, 700ms polling, original filename lookup, exact-byte baseline, POST and failed-save retry remain applicable by source inspection. |

The gateway selects an entry with `path.endsWith(FILE_NAME)` and reads `FILE_NAME`; it follows the original filename only. Renamed exports, other formats, multiple outputs and basename collisions remain limitations to exercise or explicitly exclude. These are existing constraints, not newly introduced API breaks. Capture storage is bounded; SVG sidecar resources are not a multi-file Seafile save contract.

## Changed semantics requiring rebuild/tests

Paths below are relative to the exact target clone; focused diffs preserve both old and target context.

| Change established by source | Qualification needed |
| --- | --- |
| `crates/ui-egui/src/io.rs:444-517` and `tests_saveext.rs:161-215,400+`: save/export extension normalization replaces known incompatible extensions, preserves matching case/aliases, distinguishes picked format and suggested extension | Repeat File → Export → SVG with the original basename; verify capture is found and posted. Exercise cancellation, changed basename, mixed-case extension and wrong format without falsely claiming the original file was saved. |
| `crates/engine/src/cmd/fileio/save.rs:240-287,291-414`: conflicting top-level/options values rejected; irrelevant native options produce notes; remembered artboard picks follow artboard identity/reordering/deletion | Repeat app.save harness and UI export; test repeated save after artboard edits where supported. Do not assume prior option handling or error text. |
| `crates/engine/src/cmd/fileio/svg.rs:181-185`; `crates/svg/src/export.rs:146-147,671+`: selected-artboard title, foreign namespace attributes, generated IDs and image handling changed | Validate SVG geometry and representative text/images/foreign metadata through export and fresh import; compare persisted bytes to the actual new editor output, not old golden serializer bytes. |
| `crates/svg/src/import.rs:36-75,105+`: entity expansion guard, depth prescan/height and nested-image resolver/warnings changed | Repeat synthetic.svg import and malformed/deep/entity-heavy SVG rejection; representative nested-image SVG should not silently lose content. |
| `crates/ui-egui/src/shortcuts.rs:425,585,673+`, new `keymap.rs`: craft-keymap dispatcher replaces prior shortcut handling | Exercise Ctrl+S, dialog cancellation and menu SVG export; do not infer keyboard behavior from unchanged page API. |
| `Cargo.toml:15-24,40,60,141+`, `apps/vectorcraft-web/Cargo.toml:17`: craft-pdf/backend revisions change, craft-keymap/window dependencies added; engine workspace default fonts disabled, web explicitly requests bundled-fonts | Fresh locked WASM/release build, fonts/assets smoke and new provenance. Rust minimum stays 1.95. Release workflow still uses common actions at mutable main; preserve resolved build inputs. No compilation was run here. |

## Historical assessment and required wider qualification

### Follow-up locked check (2026-10-27)

After the source-only assessment, `cargo check --locked --target
wasm32-unknown-unknown -p vectorcraft-web` under Rust 1.95.0 passed with exit 0
in 295.301 seconds on exact release commit `43313f9451de7ab5b909801006b8881458f2bf04`.
Full command output and before/after clean-tree provenance are retained in
[`../checks/vectorcraft-wasm-locked.txt`](../checks/vectorcraft-wasm-locked.txt).
This compiles the WASM target but does not build release assets or validate
fonts, browser capture/save, or Seafile persistence.

GR-058 documents an unpatched v0.14.0 source-built candidate, optional pinned-font gaps, and a local synthetic-storage roundtrip. Its runnable harness calls `vectorcraft.request('app.save', {path:'synthetic.svg',svg:{}})` (`tests/test_vectorcraft_candidate_host.py:90`) and compares captured bytes, then checks geometry on fresh reopen. Re-run it against the rebuilt target; it was not run for this assessment.

GR-063 lines 19-41 document Ctrl+S opening Save As (cancelled), then SVG export captured and posted automatically, host version confirmation, Seafile history and a distinct fresh session showing the edit. The native dirty asterisk remained; first editor was not explicitly closed. Editor-export versus Seafile-readback byte identity was NOT VERIFIED. These remain historical v0.14.0 observations, not v0.17.0 validation and not a durable host-save ACK proof.

For target qualification: build/hash inventory; run local candidate harness; then separately authorized synthetic Seafile UI export → automatic gateway POST → new version → visible host confirmation → explicitly close → fresh reopen, with exact editor-output/storage-readback bytes and geometry checks. Exercise failed-save retry, no-op repeated polling and concurrent-update rejection. Native dirty-marker and original-filename limitations must remain explicit. Existing ONLYOFFICE behavior requires its normal regression gate; nothing was changed or accessed here.

## Scope

The original source assessment above preceded this runtime follow-up. This lane changed only the VectorCraft report, checks, runtime evidence and app-specific test. No adapter/source patch was needed. No Seafile, dispatcher, ONLYOFFICE, active route, deployment, shared summary or port-manifest changes; no commit, push or upstream publication. Independent review and GPT/release/publication gates remain outstanding.


## Exact-release runtime follow-up — 2026-10-27

**PROVISIONAL: synthetic in-memory capture/save/explicit-close/fresh-reopen succeeded.**
This uses the retained gateway `render()` and unpatched `window.vectorcraft` API.
Storage is a process-local byte variable in a loopback-only test HTTP server;
`synthetic-v1` is a test response, not a Seafile version. No shared adapter was invented.

### Build and commands

Worktree base: `b538b6032ef50e013fdea67365cb626666678ad0`, branch
`upstream-refresh/wave-1`. Source remained clean at exact tag/commit
`v0.17.0` / `43313f9451de7ab5b909801006b8881458f2bf04` before build,
after the timeout, and after the successful retry (source identity/status logs).

| Command / input | Exit / evidence |
| --- | --- |
| `python3 -u docs/reviews/GR-082/runtime/vectorcraft/run_qualification.py` | 124; full first release log [`vectorcraft-release-build-r1.txt`](../checks/vectorcraft-release-build-r1.txt). Cargo completed in 26m 50s; overall Trunk pipeline timed out at 1800.014s during post-processing. Not a successful first build. |
| `python3 -u docs/reviews/GR-082/runtime/vectorcraft/run_release_retry.py` | 0; [`vectorcraft-release-build-r2.txt`](../checks/vectorcraft-release-build-r2.txt), 955.108s. Same release command, completed Cargo cache reused (0.46s), successful post-build font hook. |
| Exact build argv, both attempts | `trunk build --release --locked --dist /home/roddy/.cache/artcraft-storage-lab/upstream-refresh-outputs/vectorcraft-v0.17.0-static/vectorcraft`, cwd source `apps/vectorcraft-web`; `PATH=/home/roddy/.cargo/bin:/home/roddy/.local/bin:$PATH RUSTUP_TOOLCHAIN=1.95.0 CRAFT_FONTS_DIR=/home/roddy/.cache/artcraft-storage-lab/upstream-refresh-sources/vectorcraft-craft-fonts CRAFT_FONTS_REQUIRED=1`. |
| Toolchain | rustc 1.95.0 (`59807616e`), cargo 1.95.0 (`f2d3ce0bd`), Trunk 0.22.0; Trunk-managed wasm-bindgen 0.2.129 and wasm-opt v131 `-Oz`. Version logs and [`vectorcraft-build-inputs.json`](../checks/vectorcraft-build-inputs.json) retain binary hashes. |
| Fonts | Source release-workflow pin `a71c20e30af613287c504f7e685ca8fad77752bc`; clone/checkout exits 0 in separate logs. Manifest SHA-256 `ba26303ae75c4469104ea9dc54f828e7769e0e0259303e15f532c80ca4ed577e`. Embedded BIZ UDPGothic Regular and copied Noto Sans Arabic/Thai/Georgian with OFL files. Exact missing optional-face warning retained in both build logs; no substitution. |
| Rust output location | Persistent source `target/`, including release, wasm-bindgen and wasm-opt subdirectories. `CARGO_TARGET_DIR` and `TMPDIR` unset; neither overridden to `/tmp`. No active cache removed. |
| `python3 -u docs/reviews/GR-082/runtime/vectorcraft/run_smoke.py` — original R1 | 1 in 16.404s; [`vectorcraft-browser-smoke-r1.txt`](../checks/vectorcraft-browser-smoke-r1.txt). Save/reopen assertions reached, but Chromium evicted the large WASM response from inspector cache; `Response.body` failed, so final asset-evidence assertion failed. Original test/runner retained as `test-failed-r1.py.txt` / `run-smoke-r1.py.txt`, input hashes in `vectorcraft-test-inputs-r1.json`, partial browser evidence in `browser-evidence-r1.json`. This is a failed test, not a pass. |
| Same smoke entrypoint — corrected R2 | 0 in 16.221s; [`vectorcraft-browser-smoke-r2.txt`](../checks/vectorcraft-browser-smoke-r2.txt). Hashes exact bytes written by the isolated asset server, avoiding inspector-cache body retention; browser records response URLs/status/length. Full argv and cwd in log; uses existing offline uv Playwright/Python 3.14 environment and the documented GR-058 Chromium/SwiftShader workflow. |
| `python3 docs/reviews/GR-082/runtime/vectorcraft/verify_evidence.py` | 0; [`vectorcraft-evidence-verify.txt`](../checks/vectorcraft-evidence-verify.txt). Verifies all bundle files, test input hashes, served bytes/sizes, before/after identity, two WASM transfers, saved SVG, one save, no downloads, and index SRI. |

Preflight failures and syntax-check exits are retained in
[`vectorcraft-preflight.txt`](../checks/vectorcraft-preflight.txt). Every build/test
subprocess log records argv, cwd, combined output, exit and elapsed time. No Rust
unit-test suite was run in this follow-up; the earlier locked WASM check remains
separate evidence.

### Source, test and final bundle identity

All hashes below are SHA-256. [`vectorcraft-source-manifest.json`](../checks/vectorcraft-source-manifest.json)
records every tracked source file plus `git archive --format=tar 43313f9451de7ab5b909801006b8881458f2bf04`
(exit 0); [`vectorcraft-bundle-manifest.json`](../checks/vectorcraft-bundle-manifest.json)
records all 9 final asset files and pinned font inputs.

| Artifact | SHA-256 |
| --- | --- |
| Exact source Git archive | `11626df083757654ba4b762084d4007031f24833470d88bdef517c8b05499361` |
| Source `Cargo.lock` | `4e5da6dcba24b385663dfd2ee0b8c3ddf93385187fa354f10b7b50b248af059b` |
| Final test `tests/test_vectorcraft_gr082_release.py` | `7e3d5f65327fd0ed8934aba89059733cbf2ec949023c4634fcfee6f3e3eea083` |
| Bundle `index.html` (2,513 bytes) | `2368b429039cf4bae40078ce8812a051a3caf252335cd426e6d015267d419f51` |
| `vectorcraft-web-cc057e46baa002c5.js` (173,642 bytes) | `ccc4791abdc0611799a147e8afffc8199dad29237d7877b601900e08d19a81cc` |
| `vectorcraft-web-5bb180f07f434305_bg.wasm` (77,340,479 bytes) | `46fdcdf8440cbbb810a94f6d07686b803f32065c8d89109188fca27a5fe2346a` |
| Captured and stored `saved.svg` (609 bytes) | `fad9b3e60c2e76e29214dccdd6edfeb00b5edc9be605aaefddaed8372d3497f2` |

### Observed behavior and ceilings

| Observation | Retained evidence / limit |
| --- | --- |
| Open synthetic SVG, select pencil, draw document-space (60,60) → (180,120), `request('app.save',{path:'synthetic.svg',svg:{}})` | Actual release WASM; test lines and [`browser-evidence.json`](../runtime/vectorcraft/browser-evidence.json). No manual download/upload. Browser download events empty. |
| Capture → automatic polling POST → stored exact editor bytes → visible `Saved — new version synthetic-v1` | One POST only, byte equality assertion against `readFile('synthetic.svg')`; saved SVG plus `edited.png`. 2.1s additional polling creates no duplicate save. |
| Explicit browser close, launch fresh browser, open host again, inspect geometry | `reopened-inspect.json` and `reopened.png`; expected unfilled black pencil path at x/y 60/60, width/height 120/60. Save count remains one after reopen. |
| Actual served assets before/after | All 9 files unchanged. Server wrote matching index/JS/WASM and three startup fonts in each browser session (12 recorded asset transfers); no asset writes from the test. Hashes match bundle manifest. OFL files are manifested but not fetched by the browser. |
| Dirty marker | In this API `app.save` run, `ui.inspect.documents` reports `dirty:false`; screenshot has no tab asterisk. This differs from GR-063's historical UI-export observation. **Ctrl+S, Save As, menu export and their dirty-asterisk behavior were NOT VERIFIED on v0.17.0.** No native host-ACK API was added or demonstrated; local clean state is not durable-host acknowledgement. |
| Remaining API ceilings | Original basename polling only; basename-keyed 16-entry captured-file storage; no multi-file/renamed export contract, no dirty event or host-ACK binding. No shared host adapter qualification. See unchanged source API/gateway evidence above. |
| Not exercised | Failed-save retry, concurrent-update rejection, cancellation, wrong format/mixed-case/changed basename, malicious/deep SVG, artboard/text/image/foreign-metadata regression suite. Source-assessment recommendations above remain outstanding. |
| Publication / production gates | No Seafile, identity-binding, ONLYOFFICE regression, deployment, release-binary reproducibility, independent review or GPT acceptance claim. The source-built final WASM is 77,340,479 bytes; hosting suitability was not tested. Mutable upstream common-actions workflow was not frozen. |

Changed-file inventory and hashes for this lane are retained in
[`vectorcraft-SHA256SUMS`](../checks/vectorcraft-SHA256SUMS). Shared summary files
and `port-manifest.json` are intentionally left for the integrating agent.
