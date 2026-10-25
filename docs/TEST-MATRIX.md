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
| 10.1 | CADCraft host adapter compiles for wasm32 | pinned adapter compiles with ticketed host transport from clean checkout | [x] Rust 1.95 locked check passes with immutable `craft-platform` `56c5e16`; repin exact review passes. See `docs/reviews/GR-018/` |
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
| 11.3 | FigCraft Web shared transport build | pinned shared transport compiles for `wasm32-unknown-unknown` | [x] Rust 1.95 locked check passes against immutable `56c5e16`; existing optional-font/dead-code warnings remain |
| 11.4 | Apply stored patch to pinned upstream base | all hunks apply to clean FigCraft SHA `8d790607ff1ad40e32343ca2116d8fdcf3244c8d` | [x] `git apply --check` passes against a clean archive |
| 11.5 | Browser transport + Seafile save/version/reopen | actual Seafile click, editor save ACK, version and fresh reopen | [ ] NOT VERIFIED; patch is not in dispatch and no FigCraft bundle/runtime run was performed |
| 11.6 | Host timeout, wrong-origin/source and production security | failure paths remain safe in a real browser topology | [ ] NOT VERIFIED; source implements 120-second unknown-outcome warning; runtime path not exercised |
| 11.7 | Single-document scope guards | host mode refuses new/open/duplicate/version-duplicate, branches and collaboration; unexpected extra dirty tabs remain visible and cannot be saved as the bound file | [x] synthetic UI test covers these dispatch paths, extra-tab dirty reporting and fail-closed save; browser controls NOT VERIFIED |
| 11.8 | Independent bounded patch review and transport re-pin | no blocker/major correctness finding on the exact patch | [x] Sol low round 3 PASS; repin R2 confirmed only transport pin changes beyond the accepted source hunks. One MINOR: dirty-state transport failure is not retried until state changes; project verdict unchanged |

Patch and limits: `docs/reviews/GR-019/README.md`.

## 12. DeckCraft durable host-save acknowledgement prototype (GR-020)

| # | Test | Expected | Result |
|---|---|---|---|
| 12.1 | External ACK without a filesystem path | only the matching snapshot becomes the saved baseline; later edits remain dirty | [x] 2 focused `deckcraft-engine` tests pass; pathful documents are refused |
| 12.2 | Synthetic host open/edit/save/ACK/reopen | no clean state before ACK; serialized bytes reopen with the saved edit | [x] 4 focused `deckcraft-ui-egui` tests pass, including failure ACK and edit-after-submit |
| 12.3 | DeckCraft Web shared transport compilation | pinned adapter compiles for `wasm32-unknown-unknown` | [x] Rust 1.95 locked WASM check passes on pin `56c5e16` |
| 12.4 | Host-mode single-document and Save As guards | no second document, path-open, or Save As can bypass the host binding | [x] UI dispatch and direct helpers guard the local adapter; bounded independent review PASS |
| 12.5 | Browser messaging with real DeckCraft WASM | parent open/save/ACK exchange works in browser | [ ] NOT VERIFIED |
| 12.6 | Seafile new version and fresh-storage reopen | saved presentation survives Seafile version creation and fresh editor load | [ ] NOT VERIFIED; DeckCraft is not in the Seafile dispatcher |
| 12.7 | Independent bounded review | no blocker/major/minor in exact local patch | [x] GPT-6 Luna high R2 reviewed app source; independent re-pin review verifies exact pin/artifact; see `REVIEW-TRANSPORT-REPIN.md` |
| 12.8 | Full DeckCraft workspace CI | all xtask steps pass | [~] `assets`, `layers`, and `wasm` pass; `xtask ci` stops at existing workspace Clippy errors; full workspace tests did not complete (long-running UI tests stopped) |

Patch, exact source pin, checks and evidence limits: `docs/reviews/GR-020/README.md`.

## 13. Shared host-message pre-copy and repeat-Open bounds (GR-021 remediation)

