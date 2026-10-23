# Test Matrix

Every row is a test that must exist and have a **recorded result** before the
project may claim the MVP. Synthetic files only — no personal documents, no
production data.

Legend: `[ ]` not implemented · `[~]` implemented, not run · `[x]` passed ·
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
| 1.9 | Read-only file | the editor opens in view mode, save is refused server-side | [ ] the gateway enforces it; the browser path is not driven yet |
| 1.10 | Save failure (editor server error / network) | the editor stays dirty, the UI does **not** claim success | [ ] the HTTP path is covered (409/404); the browser path is not driven yet |
| 1.11 | Editor closed with unsaved changes | the user is warned, no version is created | [ ] not yet exercised |
| 1.12 | Concurrent modification (user B saves first) | user A's save is **refused** with a conflict, nothing is overwritten | [x] Two real WordCraft sessions: stale session received 409 and stayed dirty; simultaneous conditional requests also yielded one 200/one 409. External writers not covered; see isolated runtime evidence |

## 2. DOCX — failure and edge cases (GR-007, GR-008, GR-009)

| # | Test | Expected | Result |
| --- | --- | --- | --- |
| 2.1 | Browser reload during editing | session is re-established or the user is told to reopen; no silent data loss | [ ] |
| 2.2 | Network loss during save | save fails cleanly, document stays dirty | [ ] |
| 2.3 | Interrupted upload | no partial version is committed | [ ] |
| 2.4 | Double save / overlapping editor tickets | no lost update or false clean state | [x] Patched Seahub/C fileserver rejected one of two simultaneous conditional writes (200/409); two editor sessions also exercised sequential stale-write rejection. The direct simultaneous calls were not two simultaneous editor keystroke saves; see isolated runtime evidence |
| 2.5 | Expired session | the save is refused with an explicit "session expired", not a generic error | [ ] |
| 2.6 | Invalid / forged token | the request is rejected; nothing is read or written | [ ] |
| 2.7 | Permission revoked while editing | the save is refused | [ ] |
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
| 2.18 | Read-only bypass attempt (craft a save request) | rejected server-side | [ ] |
| 2.19 | Share-link session without write permission | save refused | [ ] |

## 3. XLSX — GridCraft (GR-010)

| # | Test | Expected | Result |
| --- | --- | --- | --- |
| 3.1 | Open a synthetic XLSX from Seafile Web | GridCraft Web opens inline | [~] historical browser simulation; no current Seafile dispatch evidence |
| 3.2 | Edit a cell value | value changes | [~] historical simulated editor run; not an accepted E2E result |
| 3.3 | Edit a formula | formula recomputes | [ ] not yet exercised |
| 3.4 | Minimal formatting | applied | [ ] not yet exercised |
| 3.5 | Save | new Seafile version | [ ] NOT VERIFIED; GridCraft bridge cannot consume durable save acknowledgement |
| 3.6 | Reopen | values and formulas preserved | [ ] NOT VERIFIED; previous assertion inspected bytes, not a reopened GridCraft editor |
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
| 5.1 | Open a synthetic PDF | PdfCraft Web opens inline | [ ] |
| 5.2 | Edit the PDF | the change is applied | [ ] |
| 5.3 | Save the PDF | new Seafile version | [ ] |
| 5.4 | Reopen the PDF | the change is preserved | [ ] |
| 5.5 | Open a synthetic SVG | VectorCraft Web opens inline | [ ] |
| 5.6 | Edit the SVG | the change is applied | [ ] |
| 5.7 | Save the SVG | new Seafile version | [ ] |
| 5.8 | Reopen the SVG | the change is preserved | [ ] |

## 6. Dispatcher and platform

| # | Test | Expected | Result |
| --- | --- | --- | --- |
| 6.1 | The extension → editor table is configurable without a code change | the table is read from configuration | [ ] |
| 6.2 | An unknown extension | the normal Seafile download/preview path is used, unchanged | [ ] |
| 6.3 | The existing ONLYOFFICE integration still works | `.docx` opened in the ONLYOFFICE path is unaffected | [ ] NOT VERIFIED — no browser open/edit/save regression was run |
| 6.4 | The ONLYOFFICE configuration is untouched | `seahub_settings.py` keeps `ENABLE_ONLYOFFICE = True` and the same 15 extensions | [x] SSH read-only check after removing the third-party `.xlsx` route; no ONLYOFFICE setting changed |
| 6.5 | The integration is reachable through configured origins | ArtCraft host/Craft are same-origin; Seahub is a separate origin; only `/open/` accepts Seahub Origin | [~] Browser flow works through a test-only same-origin proxy; intended separate-origin deployment, TLS and origin isolation remain NOT VERIFIED |
| 6.6 | Rollback | removing the added route restores the previous behaviour | [ ] |

## 7. Security (GR-009)

See `docs/SECURITY.md` for the full threat list. The matrix rows above 2.15-2.19
are the executable part of it.

## 8. How results are recorded

Each test result is recorded in the corresponding evidence bundle under
`docs/reviews/GR-XXX/` with:

```text
<test id> | <command or manual steps> | <observed result> | <evidence link>
```

A test that has not been run is `[ ]`, never `[x]`. A mock is not a result.
