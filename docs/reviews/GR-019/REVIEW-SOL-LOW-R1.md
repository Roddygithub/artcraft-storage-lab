# GR-019 — independent review round 1

**Reviewer:** GPT-6.1 Sol, low

**Verdict:** FAIL — bounded prototype patch
**Reviewed:** FigCraft base `8d790607ff1ad40e32343ca2116d8fdcf3244c8d`; patch SHA-256 `182a1d9feb1e577419707b7df4121eba842009dc4ae271b7f84176d7e7c9256e`.

## Findings

### MAJOR — extra documents could be edited while Save targeted the bound file

The new-tab action could create another document, while host Save always
serialized the Seafile-bound UID. Dirty reporting excluded the extra document,
so the user could edit one tab while the host saved another and still receive a
successful acknowledgement.

### MAJOR — branch creation/open could bypass the single-document scope

The save adapter checked the bound main document before validating branch
state. Branch UI actions could create or activate unsupported branch documents,
and the direct host save path bypassed normal branch synchronization.

### MINOR — failed `ready` handoff left host mode appearing available

`post_ready` errors were logged but retained the transport, suppressing the
UI's host-unavailable error.

## Remediation in the next patch

- Host-mode command routing rejects new/open/recent and all `branch.*` engine
  commands; the menu's direct `branch.create` path is rejected visibly.
- Host startup skips live-invite joining. Host save requires exactly one active
  document whose UID matches the bound Seafile document and refuses branch,
  preview, text-preview, and active-interaction state.
- Dirty reporting includes every open document, including an unsupported
  document that reaches the session through an unexpected path.
- If `post_ready` fails, the transport and listener are dropped, so the UI
  reports the host as unavailable.
- The UI regression test checks new-tab and branch refusal, plus fail-closed
  save and dirty reporting when a second document is injected directly.

## Verification after remediation

- `cargo +1.95.0 test -p figcraft-ui-egui --lib host_save_waits_for_ack --locked` — **PASS**, 1 test.
- `cargo +1.95.0 test -p figcraft-engine --lib external_snapshot_tests --locked` — **PASS**, 3 tests.
- `cargo +1.95.0 check -p figcraft-web --target wasm32-unknown-unknown --locked` — **PASS**.
- `cargo +1.95.0 fmt --all -- --check` and `git diff --check` — **PASS**.
- Stored patch SHA-256: `1bd98b5ec70042ea19cb2f0df42c26b3b0bad59a43590a6d000e73021e30cf83`.

This is the implementer's remediation record, **not an independent re-review**.
Browser transport, real Seafile persistence/versioning/reopen, full branch UI
coverage, timeout execution, and deployment security remain **NOT VERIFIED**.
