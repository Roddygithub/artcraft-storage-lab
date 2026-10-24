# Test Matrix

Every row is a test that must exist and have a **recorded result** before the
project may claim the MVP. Synthetic files only — no personal documents, no
production data.

Legend: `[ ]` not implemented · `[~]` partially verified / evidence limited · `[x]` passed ·
`[!]` failed (see the evidence bundle) · `[-]` out of scope

## 1. DOCX — WordCraft (GR-006, mandatory MVP)

| # | Test | Expected | Result |
| --- | --- | --- | --- |
| 1.1 | Open a synthetic DOCX from Seafile Web | WordCraft Web opens inline, no download, no manual upload | [x] Real click in isolated patched Seahub; actual WordCraft JS/WASM opened; see `docs/reviews/GR-015/ISOLATED-RUNTIME-E2E-20261023.md` |
| 1.2 | The document content is loaded and visible | the DOCX is parsed and rendered | [x] Isolated runtime E2E; real WordCraft rendered synthetic DOCX text |
| 1.3 | Edit plain text | the change is visible in the editor | [x] Isolated runtime E2E; typed a synthetic sentence in WordCraft |
| 1.4 | Apply simple formatting (bold/italic/paragraph) | the change is applied | [ ] not yet exercised |
| 1.5 | Save | bytes are returned to the host, a new Seafile version is created | [x] Patched local Seahub/C fileserver committed new head and file ID; independent metadata and content readback recorded in isolated runtime evidence |
| 1.6 | The editor confirms the save | the editor reports success **only** after Seafile accepted the write | [x] Real WordCraft UI showed `Saved — new version` after Seahub received fileserver response and read committed head |
| 1.7 | Close the editor and reopen the file from Seafile | the modification is present | [x] Navigated away and clicked the file again; fresh WordCraft session rendered saved sentence |
| 1.8 | A new Seafile version exists | the file history shows one more version | [x] Head and file ID changed; history listed the new committed revision; details in isolated runtime evidence |
| 1.9 | Read-only file | the editor opens in view mode, save is refused server-side | [~] patched Django save route refused current `r` permission (403 before update token/fileserver); browser view-mode UX is not tested |
| 1.10 | Save failure (editor server error / network) | the editor stays dirty, the UI does **not** claim success | [ ] the HTTP path is covered (409/404); the browser path is not driven yet |
| 1.11 | Editor closed with unsaved changes | the user is warned, no version is created | [ ] not yet exercised |
| 1.12 | Concurrent modification (user B saves first) | stale save is **refused** with a conflict, nothing is overwritten | [x] Two edited real WordCraft sessions sent Ctrl+S concurrently: one committed and showed a new version; the other returned 409 and stayed dirty; fresh Seahub click/reopen rendered only the winning change. External writers not covered; see isolated runtime evidence |

## 2. DOCX — failure and edge cases (GR-007, GR-008, GR-009)

| # | Test | Expected | Result |
| --- | --- | --- | --- |
| 2.1 | Browser reload during editing | session is re-established or the user is told to reopen; no silent data loss | [ ] |
| 2.2 | Network loss during save | save fails cleanly, document stays dirty | [ ] |
| 2.3 | Interrupted upload | no partial version is committed | [ ] |
| 2.4 | Double save / overlapping editor tickets | no lost update or false clean state | [x] Two real WordCraft editors saved concurrently through the bridge; one got a durable version, the loser got 409 and stayed dirty; fresh editor reopen confirmed the winner. This is separate tabs, not two overlapping tickets in one editor. See isolated runtime evidence |
| 2.5 | Expired session | the save is refused with an explicit "session expired", not a generic error | [ ] |
| 2.6 | Invalid / forged token | the request is rejected; nothing is read or written | [ ] |
| 2.7 | Permission revoked while editing | the save is refused | [~] patched Django save route refused a cached edit capability after current permission changed from `rw` to `r`; Seafile RPC/storage were synthetic |
| 2.8 | File deleted while editing | the save is refused with "file no longer exists" | [ ] |
| 2.9 | File renamed while editing | the save is refused or explicitly re-targeted, never silently written elsewhere | [ ] |
| 2.10 | Large file | either handled within a documented limit, or refused with a clear message | [ ] |
| 2.11 | Malformed / corrupt DOCX | a clear error, no crash, no save | [ ] |
| 2.12 | Unsupported format opened with a Craft | a clear "not supported by this editor" message | [x] GR-005 (the gateway refuses an extension it has no editor for) |
| 2.13 | ZIP-bomb-like DOCX (huge uncompressed size) | refused at a documented threshold | [ ] |
| 2.14 | Path traversal in the file path | normalised and rejected | [ ] |
| 2.15 | Cross-user access attempt (user B's session token used for user A's file) | rejected | [ ] not yet exercised |
| 2.16 | `postMessage` from an unexpected origin | ignored and logged | [ ] |
| 2.17 | Save forgery (crafted callback) | rejected: the callback is bound to a server-side session | [ ] |
| 2.18 | Read-only bypass attempt (craft a save request) | rejected server-side | [~] direct POST through actual Django URL returned 403; no update token or fileserver call; Seafile RPC/storage were synthetic |
| 2.19 | Share-link session without write permission | save refused | [ ] |

