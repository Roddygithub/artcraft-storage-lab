# Test Matrix

Every row is a test that must exist and have a **recorded result** before the
project may claim the MVP. Synthetic files only — no personal documents, no
production data.

Legend: `[ ]` not implemented · `[~]` partially verified / evidence limited · `[x]` passed ·
`[!]` failed (see the evidence bundle) · `[-]` out of scope

## GR-082 — upstream refresh and automatic release tracking

| Scenario | Expected | Result |
|---|---|---|
| Official release references | Resolve exact tags/commits and compare with qualified bases | [~] All five pins and ahead/behind counts were independently verified through official API compare results; first retained scanner run resolved WordCraft/GridCraft, then hit API rate limits on PdfCraft/VectorCraft/PhotoCraft (`unknown`). Its two retained null `merge_base` values predate the parser fix and provide no merge-base evidence |
| Stable-release monitor behavior | Report drift without changing source pins or deployment; retry transient API failures and treat unknown results as incomplete | [x] Eight unit tests and retained syntax command/exit cover annotated tags, merge-base parsing, all HTTP 5xx, conditional 403 rate limits, numeric/date Retry-After and cap, nonretryable errors, retried body closure, bounded backoff, and failure-to-unknown; R5 bounded review findings addressed |
| WordCraft v0.11.0 adapter | Durable identity-bound save, ACK and editor-clean behavior on refreshed base | [~] Exact-base patch; locked WASM; engine 2/2, UI 9/9; release bundle and actual-WASM memory-host edit/save/new-version/ACK/fresh-reopen pass; copied reopened editor text contains the marker. Seafile and replacement-refusal counts remain NOT VERIFIED |
| GridCraft v0.12.1 adapter | Durable identity-bound save, ACK and editor-clean behavior on refreshed base | [~] Exact-base patch includes XLSX name/content guard; locked WASM; host engine 3/3 and UI 2/2; optimized release bundle and actual-WASM synthetic memory-host active-cell Ctrl+S/version/ACK/fresh-reopen pass, with source and served-asset hashes retained. Release-evidence R2 is bounded PROVISIONAL PASS. Seafile workflow and refusal-before-serialization counts remain NOT VERIFIED |
| PdfCraft v0.14.0 adapter | Durable save/ACK and fresh-reopen behavior on refreshed base | [~] Exact-base patch; local transport; locked WASM, 30 `editing::` tests (including the 8 ACK tests), optimized release bundle, and actual-WASM synthetic memory-host edit/save/ACK/fresh-iframe reopen pass. R4 OCR asserts the reopened marker and hashes actual served assets. Release-evidence R2 is bounded PROVISIONAL PASS. Seafile and replacement-refusal counts remain NOT VERIFIED; legacy ticket protocol, not identity binding |
| VectorCraft v0.17.0 adapter | Existing page API persistence on refreshed base | [~] No adapter source port identified; locked WASM check passes. Release asset build, browser, and Seafile qualification remain NOT VERIFIED |
| PhotoCraft v0.16.0 adapter | Bounded host save/ACK lifecycle on refreshed base | [~] Exact-base patch and locked WASM pass; one standalone confirmation test passes on final local-path tree. Engine snapshot and Web/UI suites were cancelled and remain NOT VERIFIED |
| Independent review and promotion | Review each final candidate; promote only after project review gates | [~] App-port R3, pre-push R4, GridCraft/PdfCraft release R2 and final snapshot R2 are bounded PROVISIONAL PASS after findings were addressed. R9/R4 bind browser claims to test source and actual served files. Seafile acceptance remains NOT VERIFIED. No route promotion/merge or upstream issue/PR/RFC |

GR-082 evidence: [report](GR-082-UPSTREAM-REFRESH-WAVE-1.md),
[evidence bundle](reviews/GR-082/README.md),
[PdfCraft release manifest](reviews/GR-082/checks/pdfcraft-bundle-manifest.json).
The weekly task is configured but
unattended execution is NOT VERIFIED; it does not auto-promote or deploy.

## GR-081 — project GPT review remediation

| Scenario | Expected | Result |
|---|---|---|
| WordCraft/GridCraft native document binding | Refuse replacement/Save As before serialization; ordinary Save persists and confirms only the bound native document | [~] Both locked WASM checks pass; existing UI suites pass (WordCraft 824 passed/2 ignored; GridCraft 151 passed). These do not test identity refusal or browser Save/ACK. Runtime refusal, Seafile version/reopen, and public-remote resolution of transport commit `d572f2d550278a7f4aad91a1bac650105c19812b` remain NOT VERIFIED |
| Static directory index confinement | Reject an index symlink whose resolved target escapes the static root | [~] Final index path is now resolved and confined; runtime symlink exercise NOT RUN |
| Dispatcher route mapping | Verifier accepts exactly the five tracked extension routes | [~] Expected map updated for `.docx`, `.xlsx`, `.pdf`, `.svg`, `.pcraft`; verifier NOT RUN |
| Evidence and documentation accuracy | Correct deployment topology, screenshot attribution, stale evidence statements and broken links | [x] R3–R6 findings corrected; R7 PROVISIONAL PASS with no new documentation findings; identity implementation is covered separately by code/security R2 |
| Current-route ONLYOFFICE preservation | Complete current-route edit/save/version/fresh-reopen outside the ArtCraft allowlist | [ ] NOT VERIFIED; configured API script returned 404 in GR-080, no editor appeared; no settings/service changes |
| Independent review | Separate review of GR-081 implementation and evidence | [~] Code/security R1 PROVISIONAL FAIL; R2 found no new MAJOR and two MINOR artifact findings now corrected; docs/evidence R3 PROVISIONAL FAIL, R4–R7 PROVISIONAL PASS; save-identity and ONLYOFFICE MAJOR gates remain open |

Evidence: [GR-081 report](GR-081-PROJECT-GPT-REVIEW-REMEDIATION.md),
[project GPT review record](reviews/GR-081/PROJECT-GPT-REVIEW-70FA192.md),
[validation R3](reviews/GR-081/VALIDATION-R3.md).
Candidate 70fa192 received project GPT **FAIL**. GR-081 does not claim
project approval; upstream publication remains locked.

## GR-080 — security evidence and ONLYOFFICE status reconciliation

| Scenario | Expected | Result |
|---|---|---|
| GR-015 evidence reflected in security status | Separate historical GPT FAIL, later isolated synthetic runtime evidence, and production limits | [x] `docs/SECURITY.md` reconciled to `docs/reviews/GR-015/ISOLATED-RUNTIME-E2E-20261023.md` |
| Current post-change ONLYOFFICE route | Configured API script loads and editor is instantiated | [!] Synthetic DOCX route returned 404 for API script; no editor instance/frame; no setting or service changed |
| Retained evidence privacy | No credentials, identity, host address, session ID or document bytes | [x] Sanitized status-only observation; no screenshot retained |
| ONLYOFFICE edit/save/version/reopen after current route failure | Full edit/save/reopen through current route | [ ] NOT VERIFIED; editor did not initialize |
| Independent review | Separate documentation/evidence review | [x] R1 PROVISIONAL PASS, no findings |

Evidence: [GR-080 report](GR-080-SECURITY-EVIDENCE-RECONCILIATION.md),
[runtime observation](reviews/GR-080/runtime/onlyoffice-route-check.json).
Project GPT review remains pending; upstream publication remains locked.

## GR-079 — read-only Seafile history verification

| Scenario | Expected | Result |
|---|---|---|
| Current history row for each GR-078 file | Seafile History lists a current version after the browser save | [x] DOCX 5 versions; XLSX 3; PDF 4; SVG 3; Pcraft 4 |
| Current version dates and sizes | Record the displayed current-row timestamp and size | [x] Values recorded in sanitized `history-observations.json`; no separate file-list comparison retained |
| Personal data in retained evidence | Exclude modifier names and credentials | [x] Names omitted; no screenshots or file content retained |
| Editor bytes versus Seafile readback | Compare saved payload and current version bytes for all five routes | [ ] NOT VERIFIED |
| Independent review | Separate read-only evidence review | [x] R1 MINOR findings remediated; R2 PROVISIONAL PASS, no new findings |

Evidence: [GR-079 report](GR-079-SEAFILE-HISTORY-VERIFICATION.md),
[evidence bundle](reviews/GR-079/). Read-only synthetic check only; no
production or project GPT PASS is implied.

## GR-078 — combined five-route synthetic Seafile browser replay

| Scenario | Expected | Result |
|---|---|---|
| WordCraft `.docx` route | Open, edit, host-save a new version, close and reopen with edit retained | [~] `synthetic.docx`; marker and saved state retained; new-version confirmation was operator-observed but not captured |
| GridCraft `.xlsx` route | Edit a cell, save a new version, close and reopen with value/formula result retained | [x] B2 and B3 both 1338 after reopen |
| PdfCraft `.pdf` route | Edit an interactive field, save a new version, close and reopen with value retained | [x] `form.pdf`; `GR078savededit` retained |
| VectorCraft `.svg` route | Add a shape, save through SVG export, close and reopen with shape retained | [x] New 20 × 20 px rectangle remained visible |
| PhotoCraft `.pcraft` route | Add a layer, receive host-save success, close and reopen with layer retained | [~] Operator-recorded save/reopen; retained PNGs are reused GR-076 captures showing Layer 1/2, not the GR-078 edit |
| Combined active lab replay | Exercise all five tracked routes from one synthetic Seafile library/browser profile | [~] Sequential replay; PhotoCraft save/reopen is operator-recorded and retained PNGs are reused GR-076 captures; no manual download/upload |
| History rows for all five routes | Seafile History lists a current version for each replayed file | [x] Verified in GR-079; five current rows recorded |
| Saved-byte identity | Compare editor payload to Seafile readback bytes for all routes | [ ] NOT VERIFIED |
| Production security, conflict and ONLYOFFICE post-change UI | Verify production permissions/proxy/CSP/concurrency; confirm ONLYOFFICE UI after changes | [ ] NOT VERIFIED; ONLYOFFICE not used or changed in GR-078 |
| Independent review | Separate final-state evidence review | [x] R1 MAJOR/MINOR findings remediated; R2 PROVISIONAL PASS, no new findings |