| # | Test | Expected | Result |
|---|---|---|---|
| 13.1 | Native `craft-platform` suite | protocol and lifecycle tests pass | [x] 7 passed via `./scripts/check-craft-platform.sh` |
| 13.2 | Browser parser test compilation | oversized ArrayBuffer/Uint8Array and strings rejected before Rust allocation/conversion | [x] `cargo check --features browser --target wasm32-unknown-unknown --tests` passes; tests compiled but were not browser-executed |
| 13.3 | Package manifest integrity | all packaged source/attribution hashes match | [x] `sha256sum -c SHA256SUMS` from `integration/rust/craft-platform/` passes (19 entries) |
| 13.4 | Independent bounded review | pre-copy caps close DesignCraft review P2 | [x] Luna high review PASS; browser tests compile-only; see `docs/reviews/GR-021/TRANSPORT-PRECOPY-REVIEW.md` |
| 13.5 | Repeated Open compatibility and shared budget | same-session OpenRequest works; repeated buffers remain bounded across transport/listener instances | [~] Native cumulative byte/message test passes; WASM sharing test compiles; Luna high round 4 found no functional issue; browser tests not executed; see `TRANSPORT-OPEN-ADMISSION-REVIEW.md` |
| 13.6 | DesignCraft application host-save checks | snapshot opens, matching durable ACK cleans only captured revision; failures/replacements stay dirty/refused | [x] Five focused Rust 1.95 tests and locked WASM check pass on pin `56c5e16`; see `docs/reviews/GR-021/DESIGNCRAFT-HOST-SAVE.md` |
| 13.7 | DesignCraft exact-patch review | no blocker/major in adapter after transport repin | [x] Luna high R3 plus independent repin review; P3 peak serialization-memory limit remains; see `DESIGNCRAFT-REVIEW-REPIN.md` |
| 13.8 | DesignCraft Seafile browser version/reopen | saved document is persisted as a Seafile version and reopened from Seafile | [ ] NOT VERIFIED; patch not in dispatcher |
| 13.9 | Malformed host save acknowledgements | missing/non-boolean `ok` does not consume a ticket as a false ACK; valid true/false retain behavior | [x] Parser tests cover malformed values and valid booleans; WASM test target compiled but was not browser-executed; 7 native tests and 19 checksums pass; see `docs/reviews/GR-024/` |

GR-024 does not establish browser runtime, Seafile persistence, or
application-level open/edit/save/reopen behavior. Active app patches must pin
immutable transport revision `56c5e16d79b77751106173c13111ef4fe0a2c0ec`.

## 14. FilmCraft durable host-save acknowledgement prototype (GR-023)

| # | Test | Expected | Result |
|---|---|---|---|
| 14.1 | Engine host-save snapshot/ACK | only the matching serialized `.fcproj` snapshot becomes saved; later edits stay dirty | [x] 4 focused engine tests pass after final host-close guard |
| 14.2 | UI Save/Save All/ACK lifecycle | matching host ACK clears only captured state; failure, stale and unknown ACKs stay dirty | [x] 3 focused UI tests pass after final host-close guard |
| 14.3 | Host mode lifecycle guards | create-from-template, close-all, save-as-template and direct project close cannot bypass binding | [x] engine/UI regression assertions present; independent source review confirms |
| 14.4 | Rust/WASM compile and formatting | pinned app builds with transport revision `56c5e16` | [x] Rust 1.95 locked WASM check, fmt and diff checks pass per implementer |
| 14.5 | Browser host messaging | real iframe Open/Save/ACK works in browser | [ ] NOT VERIFIED |
| 14.6 | Seafile version and fresh reopen | saved edit survives durable Seafile write and new editor instance | [ ] NOT VERIFIED; app not in dispatcher |

Patch, review and limitations: `docs/reviews/GR-023/README.md`.

## 9. How results are recorded

Each test result is recorded in the corresponding evidence bundle under
`docs/reviews/GR-XXX/` with:

```text
<test id> | <command or manual steps> | <observed result> | <evidence link>
```

A test that has not been run is `[ ]`, never `[x]`. A mock is not a result.

## 15. EffectCraft host-save acknowledgement prototype (GR-022)

| # | Test | Expected | Result |
|---|---|---|---|
| 15.1 | Host-mode project replacement and unsupported save routes | host-bound project cannot be replaced or locally saved as if durable | [x] engine/UI guards and focused tests pass per implementer |
| 15.2 | Save acknowledgement matches captured project snapshot | dirty clears only after matching success; later edits remain dirty | [x] focused engine/UI host-save tests pass; independent source review found no blocker/major |
| 15.3 | Initial Open after pre-open edits | no silent replacement; user receives truthful reload guidance | [x] source/test reviewed; browser presentation not exercised |
| 15.4 | Browser host protocol and Seafile version/reopen | durable version and edit visible after fresh storage reopen | [ ] NOT VERIFIED; adapter is not in dispatch |
| 15.5 | Production host authorization and security topology | permissions/origins/proxy controls verified | [ ] NOT VERIFIED |