## 3. XLSX — GridCraft (GR-010)

| # | Test | Expected | Result |
| --- | --- | --- | --- |
| 3.1 | Open a synthetic XLSX from Seafile Web | GridCraft Web opens inline | [x] real Seahub file-list click in isolated synthetic Seafile opened GridCraft Web/WASM; see `docs/reviews/GR-010/GRIDCRAFT-SEAFILE-E2E-20261023.md` |
| 3.2 | Edit a cell value | value changes | [x] real GridCraft edit; saved value appeared in a fresh GridCraft session after a Seahub click |
| 3.3 | Edit a formula | formula recomputes | [ ] not yet exercised |
| 3.4 | Minimal formatting | applied | [ ] not yet exercised |
| 3.5 | Save | new Seafile version | [~] patched bridge received a committed head/file ID from isolated Seafile; host showed `Stored — new version`; readback bytes/hash recorded, but history-list count was not independently queried (browser API returned 403) |
| 3.6 | Reopen | values and formulas preserved | [~] fresh GridCraft session displayed the saved A3 edit; valid XLSX retained the B3 formula and cached value, but recalculation after changing an input is NOT VERIFIED |
| 3.7 | Concurrent edit | conflict, no silent overwrite | [~] fake-CAS unit test only; Seafile fileserver behavior is NOT VERIFIED |

## 4. PPTX — DeckCraft (GR-011)

| # | Test | Expected | Result |
| --- | --- | --- | --- |
| 4.1 | Open a synthetic PPTX | DeckCraft Web opens inline | [ ] |
| 4.2 | Edit a slide | the change is visible | [ ] |
| 4.3 | Save | new Seafile version | [ ] |
| 4.4 | Reopen | the slide change is preserved | [ ] |

## 5. PDF and SVG — proving non-Office formats (GR-012)

