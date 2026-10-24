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
`90c261de22ef75c4c7c5c5cd1c712d483be0bbc8`. It is stored as
[`figcraft-shared-host-save.patch`](figcraft-shared-host-save.patch); SHA-256:
`e2a55885642960cadb0a7f6dc77894f6d53c43625abc701c4cc02db2543dc366`.

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

- **NOT VERIFIED:** browser `postMessage` runtime for FigCraft, Seafile routing,
  durable Seafile version/history creation, or a fresh reopen from Seafile.
- The patch is not added to `integration/config/dispatch.json`; no deployable
  FigCraft bundle was built or installed.
- The current host page answers `openRequest` with instructions to return to
  Seahub; it does not implement a Seafile picker for switching documents.
- This first slice accepts one `.figcraft` file per iframe and deliberately
  refuses host Save As. `.fig` export, branches and preview state do not count
  as host saves.
- The 120-second timeout path, malformed messages, wrong-origin/source browser
  events, and production security controls were not runtime-tested.
- Upstream FigCraft and production Seafile were not modified. Upstream issue,
  PR, and RFC publication remain locked pending project GPT PASS.