Evidence: [GR-078 report](GR-078-COMBINED-SEAFILE-ROUTE-REPLAY.md),
[runtime bundle](reviews/GR-078/). The result is bounded to the active
synthetic lab deployment; no project GPT PASS is implied.

## GR-077 — integration coverage reconciliation

| Scenario | Expected | Result |
|---|---|---|
| Tracked dispatcher summary | App/extension mapping matches `integration/config/dispatch.json` | [x] Five routes: DOCX, XLSX, PDF, SVG and `.pcraft`; PhotoCraft addition is GR-076 |
| Per-app synthetic evidence summary | Summary points to retained app reports and does not imply one combined run | [x] WordCraft, GridCraft, PdfCraft, VectorCraft and PhotoCraft evidence is linked in `docs/ARTCRAFT-GLOBAL-INTEGRATION.md` |
| Active local static assets in this checkout | To pass, all five tracked routes must have matching assets in repository `integration/static/` | [ ] NOT VERIFIED; this checkout contains the GR-076 PhotoCraft bundle only; GR-078 separately verified all five in the active lab deployment |
| Combined five-route Seafile replay at GR-077 cutoff | All tracked routes work together in one synthetic library/session | [ ] NOT VERIFIED at GR-077; later completed in GR-078, with WordCraft new-version confirmation evidence-limited |
| Production security and conflict behavior | Production-readiness gate: verify save authorization, proxy, CSP, concurrency and permissions | [ ] NOT VERIFIED |
| Independent review | Separate review of this documentation reconciliation | [x] R1/R2 PROVISIONAL PASS; ten R1 MINOR findings remediated; R2 found none new |

Evidence: [GR-077 report](GR-077-INTEGRATION-COVERAGE-RECONCILIATION.md),
[evidence bundle](reviews/GR-077/). This is a documentation reconciliation,
not a new runtime test or project GPT PASS.

## GR-074 — gateway request-body framing

| Scenario | Expected | Result |
|---|---|---|
| Oversized `/open/` body | Reject before Seafile lookup and close the connection | [x] Loopback HTTP test: 413, close, no Seafile lookup |
| Oversized `/dirty` report | Preserve prior unsaved state and close the connection | [x] Loopback HTTP test: 413, prior dirty flag remains true |
| Invalid/duplicate lengths, unsupported transfer encoding, truncated bodies | Reject with connection closure; preserve `/dirty` state | [x] Raw loopback matrix asserts 400/EOF and dirty preservation; the oversized `/open/` test separately asserts no Seafile lookup |
| Oversized `/save` request | Return 413 and close before persistence | [x] Loopback HTTP test; active fake records no write |
| HTTP/0.9 legacy GET | Reject before assuming header-object shape | [x] Raw HTTP/0.9 GET is closed without dispatch |
| Parser-leftover malformed headers | Reject raw CR/LF residue before body framing | [x] Two pipelined raw cases return one 400, close, and preserve dirty state |
| Proxy / production behavior | Confirm front-proxy framing and deployment behavior | [ ] NOT VERIFIED |

Evidence: [GR-074 report](GR-074-HTTP-BODY-FRAMING.md),
[review bundle](reviews/GR-074/). R1–R5 bounded reviews are PROVISIONAL PASS;
no project GPT approval is implied.

## GR-075 — gateway request-body deadline

| Scenario | Expected | Result |
|---|---|---|
| Slow-drip incomplete body | Enforce a total body-read deadline despite periodic bytes | [x] Loopback `/dirty` drip test receives one 408, closes, and preserves dirty state |
| Large upload throughput / proxy buffering | A 50 MiB upload can meet the configured deadline through deployment proxies | [ ] NOT VERIFIED |
| Header-read deadline | Slow request headers cannot retain a handler indefinitely | [ ] NOT VERIFIED |

Evidence: [GR-075 report](GR-075-HTTP-BODY-DEADLINE.md),
[review bundle](reviews/GR-075/). R1/R2 test findings are fixed; R3/R4 returned
R3–R5 bounded PROVISIONAL PASS after correcting their matrix/status
documentation findings; no project GPT approval is implied.

## GR-073 — gateway `/open/` rate limit

| Scenario | Expected | Result |
|---|---|---|
| Per-peer request threshold | Excess `/open/` requests are rejected before Seafile access | [x] 60 requests / 60-second fixed window; 429 and `Retry-After` tested |
| Forwarded-header spoofing | Client-supplied XFF cannot select another bucket | [x] HTTP test changes XFF; same TCP peer remains rate limited |
| Bounded state and expiry | Peer map stays capped and resets expired windows | [x] Injected-clock checks pass; max 1,024 peers in production configuration |
| Reverse-proxy identity / multi-process behavior | Actual clients receive independent distributed limits | [ ] NOT VERIFIED; proxy peers may share one process-local bucket |
| Independent review / public deployment | Rate-limit suitability and deployment controls reviewed | [~] Bounded R1–R3 PROVISIONAL PASS; R1 code findings resolved and R2 security-table wording corrected. Public readiness remains unverified |

Evidence: [GR-073 report](GR-073-OPEN-RATE-LIMIT.md),
[review bundle](reviews/GR-073/). Project GPT remains INCOMPLETE; upstream
publication remains LOCKED.

## GR-072 — post-change ONLYOFFICE regression on real synthetic Seafile

| Scenario | Expected | Result |
|---|---|---|
| Existing route | Synthetic DOCX outside ArtCraft allowlist opens in ONLYOFFICE | [x] Operator-recorded browser open; representative assets returned HTTP 200 in its network view |
| Edit and save | Visible edit persists; editor confirms completion | [x] Operator-recorded GR-071→GR-072 marker edit and Ctrl+S; screenshot shows final marker with `All changes saved` |
| Seafile version history | Save appears as current version | [x] Operator-recorded history showed 25.3 KB then 25.4 KB after the disclosed marker correction; earlier 5.3 KB version remained |
| Later editor load | Saved edit remains visible | [x] Operator-recorded navigation and later file-route load; screenshot shows final GR-072 marker |
| Explicit in-app close | Close action observed before reopen | [ ] NOT VERIFIED; the editor was exited by navigation |
| Exact editor payload/readback identity | Matching bytes or hashes | [ ] NOT VERIFIED |
| Broader ONLYOFFICE compatibility/security | Other files, versions, users and deployment topology | [ ] NOT VERIFIED |
| Independent review | Separate review of retained evidence | [x] R1–R3 PROVISIONAL ACCEPT; R1/R2 documentation minors corrected; no remaining findings |

Evidence: [GR-072 report](GR-072-ONLYOFFICE-REAL-SEAFILE-REGRESSION.md),
[evidence bundle](reviews/GR-072/). This is a bounded one-file regression, not a
project GPT PASS or upstream authorization.

## GR-071 — shared test-root candidate provenance recheck

| Scenario | Expected | Result |
|---|---|---|
| Tracked dispatch mapping at GR-071 | DOCX/XLSX/PDF/SVG map to WordCraft/GridCraft/PdfCraft/VectorCraft | [x] GR-071 checked the four existing routes; GR-076 later added the `pcraft` → PhotoCraft route |
| Candidate assets in one local test root | All four candidates match their per-app manifests | [x] 20 files, 207,970,569 bytes; GR-055–058 verifiers pass against the GR-059 test static root |
| One combined five-route Seafile replay at GR-071 cutoff | All tracked routes work in one run | [ ] NOT VERIFIED at GR-071; later combined synthetic replay recorded in GR-078 |
| Repository `integration/static` promotion | All five tracked routes have matching assets in this checkout | [ ] NOT VERIFIED; GR-076 staged PhotoCraft here, but the other four bundles remain absent; GR-078 active lab replay used deployed assets |
| ONLYOFFICE post-change edit/save | Existing integration still saves after route changes | [x] GR-072 operator-recorded: synthetic DOCX edit, `All changes saved`, new Seafile history versions and later editor load with the final edit; explicit in-app close and byte identity remain unverified |
| Production security and byte identity | Deployment security and save/readback identity established | [ ] NOT VERIFIED |
| Independent review | Exact bounded evidence review | [x] R1–R3 PROVISIONAL PASS, no remaining findings; this is not project GPT PASS |

Evidence: [GR-071 report](GR-071-DISPATCHED-CANDIDATE-PROVENANCE.md),
[checks and review](reviews/GR-071/README.md). The check is local/read-only;
it neither contacts Seafile nor changes dispatch.

## GR-069 — FigCraft on real synthetic Seafile

| Scenario | Expected | Result |
|---|---|---|
| Candidate inventory and active static-root assets | Exact pinned FigCraft candidate served | [x] 3 assets, 23,650,333 bytes; build, staged and active hashes match |
| Synthetic Seafile file-list open | Actual FigCraft WASM loads native document | [x] File route, `/open/`, index, JS, WASM and document GET succeeded |
| Visible edit and Ctrl+S | Host ACK and Seafile version confirmed | [x] Visible 100×100 rectangle; successful retry returned HTTP 200, new-version identifier, and clean editor state |
| Failed first save | Not counted as persistence | [x] Gateway returned 502; no positive ACK; discarded edit excluded |
| Fresh-session reopen | New Seafile-backed editor renders saved edit | [x] Navigated to library and opened file again; rectangle visible |
| Edited-output download/manual upload | Not used | [x] Fixture upload was setup only; edited output was neither downloaded nor uploaded manually |
| Exact save-message/readback byte identity | Matching hashes | [ ] NOT VERIFIED |
| Seafile history-page evidence | Retained history observation/capture | [ ] NOT VERIFIED; version identifier came from successful save response; no history capture retained |
| ONLYOFFICE edit/save/version | Post-change regression | [ ] NOT VERIFIED; setting remained enabled; no edit/save regression run |
| Explicit in-app close before reopen | Document explicitly closed | [ ] NOT VERIFIED; successful editor exited by navigation |
| Broader compatibility and production security | General readiness | [ ] NOT VERIFIED |
| Independent review | Separate exact evidence review | [x] R1 bounded PROVISIONAL PASS, no findings; project GPT remains INCOMPLETE and upstream publication LOCKED |

Evidence: `docs/reviews/GR-069/`; reused GR-048 actual-WASM candidate; exact wasm-opt execution NOT VERIFIED because the GR-048 build stdout is absent
without rebuilding. Temporary `.figcraft` allowlist and dispatch changes were
restored after the run.

