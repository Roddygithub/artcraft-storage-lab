# GR-082 Wave 1 — VectorCraft source qualification

Status: **PROVISIONAL; source assessment only; GPT REVIEW PENDING**. 2026-10-27.

**Decision: no integration code port identified. Rebuild/requalify v0.17.0 using the existing gateway page API/polling adapter. This is not a runtime qualification PASS.** No durable VectorCraft host-save patch is present in the retained integration or required to port for this release comparison.

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

## Retained evidence and required next qualification

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

No project worktree edits, source clone mutations, deployment, browser, Seafile, ONLYOFFICE, compile or runtime tests. Only the authorized external output directory was written. This assessment does not satisfy GR-082's independent review or release acceptance gates.