| # | Test | Expected | Result |
| --- | --- | --- | --- |
| 5.1 | Open a synthetic PDF | PdfCraft Web opens inline | [~] Actual PdfCraft WASM opened a synthetic PDF through its direct Seahub file route; file-list click was not observed. See `docs/reviews/GR-017/SEAFILE-PDFCRAFT-E2E-20261024.md` |
| 5.2 | Edit the PDF | the change is applied | [x] Added a text annotation with PdfCraft's UI; fresh instance rendered it after reload. Same evidence report |
| 5.3 | Save the PDF | new Seafile version | [x] Host showed `Saved — new version`; isolated Seafile history grew from one to two commits and file ID changed. Same evidence report |
| 5.4 | Reopen the PDF | the change is preserved | [x] Fresh PdfCraft instance rendered `PdfCraftSeafileRoundTrip`; Seafile readback parsed and contained the annotation. Same evidence report |
| 5.5 | Open a synthetic SVG | VectorCraft Web opens inline | [x] Real Seahub file-list click in isolated synthetic Seafile; VectorCraft Web loaded; see `docs/reviews/GR-012/VECTORCRAFT-SEAFILE-E2E-20261023.md` |
| 5.6 | Edit the SVG | the change is applied | [x] Real VectorCraft pencil API drew a path; fresh editor inspect showed expected geometry |
| 5.7 | Save the SVG | new Seafile version | [x] Post-fix runtime: editor output 695 B; gateway readback hash matched; new file ID/version returned; History UI showed 270 B → 609 B → 695 B |
| 5.8 | Reopen the SVG | the change is preserved | [x] Fresh route load in VectorCraft parsed the 695 B saved SVG and showed the new path; common host-contract coverage remains unproven |
| 5.9 | Poll changed serialized bytes despite a 32-bit hash collision | exact changed bytes reach host storage once; identical output does not create duplicate saves | [x] Synthetic Chromium test uses two distinct equal-length values with the same old FNV-1a hash; post-fix VectorCraft/Seafile save/readback/reopen also passed |
| 5.10 | Retry a rejected VectorCraft write | keep the edited bytes pending and retry until persistence succeeds | [x] Synthetic Chromium test returns 503 on first write, confirms dirty state, then verifies retry and no further write after the exact bytes are stored; not a Seafile runtime test |

## 6. Dispatcher and platform

| # | Test | Expected | Result |
| --- | --- | --- | --- |
| 6.1 | The extension → editor table is configurable without a code change | the table is read from configuration | [ ] |
| 6.2 | An unknown extension | the normal Seafile download/preview path is used, unchanged | [ ] |
| 6.3 | The existing ONLYOFFICE integration still works | `.docx` opened in the ONLYOFFICE path is unaffected | [ ] NOT VERIFIED — no browser open/edit/save regression was run |
| 6.4 | The ONLYOFFICE configuration is untouched | `seahub_settings.py` keeps `ENABLE_ONLYOFFICE = True` and the same 15 extensions | [x] SSH read-only check after removing the third-party `.xlsx` route; no ONLYOFFICE setting changed |
| 6.5 | The integration is reachable through configured origins | ArtCraft host/Craft are same-origin; Seahub is a separate origin; only `/open/` accepts Seahub Origin | [x] Synthetic Chromium run used Seahub `:18000` and gateway/Craft `:18777`; `/open/` handoff, editor save, fresh route load and persisted bytes verified. Production TLS/proxy, CSP/CSRF and adversarial frame testing remain NOT VERIFIED |
| 6.6 | Rollback | removing the added route restores the previous behaviour | [ ] |

## 7. Security (GR-009)

See `docs/SECURITY.md` for the full threat list. The matrix rows above 2.15-2.19
are the executable part of it.

## 8. Shared Rust host transport prototype (GR-016)