## GR-068 — PdfCraft on real synthetic Seafile

| Scenario | Expected | Result |
|---|---|---|
| Candidate inventory and active static-root assets | Exact pinned PdfCraft candidate served | [x] Three files, 50,075,901 bytes; staged and active hashes match |
| Synthetic Seafile file-list open | Actual PdfCraft WASM loads existing PDF | [x] `/open/`, index, JS, WASM and document GET returned 200 |
| Visible edit and Ctrl+S | Host ACK and Seafile version confirmed | [x] AcroForm field changed; `Saved — new version …`; gateway save POST 200 |
| Seafile history | Editor save persists a new version | [x] Versions UI lists current 3.0 KB plus two older versions; account-bearing screenshot omitted; canceled initial attempt makes its separate revision uncertain |
| Fresh-session reopen | New editor session renders saved value | [x] Navigated away and opened the existing PDF again from Seafile list; value intact |
| Edited-output download/manual upload | Not used | [x] None occurred; existing synthetic PDF used |
| Exact save-message/readback byte identity | Matching hashes | [ ] NOT VERIFIED |
| ONLYOFFICE edit/save/version | Full regression | [ ] NOT VERIFIED; no ONLYOFFICE setting/route changed, edit/save not rerun |
| In-app close before reopen | Document explicitly closed | [ ] NOT VERIFIED; old editor view exited by navigation |
| Broader format compatibility and production security | General readiness | [ ] NOT VERIFIED |
| Independent review | Separate exact evidence review | [x] R1 bounded PROVISIONAL PASS, no findings; project GPT remains INCOMPLETE and upstream publication LOCKED |

Evidence: `docs/reviews/GR-068/`; reused GR-057 actual-WASM candidate without
rebuilding. Existing PDF dispatch and allowlist were unchanged.

## GR-067 — EffectCraft on real synthetic Seafile

| Scenario | Expected | Result |
|---|---|---|
| Candidate inventory and active static-root assets | Exact pinned EffectCraft candidate served | [x] 11 files, 57,470,921 bytes; build, staged, and active-root hashes match |
| Synthetic Seafile file-list open | Actual EffectCraft WASM loads native project | [x] `/open/`, index, JS, runtime snippet, WASM and document GET returned 200 after restoring one omitted snippet |
| Visible edit and Ctrl+S | Host ACK and Seafile version confirmed | [x] Canvas text edit; operator-recorded `Saved to host`; retained screenshot shows Seafile new-version confirmation; gateway save POST 200 |
| Seafile history | Editor save creates a version after setup upload | [~] Operator observed current and preceding Versions entries; no history capture retained. The save screenshot separately shows Seafile's new-version confirmation |
| Fresh-session reopen | New editor session renders saved edit | [x] Navigated away to file list and opened again in a new tab/session; saved text displayed |
| Edited-output download/manual upload | Not used | [x] None occurred; fixture upload was setup only |
| Exact save-message/readback byte identity | Matching hashes | [ ] NOT VERIFIED |
| ONLYOFFICE edit/save/version after route change | Full regression | [ ] NOT VERIFIED; no ONLYOFFICE setting/route changed, but edit/save was not rerun |
| In-app close before reopen | Document explicitly closed | [ ] NOT VERIFIED; old editor view exited by navigation |
| Broader format compatibility and production security | General readiness | [ ] NOT VERIFIED |
| Independent review | Separate exact evidence review | [~] R1–R4 bounded PROVISIONAL PASS; two evidence minors, one tracking minor, and two P3 documentation findings corrected; runtime limits remain |

Evidence: `docs/reviews/GR-067/`; reused GR-046 actual-WASM candidate without
rebuilding. The missing snippet found on the first attempt was copied from the
build and its digest checked before the successful retry.

## GR-066 — FilmCraft on real synthetic Seafile

| Scenario | Expected | Result |
|---|---|---|
| Candidate inventory and active static-root assets | Exact pinned FilmCraft candidate served | [x] Five files, sizes, SHA-256 and HTML/runtime references match staged and active roots |
| Synthetic Seafile file-list open | Actual FilmCraft WASM loads the native project | [x] Existing synthetic library; editor assets and document GET returned 200 |
| Visible edit and Ctrl+S | Host ACK and Seafile version are confirmed | [x] Text edit; `Saved to host`; new-version confirmation; save POST returned 200 |
| Seafile history | Fixture setup is distinct from editor save | [x] UI showed `Added` followed by `Modified`; history screenshot omitted because account name was visible |
| Fresh-session reopen | New editor session renders saved text | [x] Navigated away and reopened from Seafile list; text intact |
| Edited-output download/manual upload | Not used | [x] None occurred; fixture upload was setup only |
| Exact save-message/readback byte identity | Matching hashes | [ ] NOT VERIFIED |
| ONLYOFFICE edit/save/version after route change | Full regression | [ ] NOT VERIFIED; no ONLYOFFICE setting/route was changed in this GR |
| Browser popup lifecycle without test shim | Standard popup path | [ ] NOT VERIFIED; test-only popup-to-same-tab shim used |
| In-app close before reopen | Document explicitly closed | [ ] NOT VERIFIED; first editor exited by page navigation |
| Thumbnail route | Successful thumbnail generation | [!] HTTP 500 observed; cause not investigated |
| Broader format compatibility and production security | General readiness | [ ] NOT VERIFIED |
| Independent review | Separate exact evidence review | [x] R1–R2 bounded PROVISIONAL PASS; caption MINOR closed; runtime not independently replayed |

Evidence: `docs/reviews/GR-066/`; reused GR-047 actual-WASM candidate without rebuild. Project GPT remains INCOMPLETE; upstream publication LOCKED.

## GR-065 — DesignCraft on real synthetic Seafile

| Scenario | Expected | Result |
|---|---|---|
| Candidate inventory and active static-root assets | Exact pinned DesignCraft candidate served | [x] Three assets, sizes, SHA-256 and each index-to-file SRI association verified against staged and active roots |
| Synthetic Seafile file-list open | Actual DesignCraft WASM loads the native document | [x] Private Seafile instance, existing synthetic library; JS/WASM and document GET returned 200 |
| Visible edit and Ctrl+S | Host ACK and Seafile version are confirmed | [x] Text edit; host showed `Saved — new version …`; gateway save POST returned 200 |
| Seafile history | Setup fixture is distinct from editor saves | [x] UI showed `Added` then two `Modified` entries for `synthetic.designcraft`; no history screenshot retained because the account name was visible |
| Fresh-session reopen | New editor session renders saved text | [x] Navigated away, returned to the Seafile list, and reopened; new open/document requests returned 200 and text was intact |
| Edited-output download/manual upload | Not used | [x] None occurred; the one fixture upload was setup only |
| Exact save-message/readback byte identity | Matching hashes | [ ] NOT VERIFIED; save payload and Seafile readback were not separately hashed |
| ONLYOFFICE edit/save/version after route change | Full regression | [ ] NOT VERIFIED; no ONLYOFFICE setting was changed in this GR |
| Browser popup lifecycle without test shim | Standard popup path | [ ] NOT VERIFIED; T3 preview redirected this file's popup to the same tab |
| Broader format compatibility and production security | General readiness | [ ] NOT VERIFIED |
| Independent review | Separate exact evidence review | [x] R1 bounded PROVISIONAL PASS, no findings requiring remediation; runtime assertions not independently replayed |

Evidence: `docs/reviews/GR-065/`; candidate reuses the GR-045 optimized WASM and was not rebuilt. Project GPT remains INCOMPLETE; upstream publication LOCKED.

## GR-064 — DeckCraft on real synthetic Seafile

| Scenario | Expected | Result |
|---|---|---|
| Candidate inventory and active static-root assets | Exact pinned DeckCraft candidate served | [x] Four files, paths, sizes, SHA-256, index references, and each per-file SRI association match |
| Synthetic Seafile file-list open | Actual DeckCraft WASM loads the PPTX | [x] T3 Chromium preview; one synthetic library |
| Visible edit and Ctrl+S | Matching positive ACK clears dirty state and Seafile creates a version | [x] `Saved — new version …`; gateway `/open`, document GET, and save POST returned 200 |
| Seafile history | Fixture setup is distinct from editor save | [x] `Added` followed by `Modified` for `synthetic.pptx` |
| Fresh Seafile file-list reopen | New editor session renders the edit | [x] Text intact; editor reports no changes |
| ONLYOFFICE outside ArtCraft allowlist | Existing route still opens | [x] Synthetic DOCX opens read-only; no edit/save attempted |
| ONLYOFFICE edit/save/version after route change | Full regression | [ ] NOT VERIFIED |
| Browser popup lifecycle without test shim | Standard popup path | [ ] NOT VERIFIED; T3 preview redirected test-file popup to same tab |
| Broader PPTX compatibility, production topology/security, byte-level readback | General readiness | [ ] NOT VERIFIED |
| Independent review | Separate evidence/source review | [~] R1–R4 bounded PROVISIONAL PASS; all wording/verifier findings corrected |

Evidence: `docs/reviews/GR-064/`. Reused GR-044 optimized candidate; no rebuild in GR-064. GPT REVIEW PENDING; project verdict INCOMPLETE and upstream publication LOCKED.

## GR-062 — PdfCraft on real synthetic Seafile

The exact GR-057 bundle is now dispatched for PDF in the single synthetic
library already used by GR-059/061. The AcroForm fixture upload is setup only;
the edited field was persisted through the editor save route. Project GPT
remains INCOMPLETE and upstream publication LOCKED.

| Check | Result | Scope |
|---|---|---|
| Deployed PdfCraft candidate | [x] GR-057 verifier passes against live static root | Three served files, sizes, hashes and index references; provenance is recorded separately |
| Seafile file-list open → form edit → save → version → fresh reopen | [x] Edited AcroForm value survives a fresh editor session | One synthetic PDF; history UI showed `Modified`; screenshots retained |
| Existing DOCX/XLSX routes and ONLYOFFICE flag | [x] Both routes preserved; `ENABLE_ONLYOFFICE=True` after Seahub restart | Post-change ONLYOFFICE edit/save regression not run |
| Byte provenance, permission/concurrency failures and deployment security | [ ] NOT VERIFIED | No editor-message/readback hash or negative-path/production security test |
| Independent exact-evidence review | [x] R1–R2 bounded PROVISIONAL PASS, no blocker/major; R1 wording MINOR corrected and closed | Work-item remains GPT REVIEW PENDING; project GPT still required |

