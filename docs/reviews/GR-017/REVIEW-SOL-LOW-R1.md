# GR-017 bounded review — GPT-6.1 Sol low, round 1

**Result:** FAIL for this bounded prototype only. No overall project verdict.

## Findings

1. **BLOCKER — UI-only form typing could be lost on an old save acknowledgement.**
   `settle_host_saves()` compared only the engine edit generation. PdfCraft form
   drafts count as unsaved work without changing that generation, so a
   save-and-close callback could close the tab while newer field typing remained
   only in the view.
2. **MAJOR — overlapping saves could drop a close callback.** A Save followed
   by Save-and-close on the same generation created two tickets. The first
   `mark_saved()` increments the generation, causing the second result to look
   stale and discard its callback.
3. **MAJOR — unanswered tickets permanently consumed save capacity.** The
   bridge and app tables were bounded by count only; there was no expiry,
   cancellation or byte budget, and closing a tab did not release its retained
   snapshot.
4. **MINOR — tests bypassed the actual lifecycle.** Tests inserted pending
   records directly and did not cover drafts, overlapping requests, close
   callbacks or capacity recovery.

Positive checks: shared transport validates exact origin and parent source;
duplicate/unknown tickets are ignored; non-host browser download behavior stays
structurally unchanged. The reviewer did not rerun builds or tests.

## Remediation in the revised patch

- Commit UI typing before deciding whether an acknowledgement still matches the
  current generation; stale acknowledgements cannot close over a new form edit.
- Coalesce same-document/same-generation requests; queue a follow-up save for
  newer generations or different targets and carry close callbacks to it.
- Expire browser tickets after 120 seconds, cap retained PDF snapshots at 256
  MiB, and release app-held snapshots when a tab closes.
- Add five native tests for failed/duplicate results, exact-generation success,
  typing during save, same-snapshot coalescing/close callback, and tab cleanup.

At that round, the revised patch passed five native tests, Rust 1.95 WASM
`cargo check`, `cargo fmt --check`, and `git diff --check`. Sol low round 2
subsequently returned FAIL; its findings and their status are recorded in
`REVIEW-SOL-LOW-R2.md`. Round 3 is reviewing the current exact patch. Browser
smoke now verifies a synthetic `sessionStorage` save/reopen, but Seafile
version/reopen and timeout execution remain NOT VERIFIED.