| # | Test | Expected | Result |
| --- | --- | --- | --- |
| 8.1 | Opaque save ticket round-trip, one-time ack, bounded pending queue | JS-safe string IDs; duplicate/unknown results rejected; at most 64 pending saves | [x] 4 host protocol unit tests pass in standalone packaged crate using `./scripts/check-craft-platform.sh`; app dependencies pin its immutable commit |
| 8.2 | Parent message origin/source validation | exact origin and parent source required | [~] native predicate tests pass; actual browser message source not exercised |
| 8.3 | Shared browser transport compilation | Rust/WASM transport builds | [x] Standalone crate WASM check and four clean-checkout app WASM checks pass; exact pins in `PORTABLE-APP-PATCHES-20261024.md` |
| 8.4 | WordCraft and GridCraft adapters compile with shared transport | both pinned apps build for WASM from clean checkouts | [x] Rust 1.95 `cargo check ... --locked` passes for both against the immutable packaged transport revision; report: `docs/reviews/GR-016/PORTABLE-APP-PATCHES-20261024.md` |
| 8.5 | Browser editor saves only become clean after durable host ack | failed/stale/unknown responses keep document dirty | [~] Chromium smoke tests passed for WordCraft and GridCraft against a synthetic `sessionStorage` host; both apps stayed dirty after explicit host rejection |
| 8.6 | Browser app reopen from saved bytes after shared refactor | app displays the saved edit | [~] fresh iframe reopen passed for both apps; XLSX ZIP/formula integrity checked |
| 8.7 | WordCraft Seafile save-version-reopen flow after shared refactor | saved edit survives fresh app reopen from Seafile | [x] Reproduced on synthetic Seafile 2026-10-24. Functional release-profile build used scratch `data-wasm-opt="0"`; optional wasm-opt optimization not run. See GR-016 WordCraft E2E report. |
| 8.8 | GridCraft in-app Open requests a file from the host | parent receives `gridcraft:openRequest` and supplies the selected bytes | [x] Rust 1.95 release bundle: Ctrl+O emitted one request; synthetic parent returned stored bytes; GridCraft displayed `HostAck`; screenshot in GR-016 |
| 8.9 | Independent review of GridCraft Open/MSRV/ack remediations | no blocker or major finding remains | [x] GPT-6.1 Sol low provisional bounded PASS; three minor findings in `docs/reviews/GR-016/REVIEW-SOL-LOW-R3.md` |
| 8.10 | Seafile single-file host handles Craft `openRequest` | explain that another document must be opened from Seafile; preserve dirty state and do not broaden the current file capability | [x] T3 Chromium preview with synthetic same-origin frame: guidance shown and `dirty=true` retained; no Seafile file picker is implemented |
| 8.11 | GridCraft Seafile save-version-reopen flow after shared refactor | saved workbook survives fresh app reopen from Seafile | [x] Synthetic Seafile runtime 2026-10-24; new history/file ID, valid XLSX readback, A1 edit visible after fresh GridCraft load. Separate B2=42→1337 edit recalculated `SUM(B2:B2)` to 1337, was versioned, read back and verified in a fresh editor. Scratch build used `data-wasm-opt="0"`; exact editor→gateway byte hash and optimized bundle remain unverified. See GR-016 GridCraft E2E report. |
| 8.12 | Independent review of GR-016 Seafile evidence | no blocker/major in bounded evidence review | [x] Nemotron re-review accepted the updated WordCraft/GridCraft evidence with minor qualifications. Formula recalculation is verified; outbound byte hash and optimized bundle remain limitations. See `REVIEW-NEMOTRON-GRIDCRAFT-E2E-R2-20261024.md`. |
| 8.13 | Standalone craft-platform artifact | no scratch checkout; metadata, native tests, browser WASM check and pinned app builds pass | [x] Package review had no blocker/major; metadata uses `--locked`; WordCraft, GridCraft, PdfCraft and CADCraft clean-checkout builds pass against immutable revision `90c261d`; see GR-016 portable package/app reports |
| 8.14 | Independent review of portable app patch follow-up | exact pins, patches and docs reviewed; no blocker/major remains | [x] GPT-6.1 Sol low bounded PASS after two minor remediations; see `REVIEW-PORTABLE-APP-PATCHES-SOL-LOW-20261024.md` |

GridCraft now declares Rust 1.95 in the scratch prototype to match current
dependency MSRVs. Full commands, warnings and exact pinned SHAs are in
`docs/reviews/GR-016/README.md`.

## 9. PdfCraft durable host-save acknowledgement prototype (GR-017)