Evidence: `docs/GR-062-PDFCRAFT-REAL-SEAFILE-ROUNDTRIP.md` and
`docs/reviews/GR-062/`.

## GR-061 — GridCraft on real synthetic Seafile

The exact GR-056 bundle is now dispatched for XLSX in the single synthetic
library already used by GR-059. The fixture upload is setup only; the edited
workbook was persisted through the editor save route. Project GPT remains
INCOMPLETE and upstream publication LOCKED.

| Check | Result | Scope |
|---|---|---|
| Deployed GridCraft candidate | [x] GR-056 verifier passes against live static root | Four assets, exact recorded hashes/provenance |
| Seafile file-list open → edit → save → version → fresh reopen | [x] B2 42→1337; B3 formula recalculated and reopened as 1337 | One synthetic XLSX; history UI showed a `Modified` event; screenshots retained |
| WordCraft route and ONLYOFFICE flag | [x] DOCX dispatch remains; `ENABLE_ONLYOFFICE=True` after Seahub restart | New ONLYOFFICE edit/save regression not run; previous GR-059 check was open-only |
| Permission/concurrency/response-loss and deployment security | [ ] NOT VERIFIED | No negative-path or production topology test in this slice |
| Independent exact-evidence review | [x] R1–R3 bounded PROVISIONAL PASS; two documentation minors corrected | Exact historical comparison with earlier review snapshots not verified; project-level GPT review still required |

Evidence: `docs/GR-061-GRIDCRAFT-REAL-SEAFILE-ROUNDTRIP.md` and
`docs/reviews/GR-061/`.

## GR-060 — dedicated tailnet gateway LXC (paused)

A non-privileged Debian 13 LXC was provisioned and staged with the existing
gateway and exact GR-055 candidate. Local checks passed before shutdown. Tailscale
enrollment and Serve are not configured; the owner-requested pause leaves the
LXC stopped and the GR-059 route active. Independent R1–R2 reviews are bounded
PROVISIONAL PASS after a status-wording correction. This is not a route migration or project
GPT PASS.

| Check | Result | Scope |
|---|---|---|
| LXC service and static health | [x] Loopback health/static returned 200 before pause | LXC is now stopped; no current health claim |
| Exact WordCraft candidate staging | [x] GR-055 candidate verifier passed in the LXC staging path before pause | Candidate remains outside dispatch |
| Tailscale enrollment and HTTPS Serve | [ ] NOT VERIFIED | Node awaits owner-authenticated login; no Serve hostname |
| Seahub route migration and fresh Seafile roundtrip | [ ] NOT RUN | GR-059 route remains active; no settings changed for GR-060 |

## GR-059 — deployed WordCraft route on real synthetic Seafile

The exact GR-055 staged candidate ran through the owner-managed Seafile
instance, restricted to one synthetic library and DOCX. Seafile created a
new version and a fresh file-list reopen displayed the edit. ONLYOFFICE opened
a synthetic document outside the allowlist after deployment, without edits.
This is bounded runtime evidence, not production readiness or a project GPT
PASS. See [GR-059](GR-059-REAL-SEAFILE-WORDCRAFT-DEPLOYMENT.md).

| Check | Result | Scope |
|---|---|---|
| Exact staged WordCraft bundle | [x] GR-055 four-file candidate verifier passed against the deployed staging root | Candidate remains outside tracked static assets and dispatch |
| Seafile file-list open → edit → save → new version → fresh reopen | [x] Save confirmed; history advanced; reopened text intact | One explicitly synthetic DOCX and library; detailed boundary and limits in GR-059 |
| ONLYOFFICE post-deploy open | [x] Synthetic non-allowlisted DOCX opened; representative ONLYOFFICE 9.4 assets returned 200 | Open-only check; edit/save/version regression after this deployment is **NOT VERIFIED** |
| Security/deployment failure cases | [ ] Permission revocation, external writer, token expiry/replay, response loss and cross-origin deployment not exercised here | Keep as project gates |

## GR-058 — exact VectorCraft source candidate

Source build from pinned `v0.14.0` and `craft-fonts` passed the current page-API
host smoke in Chromium with loopback synthetic storage. Independent R1 review:
PROVISIONAL PASS, no findings. The output differs from the official release
bundle; Seafile persistence and optional missing-font rendering remain
**NOT VERIFIED**. Candidate remains outside dispatch.

| Check | Result | Scope |
|---|---|---|
| Source/font pins and release comparison | [x] Tag/commit and checksum-verified release archive match recorded inputs | Source build output is distinct from release bundle |
| Candidate inventory | [x] Nine files, index links and integrity hashes verified | [`verify_candidate.py`](reviews/GR-058/verify_candidate.py); outside dispatch |
| Actual candidate browser save/reopen | [x] Visible SVG edit, exact editor bytes stored by synthetic loopback parent, fresh session parses path | Not a Seafile test or common `?host=parent` protocol |
| Independent review | [x] R1 bounded PROVISIONAL PASS, no findings | Project GPT remains INCOMPLETE |
| Seafile storage/version/reopen | [ ] NOT RUN | No Seafile write; see GR-058 report |

## GR-057 — exact PdfCraft candidate

Actual built WASM passed synthetic AcroForm edit/save/ACK/fresh iframe reopen.
Independent R1–R2 bounded reviews are PROVISIONAL PASS; the corrected report
records that `wasm-opt` was disabled. Seafile persistence remains NOT RUN.

| Check | Result | Scope |
|---|---|---|
| Exact source/patch/transport and build | [x] Pinned inputs, Rust 1.95/Trunk 0.22 release build recorded | `data-wasm-opt=0`; optimized output not compared |
| Candidate inventory | [x] Three served files and index references verified | [`verify_candidate.py`](reviews/GR-057/verify_candidate.py); outside dispatch |
| Actual browser edit/save/reopen | [x] Visible form edit, 2,403-byte save, matching memory ACK, clean state and fresh iframe reopen | Synthetic parent only |
| Independent review | [x] R1–R2 bounded PROVISIONAL PASS; R1 wording MINOR corrected | Project GPT remains INCOMPLETE |
| Seafile storage/version/reopen | [ ] NOT RUN | No Seafile endpoint accessed in GR-057 |

## GR-056 — exact GridCraft candidate

The actual release WASM passed a synthetic memory-parent edit/save-ACK/reopen
flow, including B2/B3 formula recalculation. Independent R1–R5 bounded reviews
are PROVISIONAL PASS with no remaining findings. Seafile persistence remains
NOT RUN after a read-only 404 preflight; no write was attempted.

| Check | Result | Scope |
|---|---|---|
| Exact source/patch/transport and build | [x] Pinned GridCraft source, GR-016 patch and transport `90c261de`; Rust 1.95 build | Build-local `data-wasm-opt=0`; optimized output not verified |
| Candidate inventory | [x] Four served files, hashes, index links and provenance verifier pass | [`verify_candidate.py`](reviews/GR-056/verify_candidate.py); outside dispatch |
| Actual browser edit/save/reopen | [x] B2→1337, formula B3→1337, matching ACK and fresh iframe reopen | Synthetic memory parent only |
| Independent review | [x] R1–R5 bounded PROVISIONAL PASS, no remaining findings | Project GPT remains INCOMPLETE |
| Seafile storage/version/reopen | [ ] NOT RUN | Read-only GET preflight 404; no write attempted |

## GR-055 — exact WordCraft candidate

GR-059 deployed that exact staged candidate for one explicitly synthetic
DOCX. The live Seafile run passed edit → save acknowledgement → history
version → fresh file-list reopen with the edit visible. ONLYOFFICE was opened
after deployment from a synthetic, non-allowlisted folder; its post-deploy
save/version regression remains unverified. See [GR-059](GR-059-REAL-SEAFILE-WORDCRAFT-DEPLOYMENT.md).

GR-055 builds the exact WordCraft source/patch/transport combination with Rust
1.95 and stages it outside dispatch. The actual WASM passes the synthetic
in-memory browser edit/save-ack/reopen test. This does not replay Seafile or
establish durable Seafile versions. Independent R1–R2 reviews are bounded
PROVISIONAL PASS, no remaining findings. GR-055 is GPT REVIEW PENDING; project
GPT remains **INCOMPLETE**.

| Check | Result | Scope |
|---|---|---|
| Pinned source, patch and transport | [x] Source `00bc6a4b`, GR-054 patch SHA matches, normal `git apply --check` passes, Cargo manifest/lock both pin `90c261de` | Exact inputs documented in [GR-055](GR-055-WORDCRAFT-REPRODUCIBLE-CANDIDATE.md) |
| Rust 1.95 release Web/WASM build | [x] Trunk `--release --locked` succeeds with build-local `data-wasm-opt=0` overlay | Functional release bundle; optimized wasm-opt output not verified |
| Candidate asset manifest | [x] Four staged served files match recorded paths, sizes and SHA-256 | [`verify_candidate.py`](reviews/GR-055/verify_candidate.py); candidate stays outside dispatch |
| Actual WordCraft synthetic browser roundtrip | [x] Edit/serialize, synthetic version acknowledgement, save confirmation and fresh reopen pass | In-memory host only; no Seafile persistence |
| Exact-candidate Seafile history/readback/reopen | [x] GR-059 real synthetic library; a new history entry and fresh editor reopen with the edit intact | One file/library only; permission revocation, external writers, response loss, and ONLYOFFICE save regression remain unverified |

## GR-054 — dated inventory and later candidate follow-up

Current source snapshot: `1c7914bf1e166ac4731a1c9b11dce649210eed70`;
95d8983 is a historical reviewed candidate. Existing runtime rows below describe
recorded historical runs, not a replay of this snapshot plus current local assets.
Project GPT remains INCOMPLETE; GR-054 independent R1–R2 bounded reviews are
PROVISIONAL PASS. The 2026-10-25 parent `integration/static` snapshot still
lacks matched source provenance. Later GR-055–058 candidates were checked
together in the separate GR-059 test static root by GR-071; this does not verify
the repository `integration/static` promotion, running service root, or one
combined four-route Seafile replay.

