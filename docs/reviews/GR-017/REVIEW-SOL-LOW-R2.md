# GR-017 bounded review — GPT-6.1 Sol low, round 2

**Result:** FAIL for this bounded prototype only. No overall project verdict.

## Findings

1. **BLOCKER — paragraph line-editor drafts could be lost.** `line_editor`
   drafts count as unsaved work without advancing the engine generation. The
   prior settlement path committed form/fill typing but not the active
   paragraph draft before accepting a save acknowledgement and running a close
   callback.
2. **MINOR — tests bypassed save submission and close workflows.** Tests
   manufactured pending records and did not verify real submission, queued
   follow-ups, Save As, timeout execution, or capacity recovery.
3. **MINOR — callbacks and timeout closures were not fully bounded.** Coalesced
   close callbacks could grow without a cap. Browser timeout closures were
   forgotten and remained allocated until their 120-second timeout even after
   successful acknowledgements.

Verified improvements from round 1: form drafts were committed before snapshot
comparison; same-snapshot saves coalesced; follow-up saves retained callbacks;
pending snapshots had count/byte limits and tab-close cleanup; browser tickets
expired after 120 seconds; origin/source checks remained intact.

## Remediation under review

- Commit pending paragraph edits before comparing generations or running close
  callbacks; restore the line editor if the engine rejects the edit.
- Add a regression test that injects paragraph typing while a save is pending
  and confirms the old acknowledgement cannot close the tab or lose the text.
- Cap coalesced callbacks at 64 per document and surface capacity exhaustion.
- Retain timer closures by ticket and clear/drop them on acknowledgement, send
  failure, or processed timeout instead of leaking them with `forget()`.
- Add a callback-cap test.

## Reproduced checks

- `CARGO_BUILD_JOBS=2 CARGO_PROFILE_TEST_DEBUG=0 CARGO_INCREMENTAL=0 cargo +1.95.0 test -p pdfcraft-ui-egui host_save_ack_tests` — **PASS**, 7 tests.
- `CARGO_BUILD_JOBS=2 CARGO_PROFILE_DEV_DEBUG=0 CARGO_INCREMENTAL=0 cargo +1.95.0 check -p pdfcraft-web --target wasm32-unknown-unknown --locked --offline` — **PASS**; pre-existing unused/dead-code warnings.
- `CARGO_BUILD_JOBS=2 CARGO_PROFILE_RELEASE_DEBUG=0 CARGO_INCREMENTAL=0 trunk build --release` — **PASS**.
- `cargo +1.95.0 fmt --all -- --check` — **PASS**.
- `git diff --check` — **PASS**.
- Browser smoke with PdfCraft release WASM in Chromium and a same-origin synthetic host: opened fixture `form.pdf`, typed `test async PDF host save` into an interactive field, pressed Ctrl+S, received ticket `pdfcraft:1` with 2,395 bytes, acknowledged success, observed dirty sequence `false → true → false`, reloaded the iframe from synthetic `sessionStorage`, and visually confirmed the typed value remained rendered. This proves the PdfCraft bridge round trip against synthetic browser storage only.

## Limits

No Seafile API, library, version history, real durable storage, or production
service was used. Browser storage was `sessionStorage`. The manual browser run
does not replace an automated test of actual save submission, Save As,
timeout/response loss, or repeated close actions. The patch still depends on
the temporary GR-016 transport path and is not portable or upstream-ready.
