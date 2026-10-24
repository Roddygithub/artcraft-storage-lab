# GR-019 — independent review round 3

**Reviewer:** GPT-6.1 Sol, low

**Verdict:** PASS — bounded patch review

**Base:** FigCraft `8d790607ff1ad40e32343ca2116d8fdcf3244c8d`
**Patch SHA-256:** `e2a55885642960cadb0a7f6dc77894f6d53c43625abc701c4cc02db2543dc366`

## Findings

No blocker or major finding.

**MINOR — failed dirty-state reporting is not retried until state changes.**
`report_host_dirty` stores the requested dirty value before `host_dirty` returns;
if transport delivery fails, it will not retry until the editor's dirty state
changes. See `crates/ui-egui/src/lib.rs` around line 1625 in the patched source.

## Verification

- Prior one-document bypasses are closed: new/open/duplicate, branch and
  collaboration commands are refused; direct menu paths are guarded; URL
  invite joining is skipped in host mode.
- Save requires exactly one active document with the bound UID and rejects
  branches, previews and interactions. Dirty reporting includes all open docs
  and pending host saves.
- Snapshot ACK remains ticketed and checks UID, path and saved-document
  identity; edits after the serialized snapshot remain dirty.
- Failed readiness drops the transport and listener.
- Patch SHA, source diff, pinned base, shared dependency revision, reverse
  applicability and whitespace checks match the supplied evidence.
- Sol independently reran the focused UI test (1/1), external snapshot tests
  (3/3), WASM check and formatting check; all passed.

## Limits

This PASS applies only to the bounded local FigCraft adapter patch. Browser
message/failure injection, Seafile durable versioning and close/reopen,
production controls, and regression behavior in other storage integrations
remain **NOT VERIFIED**. It is not a project GPT verdict or upstream approval.