| Check | Result | Scope |
| --- | --- | --- |
| Dispatch/source inventory | [x] 55 pinned source/patch files match base and current files | Stdlib verifier; no services or builds |
| Parent-local inventory | [x] 82 file hashes/sizes, ignored/untracked state and seven index maps match | Optional read-only verifier; clean worktree has no static tree |
| Captured parent `integration/static` asset provenance | [ ] NOT VERIFIED for all four observed default bundles | Later GR-071 candidate verification applies to a separate test root, not this captured tree |
| Local index linkage | [~] Four dispatched apps link present JS/WASM | Static inspection only; non-dispatch PhotoCraft index points at missing WASM |
| Combined current-candidate four-route browser/Seafile replay | [ ] NOT VERIFIED | GR-071 verifies candidate bytes together; GR-059/061–063 are separate per-app runs |
| ONLYOFFICE preservation reconciliation | [x] GR-040 isolated synthetic stack proves DOCX preservation | Production/deployment, other types/versions remain NOT VERIFIED |

Evidence: [manifest](GR-054-CURRENT-CANDIDATE-MANIFEST.md),
[checks and verifier](reviews/GR-054/README.md). Inventory PASS is not a
candidate-readiness or provenance PASS.

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
| 2.5 | Expired session | the save is refused with an explicit "session expired", not a generic error | [x] GR-043 Chromium ages a real in-memory gateway session past its TTL, then verifies actual `/save` returns 404 with reopen guidance, dirty remains true, the iframe receives `saveResult ok:false`, and the fake Seafile writer is never called. Real Seafile token expiry remains NOT VERIFIED (`docs/GR-043-SESSION-EXPIRY.md`) |
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
| 3.3 | Edit a formula | formula recomputes | [x] Synthetic Seafile E2E changed B2 from 42 to 1337; `SUM(B2:B2)` recalculated to 1337 and survived save/readback/fresh reopen. One formula path only; broader compatibility is not claimed. See `docs/reviews/GR-016/SEAFILE-GRIDCRAFT-SHARED-TRANSPORT-E2E-20261024.md`. |
| 3.4 | Minimal formatting | applied | [ ] not yet exercised |
| 3.5 | Save | new Seafile version | [~] patched bridge received a committed head/file ID from isolated Seafile; host showed `Stored — new version`; readback bytes/hash recorded, but history-list count was not independently queried (browser API returned 403) |
| 3.6 | Reopen | values and formulas preserved | [x] Fresh GridCraft session displayed B2=1337 and B3=1337 after the saved `SUM(B2:B2)` recalculation; formula and cached result were present in Seafile readback. Broader formula compatibility is not claimed. See `docs/reviews/GR-016/SEAFILE-GRIDCRAFT-SHARED-TRANSPORT-E2E-20261024.md`. |
| 3.7 | Concurrent edit | conflict, no silent overwrite | [~] fake-CAS unit test only; Seafile fileserver behavior is NOT VERIFIED |

## 4. PPTX — DeckCraft (GR-011)

| # | Test | Expected | Result |
| --- | --- | --- | --- |
| 4.1 | Open a synthetic PPTX | DeckCraft Web opens inline | [x] GR-044: actual patched DeckCraft WASM loaded and displayed the synthetic one-slide PPTX from a same-origin parent in Chromium (`docs/GR-044-DECKCRAFT-WASM-SMOKE.md`) |
| 4.2 | Edit a slide | the change is visible | [x] GR-044: actual patched DeckCraft WASM opened a synthetic PPTX in Chromium; edited the slide text and saw the changed text with `dirty=true` (`docs/GR-044-DECKCRAFT-WASM-SMOKE.md`) |
| 4.3 | Save | new Seafile version | [x] GR-064: host ACK and Seafile `Modified` history event after the visible slide edit; synthetic library only (`docs/GR-064-DECKCRAFT-REAL-SEAFILE-ROUNDTRIP.md`) |
| 4.4 | Reopen from Seafile | the slide change is preserved | [x] GR-064: fresh file-list/editor session reopened the saved slide edit; no explicit in-app close was claimed (`docs/GR-064-DECKCRAFT-REAL-SEAFILE-ROUNDTRIP.md`) |
| 4.5 | Synthetic host save acknowledgement | exact serialized bytes are captured; matching `saveResult` clears dirty; a fresh editor reopens the bytes | [x] GR-044 Chromium smoke captured 7,297 bytes (SHA-256 `ce01fb7cd7819f5ee6e67c67d77aeda19829e431a2cf92bdfe396b7d76b09376`), acknowledged `deckcraft:1`, observed clean state, and reopened the same edit in a fresh iframe; no Seafile write was performed |

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
| 6.3 | The existing ONLYOFFICE integration still works | `.docx` opened in the ONLYOFFICE path is unaffected | [x] GR-040: actual ONLYOFFICE browser edited a synthetic DOCX twice; callbacks returned HTTP 200, Seafile history grew 3→5, and fresh file-list reopen showed both edits. Synthetic patched stack only; production/deployment compatibility remains NOT VERIFIED |
| 6.4 | The ONLYOFFICE configuration is untouched | `seahub_settings.py` keeps `ENABLE_ONLYOFFICE = True` and the same 15 extensions | [x] SSH read-only check after removing the third-party `.xlsx` route; no ONLYOFFICE setting changed |
| 6.5 | The integration is reachable through configured origins | ArtCraft host/Craft are same-origin; Seahub is a separate origin; only `/open/` accepts Seahub Origin | [x] Synthetic Chromium run used Seahub `:18000` and gateway/Craft `:18777`; `/open/` handoff, editor save, fresh route load and persisted bytes verified. Production TLS/proxy, CSRF and adversarial-frame testing remain NOT VERIFIED; host-page CSP generation is covered by 6.7 |
| 6.6 | Rollback | removing the added route restores the previous behaviour | [ ] |
| 6.7 | Dynamic capability host-page CSP | nonce-bound inline code, restrictive resource policy, and only configured Seafile ancestor | [x] Gateway unit tests cover nonce/origin validation; Chromium exercises actual `POST /open/`: configured Seafile ancestor succeeds, nested foreign ancestor is blocked, nonce script/style work, and no allowed-page CSP violations fire. GR-042 bounded independent review: PROVISIONAL PASS, no findings. Craft bundle, proxy, production and other browsers remain NOT VERIFIED (`docs/reviews/GR-039/`, `docs/reviews/GR-042/`) |

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
| 11.5 | Browser transport + Seafile save/version/reopen | actual Seafile click, editor save ACK, version and fresh reopen | [x] GR-069: actual Seafile open/edit/save/new-version response and fresh Seafile file-list reopen with rectangle intact; exact message/readback bytes and history-page capture NOT VERIFIED |
| 11.6 | Host timeout, wrong-origin/source and production security | failure paths remain safe in a real browser topology | [ ] NOT VERIFIED; source implements 120-second unknown-outcome warning; runtime path not exercised |
| 11.7 | Single-document scope guards | host mode refuses new/open/duplicate/version-duplicate, branches and collaboration; unexpected extra dirty tabs remain visible and cannot be saved as the bound file | [x] synthetic UI test covers these dispatch paths, extra-tab dirty reporting and fail-closed save; browser controls NOT VERIFIED |
| 11.8 | Independent bounded patch review and transport re-pin | no blocker/major correctness finding on the exact patch | [x] Sol low round 3 PASS; repin R2 confirmed only transport pin changes beyond the accepted source hunks. One MINOR: dirty-state transport failure is not retried until state changes; project verdict unchanged |
| 11.9 | Actual-WASM browser host-only smoke | same-origin native open, visible engine edit, ticketed save bytes, matching ACK, dirty-to-clean, fresh iframe reopen | [x] GR-048 exact patched WASM; 3,464-byte save, rectangle visible after fresh reopen; synthetic memory-only parent. Exact `wasm-opt -Oz` execution NOT VERIFIED because build stdout is absent (`docs/GR-048-FIGCRAFT-WASM-SMOKE.md`) |

Patch and limits: `docs/reviews/GR-019/README.md`.

## 12. DeckCraft durable host-save acknowledgement prototype (GR-020)