| # | Test | Expected | Result |
| --- | --- | --- | --- |
| 9.1 | PdfCraft Web compiles against shared Rust/WASM transport | pinned adapter compiles for `wasm32-unknown-unknown` from clean checkout | [x] Rust 1.95 locked check passes with the immutable packaged transport revision; exact evidence in GR-016 portable app report |
| 9.2 | Host save rejection and duplicate result | document remains dirty; duplicate ticket cannot clear it | [x] native focused test passed with synthetic PDF fixture |
| 9.3 | Durable success with no later edit | exact saved snapshot becomes clean | [x] covered in the successful-ack test |
| 9.4 | Edit/form/paragraph typing after request, then success for old snapshot | newer input stays dirty and a close callback cannot discard it | [x] native focused tests commit queued form and paragraph drafts before evaluating the ack |
| 9.5 | Same-snapshot Save and Save-and-close | one pending ticket preserves the close callback | [x] native coalescing/settlement test |
| 9.6 | Closing/discarding a tab with a save pending | app releases its retained PDF bytes | [x] native pending-snapshot cleanup test; browser bridge ticket expires after 120 seconds by code, not runtime-tested |
| 9.7 | PdfCraft release bundle and browser message round trip | browser receives bytes and responds with durable result | [x] exact-patch release build and Chromium form edit/Ctrl+S/ACK/fresh iframe reopen; `sessionStorage` only, not Seafile; see `docs/reviews/GR-017/RUNTIME-SMOKE-R4.md` |
| 9.8 | PdfCraft save → Seafile new version → reopen | persisted edit appears after fresh editor open | [x] Isolated synthetic Seafile E2E: 655-byte fixture → 2,034-byte PDF, new file ID/history commit, API readback parsed with annotation, fresh PdfCraft instance rendered it. Opened via direct Seahub file route, not observed list click; editor-to-gateway payload hash not captured. See `docs/reviews/GR-017/SEAFILE-PDFCRAFT-E2E-20261024.md` |
| 9.9 | Bounded code review of PdfCraft save acknowledgement | no blocker/major in exact patch | [x] GPT-6.1 Sol low round 4 PASS; lifecycle test coverage remains minor. This code review is separate from the Seafile runtime evidence in 9.8 |

Patch, commands and limits: `docs/reviews/GR-017/README.md`.

## 10. CADCraft durable host-save acknowledgement prototype (GR-018)

| # | Test | Expected | Result |
|---|---|---|---|
| 10.1 | CADCraft host adapter compiles for wasm32 | pinned adapter compiles with ticketed host transport from clean checkout | [x] Rust 1.95 locked check passes with immutable packaged transport revision; exact evidence in GR-016 portable app report |
| 10.2 | Save acknowledgement engine behavior | success, rejection, stale edit, expiry cancellation, capacity and overlap rules preserve data integrity | [x] 8 focused `host_ack_tests` pass, including undo to acknowledged snapshot |
| 10.3 | CADCraft engine regression suite | existing engine behavior remains intact | [x] 344 `cadcraft-engine` library tests pass |
| 10.4 | CADCraft browser save ACK and fresh-editor reopen | edit serializes, host receives/hash-checks bytes, ACK clears dirty, fresh editor reopens saved bytes | [x] Local Chromium synthetic-host smoke 2026-10-24; 17,504 bytes, SHA-256 recorded, circle visible after fresh editor reopen. No Seafile persistence. See `CADCRAFT-BROWSER-ACK-SMOKE-20261024.md` |
| 10.5 | CADCraft negative ACK preserves dirty state and allows retry | failure does not mark clean; a new save ticket can later succeed | [x] Chromium synthetic host rejected `cadcraft:1`; dirty stayed true; retry `cadcraft:2` succeeded and cleared dirty. No Seafile persistence. See `CADCRAFT-BROWSER-ACK-SMOKE-20261024.md` |
| 10.6 | CADCraft timeout scheduling, export feedback and origin/source rejection | browser host protocol handles negative and adversarial paths | [ ] NOT VERIFIED in browser; source-level behavior bounded-reviewed by Sol, runtime paths remain untested |
| 10.7 | CADCraft save → Seafile new version → close/reopen | saved CAD drawing persists and reopens with edit intact | [x] Reproduced 2026-10-24 in isolated synthetic Seafile: two history commits, new file ID, 17,501-byte DXF readback with CIRCLE, fresh Seahub click reopened the circle. Editor→gateway byte hash not captured; see `CADCRAFT-SEAFILE-E2E-20261024.md` |
| 10.8 | Independent bounded code review | no blocker/major correctness issue in exact patch | [x] GPT-6.1 Sol low round 4 PASS; local prototype only; reproducible package build separately verified; overall project remains FAIL |

Patch and bounded-review reports: `docs/reviews/GR-018/`.

## 11. FigCraft durable host-save adapter prototype (GR-019)

