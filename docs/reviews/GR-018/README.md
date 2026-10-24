# GR-018 — CADCraft durable host-save acknowledgement

Status: **bounded local prototype review PASS (GPT-6.1 Sol low round 4); a
separate synthetic Seafile runtime E2E is also reproduced.** These bounded
results are not a project-level GPT verdict and do not unlock upstream
publication. The project-level GPT result remains FAIL on
`0edbe524b4fa321b0f73f8601afef390e7f785e6`.

## Scope and source

This bundle records a local patch for the pinned CADCraft Web bridge. The editor
sends ticketed serialized bytes to its embedding host and retains dirty state
until a matching durable-save acknowledgement arrives. The host transport is
the GR-016 `craft-platform` prototype.

| Repository | Base SHA | Source patch |
|---|---|---|
| `storytold/cadcraft` | `7bf5905ac97316a7896de8cbc12d243f57b09bd8` | [`cadcraft-host-save.patch`](cadcraft-host-save.patch) |

Patch SHA-256: `cb85f2ed0493333d4e3dfa6df959cbc85e460ca208c4f07d9e59f740525a516e`.

The standalone `craft-platform` source snapshot is now packaged at
[`integration/rust/craft-platform`](../../../integration/rust/craft-platform)
and exposed through a minimal root Cargo workspace for future git dependencies.
It has a runnable metadata/native-test/WASM-build check at
[`scripts/check-craft-platform.sh`](../../../scripts/check-craft-platform.sh).
The package received a bounded independent review with no blocker/major; see
the GR-016 packaging review.
The CADCraft patch pins `craft-platform` to repository revision
`90c261de22ef75c4c7c5c5cd1c712d483be0bbc8`. It applies to a clean CADCraft
checkout and passes the Rust 1.95 locked WASM check. Exact commands and all four
app patch hashes are recorded in
[`../GR-016/PORTABLE-APP-PATCHES-20261024.md`](../GR-016/PORTABLE-APP-PATCHES-20261024.md).

## Behavior in the patch

- `cadcraft:save` carries a bounded ticket, filename, serialized bytes, and
  SaveAs flag; the parent replies with `cadcraft:saveResult`.
- Drawing snapshots stay dirty until successful acknowledgement. Stale success
  records the committed destination while preserving newer edits; failure,
  timeout, duplicate, and unknown results do not clean a drawing.
- Only one drawing save per drawing can be in flight; session and browser
  pending requests are bounded. Browser deadlines use `performance.now()` and
  repaint against the earliest outstanding absolute deadline.
- Export acknowledgements report completion without clearing the drawing's
  dirty state. Standalone browser downloads and native atomic writes retain
  their synchronous behavior.
- Same-origin and parent-window validation plus listener cleanup are delegated
  to the GR-016 transport implementation.

## Reproduced checks

Commands ran in `/home/roddy/.cache/artcraft-gr018-cadcraft-work` at base
`7bf5905ac97316a7896de8cbc12d243f57b09bd8`, using Rust 1.95.0:

| Command | Result |
|---|---|
| `cargo +1.95.0 fmt --all -- --check` | PASS |
| `cargo +1.95.0 check -p cadcraft-web --target wasm32-unknown-unknown --locked --offline` | PASS; existing UI dead-code warnings |
| `cargo +1.95.0 test -p cadcraft-engine host_ack_tests --lib --locked --offline` | PASS; 8 tests |
| `cargo +1.95.0 test -p cadcraft-engine --lib --locked --offline` | PASS; 344 tests |
| `rtk git diff --check` | PASS |

The focused tests cover success, failure, stale edits, undo to a saved snapshot,
timeout removal, capacity, overlap rejection, and avoiding a false browser
download result. The native suite does not execute the browser message listener
or timer; those remain unverified at runtime.

## Review and evidence boundaries

GPT-6.1 Sol low round 1 found one blocker and five major issues plus a minor.
Round 2 found one major and two minor issues; round 3 returned a bounded PASS
with one minor concerning export-timeout messaging. Round 4 returned **PASS**
for the exact patch hash above and confirmed the timeout messages distinguish
drawing, export, and mixed operations. Findings and review scope are recorded
in `REVIEW-SOL-LOW-R1.md` through `REVIEW-SOL-LOW-R4.md`.

**NOT VERIFIED:** browser-host behavior, save confirmation in a browser, Seafile
The separate synthetic Seafile run reproduced a browser save, Seafile version,
and fresh reopen; its full record is in
[`CADCRAFT-SEAFILE-E2E-20261024.md`](CADCRAFT-SEAFILE-E2E-20261024.md).

**NOT VERIFIED:** browser timeout/failure and adversarial-origin paths,
production authorization, exact editor-to-gateway byte identity, optimized
bundle performance, and standalone reproducibility. This work does not change
overall project, public deployment, or upstream readiness.
