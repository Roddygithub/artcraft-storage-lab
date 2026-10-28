# GR-082 PhotoCraft implementation lane — PROVISIONAL

Base: official `v0.16.0`, `b1794c6e0608ccfc887213dcf58398977c5cb75e` (HEAD unchanged). Changes confined to the supplied source clone; output patch and this report only. No dispatch, deployment, service access, upstream publication, or main-repository changes.

- Ported GR-076 pathless single-native-document adapter, nested engine authorization, replacement/close/Save As/picker/drop guards, immutable snapshot ACK handling, timeout-without-retry, and explicit-download behavior.
- Strict transport uses a vendored path snapshot of `craft-platform` commit `d572f2d550278a7f4aad91a1bac650105c19812b` at `integration/craft-platform`; the included source is checksum-manifested and matches the supplied contract. No writable legacy fallback. Ready advertises `saveIdentity: 1`; initial Open requires identity/update-only fields. Opened reports the parsed native `DocId` as a decimal string. Save carries openId/documentId/intent/ticket; ACK admission requires all three correlation values. Clean confirmation includes the successful ticket only after the captured snapshot is acknowledged and there is no remaining work.
- Native decoder requests persisted IDs and then compares the loaded ID with the stored manifest ID. A remap is rejected before opening/binding; the manifest is reread only after the bounded load admits the same immutable bytes. It accepts `.pcraft` only, and applies 50 MiB input/output handoff, 8 MiB manifest, 50 MiB blob, 256 MiB total decoded data and 16,777,216 canvas-pixel limits. The serialized output is a complete Vec before its handoff limit is checked; this is not a peak-memory guarantee.
- Host save calls v0.16.0 `menus::modal_allows` plus `save_options_open` before serialization. Upstream import/export/batch bounds remain unchanged (`crates/format`, `crates/io`, `crates/engine/src/file_cmds.rs` have no diff).
- Added actual native open/edit/export/reopen identity regression, rejection when the upstream loader remaps an ID above JS exact-integer range, malformed/oversized-canvas rejection, wrong-identity ACK rejection, and modal workspace/save/changed-identity coverage. Preserved GR-076 snapshot/timeout/bypass/standalone regressions.

## Applicability

The original GR-076 combined patch does **not** apply completely to this tag: `Cargo.lock:1227` fails; all non-lockfile hunks pass `git apply --exclude=Cargo.lock --check`.

The final generated `photocraft.patch` includes the local transport snapshot, identity adapter, and lockfile changes. It applies cleanly to the exact tag: independent Git index initialized with `git read-tree HEAD`, then `git apply --cached --check <output>/photocraft.patch`, exit 0. `integration/craft-platform/SHA256SUMS` verifies the packaged transport files. The R1 reviewer found that an earlier patch omitted this directory; the final patch was regenerated with it included and rechecked.

## Validation

- Focused rustfmt check of all 13 changed Rust files (`--edition 2024 --config skip_children=true --check`): exit 0.
- `git diff --check`: exit 0.
- Standalone `rustc --edition 2024 --test apps/photocraft-web/src/host_inbox.rs -o temp/host-inbox-tests`, then binary: exit 0; **3 passed**.
- Initial pre-refresh `cargo check -p photocraft-web --target wasm32-unknown-unknown --locked`: exit 101, expected stale-lock rejection. `cargo check --offline` refreshed the lockfile; its initial optimized dependency build was interrupted (130) to reduce resource contention. A queued engine invocation was also interrupted (130) before acquiring the build lock.
Final commands below use the common prefix `cargo --config profile.dev.opt-level=0 --config 'profile.dev.package."*".opt-level=0'`:

- `check --locked -j 1 -p photocraft-web --target wasm32-unknown-unknown`: **exit 0**, both initial complete build and final rerun (`wasm-locked.log`, `wasm-locked-r2.log`). Final output has existing unused-code warnings in untouched plugins/engine code.
The implementation lane reported 19 focused tests passing before the remote
transport dependency was relocated to the packaged local snapshot. That result
is historical and is not attributed to the final package layout. After that
packaging-only change,
the locked WASM check passed and the standalone confirmation test was rerun
against the final tree and passed 1/1; its retained log is
`docs/reviews/GR-082/checks/photocraft-standalone.txt`. At this packaging-stage
checkpoint, the engine snapshot, Web and UI host tests were **NOT VERIFIED
against the final local-path tree**: those commands were cancelled during cold
compilation or while waiting for Cargo locks (exit 143). The earlier 19-test
result remains source-level historical evidence only, not a final-tree test
claim. The first web run's ID-remap failure and fix remain described in the
prior lane record. The 2026-10-28 report follow-up below records targeted
Web/UI commands started on 2026-10-27; the engine snapshot suite remains
unverified.