Patch, commands, and limits: `docs/reviews/GR-022/`.

## 16. PhotoCraft host integration assessment (GR-026)

| # | Test | Expected | Result |
|---|---|---|---|
| 16.1 | Audit immutable PhotoCraft source | Findings refer to the requested exact SHA | [x] `storytold/photocraft` SHA `a02f2ee41059d3312e7ff24a5af5edcac7b6435a` inspected; evidence in `docs/reviews/GR-026/README.md` |
| 16.2 | Pathless open and revision-specific saved-baseline core | host names are not native paths; ACK only confirms the captured revision/incarnation | [x] R2 patch adds pathless open and per-open Arc identity; independent bounded PROVISIONAL PASS |
| 16.3 | Rust 1.95 focused engine/UI tests and Web WASM check | core stale/current/close-reopen ACK behavior, pathless open, and app compile pass | [x] Engine 4/4, UI 1/1, locked `photocraft-web` WASM check pass |
| 16.4 | Browser host flow / Seafile version / fresh reopen | Persisted edit reopens from new host session | [ ] NOT VERIFIED |
| 16.5 | ACK after closing and reopening same document ID | old ticket cannot modify a replacement document incarnation | [x] Incarnation-token regression is present and engine test passes; independent R2 review confirms source fix |

The core patch fixes stale-ACK identity and standard patch applicability. It is
not yet a PhotoCraft browser host adapter or project-level PASS. See
`docs/GR-026-PHOTOCRAFT-HOST-SAVE.md`.


## 17. SoundCraft host-save prototype (GR-025)

| # | Test | Expected | Result |
|---|---|---|---|
| 17.1 | Host snapshot ACK ledger | exact success ACK clears only captured state; failure/retry/timeout remain safe | [x] 2 focused host-save ledger tests pass; independent source review found no new blocker/major |
| 17.2 | Local picker/drop cannot replace host-bound session | dirty content and history remain unchanged | [ ] Regression added but not executed: test target blocked by existing base Symphonia 0.6.1 API errors |
| 17.3 | SoundCraft Web WASM build | pinned host adapter builds for browser target | [ ] BLOCKED: GR-027 audio and GR-028 playback now compile separately; full Web build reaches egui 0.36/0.37 mismatch in pinned craft-ui/UI |
| 17.4 | Browser host messaging and Seafile version/reopen | durable saved edit reopens from a fresh session | [ ] NOT VERIFIED; adapter is not in dispatch |

Patch, review, base-build blockers and limits: `docs/reviews/GR-025/`.


## 18. SoundCraft Symphonia compatibility (GR-027)

| # | Test | Expected | Result |
|---|---|---|---|
| 18.1 | Symphonia 0.6.1 audio crate native suite | Decoder, format and malformed-input behavior pass | [x] 57 tests pass |
| 18.2 | Audio crate WASM check | Audio crate compiles for browser target | [x] Rust 1.95 locked check passes |
| 18.3 | Root container / MP4 preflight edge cases | Markers only select root format; ftyp bounds and padded offset are checked; null codec skipped | [x] Regressions added; GR-027 exact review R5 provisional PASS |

## 19. SoundCraft CPAL playback compatibility (GR-028)

| # | Test | Expected | Result |
|---|---|---|---|
| 19.1 | Playback native and WASM checks | Locked CPAL 0.18.2 APIs compile | [x] Reran in this session; both pass |
| 19.2 | Playback native unit tests | Playback/recording behavior remains covered | [x] Reran in this session; 36 pass |
| 19.3 | Full SoundCraft Web WASM | App and host adapter compile | [ ] BLOCKED by separate egui 0.36/0.37 mismatch in existing UI/dependency code |
| 19.4 | Browser host save / Seafile version / fresh reopen | Durable version and edit survive reopen | [ ] NOT VERIFIED |

Independent CPAL patch review: `docs/reviews/GR-028/REVIEW-INDEPENDENT-R1.md`.
