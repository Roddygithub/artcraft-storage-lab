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
`docs/reviews/GR-082/checks/photocraft-standalone.txt`. Fresh engine snapshot
tests were cancelled during cold compilation (exit 143), and fresh Web/UI host
test commands were cancelled while waiting for Cargo locks (exit 143). Those
three suites are **NOT VERIFIED against the final local-path tree**. The
earlier 19-test result remains source-level historical evidence only, not a
final-tree test claim. The first web run's ID-remap failure and fix remain
described in the prior lane record; no claim of final-tree web-test success is
made here.

Validation uses Rust/Cargo 1.95.0 from `/home/roddy/.rustup/toolchains/1.95.0-x86_64-unknown-linux-gnu/bin` (the default mise cargo shim has no version configured). Cargo registry/git caches use the persistent default home. Build outputs are the source clone's persistent `target/`; `TMPDIR` is the clone's `temp/cargo-tmp`; neither is under `/tmp`. Final checks use one job and CLI-only `profile.dev.opt-level=0` / `profile.dev.package."*".opt-level=0` to reduce contention, with no profile source edits.

## Integration limit

This is an adapter patch, **not an integrated MVP or review PASS**. Browser/gateway/Seafile durable save and reopen: NOT VERIFIED (outside this lane). The supplied gateway currently has `IDENTITY_REQUIRED` enabled only for WordCraft/GridCraft (`integration/gateway/hostpage.py:93`); its rollout must enable the same contract for PhotoCraft. Until then this adapter rejects legacy Open and cannot save. No gateway code was changed here. Independent review remains required.

After switching the transport dependency from the remote Git pin to the included path snapshot, the locked WASM check was rerun with Cargo offline and exited 0. No Rust source changed in that packaging-only dependency-location change. The standalone confirmation test was rerun against the final tree and passed; engine/Web/UI final-tree test suites remain unverified or cancelled as specified above. Final patch SHA-256: `73a68d4fd0199e78963061fe6b6d1266704c202633b20ccce2d49f285dc6e089`. Final exact-tag apply check, local transport checksums, and 13-file rustfmt check all exit 0.