| # | Test | Expected | Result |
|---|---|---|---|
| 11.1 | External ACK without a filesystem path | only the matching serialized snapshot becomes the saved baseline | [x] 3 focused `figcraft-engine` tests pass; later edits remain dirty and pathful native documents cannot be externally acknowledged |
| 11.2 | Synthetic host open/edit/save/ACK flow | no clean state before ACK; unknown ticket ignored; exact snapshot bytes reopen; later edit remains dirty | [x] 1 focused `figcraft-ui-egui` test passes with a mock transport service and real FigCraft serialization |
| 11.3 | FigCraft Web shared transport build | pinned shared transport compiles for `wasm32-unknown-unknown` | [x] Rust 1.95 locked check passes; existing optional-font/dead-code warnings remain |
| 11.4 | Apply stored patch to pinned upstream base | all hunks apply to clean FigCraft SHA `8d790607ff1ad40e32343ca2116d8fdcf3244c8d` | [x] `git apply --check` passes against a clean archive |
| 11.5 | Browser transport + Seafile save/version/reopen | actual Seafile click, editor save ACK, version and fresh reopen | [ ] NOT VERIFIED; patch is not in dispatch and no FigCraft bundle/runtime run was performed |
| 11.6 | Host timeout, wrong-origin/source and production security | failure paths remain safe in a real browser topology | [ ] NOT VERIFIED; source implements 120-second unknown-outcome warning; runtime path not exercised |
| 11.7 | Single-document scope guards | host mode refuses new/open/duplicate/version-duplicate, branches and collaboration; unexpected extra dirty tabs remain visible and cannot be saved as the bound file | [x] synthetic UI test covers these dispatch paths, extra-tab dirty reporting and fail-closed save; browser controls NOT VERIFIED |
| 11.8 | Independent bounded patch review | no blocker/major correctness finding on exact patch SHA | [x] GPT-6.1 Sol low round 3 PASS; one MINOR: dirty-state transport failure is not retried until the state changes; project verdict unchanged |

Patch and limits: `docs/reviews/GR-019/README.md`.

## 12. DeckCraft durable host-save acknowledgement prototype (GR-020)

| # | Test | Expected | Result |
|---|---|---|---|
| 12.1 | External ACK without a filesystem path | only the matching snapshot becomes the saved baseline; later edits remain dirty | [x] 2 focused `deckcraft-engine` tests pass; pathful documents are refused |
| 12.2 | Synthetic host open/edit/save/ACK/reopen | no clean state before ACK; serialized bytes reopen with the saved edit | [x] 4 focused `deckcraft-ui-egui` tests pass, including failure ACK and edit-after-submit |
| 12.3 | DeckCraft Web shared transport compilation | pinned adapter compiles for `wasm32-unknown-unknown` | [x] Rust 1.95 locked WASM check passes |
| 12.4 | Host-mode single-document and Save As guards | no second document, path-open, or Save As can bypass the host binding | [x] UI dispatch and direct helpers guard the local adapter; bounded independent review PASS |
| 12.5 | Browser messaging with real DeckCraft WASM | parent open/save/ACK exchange works in browser | [ ] NOT VERIFIED |
| 12.6 | Seafile new version and fresh-storage reopen | saved presentation survives Seafile version creation and fresh editor load | [ ] NOT VERIFIED; DeckCraft is not in the Seafile dispatcher |
| 12.7 | Independent bounded review | no blocker/major/minor in exact local patch | [x] GPT-6 Luna high R2 PASS on `b00e36ec…7186`; see `docs/reviews/GR-020/REVIEW-LUNA-HIGH-R2.md` |
| 12.8 | Full DeckCraft workspace CI | all xtask steps pass | [~] `assets`, `layers`, and `wasm` pass; `xtask ci` stops at existing workspace Clippy errors; full workspace tests did not complete (long-running UI tests stopped) |

Patch, exact source pin, checks and evidence limits: `docs/reviews/GR-020/README.md`.

## 9. How results are recorded

Each test result is recorded in the corresponding evidence bundle under
`docs/reviews/GR-XXX/` with:

```text
<test id> | <command or manual steps> | <observed result> | <evidence link>
```

A test that has not been run is `[ ]`, never `[x]`. A mock is not a result.