| # | Test | Expected | Result |
|---|---|---|---|
| 12.1 | External ACK without a filesystem path | only the matching snapshot becomes the saved baseline; later edits remain dirty | [x] 2 focused `deckcraft-engine` tests pass; pathful documents are refused |
| 12.2 | Synthetic host open/edit/save/ACK/reopen | no clean state before ACK; serialized bytes reopen with the saved edit | [x] 4 focused `deckcraft-ui-egui` tests pass, including failure ACK and edit-after-submit |
| 12.3 | DeckCraft Web shared transport compilation | pinned adapter compiles for `wasm32-unknown-unknown` | [x] Rust 1.95 locked WASM check passes on pin `56c5e16` |
| 12.4 | Host-mode single-document and Save As guards | no second document, path-open, or Save As can bypass the host binding | [x] UI dispatch and direct helpers guard the local adapter; bounded independent review PASS |
| 12.5 | Browser messaging with real DeckCraft WASM | parent open/save/ACK exchange works in browser | [x] GR-044: actual patched WASM opened, edited, saved and received matching ACK in Chromium; fresh iframe reopened captured bytes. Synthetic parent only; see `docs/GR-044-DECKCRAFT-WASM-SMOKE.md` |
| 12.6 | Seafile new version and fresh-storage reopen | saved presentation survives Seafile version creation and fresh editor load | [x] GR-064 synthetic-library test created a history modification and reopened the slide edit in a fresh editor session; popup shim disclosed, no explicit in-app close claimed |
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
| 13.8 | DesignCraft Seafile browser version/reopen | saved document is persisted as a Seafile version and reopened from Seafile | [x] GR-065 synthetic-library run observed two `Modified` events and fresh file-list reopen; save/readback byte identity remains NOT VERIFIED |
| 13.9 | Malformed host save acknowledgements | missing/non-boolean `ok` does not consume a ticket as a false ACK; valid true/false retain behavior | [x] Parser tests cover malformed values and valid booleans; WASM test target compiled but was not browser-executed; 7 native tests and 19 checksums pass; see `docs/reviews/GR-024/` |
| 13.10 | DesignCraft actual WASM host runtime | synthetic native file opens, visible edit emits save bytes, matching ACK clears dirty, fresh iframe reopens captured bytes | [x] GR-045: built the patched WASM from source pin `80d13911`; Chromium opened the 6,585-byte synthetic document, saved 3,184 bytes, accepted matching ticket `designcraft:1:1`, became clean and reopened the edit in a fresh iframe. Synthetic parent only; no Seafile write. See `docs/GR-045-DESIGNCRAFT-WASM-SMOKE.md` |

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
| 14.5 | Browser host messaging | real iframe Open/Save/ACK works in browser | [x] GR-047 original run and supplemental Chromium replay; three bounded independent reviews PROVISIONAL PASS, no findings remain. Replay retains response-body hashes and R3 independently checked the separate pre-packaging WASM cache hash; historical continuity remains NOT VERIFIED. See `docs/GR-047-FILMCRAFT-WASM-SMOKE.md` |
| 14.6 | Seafile version and fresh reopen | saved edit survives durable Seafile write and new editor instance | [x] GR-066 synthetic-library run observed new-version confirmation/history modification and fresh file-list reopen; exact byte identity and explicit in-app close remain NOT VERIFIED |
| 14.7 | Fresh iframe host-only reopen | new editor instance opens captured bytes and renders the edit | [x] GR-047: fresh iframe opened the captured bytes and visibly rendered `GR-047 visible edit passed`; no Seafile write. See `docs/GR-047-FILMCRAFT-WASM-SMOKE.md` |

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
| 15.4 | Browser host protocol and Seafile version/reopen | durable version and edit visible after fresh storage reopen | [x] GR-067 synthetic-library run saved a visible edit and reopened it in a fresh Seafile editor session; exact byte identity and explicit in-app close remain NOT VERIFIED |
| 15.5 | Production host authorization and security topology | permissions/origins/proxy controls verified | [ ] NOT VERIFIED |
| 15.6 | EffectCraft actual WASM host open/edit/save/ACK/reopen | native synthetic project opens; visible edit serializes; matching positive ACK clears dirty; fresh iframe reopens captured bytes with edit intact | [x] GR-046 built the exact GR-022 patch and passed in Chromium; parent captured 62,136 bytes (SHA-256 `0828d978e619e0b3afdfd9a8bfba3578b3844aebb9e18f24f412d3eadba2b3d6`), ACKed `effectcraft:1`, observed clean state and reopened with the edit visible. Parent storage is in-memory only; no Seafile persistence. See `docs/GR-046-EFFECTCRAFT-WASM-SMOKE.md` and `docs/reviews/GR-046/` |

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
| 17.2 | Local picker/drop cannot replace host-bound session | dirty content and history remain unchanged | [x] Focused host-bound UI library regression passes 1/1 with GR-029 overlay |
| 17.3 | SoundCraft Web WASM build | pinned host adapter builds for browser target | [x] Rust 1.95 locked check passes with GR-027/028 and local GR-029 egui overlays |
| 17.4 | Browser host messaging and Seafile version/reopen | durable saved edit reopens from a fresh session | [x] GR-031 confirms this bounded flow; adapter remains outside dispatch |

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
| 19.3 | Full SoundCraft Web WASM | App and host adapter compile | [x] Rust 1.95 locked check passes with local GR-029 craft-ui and SoundCraft compatibility patches; no upstream edits |
| 19.4 | Browser host save / Seafile version / fresh reopen | Durable version and edit survive reopen | [x] GR-031 reproduced with SoundCraft Web/WASM in isolated synthetic Seafile; exact outbound payload hash and deployment behavior remain unverified |

Independent CPAL patch review: `docs/reviews/GR-028/REVIEW-INDEPENDENT-R1.md`.

## 20. SoundCraft egui 0.37 compatibility (GR-029)

| # | Test | Expected | Result |
|---|---|---|---|
| 20.1 | craft-ui egui 0.37 port | Pinned shared UI crate builds against SoundCraft's egui 0.37 | [x] Local compatibility patch passes as part of the full app WASM check |
| 20.2 | SoundCraft egui API port | Screenshot, wheel, widget-role and gutter-scroll APIs compile | [x] Rust 1.95 locked full Web WASM check passes after exact GR-025→027→028→029 patch sequence |
| 20.3 | GR-025 host-save guard regression | Host Save routes through the adapter; replacement and Save As remain refused | [x] Focused UI library test passes 1/1 |
| 20.4 | Browser/Seafile save and reopen | Actual Web/WASM editor creates a Seafile version and reopens it | [x] GR-031 actual Seahub file-list open, save ACK, new version and fresh reopen; bounded synthetic stack only |
| 20.5 | Independent GR-029 review | Exact patches, lock order and scoped code review | [x] Sol low R3 bounded PROVISIONAL PASS; project GPT review remains pending |

Patch hashes, application order, commands and limits: `docs/reviews/GR-029/`.


## 21. SoundCraft browser host-save smoke (GR-030)

| # | Test | Expected | Result |
|---|---|---|---|
| 21.1 | Open through host `postMessage` | SoundCraft Web opens the supplied synthetic `.scraftz` | [x] Chromium/T3 preview: same-origin parent sent the bundle; actual WASM editor opened it clean |
| 21.2 | Real UI edit and save handoff | Added track is serialized and sent to the parent | [x] Added `Audio 1`; Ctrl+S delivered 66,203,163 bytes, SHA-256 recorded in GR-030 evidence |
| 21.3 | Host ACK state transition | Matching positive ACK clears the captured current state | [x] In-memory parent replied with the same ticket; editor reported `dirty: false` |
| 21.4 | Fresh editor reopen | A new editor instance opens the acknowledged bytes and retains the edit | [x] Fresh iframe displayed ten tracks including `Audio 1`; screenshot retained |
| 21.5 | Seafile new version and storage-backed reopen | Save creates a Seafile version and a fresh Seahub open retains the edit | [ ] NOT VERIFIED; parent kept bytes in memory only |
| 21.6 | Default gateway size compatibility | Current host-save payload is accepted by the gateway default ceiling | [ ] NOT VERIFIED / known mismatch: 66,203,163-byte payload exceeds the 50 MiB `ARTCRAFT_MAX_BYTES` default |

Build used the release profile with `data-wasm-opt="0"`; it is functional
browser evidence, not optimized production bundle evidence. See
`docs/reviews/GR-030/` and `docs/GR-030-SOUNDCRAFT-BROWSER-SMOKE.md`.

## 22. SoundCraft isolated Seafile save and reopen (GR-031)

| # | Test | Expected | Result |
|---|---|---|---|
| 22.1 | Seahub file-list open | Selected `.scraftz` opens in SoundCraft Web/WASM | [x] Reproduced through the synthetic Seahub file-list route |
| 22.2 | Editor Save creates Seafile version | Edit is stored as a new Seafile head and receives host confirmation | [x] Added `Audio 2`; new file ID/head; editor showed “Saved — new version” |
| 22.3 | User-bound readback | Seafile returns the saved project bytes | [x] 6,877 bytes, SHA-256 `895bce8fa565730ded872bbf1dd1746ddddc0345e72d9485279e3d987a5a3aff`; exact outbound message bytes were not independently hashed |
| 22.4 | Fresh storage-backed reopen | New Seahub click renders the saved edit in a fresh editor session | [x] Three tracks visible and editor clean after reopen |
| 22.5 | Gateway `.scraftz` archive-shape check | ZIP directory has one nonempty root `.scraft` entry; missing entry is rejected | [x] Gateway unit suite passes; this does not validate entry CRC or session semantics |
| 22.6 | Independent bounded review | Evidence and implementation reviewed without blocker/major finding | [x] Luna High PROVISIONAL PASS with three minor qualifications; Playwright refusal cases and independent Seafile-byte verification remain open |

The functional release bundle used `wasm-opt=0`; production optimization,
security hardening, ONLYOFFICE regression and deployment behavior remain
NOT VERIFIED. SoundCraft remains excluded from the committed dispatch. See
`docs/GR-031-SOUNDCRAFT-SEAFILE-E2E.md` and `docs/reviews/GR-031/`.

## 23. PhotoCraft host-save source prototype (GR-032)

| # | Test | Expected | Result |
|---|---|---|---|
| 23.1 | Pathless host open | One `.pcraft` opens without local path/recent entry; second open is refused | [x] GR-026 pathless-open regression and GR-032 one-open assertion pass |
| 23.2 | File Save dispatch and serialization | File Save sends one serialized `.pcraft` snapshot with one ticket | [x] Focused UI lifecycle test passes 1/1 |
| 23.3 | ACK identity and dirty state | Unknown ticket ignored; only matching positive ACK acknowledges captured snapshot; negative leaves baseline unchanged | [x] Test covers negative ACK, dirty preservation, unique retry ticket, stale ACK rejection and matching success |
| 23.4 | Unknown timeout and unsafe close/retry | Missing result locks retry; dirty or unresolved close cannot discard snapshot | [x] Focused UI test exercises timeout, retry refusal and close refusal |
| 23.5 | Open/replace/Save As bypasses | Local picker/drop, new/open, action playback, Save As/Copy cannot replace host-bound document | [ ] New/Save As guards and one-open are tested; remaining picker/drop/action routes are source-inspected only |
| 23.6 | Rust 1.95 Web WASM check | Pinned transport and PhotoCraft app compile for WASM | [x] `cargo +1.95.0 check --locked -p photocraft-web --target wasm32-unknown-unknown` passes |
| 23.7 | Browser host and Seafile version/reopen | Edit creates durable Seafile version and survives fresh editor reopen | [ ] NOT VERIFIED; no browser or Seafile accessed |
| 23.8 | R1 bounded ACK inbox | Unknown/duplicate replies cannot grow the queue or block a matching ACK | [x] `cargo +1.95.0 test --locked -p photocraft-web host_inbox::tests::`; 1 queue flood regression passes |
| 23.9 | Listener registration failure | Host startup reports listener error and never posts ready | [x] Listener error propagation helper test passes; browser startup rendering is NOT VERIFIED |
| 23.10 | Gateway size limit / pre-serialization memory | Saves within default ceiling reach gateway; oversized document fails without excessive allocation | [ ] NOT VERIFIED; gateway defaults to 50 MiB (`integration/gateway/server.py:98`); PhotoCraft serializes first and rejection only preserves dirty state |
| 23.11 | Independent exact-patch review | Corrected patch includes inbox module and bounded ticket filtering | [x] R2/R3 bounded PROVISIONAL PASS; builds/tests are implementer-reported, not independently rerun |

