# GR-017 — PdfCraft durable host-save acknowledgement

Status: **bounded prototype review PASS; synthetic Seafile runtime save/version/
reopen reproduced; not upstream-ready, not a project GPT candidate**. The
project-level GPT verdict remains FAIL on `0edbe524`; upstream publication stays
locked. Only the local lab repository receives this evidence.

## Scope

This bounded adapter applies the GR-016 `craft-platform` transport to PdfCraft's
existing `?host=parent` bridge. It sends serialized PDF bytes with a save ticket,
keeps PdfCraft dirty while the host stores them, and settles the editor only after
a matching durable success/failure response. App serialization and saved-state
logic remain in PdfCraft; the parent remains responsible for storage.

The experiment uses read-only scratch clones:

| Repository | Base SHA | Notes |
| --- | --- | --- |
| `storytold/pdfcraft` | `57e531ccca0047597809748b5cb4276336d6051a` | shallow source clone; no upstream edits |
| `storytold/craft-libs` | `f180fc0d35d521c5d18e118c881d3efde1ec1eee` | GR-016 transport prototype; dependency is a temporary local path |

Patch: [`patches/pdfcraft-durable-host-ack.patch`](patches/pdfcraft-durable-host-ack.patch).
The manifest deliberately points at `/tmp/artcraft-gr016-craft-libs`; the patch
is evidence for review, not a portable upstream patch. It requires the GR-016
transport patch/revision first.

## Implemented behavior

- Same-origin parent messages use `HostTransport`; origin and `event.source`
  validation and listener cleanup come from GR-016.
- PDF `save`/`save as` sends bytes with a bounded opaque ticket. The application
  retains the serialized snapshot and editor generation until a matching result.
- Failed/duplicate/unknown acknowledgements do not mark the PDF clean. A success
  clears dirty state only if the document still has the exact saved generation;
  edits made while storage is pending remain dirty.
- Form, fill-text, and paragraph line-editor drafts are committed before the
  acknowledgement compares generations or runs close callbacks; rejected text
  edits leave the line editor available to the user.
- `after` actions such as closing a tab run only after confirmed success.
- Coalesced close callbacks are capped at 64 per document, including callback
  groups carried through queued follow-up saves. Browser timer closures are
  retained by ticket and released on acknowledgement, send failure, or processed
  timeout.
- The existing standalone web download path remains unchanged when no same-origin
  host bridge is active.

## Reproduced checks

| Command | Result |
| --- | --- |
| `CARGO_BUILD_JOBS=2 CARGO_PROFILE_DEV_DEBUG=0 CARGO_INCREMENTAL=0 cargo +1.95.0 check -p pdfcraft-web --target wasm32-unknown-unknown --locked --offline` | PASS; pre-existing unused/dead-code warnings only |
| `CARGO_BUILD_JOBS=2 CARGO_PROFILE_TEST_DEBUG=0 CARGO_INCREMENTAL=0 cargo +1.95.0 test -p pdfcraft-ui-egui --lib host_save_ack_tests` | PASS — 7 tests: rejection/duplicate ack, exact snapshot, same-snapshot coalescing, form and paragraph typing during save, aggregated callback cap, and tab-close snapshot cleanup |
| `cargo +1.95.0 fmt --all -- --check` | PASS |
| `git diff --check` | PASS |
| `CARGO_BUILD_JOBS=2 CARGO_PROFILE_RELEASE_DEBUG=0 CARGO_INCREMENTAL=0 trunk build --release` from `apps/pdfcraft-web` | PASS on the exact current patch with Rust 1.97; 12m31s release compile plus `wasm-opt -Oz`; existing unused/dead-code warnings only |
| Chromium synthetic-host smoke | PASS on the exact current patch — form edit, ticket `pdfcraft:1`, 2,385-byte save, matching ACK, clean state, fresh iframe reopen renders `r4-exact-host-ack`; `sessionStorage` only. Full record and hashes: [`RUNTIME-SMOKE-R4.md`](RUNTIME-SMOKE-R4.md). |
| Chromium + isolated synthetic Seafile E2E | PASS, bounded — PdfCraft text annotation saved as a new Seafile revision and displayed in a fresh PdfCraft instance. The file was opened through the direct Seahub file route; a file-list click was not observed. Details, IDs, hash, screenshots and limits: [`SEAFILE-PDFCRAFT-E2E-20261024.md`](SEAFILE-PDFCRAFT-E2E-20261024.md). |

The native tests exercise save-state handling with a synthetic PDF fixture. The
synthetic-host browser smoke uses the actual release WASM bridge and Chromium,
but its parent stores bytes in `sessionStorage`; that smoke alone does **not**
test Seafile persistence or version creation. A separate isolated synthetic
Seafile E2E is recorded below. No production Seafile service or production
editor was accessed.

## Not verified / remaining work

- The 120-second timeout path and response-loss behavior were not exercised in
  the browser.
- Save As, timeout execution, send failure and capacity recovery are not covered
  by automated lifecycle tests; the native tests construct pending-save state
  directly. This remains a bounded test-coverage gap.
- The synthetic Seafile E2E covers one text annotation only; it does not establish
  broad PDF feature compatibility. The file-list click path was not observed.
- The exact outgoing `pdfcraft:save` payload was not independently hashed at the
  browser boundary; see the E2E report for the readback hash and its limits.
- The change depends on the GR-016 shared transport patch, which is not yet an
  upstream published library revision.
- Only a bounded source/runtime review can assess this prototype; the overall
  project verdict remains the previous Sol FAIL.

## Review

Independent bounded review rounds 1–3: GPT-6.1 Sol low returned **FAIL**. Round 1 found
that a save acknowledgement could close over newer uncommitted form typing,
same-generation overlapping saves could lose a close callback, and unanswered
tickets could retain snapshots/capacity indefinitely. The patch now commits UI
typing before the generation check, coalesces/queues per-document requests,
expires unanswered browser tickets after 120 seconds, bounds retained bytes,
and releases app snapshots when a tab closes. Round 2 also returned **FAIL**:
paragraph line-editor drafts were not committed; callback lists and forgotten
timeout closures were not fully bounded. Round 3 found no blocker or major issue,
but identified that callback limits could be bypassed when callback groups were
wrapped during follow-up saves. The current scratch patch carries the retained
callback count through aggregation and tests the 64-callback boundary. Seven
focused native tests, Rust 1.95 WASM check, formatting and diff checks pass on
this revision. A fresh Rust 1.97 release build and Chromium smoke on the exact
current patch also pass. Sol low round 4 returned
**PASS** for this bounded prototype,
with no blocker/major and one non-blocking lifecycle-test minor. See
`REVIEW-SOL-LOW-R4.md`. That bounded code review does not change the project-
level GPT FAIL. The separate synthetic Seafile persistence/version/reopen
evidence is recorded in `SEAFILE-PDFCRAFT-E2E-20261024.md` and independently
reviewed below.

The synthetic Seafile E2E evidence was independently reviewed by Nemotron Free
round 1: **ACCEPT WITH MINOR QUALIFICATIONS**, with no blocker or major finding.
The reviewer confirmed that the file-list click and exact outbound payload hash
are explicitly not claimed, and that the fresh-instance screenshot shows the
annotation. The lifecycle-test coverage gap remains minor and is recorded in
[`REVIEW-NEMOTRON-SEAFILE-E2E-R1.md`](REVIEW-NEMOTRON-SEAFILE-E2E-R1.md). This
bounded review does not change the project-level GPT FAIL.
