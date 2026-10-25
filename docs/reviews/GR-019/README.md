# GR-019 — FigCraft host-save adapter prototype

**Status:** bounded local prototype; not Seafile E2E, not a project GPT PASS.

## Scope

This patch adds the shared `craft-platform` transport to FigCraft Web and a
single-file `.figcraft` host session. It opens host-supplied bytes, sends a
ticketed save, and marks only the acknowledged snapshot saved. An edit made
while a save is pending remains dirty. Host Save As and unsupported preview,
branch, or active-interaction states fail visibly. UI creation/duplication of
extra files, opening another file, branch actions, and live collaboration are
blocked; save also fails closed unless the bound document is the only active
document. Dirty reporting covers every open tab. A failed `ready` handoff leaves
the bridge unavailable. A 120-second missing-ACK warning treats the outcome as
unknown and does not retry automatically.

The patch is based on upstream FigCraft
`8d790607ff1ad40e32343ca2116d8fdcf3244c8d` and pins `craft-platform` at
`56c5e16d79b77751106173c13111ef4fe0a2c0ec`. The patch includes the original
GR-019 app changes plus this immutable dependency pin. It is stored as
[`figcraft-shared-host-save.patch`](figcraft-shared-host-save.patch); SHA-256:
`954850ba5aff7362e776b2331a5a5ff54bf9d71374d7b29bc856c2b7a47c4798`.

## Reproduction

Rust 1.95.0, run from the FigCraft checkout after applying the patch:

```sh
cargo +1.95.0 test -p figcraft-engine external_snapshot_tests --locked
cargo +1.95.0 test -p figcraft-ui-egui host_save_waits_for_ack --locked
cargo +1.95.0 check -p figcraft-web --target wasm32-unknown-unknown --locked
cargo +1.95.0 fmt --all -- --check
git diff --check
```

Observed: engine tests **3 passed**; UI adapter test **1 passed**; WASM check
**passed**; formatting and whitespace checks **passed**. Cargo reported existing
missing optional `craft-fonts` and dead-code/unused warnings. The patch also
passes `git apply --check` against a clean archive of the pinned base.

The UI test uses a synthetic parent service and actual FigCraft engine
serialization/acknowledgement. It covers initial open, save handoff without
premature clean state, unknown-ticket rejection, valid ACK, edit-during-save,
fresh decoding of the exact outbound snapshot, a subsequent successful save,
explicit Save As, branch and collaboration-menu refusal, duplicate-file and
duplicate-version refusal, rejection of a second UI-created document, and
fail-closed behavior plus dirty reporting when a second document is injected
through an unexpected path.

## Limits

- GR-048 verifies browser `postMessage` runtime on the exact patched optimized
  actual-WASM build with a synthetic memory-only parent: open, visible rectangle
  edit, ticketed save bytes, matching ACK, clean and fresh iframe reopen. See
  [`GR-048 report`](../../GR-048-FIGCRAFT-WASM-SMOKE.md).
- **NOT VERIFIED:** Seafile routing, durable Seafile version/history creation,
  or a fresh reopen from Seafile.
- The patch is not added to `integration/config/dispatch.json`; GR-048 built a local optimized
  FigCraft bundle for the synthetic smoke; no production bundle was installed.
- The current host page answers `openRequest` with instructions to return to
  Seahub; it does not implement a Seafile picker for switching documents.
- This first slice accepts one `.figcraft` file per iframe and deliberately
  refuses host Save As. `.fig` export, branches and preview state do not count
  as host saves.
- The 120-second timeout path, malformed messages, wrong-origin/source browser
  events, and production security controls were not runtime-tested.
- Upstream FigCraft and production Seafile were not modified. Upstream issue,
  PR, and RFC publication remain locked pending project GPT PASS.

## Transport re-pin follow-up

The first repin review mistook the full patch against upstream for a repin-only
diff. A follow-up compared the exact artifact with the previously accepted
GR-019 patch after normalizing path prefixes and transport revisions: all source
hunks match, and only the manifest/lock pin changes. The reviewer matched the
full patch hash and confirmed the pinned malformed-ACK behavior; tests/builds
were not rerun. The earlier minor about retrying failed dirty-state reports
remains. See [`REVIEW-TRANSPORT-REPIN-R2.md`](REVIEW-TRANSPORT-REPIN-R2.md).