Patch hash, exact base, review request and limits: `docs/reviews/GR-032/` and
`docs/GR-032-PHOTOCRAFT-HOST-SAVE.md`.

## 24. PhotoCraft browser host-protocol smoke (GR-033)

| # | Test | Expected | Result |
|---|---|---|---|
| 24.1 | Browser host Open | Same-origin parent opens the synthetic file in PhotoCraft Web/WASM | [x] Chromium preview received ready and sent the 4,000-byte fixture |
| 24.2 | UI edit and save handoff | Real editor edit emits serialized bytes and a correlated ticket | [x] Added GR-033 saved layer; captured 4,995 bytes, SHA-256 cbaa7b458588780210d1da7a267d2d5223d6808e0b15ea9e80e84d23ea980f34 |
| 24.3 | Matching ACK | Only matching parent success ACK makes the editor clean | [x] Matching ticket returned; editor reported dirty=false |
| 24.4 | Fresh iframe reopen | Reopened bytes render the edit in a new editor instance | [x] New iframe showed GR-033 saved layer; screenshot and harness log retained |
| 24.5 | Durable host write / Seafile version | ACK follows a committed Seafile version and readback | [ ] NOT VERIFIED; harness retains bytes only in page memory |
| 24.6 | Optimized bundle and deployment controls | Production-optimized WASM works under TLS, proxy, CSP and adversarial-frame checks | [ ] NOT VERIFIED; build used wasm-opt=0, local same-origin loopback only |
| 24.7 | Independent bounded evidence review | Browser claims and limits agree with retained artifacts | [x] Nemotron 3 Ultra PROVISIONAL ACCEPT; read-only artifact review, runtime not rerun |

This smoke does not add PhotoCraft to the Seafile dispatch and is not a Seafile
MVP or project GPT PASS. Evidence and limits: `docs/GR-033-PHOTOCRAFT-BROWSER-SMOKE.md`
and `docs/reviews/GR-033/`.

## 25. PhotoCraft gateway payload validation (GR-034)

| # | Test | Expected | Result |
|---|---|---|---|
| 25.1 | Native `.pcraft` fixture validation | PhotoCraft's generated ZIP with root `manifest.json` is accepted | [x] Project-native GR-033 fixture passes metadata-only validation |
| 25.2 | Malformed ZIP validation | Malformed `.pcraft` ZIP is rejected without an exception escaping | [x] Focused gateway unit check passes |
| 25.3 | Root manifest requirement | Missing, nested-only, duplicate, or empty exact-root `manifest.json` is rejected | [x] Four focused cases pass |
| 25.4 | Save-path rejection | Invalid `.pcraft` is refused before Seafile write | [x] Gateway returns status 400; fake Seafile save calls=0 and no writes |
| 25.5 | Seafile runtime/version check | A valid `.pcraft` writes a durable new version and reopens from Seafile | [ ] NOT VERIFIED; Seafile runtime unavailable and not accessed; `.pcraft` remains excluded from dispatch |
| 25.6 | Independent bounded review | Validation and focused tests have no blocker/major finding | [x] Nemotron 3 Ultra R2 PROVISIONAL PASS; initial MINOR test gap remediated |

The validator inspects ZIP central-directory metadata only; it does not
decompress/parse `manifest.json` or verify member CRC/data. Full limits and
source reference: `docs/GR-034-PHOTOCRAFT-GATEWAY-VALIDATION.md`.

## 26. PhotoCraft optimized Web host smoke (GR-035)

| # | Test | Expected | Result |
|---|---|---|---|
| 26.1 | Optimized release Web bundle | Release build completes with `wasm-opt -Oz` | [x] `trunk build --release` completed; WASM 26,342,447 bytes |
| 26.2 | Host Open and editor startup | Same-origin parent receives ready and opens synthetic `.pcraft` | [x] PhotoCraft 0.15.1 opened the 4,000-byte fixture |
| 26.3 | UI edit and ticketed Save | Editor emits a save ticket and serialized bytes while dirty | [x] UI-created `Layer 1`; 4,984 bytes; SHA-256 recorded in GR-035 |
| 26.4 | Matching positive ACK and fresh iframe reopen | Matching in-memory ACK clears dirty; fresh app instance renders saved edit | [x] In-memory parent ACK and fresh iframe reopen showed `Layer 1`, `dirty=false` |
| 26.5 | Seafile version and fresh storage-backed reopen | Seafile creates a new version and a fresh Seahub click reads the saved edit | [ ] NOT VERIFIED; parent retained bytes in memory only; PhotoCraft remains out of dispatch |
| 26.6 | Independent bounded evidence review | Reviewer confirms artifact and scope without blocker/major finding | [x] PROVISIONAL ACCEPT; no blocker/major; minor note: browser capture does not bind loaded WASM resource to recorded artifact hash |

This smoke establishes optimized-bundle browser execution only. It is not
Seafile E2E or a project GPT PASS. Evidence: `docs/reviews/GR-035/` and
`docs/GR-035-PHOTOCRAFT-OPTIMIZED-BROWSER-SMOKE.md`.

## 27. PhotoCraft synthetic Seafile version and reopen (GR-036)

| # | Test | Expected | Result |
|---|---|---|---|
| 27.1 | Seahub file route opens PhotoCraft | Actual Web/WASM receives the host Open and renders the document | [x] Synthetic Seahub route fetched the document; explicit repaint after queueing allowed the idle editor to process the host event |
| 27.2 | Edit and save through host | UI edit is sent to gateway; editor reports success after host save response | [x] Added `Layer 1`; Ctrl+S returned 200 and editor displayed “Saved to host” |
| 27.3 | Seafile history and readback | Save creates a new version whose content includes the edit | [x] History grew 1→2; readback 4,984 bytes; ZIP manifest contains `Layer 1` |
| 27.4 | Fresh storage-backed reopen | A new Seahub route/session loads the saved edit from Seafile | [x] Fresh route created a new session; document GET returned 200 and reopened editor displayed `Layer 1` |
| 27.5 | Independent exact evidence review | No blocker/major remains for this bounded evidence claim | [x] R2 PROVISIONAL ACCEPT; evidence substantiated with read-only readback artifact; duplicate README entry fixed |
| 27.6 | Optimized bundle and deployment/security | Optimized output and production topology are validated | [ ] NOT VERIFIED; `wasm-opt=0`, synthetic loopback only |

This is synthetic Seafile runtime evidence, not a production deployment or
project-level GPT PASS. The temporary `.pcraft` route was outside the committed
dispatcher. See `docs/GR-036-PHOTOCRAFT-SEAFILE-E2E.md` and `docs/reviews/GR-036/`.

## 28. PhotoCraft save-byte provenance follow-up (GR-037)

| # | Test | Expected | Result |
|---|---|---|---|
| 28.1 | Editor-to-host save payload hash | Hash the transferred PhotoCraft bytes before host persistence | [x] Browser message: 8,555 bytes, SHA-256 `ea0121c1e465c753947005e1ff4452cc031f734baed3345400bcd3a96218c4ca` |
| 28.2 | Gateway request-body hash | Hash bytes received by the gateway | [x] Browser request-body capture plus one gateway server-side digest; same byte count and SHA-256 as editor message |
| 28.3 | Seafile storage readback | Download bytes from Seafile and compare exact size/hash | [x] 8,555 bytes; exact hash match across all three boundaries; latest history file ID matches current detail |
| 28.4 | Version and fresh reopen | New Seafile version and a new editor session load the saved content | [x] History grew 2→3; fresh Seahub route fetched the document (HTTP 200) and PhotoCraft reported clean |
| 28.5 | Production/deployment and optimized bundle | Validate production topology, hardening and optimized artifact | [ ] NOT VERIFIED; synthetic loopback only, `wasm-opt=0`; PhotoCraft remains excluded from committed dispatch |
| 28.6 | Local Rust build storage | Confirm Cargo targets and child temporary files stay off `/tmp` | [x] `scripts/check-build-storage.sh` confirms both paths under `/home/roddy/.cache` |

Bounded synthetic evidence only; independent review was PROVISIONAL ACCEPT
without blocker/major; final wording MINOR corrected afterward. See
`docs/reviews/GR-037/`.

## GR-063. VectorCraft real synthetic Seafile roundtrip

| Scenario | Result |
|---|---|
| Exact deployed VectorCraft candidate | [x] GR-058 verifier passes against active static root: nine files, hashes, index references, and SRI |
| Synthetic SVG opened from Seafile file list | [x] Actual VectorCraft WASM and session document returned HTTP 200 |
| Edit SVG and persist without browser download/manual upload | [x] Added rectangle; File → Export → Export As SVG was captured in page memory and gateway save returned HTTP 200 |
| Host save confirmation and version history | [x] New-version confirmation; Seafile UI history shows Modified after Added |
| Fresh-session open from Seafile file list | [x] A second editor/session displays the stored rectangle; first session was not explicitly closed |
| Ctrl+S native dirty marker | [ ] Limitation: opens Save As for imported SVG; cancelled; export succeeds but app's asterisk remains |
| Exact editor-export bytes vs Seafile content readback | [ ] NOT VERIFIED; no direct readback/hash comparison |
| Permission revocation, external writer, response loss, concurrency, production security | [ ] NOT VERIFIED |
| Post-change ONLYOFFICE edit/save regression | [ ] NOT RUN; integration stayed enabled and its settings/routes were untouched |
| Independent review | [x] R1–R2 bounded PROVISIONAL PASS, no remaining findings; reviewers did not replay live behavior |

Evidence: `docs/reviews/GR-063/`; report: `docs/GR-063-VECTORCRAFT-REAL-SEAFILE-ROUNDTRIP.md`.
Project GPT remains INCOMPLETE; upstream publication remains LOCKED.

## 29. Craft Web asset ingestion safety (GR-038, GR-041)