Validation uses Rust/Cargo 1.95.0 from `/home/roddy/.rustup/toolchains/1.95.0-x86_64-unknown-linux-gnu/bin` (the default mise cargo shim has no version configured). Cargo registry/git caches use the persistent default home. Build outputs are the source clone's persistent `target/`; `TMPDIR` is the clone's `temp/cargo-tmp`; neither is under `/tmp`. Final checks use one job and CLI-only `profile.dev.opt-level=0` / `profile.dev.package."*".opt-level=0` to reduce contention, with no profile source edits.

## Integration limit

This is an adapter patch, **not an integrated MVP or review PASS**. Browser/gateway/Seafile durable save and reopen: NOT VERIFIED (outside this lane). The supplied gateway currently has `IDENTITY_REQUIRED` enabled only for WordCraft/GridCraft (`integration/gateway/hostpage.py:93`); its rollout must enable the same contract for PhotoCraft. Until then this adapter rejects legacy Open and cannot save. No gateway code was changed here. The source-port review and release-smoke reviews R1–R3 are recorded in the evidence bundle; all free-model results remain PROVISIONAL.

At the local-path packaging checkpoint (before the focused Web/UI commands
started on 2026-10-27 and recorded in the 2026-10-28 report follow-up), the
locked WASM check had been rerun offline and passed; no Rust source changed in
that dependency-location change. The standalone confirmation test also passed,
while the engine snapshot, Web and UI suites remained unverified at that point.
Final patch SHA-256: `73a68d4fd0199e78963061fe6b6d1266704c202633b20ccce2d49f285dc6e089`.
Final exact-tag apply check, local transport checksums, and 13-file rustfmt
check all exit 0.

### Optimized release and actual-WASM memory-host follow-up — 2026-10-28

The exact v0.16.0 source patch remains unchanged. Rust 1.95.0 and Trunk 0.22.0
completed `trunk build --release --locked` from `apps/photocraft-web`; retained
output [`checks/photocraft-qualification-release.txt`](../checks/photocraft-qualification-release.txt)
records the optimized `wasm-release` build and Trunk success. The four-file
bundle hash inventory is [`checks/photocraft-bundle-final.sha256`](../checks/photocraft-bundle-final.sha256).
The build produced `index.html`, the hashed JS glue, and the 26,405,959-byte
WASM module. The optional `fonts/manifest.txt` is absent: v0.16.0's
`web.rs` documents a 404 as the normal case when a host serves no custom fonts.

The final browser test is [`tests/test_photocraft_gr082_release.py`](../../../../tests/test_photocraft_gr082_release.py);
its exact `uv`/Playwright command and exit 0 are in
[`checks/photocraft-qualification-browser-smoke-final.txt`](../checks/photocraft-qualification-browser-smoke-final.txt).
It opened the deterministic 64×64 native fixture in the actual release WASM,
created a paint layer, drew a black stroke, and used Ctrl+S. The memory-only
host received a 6,890-byte `.pcraft` save with document ID 82, `intent:"save"`,
and a ticket; its SHA-256 is
`b5bf27c8e6325b83b15b0b27fcfc433e0ee0e8401011efa7c6b512ed327bcd46`. The host
sent a matching identity/ticket ACK, then a new editor iframe reopened the
saved bytes with the same document ID and clean state. No browser download
occurred. `runtime/photocraft/browser-evidence.json` records the events, HTTP
responses, exact served asset hashes, byte count, and before/after bundle
inventory; `edited.png`, `saved.png`, and `reopened.png` show the visual state.

This is synthetic **in-memory** storage, not Seafile. Refreshed Seafile
version/history/readback/fresh reopen, gateway identity-mode enablement, and
the separate engine snapshot test remain **NOT VERIFIED**. The earlier 19-test
result remains historical; final-tree focused Web 6/6 and UI 8/8 host tests are
recorded separately in `checks/photocraft-qualification-web-focused.txt` and
`checks/photocraft-qualification-ui-focused.txt`.

## Optimized-release qualification continuation (2026-10-27) — PROVISIONAL

This continuation starts at lab commit `b538b6032ef50e013fdea67365cb626666678ad0`, in the shared `upstream-refresh/wave-1` worktree. It does not change the application source or archived patch. `runtime/photocraft/verify-source.py` independently applies the archive to an alternate Git index and compares that index with the actual source worktree; exit 0 proves the supplied archive matches this tree. Source HEAD remains `b1794c6e0608ccfc887213dcf58398977c5cb75e`.

