# GR-082 PdfCraft bounded implementation — PROVISIONAL

Source: `https://github.com/storytold/pdfcraft.git`, official `v0.14.0`, HEAD
`5a78b223871add8e3883856205cc653d741e0e94` (Release 0.14.0, 2026-10-25).
Source clone was clean initially; HEAD/tag/origin remain unchanged. No commit,
dispatch, deployment, upstream publication, Seafile or ONLYOFFICE access performed.
Only six source-clone files changed; output is `pdfcraft.patch` beside this report.
No independent review or GPT verdict is claimed.

## Port and provenance

- Input: `docs/reviews/GR-017/patches/pdfcraft-durable-host-ack.patch`, SHA-256
  `6d50eb1f45e81f2037948cd6160878feb2d87eb0881d167f0fc1d290e4450562`.
- Original patch does **not** apply unchanged: `git apply --check` rejects
  `Cargo.lock`, `crates/ui-egui/src/editing.rs`, `crates/ui-egui/src/lib.rs`.
  Port resolves version/context changes against the exact tag.
- Retained ticket ACK gating, 120000ms timeout, failed/duplicate/stale ACK handling,
  generation-matched saved snapshots, deferred close callbacks, save coalescing,
  64 pending-save/callback caps and 256MiB retained snapshot cap
  (`apps/pdfcraft-web/src/main.rs` host module; `editing.rs:8-199,869-915`).
- Upstream `commit_typing_in`, `commit_open_text_edits`, `resolve_close`,
  `close_and_continue`, `attend_save_prompt` compared byte-for-byte to HEAD:
  unchanged. The obsolete GR-017 `commit_open_line_edit` is absent. Upstream new
  text-box unsaved detection remains; retained paragraph formatting detection
  uses `has_changes` (`editing.rs:791`). All upstream save-prompt logic remains.
- Retained 7 ACK tests and added a new text-box-draft ACK regression checking
  that stale success cannot close over newer typing and that the typing survives
  serialization/reopen (`editing.rs:2065` host_save_ack_tests; 8 tests total).
- Updated GR-017's shared transport from the old `90c261de...` API to exact
  `d572f2d550278a7f4aad91a1bac650105c19812b`, vendored under
  `integration/craft-platform` and referenced by a relative path in the web
  manifest and lockfile. Its `src/browser/host.rs` is byte-for-byte the
  supplied current source, SHA-256
  `dfd3d3e2d2dde7d9a630e487ea79d6b3adf0085266d7480825900e912d0a9dda`.
  This preserves its cumulative open-admission budget, bounded fields/bytes and
  exact parent source/origin validation (`host.rs:9-17,90-122`).

## Identity protocol decision

The port deliberately remains on the existing PdfCraft ticket protocol; it does
not advertise `saveIdentity:1`. This matches the current gateway's PdfCraft
branch: `integration/gateway/hostpage.py:93` requires identity only for WordCraft
and GridCraft; lines 281-289 send legacy opens otherwise. Runtime compatibility
and Seafile roundtrip remain **NOT VERIFIED**.

Identity binding is feasible as a separate lifecycle change using native
`DocId` (`crates/engine/src/lib.rs:234`), not filename or whichever tab is active.
It cannot be truthfully enabled just by swapping `post_save`: the current inbox
carries only `(name, bytes)` (`lib.rs:779,3582`) and `open_bytes` returns `()`
(`lib.rs:1396`). A complete implementation must carry the admitted `openId`
through successful parsing, capture the actual native document identity, send
`opened`, retain/check identity per pending save, enforce update-only Save
(including replacement/import/Save As paths), and send identity-bearing dirty
confirmations with the successful ticket. Existing transport APIs provide those
wire semantics (`host.rs:196,242,249,265`). None were replaced or fabricated in
this bounded GR-017 port. This patch is not evidence of identity-aware PdfCraft.

## Validation

All commands ran in the source clone. Cargo invoked with
`PATH=/home/roddy/.cargo/bin:$PATH` (the default mise cargo/rustup shims otherwise
fail with `mise ERROR No version is set for shim: cargo` / `rustup`). Toolchain
is 1.95.0; native and wasm32-unknown-unknown targets are installed.
`TMPDIR=$PWD/target/build-tmp` is persistent; Cargo uses its normal persistent
clone `target/` because this environment has no global target-dir setting.
No `/tmp` build output or cache removal.

| Check | Exact result |
| --- | --- |
| `git diff --check` | exit 0, no output |
| Initial `cargo fmt --check` (before final regression) | exit 0, no output |
| Later `timeout 60 cargo fmt --check` | exit 124, no output |
| `timeout 60 /home/roddy/.rustup/toolchains/1.95.0-x86_64-unknown-linux-gnu/bin/rustfmt --check --edition 2024 apps/pdfcraft-web/src/main.rs crates/ui-egui/src/edit_text_ui.rs crates/ui-egui/src/editing.rs crates/ui-egui/src/lib.rs` | exit 0, no output |
| `GIT_INDEX_FILE=$PWD/target/gr082-base.index git read-tree HEAD`, then `git apply --cached --check .../pdfcraft.patch` with that index | exit 0, no output: applicable to exact clean tag |
| `git apply --reverse --check .../pdfcraft.patch` | exit 0, no output: matches modified tree |

`timeout 600 cargo test --locked -p pdfcraft-ui-egui -j 2 --lib host_save_ack_tests`
exited **124** during cold dependency compilation; zero tests ran. Last exact
output: `   Compiling winnow v1.0.4`. No compiler verdict on PdfCraft code.

`timeout 600 cargo check --locked -p pdfcraft-web --target wasm32-unknown-unknown -j 2`
on the first Git-pinned attempt exited **124**. Initial exact output included `    Blocking waiting for file lock
on package cache` and `    Blocking waiting for file lock on build directory`.
After the native timeout released the build lock, wasm dependency compilation
started. Final exact output:

```text
   Compiling wasm-bindgen v0.2.129
   Compiling serde v1.0.229
   Compiling libm v0.2.16
   Compiling num-traits v0.2.19
    Checking subtle v2.6.1
    Checking rand_core v0.10.1
    Checking zeroize v1.9.0
    Checking smallvec v1.16.2
```

The initial attempts hit cold dependency builds and shared-build lock contention.
The final bounded native ACK test and broader UI editing regression group were
rerun after dependencies were cached; their exact results are retained in the
GR-082 evidence bundle. Clippy and browser/runtime checks were not run.

After switching to the included local transport snapshot, the locked WASM check
was rerun with `PATH=/home/roddy/.rustup/toolchains/1.95.0-x86_64-unknown-linux-gnu/bin:$PATH cargo check --locked --target wasm32-unknown-unknown -j 1 -p pdfcraft-web` and exited **0** in 8m10s. Exact release patch apply check and the local transport `SHA256SUMS` check also exited 0. The UI `editing::` regression group passes **30/30** (`checks/pdfcraft-editing-regressions.txt`); it includes the 8 host ACK tests retained separately in `checks/pdfcraft-native-host-ack.txt`, so these are 30 total tests, not 38. Broader system/browser behavior remains unverified.

Final patch SHA-256:
`90a596e2b54d32f859cd01ea26525667d3cce4f6eef97656455a7a717792d6d7`.

The bounded native tests and `editing::` UI regression group have recorded
passes, but independent review and a real browser storage roundtrip remain
outstanding; this handoff must not be counted as a GR-057/MVP PASS.