| # | Test | Expected | Result |
|---|---|---|---|
| 29.1 | Release selection | A caller names an exact release tag and digest; no mutable `latest` lookup | [x] WordCraft v0.10.0 selected explicitly |
| 29.2 | Pinned archive integrity and basic layout | Digest matches; one-root ZIP contains root `index.html` and WASM | [x] Exact WordCraft release passed digest and layout validation |
| 29.3 | Unsafe ZIP rejection | Traversal, absolute/backslash paths, duplicate names, symlinks, ambiguous roots, and missing index/WASM are rejected | [x] `python3 tests/test_gr041_craft_zip_limits.py` exercises each listed negative case |
| 29.4 | Active build safety | Fetching must not overwrite dispatcher-selected `integration/static/<app>/` | [x] Output staged under `integration/static/candidates/wordcraft/`; promotion is separate; final move uses no-clobber semantics |
| 29.5 | Host protocol compatibility | Staged release passes Open/Save/ACK app smoke before promotion | [ ] NOT VERIFIED; candidate is not promoted |
| 29.6 | Independent review of original GR-038 | No blocker/major remains in the original staged-fetch change | [x] Luna High bounded GR-038 re-review: provisional ACCEPT; predates GR-041 |
| 29.7 | Download byte limit and deadline | Exact limit accepted; larger download refused; slow download ends within bounded deadline plus one socket timeout | [x] Synthetic stream verifies byte cap, reduced total-deadline behavior and 30-second socket timeout |
| 29.8 | Extracted byte and entry limits | Exact total/count accepted; greater declared/streamed total or entry count refused | [x] Synthetic ZIPs verify exact byte cap and reject entry count before `ZipFile` construction |
| 29.9 | Malformed and conflicting ZIP metadata | Malformed, ZIP64, multi-disk, duplicate and unsafe-path entries are rejected | [x] `python3 tests/test_gr041_craft_zip_limits.py`; EOCD boundary cases covered with synthetic records |
| 29.10 | Independent exact review of GR-041 | No blocker/major remains in bounded candidate ingestion | [x] Nemotron R3 PROVISIONAL PASS; cleanup trap verified; live release fetch and protocol compatibility remain NOT VERIFIED |

See `docs/GR-038-CRAFT-ASSET-INGESTION.md` and `docs/ASSET-INGESTION.md`.


## GR-049. Gateway committed-save retry

| Test | Expected | Result |
|---|---|---|
| Discard committed result, save identical bytes again | Same result, one write, no retained document bytes | [x] Synthetic regression |
| Concurrent same-session identical saves | Two acknowledgments, one upstream save | [x] Synthetic regression |
| Changed bytes / external head | Updated IDs passed to CAS; external change refused | [x] Synthetic regression |
| Replay validation / permission / identity / freshness | Invalid payload/name/size and unauthorized or stale replay refused | [x] Synthetic regression |
| Upstream error | No false receipt; reauthorization errors fail closed | [x] Synthetic regression |
| Existing gateway security and two-session CAS race | Existing checks pass | [x] `python3 tests/test_gateway_unit.py` |
| Gateway socket response loss after commit | Real save route then identical HTTP retry, without duplicate write | [x] GR-050 loopback TCP regression |
| Browser / real Seafile new version and reopen | Durable end-to-end retry | [ ] NOT VERIFIED |
| Independent review | Separate bounded reviewer | [x] PROVISIONAL PASS R1, no findings; network/runtime gaps remain |

Run `python3 tests/test_gr049_save_retry.py`; evidence in `docs/reviews/GR-049/`.

## GR-050. HTTP response loss after committed save

| Scenario | Expected | Result |
|---|---|---|
| Real save route commits, server closes socket before any HTTP response, identical bytes retried over HTTP | Client sees RemoteDisconnected; retry returns original success, exactly one fake upstream write/version | [x] Synthetic loopback TCP regression; `tests/test_gr050_http_save_retry.py` |
| Browser / real Seafile versions | Durable end-to-end retry | [ ] NOT VERIFIED by this slice |

| Independent review | Exact test/evidence review | [x] PROVISIONAL PASS R1, no blocker/major |

Evidence: `docs/reviews/GR-050/`. GPT REVIEW PENDING; no project-level verdict.

## GR-051. Browser retry after lost gateway response

| Scenario | Expected | Result |
|---|---|---|
| Real open/render/document routes | Browser loads synthetic editor/document, HTTP 200 | [x] Cached Playwright Chromium, loopback only |
| First save commits then gateway response socket drops | Browser fetch fails; ticket-1 negative, editor/host dirty and unconfirmed | [x] Exact `net::ERR_EMPTY_RESPONSE`, internal 200, no browser response |
| User retry, same bytes, fresh ticket-2 | Receipt HTTP 200, one fake upstream write/version | [x] Exact result, bytes, CAS expectation and write count |
| Editor sends dirty=false after success | Host clean/confirmed, gateway unsaved=false | [x] State and dirty route ACK asserted |
| Exact route status observations and cleanup | No extra routes/writes; browser and servers stop | [x] Browser/server route multisets, failed request, joins asserted |
| Actual WordCraft WASM / real Seafile / reopen | Complete MVP | [ ] NOT VERIFIED; synthetic editor and FakeSeafile only |
| Upstream response loss before gateway receipt | Safe end-to-end retry | [ ] NOT VERIFIED; only gateway-to-browser response loss covered |
| Independent review | Separate bounded reviewer | [x] R1 PROVISIONAL PASS, no blocker/major; two P3 wording corrections closed |

Evidence: `docs/reviews/GR-051/`; `tests/test_gr051_browser_save_retry.py`.
GR-049/050 and gateway checks pass. GPT REVIEW PENDING; no project verdict.

## GR-052. Ambiguous upstream save response loss

| Scenario | Expected | Result |
|---|---|---|
| Fake commit then status=None; exact user-bound reread | Success, current IDs, clean, receipt; identical retry adds no write | [x] Native synthetic test |
| Different current bytes | 502, no receipt, dirty and old baseline; retry CAS conflicts | [x] Native synthetic test |
| Revoked permission / token bound to another user, repo or path | 403, no baseline advance or receipt | [x] Native synthetic tests |
| Info/content auth, missing file, transport or service failure | Safe 403/404/502; no receipt or baseline advance | [x] Native synthetic tests |
| Missing content API / missing current IDs | 503/502, fail closed | [x] Native synthetic tests |
| File/head, permission or user changes during content read | 409/403, fail closed | [x] Native synthetic tests |
| Known 409/403/400/502 from save | No reconciliation content read; existing error mapping retained | [x] Native synthetic tests |
| Identical retry contends while response-loss reconciliation is pending | Retry waits on session lock, reuses receipt, causes no second upstream write | [x] Event-gated lock-contention test; repeated 25 times |
| Existing GR-049/050 and gateway suite | Existing behavior intact | [x] PASS |
| Real Seafile / browser / ONLYOFFICE | Complete MVP | [ ] NOT VERIFIED; untouched |
| Independent review | Separate reviewer | [x] R1–R3 PROVISIONAL PASS, no blocker/major |

Evidence: `docs/reviews/GR-052/`; `tests/test_gr052_upstream_save_loss.py`.
PROVISIONAL implementation; GPT REVIEW PENDING; no project GPT PASS.

## GR-053. Credential redirect isolation

| Scenario | Result |
|---|---|
| 301/302/303/307/308 with Authorization or credential query | PASS; target receives no request |
| Signed download/update/upload path-only bearer | PASS; redirect refused |
| Public no-credential request with ordinary query | PASS; 302 followed intentionally |
| Gateway suite / pycompile / diff check | PASS; docs/reviews/GR-053/ |
| Real Seafile redirects / browser MVP | NOT VERIFIED; no external access |
| Independent review | [x] R1–R2 PROVISIONAL PASS, no blocker/major; GPT REVIEW PENDING |

## GR-076 — bounded PhotoCraft browser host adapter

| Check | Evidence / status |
|---|---|
| Exact source/core/adapter/transport and locked dependency resolution | Exact pins in `reviews/GR-076/pins.json`; retained-base locked WASM check passed |
| Captured snapshot ACK, stale incarnation, later edits | PASS per retained `reviews/GR-076/check-result.json`; the original test stdout (`checks.log`) was not retained |
| Matching/negative/unknown/duplicate ACK, timeout/no retry and payload bounds | PASS, selected host cases in 7-test host filter |
| Menu/direct/nested commands, local/picker/drop/Save As/duplicate/close guards | PASS, source guards and focused UI test; all denial events not replayed in browser |
| Standalone/native file-open and save/download baseline regressions | PASS, 47 file-open tests including confirmed/unconfirmed writer regression |
| One Open across inbox drains, unknown/duplicate ACK flood, listener failure | PASS, 2 inbox tests; GR-076 browser received Open/save/ACK and fresh iframe reopen |
| Rust 1.95 locked WASM, format, whitespace and clean-base patch application | PASS, final script exit 0 and `reviews/GR-076/patch-check.txt` |
| Live iframe Open/save/ACK/fresh reopen | PASS, actual GR-076 patched WASM in T3 Chromium; in-memory smoke, low-optimization bundle; `reviews/GR-076/runtime/` |
| Dispatcher route `pcraft` → PhotoCraft | PASS, recorded in `integration/config/dispatch.json`; deployed synthetic route passed the browser workflow below |
| Synthetic Seafile click/open/edit/save/version/close/reopen | PASS, history has 3 versions; current readback hash and reopened two-layer view recorded in `reviews/GR-076/runtime/README.md` and `reviews/GR-076/runtime/seafile-readback.json` |
| WordCraft synthetic DOCX after `.pcraft` allowlist addition | PASS, edit/save/new version/close/reopen; marker remained visible; history count is 4; `reviews/GR-076/runtime/README.md` |
| Browser unload/clock and optimized bundle | NOT VERIFIED |
| ONLYOFFICE UI regression after GR-076 runtime deployment | NOT VERIFIED; configured API script URL returned 404, `docEditor` undefined. Document Server API and healthcheck returned 200 when probed on the service. ONLYOFFICE settings remained unchanged/enabled; prior GR-072 evidence is separate |
| Independent runtime/docs and dispatcher review | PASS, runtime R1 MINOR findings closed in R2; R2/R3 and dispatcher R1 PROVISIONAL PASS; `reviews/GR-076/runtime/review-r1-and-response.md` |
| Full desktop suite / visual QA / clippy / corpus | NOT VERIFIED |