All paths below are relative to `docs/reviews/GR-082/`. Exact argv, cwd, selected environment, combined stdout/stderr, and recorded exit are retained in `checks/photocraft-qualification-*.txt`. `runtime/photocraft/run-check.py` is the bounded command runner. Cargo and temporary Rust output stay under the persistent source checkout, with one build job; no Rust output is directed into `/tmp`.

| Check | Evidence | Exit/result |
|---|---|---|
| Exact tag + archived patch application + actual tree comparison + whitespace | `checks/photocraft-qualification-source.txt` | 0 |
| Vendored transport checksums | `checks/photocraft-qualification-transport.txt` | 0 |
| Compile/run final-tree inbox tests directly with Rust 1.95 | `checks/photocraft-qualification-inbox-compile.txt`, `checks/photocraft-qualification-inbox.txt` | 0 / 0; 3 passed |
| Compile/run vendored protocol tests directly with Rust 1.95 | `checks/photocraft-qualification-protocol-compile.txt`, `checks/photocraft-qualification-protocol.txt` | 0 / 0; 5 passed |
| Changed app Rust formatting (13 files) | `checks/photocraft-qualification-rustfmt-app.txt` | 0 |
| Formatting including vendored transport | `checks/photocraft-qualification-rustfmt.txt` | 1; vendored snapshot formatting differs; unchanged to preserve checksums. Trailing whitespace in captured blank diagnostic lines was removed for repository diff hygiene; output meaning and recorded exit are unchanged |
| Tool versions (initial PATH-based rustup) | `checks/photocraft-qualification-versions.txt` | 1; Rust/Cargo 1.95 and Trunk 0.22 succeed; mise rustup shim has no selected version |
| Tool versions (absolute rustup executable) | `checks/photocraft-qualification-versions-direct.txt` | 0; Rust/Cargo 1.95.0, Trunk 0.22.0, wasm32 target installed |

Before-source manifest: `checks/photocraft-source-before.sha256`, SHA-256 `994323049a72bdc16f0d1b122f19f65edca99b5f6a790b9f21aa2171aa44637c`. Archive SHA-256 remains `73a68d4fd0199e78963061fe6b6d1266704c202633b20ccce2d49f285dc6e089`. The manifest hashes every tracked and nonignored source file; individual test source hashes are included.

The release command is `trunk build --release --locked`, from `apps/photocraft-web`, with Rust 1.95 first in PATH. Upstream `index.html:8` selects `wasm-release`, feature `heif`, `data-wasm-opt="z"`, `--converge`, and weak references. `Cargo.toml:114` defines fat LTO and size optimization, plus crate overrides. No profile or optimization settings are relaxed for this release run.

The synthetic browser harness is `runtime/photocraft/host.html`; `serve.py` binds only a new loopback port and serves this harness, its deterministic 64×64 empty native fixture, and the actual Trunk output. `make-fixture.py` writes `synthetic.pcraft` (536 bytes; SHA-256 `4cbfc5ed44d02b15dc139ae6db5e2e5333d80caef8a3c0539664ac095a230973`). The host retains bytes in memory, requires explicit ACK, and replaces the entire iframe for reopen. It has no Seafile/gateway access. Harness availability alone is **not runtime evidence**.

Production/publication gates remain in force. This lane supplies no Seafile, durable storage, identity-binding qualification, independent review PASS, or GPT REVIEW PASS. No dispatcher, active route, ONLYOFFICE, Seafile, shared summary, or manifest is edited. No commit, push, issue, PR, RFC, or publication is performed.

### Fresh focused checks after optimized Cargo compilation

The native commands below reuse the existing persistent native cache. The common prefix is `cargo --config profile.dev.opt-level=0 --config 'profile.dev.package."*".opt-level=0'`; these CLI overrides affect only these native test commands, not the release build.

| Command after prefix | Retained log | Result |
|---|---|---|
| `test --locked -j 1 -p photocraft-web --bin photocraft-web host_` | `checks/photocraft-qualification-web-focused.txt` | exit 0; 6 passed (native document roundtrip/rejection and inbox tests) |
| `test --locked -j 1 -p photocraft-ui-egui --lib host_` | `checks/photocraft-qualification-ui-focused.txt` | exit 0; 8 passed, including rendered workspace guard; 44.09 seconds test time |

These are fresh final-tree results and supersede the earlier Web/UI cancellation records for these exact filtered tests only. The separate engine snapshot suite was not retried; its earlier final-tree cancellation remains a limitation. The standalone inbox run overlaps three tests in the web command; counts should not be added as unique test coverage.
