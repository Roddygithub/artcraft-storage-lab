## 2026-10-25 — GR-049 gateway committed-save retry

- Added a bounded per-session digest/length/result receipt and session locking.
  Identical retries recheck user-bound permission and current file/head before
  acknowledging the committed result; changed bytes retain upstream CAS.
- Six synthetic regressions and existing gateway unit checks pass; syntax and
  diff checks pass. Direct-call discarded-result simulation only: actual
  network-loss/browser/Seafile runtime NOT VERIFIED. Production/upstream untouched.
- Evidence: `docs/GR-049-IDEMPOTENT-SAVE-RETRY.md`, `docs/reviews/GR-049/`.
  Independent R1 bounded review: PROVISIONAL PASS, no findings. GPT review
  pending; no project GPT PASS or upstream publication authorization.

## 2026-10-25 — GR-048 FigCraft browser host-save smoke

- Applied the exact accepted GR-019 patch to clean FigCraft `8d790607`;
  built optimized actual Web/WASM against transport `56c5e16d` with persistent
  Cargo caches and the configured wasm-opt pass.
- T3 collaborative Chromium opened a synthetic native fixture, created a
  visible rectangle through UI input, emitted 3,464 save bytes, stayed dirty
  before matching ACK, became clean, and reopened the captured bytes visibly
  in a fresh iframe. Parent storage was memory-only; durable Seafile remains
  NOT VERIFIED. No upstream or production changes; no commit/push in this task.
- Evidence: `docs/GR-048-FIGCRAFT-WASM-SMOKE.md`, `docs/reviews/GR-048/`.
  Independent free R1: PROVISIONAL PASS, no blocker/major; warnings/setup
  MINOR observations retained. Status: GPT REVIEW PENDING.


## 2026-10-25 — GR-046 EffectCraft browser host-save smoke

* Built the exact GR-022 patched EffectCraft Web/WASM from pinned source and
  exercised open/edit/save/positive ACK/clean/reopen in Chromium with a
  same-origin synthetic parent. A visible text edit emitted 62,136 bytes; a
  fresh iframe reopened the captured bytes with the edit intact.
* Added the native synthetic project, parent harness and screenshot under
  `docs/reviews/GR-046/`; updated matrix, status and GPT review queue. The
  parent ACK was in-memory only. Seafile version/readback, dispatch, deployment,
  production and ONLYOFFICE remain **NOT VERIFIED**. Independent R1/R2 reviews
  returned bounded PROVISIONAL PASS with no remaining findings. No upstream
  changes.


## 2026-10-25 — GR-045 DesignCraft browser host-save smoke

* Built the actual GR-021 patched DesignCraft WASM from pinned source and
  exercised it in Chromium with a same-origin synthetic parent. A visible
  native-document text edit emitted 3,184 bytes; the matching positive ACK
  cleared dirty state, and a fresh iframe reopened the edit from those bytes.
* Added the reproducible harness, native fixture, captured payload and browser
  screenshot under `docs/reviews/GR-045/`; updated the DesignCraft test matrix
  and review queue. Independent R1/R2 reviews returned bounded PROVISIONAL PASS
  with no remaining findings. Seafile version/reopen, dispatcher, production and
  ONLYOFFICE remain **NOT VERIFIED**; no upstream changes were made.

## 2026-10-25 — GR-044 DeckCraft browser host-save smoke

* Built the actual DeckCraft WASM from the GR-020 patched source and exercised
  it in Chromium with a same-origin synthetic parent. A visible slide-text edit
  produced 7,297 save bytes; the matching positive ACK cleared dirty state, and
  a fresh iframe reopened the edit from the captured bytes.
* Added the bounded runtime harness, synthetic PPTX fixture and captured save
  payload under `docs/reviews/GR-044/`; updated the DeckCraft test matrix and
  review queue. Independent reviews R1 and R2 recorded PROVISIONAL PASS; R2
  rechecked the corrected page-memory host. Seafile version/reopen, dispatcher,
  production and ONLYOFFICE remain **NOT VERIFIED**. No upstream changes were made.

## 2026-10-25 — GR-043 expired-session save refusal

* Added a Chromium regression that expires the actual gateway session between
  host open and save. The real save route returns 404 with reopen guidance,
  keeps the editor dirty, sends a negative acknowledgement and makes no
  synthetic Seafile write.
* Documented evidence in `docs/reviews/GR-043/`; real Seafile token expiry,
  permission revocation and production behavior remain **NOT VERIFIED**.
  GPT review is pending and no upstream or production state changed.

## 2026-10-25 — GR-042 browser-enforced dynamic host CSP

* Added a Chromium check that posts a synthetic Seafile capability through the
  real gateway `Handler._open` route. The configured Seafile ancestor can frame
  the response; a nested disallowed outer ancestor is refused. The nonce inline
  script and stylesheet execute, with no CSP violations on the allowed page.
* Updated matrix row 6.7 and recorded the run in `docs/reviews/GR-042/`. Craft
  bundle CSP, proxy behavior, production and other browsers remain
  **NOT VERIFIED**. No Seafile or ONLYOFFICE service, production data or
  upstream repository was touched. GPT REVIEW remains INCOMPLETE.

## 2026-10-25 — GR-041 bounded Craft Web asset staging

* Added a 256 MiB streaming download cap and a 1 GiB extracted-content cap to
  the GR-038 staging fetcher. ZIP path and symlink checks and candidate-only
  staging are retained; no active `integration/static/<app>` tree is touched.
* Added eight focused standard-library tests for byte/count limits, deadline,
  ZIP64/multi-disk, duplicate/unsafe-path/symlink rejection and malformed
  archives. Independent exact review round 3 returned bounded PROVISIONAL PASS,
  no blocker/major; host protocol compatibility remains NOT VERIFIED.
* No service or upstream state changed. See
  `docs/GR-038-CRAFT-ASSET-INGESTION.md`.

## 2026-10-25 — GR-040 synthetic ONLYOFFICE regression

* Reproduced the existing Seafile → ONLYOFFICE browser path on a loopback-only
  synthetic stack. Two UI edits produced two successful Seahub callbacks and
  Seafile history advanced 3→5. API readback validated as DOCX; a fresh library
  file-list click/reopen displayed both edits. Evidence and retained screenshots
  are in `docs/reviews/GR-040/`.
* Updated matrix row 6.3. This verifies one synthetic DOCX flow on the local
  patched stack; deployed/production ONLYOFFICE, security topology, other file
  types and versions remain NOT VERIFIED. No production or upstream system was
  changed; GPT REVIEW remains INCOMPLETE.

## 2026-10-25 — GR-039 dynamic host-page CSP

* Added a per-response cryptographic nonce CSP to the gateway-generated
  `/open/` host page. The parent page now defaults to deny, permits only its
  nonce-bearing inline code, limits frames/connects to its own origin, and
  restricts embedding to the configured Seahub origin. Invalid origin config
  fails closed to `frame-ancestors 'none'`; CSP separators and percent-encoded
  control characters, empty user-info, query and fragment delimiters are
  rejected; default HTTPS port normalization is covered.
* `python3 tests/test_gateway_unit.py`, Python bytecode compilation, and
  `git diff --check` pass. Static Craft editor HTML, reverse-proxy behavior,
  browser CSP enforcement and bundle compatibility remain NOT VERIFIED. Three
  bounded independent review rounds returned PROVISIONAL PASS after two origin
  validation findings and one documentation discrepancy were fixed. ONLYOFFICE
  regression and project GPT PASS remain open. No Seafile production system or
  upstream repository was changed.

## 2026-10-25 — GR-038 pinned Web asset staging

* Reworked `scripts/fetch-craft-web.sh` to require an exact release tag and
  SHA-256, validate the ZIP structure and paths, and stage under a candidate
  directory instead of replacing the active app build.
* Verified shell syntax and staged the exact WordCraft v0.10.0 release asset
  (SHA-256 `46e32c024cac86d644874e7120ee9e42a6c0ccc76bd020ba9c741706b5b77b05`).
  A repeated staging attempt refused the existing candidate without changing
  its provenance record. Symlinked candidate directories are also refused.
  Luna High returned bounded provisional ACCEPT with no material finding;
  negative ZIP cases remain untested and host-protocol compatibility remains
  NOT VERIFIED. Evidence: `docs/GR-038-CRAFT-ASSET-INGESTION.md`.

## 2026-10-25 — First GPT-6.1 review of current remediation

* GPT-6.1 Sol reviewed exact HEAD `95d89835b2b1d06fd098c586469ed03b8fd0549e`
  and returned **INCOMPLETE**; GPT REVIEW PASS was not granted and upstream
  publication remains locked.
* The review accepts the synthetic DOCX click/edit/version/confirmation/reopen
  evidence as demonstrated. It leaves ONLYOFFICE regression, authorization and
  failure cases, patched-server compatibility, production security, pinned
  editor assets/protocol compatibility, and distribution/licensing treatment
  open. Full findings are recorded in `docs/reviews/GPT-FIRST-PASS-95D8983.md`.
* Reconciled the GridCraft formula rows in `docs/TEST-MATRIX.md` with the later
  GR-016 runtime evidence; this verifies one tested `SUM(B2:B2)` path only.

## 2026-10-25 — GR-037 PhotoCraft save-byte provenance

* Re-ran a real PhotoCraft Web/WASM edit and host save through isolated synthetic
  Seahub and Seafile. The editor message, gateway request body, and Seafile
  content readback were each 8,555 bytes with identical SHA-256
  `ea0121c1e465c753947005e1ff4452cc031f734baed3345400bcd3a96218c4ca`.
* Seafile history advanced from two to three versions. Reloading the Seahub
  file route created a new editor session, fetched the document successfully,
  and displayed it clean. The redacted API facts and screenshot are in
  `docs/reviews/GR-037/`.
* The runtime used a temporary synthetic dispatch and loopback-only config;
  both were restored, the test gateway and Seafile container were stopped,
  and temporary logs/capabilities were removed. PhotoCraft remains excluded
  from committed dispatch. Independent bounded review returned PROVISIONAL
  ACCEPT without blocker/major; its final wording MINOR was corrected but not
  separately re-reviewed. No project-level GPT verdict or upstream action.

## 2026-10-25 — GR-036 PhotoCraft Seafile version and reopen

* Reproduced a real PhotoCraft Web/WASM host open from a Seahub file route,
  added a layer, saved through the gateway, and observed the editor report
  “Saved to host” after the write returned. Seafile history grew from one to
  two versions; readback was 4,984 bytes and contained `Layer 1`.
* A fresh Seahub route opened a new editor session and displayed the saved
  layer. The incremental PhotoCraft fix requests an egui repaint after queuing
  asynchronous host messages; its patch and the reopen screenshot are recorded
  in `docs/reviews/GR-036/`.
* The runtime used the isolated synthetic stack and temporary `.pcraft`
  dispatch, not the committed dispatcher. Build used `wasm-opt=0`; optimized
  production output, deployment security and ONLYOFFICE regression remain
  NOT VERIFIED. Independent review returned PROVISIONAL ACCEPT without
  blocker/major; a GET-only readback artifact and verifier were added to close
  its evidence-substantiation qualification. No upstream changes were made.
* Full evidence and limitations: `docs/GR-036-PHOTOCRAFT-SEAFILE-E2E.md`.

## 2026-10-25 — GR-035 PhotoCraft optimized Web smoke

* Built the GR-032 PhotoCraft host adapter with `trunk build --release`;
  release `wasm-opt -Oz` completed. The 26,342,447-byte WASM loaded in a
  same-origin T3 Chromium parent harness.
* Reproduced fixture open, UI edit, ticketed save, matching in-memory success
  ACK, and fresh iframe reopen with the added layer intact. The save payload
  was 4,984 bytes with recorded SHA-256.
* The parent retained bytes in memory. Seafile version creation and
  storage-backed reopen remain NOT VERIFIED. Nemotron returned PROVISIONAL
  ACCEPT for this bounded smoke; its minor browser-to-WASM-hash binding
  qualification is recorded in the evidence bundle. No project GPT PASS is
  claimed.
* Scope and limits: `docs/GR-035-PHOTOCRAFT-OPTIMIZED-BROWSER-SMOKE.md`.

## 2026-10-25 — GR-034 PhotoCraft gateway payload validation

* Added gateway `.pcraft` type validation that requires exactly one nonempty
  root `manifest.json` in the ZIP central directory. The check does not
  decompress any members; malformed, missing-root, and nested-only manifest
  cases are rejected. `Gateway.save` rejects an invalid `.pcraft` before its
  Seafile save method is called.
* `python3 tests/test_gateway_unit.py` passes, including acceptance of the
  project-native PhotoCraft fixture. `git diff --check` is recorded in the
  GR-034 assessment.
* Added duplicate-root and empty-root manifest rejection tests after the initial
  independent reviewer noted that those code paths were not explicit in the
  test suite. Nemotron 3 Ultra R2 returned a bounded PROVISIONAL PASS after the
  remediation; the review did not rerun tests or access services.
* The PhotoCraft dispatcher, Seahub patches/configuration, app bundles and
  services were not changed. Seafile runtime was unavailable and not accessed.
* Scope and limits: `docs/GR-034-PHOTOCRAFT-GATEWAY-VALIDATION.md`.

## 2026-10-25 — GR-033 PhotoCraft browser host-protocol smoke

* Reproduced the actual PhotoCraft Web/WASM host protocol in a same-origin
  Chromium preview: synthetic Open, UI layer edit, exact save-message bytes and
  ticket capture, matching in-memory success ACK, clean-state report, and fresh
  iframe reopen showing the saved layer.
* The parent retained bytes only in JavaScript memory. This proves browser
  adapter interoperability, not Seafile persistence or a new server version.
  The functional release build used wasm-opt=0; optimized bundle, deployment
  security and ONLYOFFICE regression remain NOT VERIFIED.
* Harness, screenshot, fixture hashes, and limitations are in
  `docs/reviews/GR-033/`; summary: `docs/GR-033-PHOTOCRAFT-BROWSER-SMOKE.md`.

## 2026-10-25 — GR-032 PhotoCraft host-save adapter

* Added a local one-document Rust Web adapter to the exact PhotoCraft `a02f2ee`
  base with the accepted GR-026 core patch applied. `?host=parent` opens one
  pathless `.pcraft`; File › Save serializes and sends ticketed bytes through
  pinned `craft-platform` `56c5e16`, and only the matching positive ACK advances
  the captured snapshot baseline. Negative ACK stays unsaved; timeout retains
  an unknown ticket and blocks retry/dirty close.
* Added route guards for new/open/replace, local picker/drop, Save As/Copy,
  action playback, automation open and unsafe close. Standalone browser download
  and native write paths are unchanged outside host mode.
* Rust 1.95 locked Web WASM check, focused lifecycle UI test 1/1, exact-base
  patch apply and diff checks pass. Browser runtime, Seafile save/version/reopen
  and independent review are NOT VERIFIED. No upstream or production actions
  were taken.
* Patch and evidence: `docs/reviews/GR-032/`; full scope and limits:
  `docs/GR-032-PHOTOCRAFT-HOST-SAVE.md`.

## 2026-10-25 — GR-032 R1 queue/listener remediation

* Addressed the independent R1 finding that every parsed `SaveResult` entered
  an unbounded inbox before ticket validation. The new inbox has separate fixed
  slots for the first Open and one result matching the live ticket; unknown and
  duplicate ACKs are discarded before storage.
* Listener registration errors now fail the Web app creator before `post_ready`.
  Two focused PhotoCraft Web tests pass (queue flood protection and listener
  error propagation), as does the Rust 1.95 locked WASM check. Updated patch SHA
  is recorded in `docs/reviews/GR-032/README.md`; independent re-review is
  pending. Browser runtime and Seafile version/reopen remain NOT VERIFIED.
* R2/R3 bounded independent reviews returned PROVISIONAL PASS after confirming
  the exact patch includes the new inbox module and documenting this size limit:
  the gateway defaults to 50 MiB, while PhotoCraft
  serializes before handoff, so oversized payloads may allocate before rejection.
  Negative ACK preserves dirty state; peak memory and large-payload compatibility
  remain unverified.

## 2026-10-25 — GR-031 SoundCraft Seafile save and reopen

* In an isolated rootless Podman Seafile stack, a Seahub file-list click opened
  SoundCraft Web/WASM; adding `Audio 2` and pressing Ctrl+S created a new Seafile
  file ID and head. The host confirmed the save, API readback returned 6,877
  bytes, and a fresh Seahub click reopened all three tracks cleanly.
* The final content readback SHA-256, before/after IDs, and screenshots are in
  `docs/reviews/GR-031/`. This is synthetic loopback evidence; exact outbound
  message-byte identity, optimized bundle, deployment security and ONLYOFFICE
  regression remain unverified. Luna High returned a bounded PROVISIONAL PASS
  with minor evidence qualifications; SoundCraft stays out of dispatch. No
  upstream or production change was made.

## 2026-10-25 — GR-030 SoundCraft browser host-save smoke

* Ran the GR-025 host-save adapter in a real Chromium browser with the exact
  GR-025/027/028/029 local overlay sequence. A synthetic host opened a
  `.scraftz`, a UI-created audio track was saved, a matching ACK returned the
  editor to clean, and a fresh iframe reopened the retained bytes with the new
  track. The outbound bytes were hashed and the browser capture/harness were
  recorded in `docs/reviews/GR-030/`.
* The host stored bytes only in JavaScript memory. GR-031 later verifies a
  separate storage-backed flow with a smaller fixture. The 66.2 MB output from
  this specific smoke exceeds the gateway’s 50 MiB default request cap. This
  remains bounded browser protocol evidence, not an MVP or GPT PASS.

## 2026-10-25 — GR-029 SoundCraft egui 0.37 compatibility

* Added local compatibility patches for the pinned `craft-ui` and SoundCraft
  UI code. The full Rust 1.95 locked `soundcraft-web` WASM check now passes with
  GR-025/027/028 and both GR-029 patches applied. The focused GR-025 host-save
  UI test passes 1/1. R2 caught an incorrect lock-patch base; the incremental
  GR-029 lock patch was regenerated from the post-GR-025 state, the full order
  was replayed, and the locked WASM check passed again. Independent Sol low R3
  returned a bounded provisional PASS with no findings. Browser/Seafile E2E is
  still NOT VERIFIED; this slice is GPT REVIEW PENDING.
* This is build compatibility only. Browser behavior, Seafile version creation
  and fresh reopen remain NOT VERIFIED; no upstream or production change.

## 2026-10-25 — GR-028 SoundCraft playback compatibility slice

* Added a local CPAL 0.18.2 compatibility patch for native and WASM playback;
  both target checks and 36 unit tests were rerun successfully in this session.
  Independent R1 found no API-semantic issue but was incomplete because its
  review checkout lacked the SoundCraft base. Full SoundCraft Web WASM initially
  failed because pinned craft-ui used egui 0.36 while SoundCraft uses egui
  0.37; local GR-029 compatibility patches now clear that build blocker.
* Browser, Seafile version/reopen and production behavior remain NOT VERIFIED.

## 2026-10-25 — GR-027 SoundCraft Symphonia compatibility slice

* Added the locked Symphonia 0.6.1 API port without dependency changes. Five
  review rounds remediated marker-scope, ftyp bounds, null-codec selection, and
  zero-padded MP4 preflight findings. Exact R5 review is PROVISIONAL PASS; 57
  audio-io tests and locked audio-io WASM check pass.
* Full SoundCraft Web WASM, browser, and Seafile save/version/reopen remain NOT
  VERIFIED.

## 2026-10-25 — GR-025 SoundCraft host-save prototype review

* Added a ticketed host-save path for one pathless `.scraftz` session. The
  independent review found and the follow-up fixed a local picker/drop route
  that could replace the host-bound session. R2 source review found no new
  blocker/major but did not rerun the UI tests.
* The Web build and UI regression remain blocked by base dependency/API
  mismatches in Symphonia 0.6.1 and CPAL 0.18.2; GR-027/028 track their local
  compatibility work. Browser, Seafile version and fresh reopen are NOT
  VERIFIED. See `docs/reviews/GR-025/`.

## 2026-10-25 — GR-019 FigCraft transport re-pin

* Updated the stored FigCraft host-save patch to pin `craft-platform`
  `56c5e16`. The full patch retains the previously reviewed GR-019 app changes;
  an independent comparison confirmed no new source hunks beyond the manifest
  and lock pin.
* Engine 3/3 and UI 1/1 focused tests, locked Rust 1.95 WASM check, formatting,
  diff and reverse-apply checks pass per implementer. Repin review round 2
  found no new blocker/major; its reviewer did not rerun tests/builds. The known
  minor dirty-report retry issue and lack of browser/Seafile E2E remain. See
  `docs/reviews/GR-019/`.

## 2026-10-25 — GR-018 CADCraft transport re-pin

* Updated the stored CADCraft host-save patch and lockfile to pin
  `craft-platform` `56c5e16`. The CADCraft source behavior is unchanged from the
  previously reviewed GR-018 implementation.
* Three focused engine acknowledgement tests, the locked Rust 1.95 WASM check,
  formatting, diff and reverse-apply checks pass per implementer. Independent
  exact review matched the base/hash/pin and found no blocker/major; it did not
  rerun tests or builds. Browser/Seafile runtime evidence remains the earlier
  synthetic reproduction, not a result of the repin. See `docs/reviews/GR-018/`.

## 2026-10-25 — GR-026 PhotoCraft host integration assessment

* Audited `storytold/photocraft` at exact SHA
  `a02f2ee41059d3312e7ff24a5af5edcac7b6435a`. Stopped without app code
  because `open_file(path, bytes)` binds host names as local paths and the
  browser download writer is intentionally unconfirmed; a safe host path needs
  pathless open, revision-specific ACK and host-mode route guards.
* Recorded the minimal Rust-only design in
  `docs/GR-026-PHOTOCRAFT-HOST-SAVE.md`. No app build/test, browser flow,
  Seafile version/reopen, production access or upstream publication was claimed.
  See `docs/reviews/GR-026/`.

## 2026-10-25 — GR-026 PhotoCraft pathless-open/snapshot-ACK core

* Added a pathless open API and snapshot ACK tied to a unique document-open
  incarnation. The regression closes and reopens the same document ID, then
  verifies the old ACK is rejected and the replacement remains dirty.
* Fixed the patch hunk counts; ordinary `git apply --check` passes on the exact
  pinned base. Four engine tests, the pathless-open UI test, and locked PhotoCraft
  Web WASM check pass. Independent R2 review is PROVISIONAL PASS; its test run
  hit `/tmp` quota. Browser transport and Seafile version/reopen remain
  unverified.

## 2026-10-25 — GR-022 EffectCraft host-save prototype

* Added a one-document host-save adapter using `craft-platform` `56c5e16`.
  Snapshot saves use ticketed durable acknowledgements; host-mode replacement
  and unsupported save routes are refused, and pre-open edits are not silently
  discarded.
* Engine 2/2 and UI 4/4 focused tests, locked Rust 1.95 WASM check, formatting
  and diff checks pass per implementer. Independent exact review found no
  blocker/major, but did not rerun build/tests. Browser/Seafile version and
  fresh-reopen behavior remain NOT VERIFIED; see `docs/reviews/GR-022/`.

# HISTORY

## 2026-10-25 — GR-047 FilmCraft browser host-save smoke

* Built and ran the actual GR-023 patched FilmCraft Web/WASM from source pin
  `fa550ce2d07bdfee6b1d7b6835e8abc8c6913d00` with transport pin
  `56c5e16d79b77751106173c13111ef4fe0a2c0ec`; the regenerated source diff
  matched the stored patch SHA-256.
* Chromium opened a synthetic native `.fcproj`; a visible text edit became
  dirty, Ctrl+S emitted 6,468 bytes, matching `filmcraft:1` ACK cleared dirty,
  and a fresh iframe rendered the saved edit. The parent retained bytes in
  memory only.
* Seafile version creation/readback, dispatcher, production behavior and
  ONLYOFFICE were not exercised. No independent review, commit or upstream
  write was performed. Evidence: `docs/GR-047-FILMCRAFT-WASM-SMOKE.md` and
  `docs/reviews/GR-047/`.

## 2026-10-25 — GR-047 review evidence follow-up

* Independent R1/R2 bounded reviews found no blocker or major issue. R1's
  browser asset evidence gap was addressed with a retained Chromium response
  hash/network transcript and fresh-iframe replay screenshot.
* R2's minor about the distinct pre-packaging WASM hash was addressed by
  verifying the 40,913,852-byte cache artifact and clarifying its distinction
  from the 37,637,092-byte packaged WASM. R3 returned bounded PROVISIONAL PASS
  with no findings; historical continuity with the original build remains
  unverified.
* Seafile version/readback, dispatch, deployment, and ONLYOFFICE remain
  **NOT VERIFIED**; no project-level GPT PASS or upstream permission follows.

## 2026-10-25 — GR-023 FilmCraft host-save prototype

* Added a one-document FilmCraft Web host-save adapter over the shared
  `craft-platform` transport pinned to `56c5e16`. Save/Save All route a captured
  `.fcproj` snapshot through a ticketed host ACK; ordinary downloads and native
  saves remain separate.
* Added host-mode refusals for project-from-template, close-all, save-as-template
  and direct project-close routes. Engine tests 4/4, UI tests 3/3, locked Rust
  1.95 WASM, fmt and diff checks pass. Independent exact review verified the
  final hash and found no blocker/major.
* Browser host messaging, authorization, durable Seafile version creation and
  fresh-storage reopen remain NOT VERIFIED. See `docs/reviews/GR-023/`.

## 2026-10-25 — GR-024 malformed host save acknowledgement handling

* Changed the shared browser transport to ignore `saveResult` messages whose
  `ok` field is absent or not a JavaScript boolean. Valid success/failure ACKs
  keep the same public shape; malformed replies leave app tickets pending so
  the save outcome remains unknown instead of triggering an unsafe retry.
* Added parser coverage for malformed values plus valid `true` and `false`.
  Seven native tests, WASM test-target compilation, 19 package checksums,
  formatting and diff checks pass. Browser execution remains NOT VERIFIED.
* An independent read-only review verified the exact diff and found no
  functional issue; app consumers still need to pin this committed revision.
  See `docs/reviews/GR-024/`.

## 2026-10-25 — GR-020 DeckCraft transport re-pin

* Updated the stored DeckCraft host-save patch to transport commit `56c5e16`;
  app source is unchanged. The locked WASM check, formatting, diff and
  reverse-apply checks pass per implementer. Independent review confirmed the
  exact base, hash and pin. Browser/Seafile runtime remain NOT VERIFIED; see
  `docs/reviews/GR-020/`.

## 2026-10-24 — GR-021 DesignCraft host-save prototype

* Added a local one-document DesignCraft adapter over `craft-platform`
  `91836a9ebad5ffcd8f1966fb4f36dc84387f2cdd`. It opens native `.designcraft`
  bytes without a local path, serializes a captured snapshot, and marks it
  clean only after the matching host ACK. Save As and multi-document flows are
  refused.
* Five focused Rust 1.95 tests, the locked WASM check, formatting and diff checks
  pass. Luna high R3 found no code-level blocker or major and verified the exact
  patch SHA. The known P3 limit is that the 64 MiB outbound cap runs after
  serialization allocates its buffer.
* No browser messaging or Seafile version/reopen test has run, and the patch is
  not in the dispatcher. See `docs/reviews/GR-021/`.
* Re-pinned the stored exact patch to transport commit `56c5e16`; five focused
  tests and the locked WASM check passed again. Independent review confirmed
  only manifest/lock revisions changed from the previously reviewed app code.

## 2026-10-24 — GR-021 cumulative Open admission

* Extended the shared browser transport's pre-copy limits to repeated Open
  messages. A same-origin app runtime allows multiple Opens within a cumulative
  256 MiB and 64-message budget; separate transports/listeners share the same
  accounting. This preserves the existing in-session OpenRequest path while
  bounding repeated large copies and zero-byte message floods.
* Added native cumulative-budget coverage and a WASM shared-state test. Seven
  native tests, the WASM browser-feature test compilation, package checksums,
  formatting and whitespace checks pass. Browser tests were not executed.
* Luna high round 2 found the one-Open attempt broke compatibility; follow-up
  review found per-listener state could be bypassed. The final cumulative
  implementation received bounded PASS in round 4. The app-level GR-021 patch
  still needs repinning and re-review. See
  `docs/reviews/GR-021/TRANSPORT-OPEN-ADMISSION-REVIEW.md`.

## 2026-10-24 — GR-021 shared host-message allocation bounds

* Hardened the shared browser host transport to reject oversized
  ArrayBuffer/Uint8Array payloads before copying and oversized metadata strings
  before Rust conversion. App-specific limits still apply after transport
  admission.
* Added WASM browser tests for oversize rejection and made the package check
  compile those tests. Six native tests, the WASM browser-feature test compile,
  formatting, checksum and whitespace checks pass. The browser tests were not
  executed because no browser runner is installed.
* Independent Luna high review returned bounded PASS. This fixes the P2 raised
  during GR-021 DesignCraft review; the DesignCraft app patch still needs to be
  repinned and re-reviewed. See
  `docs/reviews/GR-021/TRANSPORT-PRECOPY-REVIEW.md`.

## 2026-10-24 — GR-020 DeckCraft host-save acknowledgement prototype

* Added a local DeckCraft Web adapter on the immutable shared `craft-platform`
  transport. Host mode opens one presentation and only clears dirty state after
  a matching durable save acknowledgement for the serialized snapshot.
* Added engine snapshot-acknowledgement tests and synthetic-host UI tests for
  positive/negative ACKs, edits during a pending save, and reopen from saved
  bytes. Rust 1.95 focused tests and the WASM check pass.
* Independent GPT-6 Luna high bounded review returned PASS with no findings on
  the exact current patch. The initial review was followed by a one-line
  Clippy simplification and a second review of the regenerated patch.
  DeckCraft browser messaging and Seafile version/reopen remain NOT VERIFIED;
  no Seafile dispatch, production system, or upstream source changed. The
  `assets`, `layers`, and `wasm` checks pass; full workspace tests did not
  complete, and workspace Clippy is blocked by existing findings in untouched
  crates. See `docs/reviews/GR-020/README.md` and `REVIEW-LUNA-HIGH-R2.md`.

## 2026-10-24 — GR-019 FigCraft shared host-save adapter prototype

* Added a FigCraft Web adapter using the immutable shared `craft-platform`
  transport. The bounded slice opens one pathless `.figcraft` document, sends
  snapshot bytes with a ticket, and clears dirty state only after the matching
  durable host acknowledgement.
* Added engine tests for pathless snapshot acknowledgement, edit-during-save,
  and refusal to acknowledge documents with native filesystem paths; added a
  synthetic-host UI test covering unknown/valid tickets and later edits.
* Rust 1.95 focused tests, WASM compile, clean-base patch applicability,
  formatting and whitespace checks passed. Browser and Seafile runtime remain
  NOT VERIFIED; no dispatch entry, upstream source, or production service was
  changed. See `docs/reviews/GR-019/README.md`.
* Sol low round 1 found two major scope-guard issues and a ready-reporting
  defect. The local remediation blocks those UI routes, fails closed for an
  unexpected extra tab, includes all tabs in dirty reporting, and drops an
  unready bridge; focused tests and WASM checks passed. Round 2 found reachable
  file/version duplication and live-session join paths; those are now being
  blocked and added to the regression test. Rust 1.95 focused UI test and WASM
  check pass on the updated patch. Sol low round 3 returned bounded PASS with
  one minor: failed dirty-state reports are not retried until the state changes.
  Browser and Seafile runtime remain NOT VERIFIED.

## 2026-10-24 — Standalone GR-016 craft-platform source artifact

* Packaged the GR-016 craft-platform snapshot under
  `integration/rust/craft-platform`, preserving the MIT/Apache licenses and
  NOTICE attribution and replacing workspace-inherited Cargo settings with
  explicit standalone metadata.
* Added a lockfile and `scripts/check-craft-platform.sh`; metadata, six native
  tests, and the browser-feature WASM check pass without the `/tmp` checkout.
* WordCraft/GridCraft/PdfCraft/CADCraft app manifests were subsequently pinned
  to this artifact's immutable Git revision; clean-checkout locked WASM builds
  are recorded in the follow-up report. No project GPT verdict or upstream
  readiness changed.
* A bounded independent Sol low review found no blocker/major; its minor
  metadata-lock finding was fixed and the standalone check was rerun. See
  `docs/reviews/GR-016/REVIEW-PORTABLE-CRAFT-PLATFORM-20261024.md`.

## 2026-10-24 — Pin shared transport in four Craft app patches

* Replaced the local `/tmp` dependency in the stored WordCraft, GridCraft,
  PdfCraft, and CADCraft patches with immutable `craft-platform` revision
  `90c261de22ef75c4c7c5c5cd1c712d483be0bbc8`.
* Applied each patch to a clean checkout at its recorded source SHA and passed
  Rust 1.95 WASM `cargo check --locked`. Neither WordCraft nor GridCraft patch
  changes the temporary `wasm-opt=0` setting used for their functional browser
  bundles; optimized bundle performance remains unverified.
* Generated diffs match the stored patch hashes. The report is
  `docs/reviews/GR-016/PORTABLE-APP-PATCHES-20261024.md`. This closes build
  reproducibility for these four patches only; other apps, runtime coverage,
  overall GPT review and upstream readiness remain open/locked.
* GPT-6.1 Sol independently reviewed the follow-up: round 1 found two MINOR
  stale-status/optimizer-scope issues; both were corrected, and round 3 returned
  bounded PASS. See
  `docs/reviews/GR-016/REVIEW-PORTABLE-APP-PATCHES-SOL-LOW-20261024.md`.

## 2026-10-24 — GR-018 CADCraft host-save acknowledgement prototype

* Added a bounded patch for CADCraft Web that sends serialized drawing saves
  with correlation tickets and keeps drawings dirty until the host confirms
  persistence. Failed/stale results preserve newer edits; SaveAs metadata,
  export completion feedback, expiry and undo-to-saved-snapshot state are
  handled.
* Four GPT-6.1 Sol low bounded review rounds remediated the initial wasm clock,
  save lifecycle, expiry, export, queue, and snapshot-baseline findings. The
  final bounded review returned PASS; it is not a project-level GPT verdict.
* Rust 1.95 formatting and wasm32 check pass; eight focused tests and all 344
  CADCraft engine library tests pass. No browser CADCraft runtime or Seafile
  save/version/reopen test was run.
* A standalone `craft-platform` artifact is now packaged in this repository and
  builds without the scratch checkout. The stored patch still awaits a second
  commit to pin that artifact's exact git revision. The overall project GPT
  FAIL and upstream lock remain unchanged. Details: `docs/reviews/GR-018/`.
* Follow-up local Chromium smoke used the built CADCraft WASM and a synthetic
  in-memory host: a real canvas circle edit produced a ticketed 17,504-byte
  save, the host hashed those exact received bytes and acknowledged them, the
  editor became clean, and a fresh iframe reopened the circle. No Seafile
  version was created; optimized wasm-opt output and Seafile persistence remain
  unverified. A second browser run rejected a save, confirmed dirty remained
  true, then accepted a retry. See
  `docs/reviews/GR-018/CADCRAFT-BROWSER-ACK-SMOKE-20261024.md`.
* A subsequent isolated synthetic Seafile run used the real Seahub file list:
  uploading a synthetic DXF fixture, clicking it opened CADCraft Web/WASM,
  adding a circle and Ctrl+S produced a Seafile history entry and new file ID,
  and a fresh Seahub click reopened the circle in a new CADCraft instance.
  Seafile API readback was 17,501 bytes and contained a `CIRCLE` entity. The
  readback hash is recorded, but the exact editor-to-gateway message bytes were
  not captured. The test remained local/synthetic; the shared transport path,
  non-optimized wasm bundle, public deployment and all-app coverage remain open.
  See `docs/reviews/GR-018/CADCRAFT-SEAFILE-E2E-20261024.md`.

## 2026-10-24 — GR-016 shared transport on synthetic Seafile: WordCraft and GridCraft

* Built the pinned GR-016 WordCraft Rust/WASM adapter and exercised it through
  the patched isolated Seahub file route and local Seafile gateway. A real
  browser edit reached WordCraft's host save path, created a new Seafile head,
  file ID and history entry, and was read back as a valid DOCX containing the
  edit. A fresh Seahub file-list open rendered that edit.
* The runtime stack used synthetic data and loopback-only services. The WASM
  optimizer was disabled for this functional run after its `-Oz` pass consumed
  several minutes; the Rust release build itself succeeded. No production
  service, ONLYOFFICE configuration, or upstream repository was changed.
* A separate GridCraft Web/WASM run edited XLSX cell A1, received a durable host
  result, created a new Seafile version, and reopened with the cell edit shown.
  A follow-up changed B2 from 42 to 1337; GridCraft recalculated B3's
  `SUM(B2:B2)` to 1337, saved another Seafile version, and a fresh editor load
  displayed the recalculated value. The returned XLSX remained valid and its
  formula and cached result matched. Exact editor-to-gateway bytes were not
  independently hashed; the optional wasm-opt pass was skipped. Evidence:
  `docs/reviews/GR-016/SEAFILE-GRIDCRAFT-SHARED-TRANSPORT-E2E-20261024.md`.
* A combined bounded Nemotron evidence review returned PROVISIONAL FAIL: it
  accepted the runtime flows but flagged the missing outbound-byte hash,
  untested formula recalculation, and non-optimized bundle. The formula concern
  was then tested and reproduced as described above. Hash-boundary capture and
  optimized-bundle performance remain open. A second bounded independent
  review accepted the updated evidence with minor qualifications; it did not
  change the overall GPT status or establish deployment/upstream readiness.
  See `docs/reviews/GR-016/REVIEW-NEMOTRON-GRIDCRAFT-E2E-R2-20261024.md`.
* Both runs are synthetic/loopback evidence only. Other ArtCraft apps, public
  security controls and overall project GPT status remain open. The DOCX evidence
  is in `docs/reviews/GR-016/SEAFILE-WORDCRAFT-SHARED-TRANSPORT-E2E-20261024.md`.

## 2026-10-24 — GR-017 PdfCraft durable host acknowledgement prototype

* Started a bounded PdfCraft adapter on pinned upstream SHA
  `57e531ccca0047597809748b5cb4276336d6051a`, reusing the GR-016
  `craft-platform` transport from its pinned scratch checkout.
* The adapter now sends ticketed saves and keeps the editor dirty until the host
  returns a durable result. Sol low review round 1 found that drafts could be
  lost, overlapping saves could discard a close callback, and unanswered saves
  could retain capacity indefinitely. The patch now commits form typing before
  stale-generation checks, coalesces/queues same-document requests, expires
  unanswered browser tickets after 120 seconds, bounds retained bytes and
  drops pending snapshots when tabs close. Five native tests and the Rust 1.95
  WASM check pass. A release build hit `/tmp` quota and was stopped while the
  review fixes were applied; it has not yet been rerun.
* At this point no browser runtime, Seafile persistence, new Seafile version,
  or reopen claim was made for this adapter. The initial patch and limits are
  recorded under `docs/reviews/GR-017/`. Project GPT remains FAIL and upstream
  publication remains locked.
* Sol low round 2 found a remaining paragraph line-editor draft loss and
  unbounded coalesced callbacks/forgotten timer closures. The current scratch
  patch commits paragraph drafts before ACK settlement, caps callbacks, and
  clears timer closures on result. Seven native tests, Rust 1.95 WASM check,
  release build and Chromium synthetic-host edit/save/ACK/reopen pass. Sol low
  round 3 found no blocker/major but found a callback-cap bypass through wrapped
  follow-up callbacks. The current scratch patch preserves retained callback
  counts and extends the cap regression test; seven focused native tests and a
  Rust 1.95 WASM check pass. The release/browser smoke predates this
  callback-accounting-only change. Sol low round 4 returned bounded prototype
  PASS (no blocker/major; lifecycle test gap remains minor). Seafile persistence
  remained NOT VERIFIED at that point and the project GPT verdict remained FAIL. The evidence
  bundle and project status were committed and pushed to `main` as `af510c4`.
  Afterwards, Trunk built the exact patch revision and Chromium reproduced the
  form edit → 2,385-byte save → matching ACK → clean → fresh iframe reopen path.
* Follow-up on 2026-10-24 used the patched PdfCraft release WASM with an
  isolated synthetic Seahub/Seafile stack. A PdfCraft text annotation produced
  a new Seafile file ID and history commit; API readback parsed as a valid PDF
  containing the annotation, and a fresh PdfCraft instance rendered it. The
  file was opened by direct Seahub route navigation, not an observed file-list
  click, and the exact outgoing bridge payload was not captured for hash
  comparison. Full IDs, hash, screenshots and limits are in
  `docs/reviews/GR-017/SEAFILE-PDFCRAFT-E2E-20261024.md`. Nemotron Free accepted
  this bounded evidence with minor qualifications and no blocker/major finding;
  see `REVIEW-NEMOTRON-SEAFILE-E2E-R1.md`. Production and upstream repositories
  remain untouched. Project GPT review remains FAIL.
* The separate synthetic-host smoke stores bytes in `sessionStorage` and is not
  Seafile evidence; see `docs/reviews/GR-017/RUNTIME-SMOKE-R4.md`.

## 2026-10-24 — GR-016 app seam inventory and Rust transport prototype

* Consolidated source-only host seam findings for all 13 ArtCraft Web apps in
  `docs/reviews/GR-016/APP-SEAM-AUDITS-20261024.md`. The inventory corrects
  outdated claims about FigCraft `Services`, FilmCraft's page API and
  LightCraft's local photo library. It does not claim runtime save/version/reopen
  support for apps outside the existing WordCraft, GridCraft and VectorCraft
  synthetic Seafile evidence.
* Six slow GLM-5.3-Flash retry lanes were canceled at the user's request; the
  remaining source audits completed through GPT-6 Luna high with concise briefs.
  No upstream repositories or production services were changed.
* Prototyped a shared transport in a scratch `craft-platform` checkout and
  migrated the already-patched WordCraft and GridCraft host adapters to it.
  `cargo test -p craft-platform` (6 tests), its strict clippy and browser-feature
  WASM check passed. WordCraft and GridCraft WASM `cargo check`s passed on their
  pinned source SHAs with a local path dependency. Release bundles and Chromium
  synthetic-host tests now pass for WordCraft and GridCraft: both serialized a
  real editor change, stayed dirty on an explicit host rejection, and reopened
  the acknowledged bytes in a fresh iframe. After review found GridCraft's
  in-app Open still used the browser picker, its adapter was corrected; a Rust
  1.95 release-bundle browser run confirmed Ctrl+O requests a file from the
  parent and reopens the stored `HostAck` edit. The host used `sessionStorage`,
  not Seafile. GridCraft's declared MSRV is raised to 1.95 in the scratch patch
  because its dependency graph already requires 1.95. GPT-6.1 Sol low
  independently returned provisional PASS for the bounded fixes with three
  minor notes in `docs/reviews/GR-016/REVIEW-SOL-LOW-R3.md`. The existing
  project-level GPT-6.1 Sol FAIL and upstream publication lock are unchanged.
* The prototype and audit report are documented in `docs/reviews/GR-016/`.

## 2026-10-24 — GR-016 Seafile Open-request boundary

* Comparing the shared transport with the Seafile gateway found that the new
  `gridcraft:openRequest` had no handler in the single-file host page. The page
  now tells the user to return to Seafile and select another document; it does
  not reuse the active document capability to browse or open another path.
* A T3 Chromium preview with a synthetic same-origin frame verified the message
  and that an existing `dirty=true` state remains dirty. This is UI/protocol
  evidence only, not a Seafile file picker or save E2E.
* `python3 tests/test_gateway_unit.py` passes. The documented Playwright
  protocol test could not run under system Python because Playwright is absent;
  the test now includes the Open-request case for the browser-test environment.

## 2026-10-23 — Common Rust host transport plan clarified

* The Sol low interim review identified the ticket-format mismatch between the
  WordCraft and GridCraft save adapters and recommended extracting a shared
  Rust/WASM transport, then migrating those two different lifecycles first.
* Read-only inspection of `storytold/craft-libs` at
  `f180fc0d35d521c5d18e118c881d3efde1ec1eee` found an existing optional browser
  module in `craft-platform`, but no common host/postMessage transport. The
  RFC now leaves open whether to extend that module or add a focused crate.
* The proposed common JSON ticket is an opaque string echoed unchanged. Local
  WordCraft/GridCraft patches still differed and needed normalization before
  they could be presented as one implementation. The 13-app source audit later
  completed under GR-016; no upstream source was modified or published.

## 2026-10-23 — VectorCraft polling collision guard

* Sol 6.1 low's interim architecture review found a collision risk in the
  VectorCraft host poll's 32-bit fingerprint and corrected an inaccurate claim
  that identical-byte saves were detectable. The host now compares exact byte
  sequences and treats equal output as a no-op, not a save event.
* The focused synthetic Chromium test passes with two distinct, equal-length
  byte strings that collide under the old FNV-1a check; it confirms changed
  bytes reach storage once and unchanged bytes do not create duplicate saves.
* A fresh VectorCraft run in isolated synthetic Seafile passed after the fix:
  695 B editor output was durably versioned, read back byte-identically and
  reopened with the new path; Seafile History showed 695 B → 609 B → 270 B.
  The exact collision pair itself is covered by the synthetic Chromium test.
* Nemotron independently reviewed this bounded exact-byte fix and returned
  PASS for the collision regression and post-fix Seafile evidence. It recorded
  dirty-warning, retry/concurrency, iframe sandbox and CSP gaps. This does not
  change the project-level GPT FAIL.
* Added a synthetic Chromium retry check: VectorCraft's first write is rejected,
  the document remains dirty, the next poll retries the exact edited bytes, and
  unchanged persisted output does not create another write. This closes only
  the retry-test gap; concurrent saves and durable Seafile failure/retry remain
  unverified.

## 2026-10-23 — VectorCraft SVG round-trip in isolated Seafile

* Clicked a synthetic SVG in the isolated Seahub file list, edited it in the
  pinned VectorCraft Web build using its deterministic page API, and saved from
  the editor. Seafile's content ID changed; the History UI showed 270 B and
  609 B versions; gateway readback matched the editor's 609-byte output hash.
* A fresh Seahub click opened a new VectorCraft session that parsed the saved
  pencil path at the expected geometry. Evidence:
  `docs/reviews/GR-012/VECTORCRAFT-SEAFILE-E2E-20261023.md`.
* This is one app-specific runtime proof. VectorCraft uses its private page API,
  so the common host contract is not proven; PdfCraft and the remaining Craft
  apps are still open. Temporary upload/dispatch changes were restored in the
  synthetic container. Production Seafile and ONLYOFFICE were untouched.

## 2026-10-23 — GridCraft saves and reopens through synthetic Seafile

* Reproduced a real Seahub file-list click → patched GridCraft Web/WASM edit →
  Ctrl+S → Seafile committed-head acknowledgement → fresh Seahub click/reopen
  in the isolated synthetic stack. The reopened editor displayed the saved A3
  marker; Seafile readback was a valid XLSX containing that marker and the B3
  formula plus cached value. Full hashes, screenshot and limits are recorded
  in `docs/reviews/GR-010/GRIDCRAFT-SEAFILE-E2E-20261023.md`.
* The XLSX fixture used for that run was missing `xl/styles.xml`, which caused
  a real GridCraft warning. Added a minimal styles part, its workbook
  relationship/content type, and assertions to the fixture check. That new
  fixture was then opened from the Seahub list in a fresh GridCraft session;
  it loaded without the warning. The edited save/reopen sequence has not yet
  been repeated with this corrected fixture.
* This advances GR-010 runtime evidence only. Formula recalculation, GridCraft
  conflict/failure cases, remaining Craft apps, other storage platforms,
  public deployment, and the prior GPT Sol FAIL remain open. Production
  Seafile and upstream repositories were not changed.

## 2026-10-23 — clarified the multi-platform, all-Craft target

* Documented the target as Seafile/Nextcloud/ownCloud adapters feeding one
  platform-neutral Craft host contract and extension dispatcher, then all
  ArtCraft Web editors. Seafile remains the first adapter under test.
* Added an explicit long-term roadmap for adapting all Craft apps according to
  their individual Web/save capabilities. Nextcloud, ownCloud, and full app
  coverage remain unimplemented and unverified; the GridCraft patch is one
  focused fix, not the product scope.

## 2026-10-23 — GridCraft waits for a durable host save result

* Prepared a patch against GridCraft `06920de8da609c19de7446945cfc62b844691efd`.
  Save messages now carry a ticket and the exact immutable workbook snapshot;
  GridCraft marks only that document snapshot clean after a successful host
  `saveResult`. Edits made while saving remain dirty, and PDF/export callbacks
  cannot mark the source workbook clean.
* Added a focused engine test for an older acknowledged snapshot, document
  switching, and a late acknowledgement after close. The test passed, and
  `cargo check -p gridcraft-web --target wasm32-unknown-unknown` passed against
  the pinned checkout. These checks do not prove the patch works in the
  gateway/Seafile browser runtime or that XLSX formulas survive editor reopen.
* Also built the optimized Web artifact and ran it in headless Chromium with a
  synthetic parent/storage. A real cell edit serialized into valid XLSX bytes;
  a failed save result kept GridCraft dirty, and a successful retry result
  cleared it. This tests the editor bridge, not Seafile persistence or formula
  recalculation. Full results and limits are in `docs/reviews/GR-010/README.md`.
* A full `cargo test -p gridcraft-ui-egui` attempt hit the `/tmp` disk quota
  compiling unrelated integration binaries. The two changed callback targets
  were then run individually: `file_menu` 12/12 and `text_box_editing` 4/4.
* The source patch and evidence limits are in `docs/reviews/GR-010/`. GridCraft
  remains one step in the broader goal of connecting all ArtCraft web editors;
  this does not complete or independently review GR-010. No upstream ArtCraft,
  production Seafile, or public service was changed.

## 2026-10-23 — independent review of the GridCraft acknowledgement patch

* Nemotron independently reviewed the eight changed GridCraft files and the
  pinned-source patch: narrow **PASS**, no blocker or major finding.
* Recorded three minor follow-ups: pending-save cleanup if the host vanishes,
  protocol-version negotiation, and a low-risk Save/Save As title race.
* This review does not prove GridCraft→Seafile persistence, version creation,
  formula semantics, or editor reopen. The prior GPT FAIL remains unchanged;
  upstream publication remains locked.

## 2026-10-23 — GR-015 read-only and revoked-save runtime guard

* Added a focused Django URL-level test for the patched save view. It uses the
  actual Seahub route, DRF view, and Seafile permission parser with a valid
  synthetic DOCX. Both a read-only save and a cached edit capability revoked
  from `rw` to `r` returned 403 before update-token minting/fileserver access.
* Recorded the command, result and evidence limits in the GR-015 bundle; the
  cache, user lookup and Seafile RPC permission response are test doubles, so
  live permission-revocation propagation remains unverified.

## 2026-10-23 — concurrent real WordCraft saves

* In the isolated synthetic Seafile/WordCraft stack, opened the same current
  DOCX in two browser sessions, made a separate edit in each actual WordCraft
  editor, then sent Ctrl+S to both concurrently. One save created a new Seafile
  head/file ID and showed `Saved — new version`; the other returned 409 and
  remained dirty.
* Reopened the file by clicking it in the Seahub file list. The fresh WordCraft
  editor rendered the winning edit. Readback through Seafile's file-content
  endpoint confirmed the same current head and included A's phrase, while B's
  phrase was absent. Evidence and screenshot:
  `docs/reviews/GR-015/ISOLATED-RUNTIME-E2E-20261023.md` and
  `docs/reviews/GR-015/concurrent-editor-save-reopen.png`.
* This closes the earlier gap where the simultaneous requests bypassed the
  editor bridge. Same-editor overlapping tickets, Go/stock fileserver behavior,
  permission revocation, production topology and ONLYOFFICE regression remain
  unverified. No production or upstream service was changed; GPT review remains
  FAIL and upstream publication remains locked.

## 2026-10-23 — independent Nemotron review of `a4ecc8e`

* Nemotron reviewed exact SHA `a4ecc8e1d0da44a12f7bd9c4e529ed4accdb4a0e` at
  medium effort and returned FAIL for GPT-candidate readiness. It accepted the
  isolated DOCX E2E and route-token runtime evidence, while retaining blockers
  for ONLYOFFICE regression and major findings for origin separation, permission
  revocation/read-only/expiry, editor-level concurrency, other Craft apps,
  deployment controls and licensing.
* The two-editor concurrent save/reopen test documented above ran after that
  review and addresses its direct-request-only concurrency objection. Nemotron
  has not reviewed the later evidence. Full report:
  `docs/reviews/REVIEW-NEMOTRON-A4ECC8E.md`.

## 2026-10-23 — separate-origin synthetic browser save

* Changed only the isolated synthetic Seahub action URL temporarily to post to
  the loopback gateway on port 18777, distinct from Seahub on port 18000. The
  browser loaded the real WordCraft Web/WASM editor; Chromium enforced the
  cross-origin boundary between Seahub and its editor frame.
* Typed `OriginCheck`, pressed Ctrl+S, and verified a 200 save response, a new
  Seafile file ID/head, and a six-entry history. After reloading the file route,
  Seafile readback returned a 5,351-byte DOCX containing `OriginCheck` and the
  earlier winning edit, with the losing edit absent. The temporary Seahub
  setting was restored and the synthetic service restarted.
* The editor's visible clean indicator was not captured in this follow-up;
  production proxy/TLS/CSP/CSRF, ONLYOFFICE regression and authorization edge
  cases remain open. No production or upstream service was changed. GPT review
  remains FAIL and upstream remains locked. Evidence:
  `docs/reviews/GR-015/ISOLATED-RUNTIME-E2E-20261023.md`.

## 2026-10-23 — independent review of separate-origin evidence

* Nemotron reviewed exact SHA
  `36c0bc0f2b534b34c52193519fbb422ac5c22948` and returned FAIL for candidate
  readiness. It accepted the separate-origin synthetic handoff and persistent
  DOCX evidence, while keeping ONLYOFFICE preservation, authorization edge
  cases, production security topology, unsupported fileserver behavior,
  GridCraft/VectorCraft semantic saves, and licensing open. Full report:
  `docs/reviews/REVIEW-NEMOTRON-36C0BC0.md`.
* After the review, another fresh gateway session saved `AckConfirmed` and
  reported `Saved — new version`, `dirty=false`, and `confirmedSave=true`.
  A subsequent Seafile-backed WordCraft document fetch returned a valid DOCX
  whose XML contained `AckConfirmed`, `OriginCheck`, and the winning edit, and
  omitted the losing edit. This improves local DOCX evidence but does not close
  the review findings or make this tip a GPT candidate.
* A runtime guard also called the patched Seahub view with synthetic storage
  and ONLYOFFICE response doubles: allow-listed DOCX selected ArtCraft, and
  non-allow-listed DOCX selected the existing ONLYOFFICE view template. This
  confirms dispatch fallback only; Document Server save preservation is still
  unverified. Reproduction: `tests/test_gr015_dispatch.py`.

## 2026-10-23 — isolated Seafile/WordCraft runtime E2E and conditional race

* Starting from local tip `7f828a4c58f49de247ac71bc66e58d2f41bfa230`, applied
  the recorded GR-015 patches to the exact pinned Seahub and Seafile Server
  sources, built the C server, ran Django checks/migrations, and started the
  stack in a rootless Podman container. No production guest or upstream repo
  was modified.
* The synthetic Seahub file-list click opened the actual WordCraft Web/WASM
  build. A real UI text edit was saved; the editor reported `Saved — new
  version` after the patched server committed a new head/file ID. Independent
  content readback confirmed a valid DOCX with the sentence in document XML.
  Navigating away and clicking the file again created a new WordCraft session
  that rendered the saved sentence. Full values and limits are recorded in
  `docs/reviews/GR-015/ISOLATED-RUNTIME-E2E-20261023.md`.
* A stale second WordCraft session received 409 and remained dirty. A separate
  pair of concurrent HTTP saves through the same Seahub view and C conditional
  route returned one 200 and one 409. Seafile history advanced to one winning
  head; a fresh WordCraft open rendered Writer A's paragraph, with Writer B's
  paragraph absent. This tests the actual patched runtime, but the two direct
  race requests were not concurrent keystroke-driven editor saves.
* Runtime token test: `op=update` passed the existing header hook on
  `update-conditional-api`; an `op=view` token was rejected with HTTP 403.
  This resolves the narrow route-prefix behavior, not the remaining Sol review
  findings.
* The browser used a test-only same-origin loopback reverse proxy. This proved
  the local functional flow while leaving the intended separated-origin
  security topology unverified. ONLYOFFICE regression, permissions/revocation,
  unsupported Go/stock server behavior, and other Craft apps remain open.
  The current worktree tip is not frozen or reviewed; GPT remains FAIL and
  upstream remains locked.

## 2026-10-23 — Sol re-review of 0edbe52 and route-token remediation

* GPT-6.1 Sol reviewed exact SHA
  `0edbe524b4fa321b0f73f8601afef390e7f785e6` at medium effort/default tier and
  returned **FAIL**. Full report: `docs/reviews/GPT-SOL-REREVIEW-0EDBE52.md`.
* Sol independently found the dedicated C path `conditional-update-api` did not
  begin with `update`, while the existing `upload_headers_cb` passes the first
  path component to `check_access_token`, which enforces the `op=update` prefix.
  Thus the proposed save route would reject the minted update token before the
  conditional handler. The route is now named `update-conditional-api`, keeping
  the route distinct while preserving the existing operation check. The GR-015
  source harness passes against pinned Seahub/Seafile sources with both patches
  applied, and both patches pass applicability checks. The harness confirms the
  route begins with `update` and the existing hook still enforces the token
  operation; it is source-level evidence, not actual hook execution. C/Django
  runtime behavior remains **NOT VERIFIED**.
* The GR-006 historical free-model “VERIFIED END-TO-END” claim is explicitly
  marked superseded, and the RFC now documents the browser-mediated capability
  handoff to the gateway. These changes correct claims; they do not add Seafile
  E2E evidence.
* System Python has no Playwright module and the prior temporary Playwright
  environment is gone, so the host/WordCraft/VectorCraft Chromium suites could
  not be rerun during this pass. Gateway unit, SVG assertion, XLSX fixture,
  Python compilation, patch applicability and GR-015 source checks were rerun;
  no production files were altered.
* Blockers remain: real Seafile DOCX version/reopen and ONLYOFFICE regression are
  unverified. Public deployment and upstream publication remain locked.

* A bounded, independent Nemotron review returned **PASS for the route-prefix
  finding only**. It confirmed that `update-conditional-api` preserves the
  existing token-operation check. The reviewer classified the evidence as
  static/source-only; no C/Django/runtime behavior was tested. See
  `docs/reviews/GR-015/ROUTE-TOKEN-REVIEW.md`.
* The exact patched Seafile Server 12.0.14 source was subsequently configured
  and built in an isolated `/tmp` tree. `server/upload-file.o` compiled and
  `make -C server -j2` linked the complete fileserver subproject successfully.
  An earlier apparent build PASS was discarded after a source-tree check showed
  it had built the clean upstream base without the patch; both exact GR-015
  patches were then applied and the build repeated successfully.
  The workstation's `libjwt` 3.2.3 API is incompatible with this Seafile source,
  so `libjwt` 1.18.4 was built from its upstream tag into `/tmp`; Seafile's other
  missing build dependencies were staged under `/tmp` as well. GNU C11 flags
  were needed for this older source's callback signatures with the current GCC.
  This establishes compile/link only: the binary was not installed or run, and
  no HTTP route, token hook, Django flow, race, or save was exercised. The
  earlier “configure stopped/no C compilation” row below is superseded by this
  result.

### Reproduction record for the local route remediation

Reviewed base SHA: `0edbe524b4fa321b0f73f8601afef390e7f785e6`. The commands below
ran on 2026-10-23 against the working tree after that SHA; the source clones
were pinned to the Seahub and Seafile SHAs listed in `docs/reviews/GR-015/README.md`.

| Command | Exit | What it establishes |
| --- | ---: | --- |
| `env ARTCRAFT_SEAHUB_SOURCE=/tmp/artcraft-seahub-sol-next ARTCRAFT_SEAFILE_SERVER_SOURCE=/tmp/artcraft-seafile-server-sol-next python3 tests/test_gr015_authorization.py` | 0 | Synthetic helper checks plus source assertions for the update token, route, callback, path operation extraction and existing prefix check; no C/Django runtime |
| `python3 tests/test_gateway_unit.py` | 0 | Gateway tests against fake upstream/CAS; not real Seafile |
| `python3 tests/test_gr012_svg_assertions.py` | 0 | Offline SVG assertion unit checks; not an editor/Seafile round trip |
| `python3 tests/test_xlsx_fixture.py` | 0 | Fixture has a formula element and cached value; no GridCraft recalculation/reopen |
| `python3 -m py_compile integration/gateway/*.py tests/*.py tests/fixtures/make_fixtures.py` | 0 | Python syntax only |
| `git diff --check` plus pinned-source `git apply --check` for each GR-015 patch | 0 | Whitespace and applicability against clean source trees; no build/runtime |
| `python3 tests/test_gr012_svg.py` without its required Seafile URL/token, gateway, repository and path | 2 | Not run; the script printed its invocation and stopped |
| `python3 tests/test_gr010_xlsx.py` | 2 | Not run; no such test file exists (`tests/test_xlsx_fixture.py` is the fixture check) |
| `./autogen.sh && ./configure --disable-fuse --disable-python --enable-httpserver` in the pinned patched Seafile Server clone, after staging its build dependencies under `/tmp` | 0 | Configure passed; `intltoolize` was unavailable but `autogen.sh` continued and generated the configure script |
| `make -C lib libseafile_common.la` and `make -C common/cdc libcdc.la` with temporary dependency paths | 0 | Built required local static dependencies in the pinned source clone |
| `git apply --check` then `git apply` for both GR-015 patches on the pinned Seahub and Seafile Server clones | 0 | Confirms both exact patch artifacts apply to the recorded upstream source commits; the Seafile Server worktree contains the patch during the build below |
| `make -C server -j2` with `CPPFLAGS` for staged libjwt/libsearpc/evhtp headers, `CFLAGS='-std=gnu11 -g -O2'`, and temporary `LDFLAGS`/runtime library paths | 0 | Rebuilt and linked the complete fileserver subproject, including patched `upload-file.c`, against the pinned patched source; not runtime or integration evidence |
| `env ARTCRAFT_SEAHUB_SOURCE=/tmp/artcraft-seahub-sol-next ARTCRAFT_SEAFILE_SERVER_SOURCE=/tmp/artcraft-seafile-server-sol-next python3 tests/test_gr015_authorization.py` after applying both patches | 0 | Synthetic decorator/helper execution and route source assertions against the exact patched sources; Django and C request runtime remain untested |
| `python3 tests/test_gateway_unit.py` | 0 | All gateway unit checks passed, including malformed-response redaction and fake concurrent CAS; upstream is simulated |
| `python3 tests/test_gr012_svg_assertions.py && python3 tests/test_xlsx_fixture.py` | 0 | SVG false-positive checks and OOXML formula fixture check passed; no editor or Seafile persistence |
| `python3 -m py_compile integration/gateway/*.py tests/*.py tests/fixtures/make_fixtures.py && git diff --check` | 0 | Python syntax and whitespace checks passed |

Environment: Python 3 on the local workstation; Playwright is unavailable in the
system Python and the old temporary browser-test environment is absent. No
production service or upstream artifact was changed. These checks do not resolve
Sol's real-Seafile E2E blocker.

## 2026-10-23 — Sol final re-review and focused remediation (local only)

* GPT-6.1 Sol reviewed exact candidate
  `afec19e63a6a4faec8a94f93651363dbe007e526` and returned **FAIL**. The full
  findings are preserved in `docs/reviews/GPT-SOL-REREVIEW-AFEC19E.md`; the
  previous `d9ef476e` FAIL remains unchanged.
* The confirmed overlapping-save defect now rejects a second host save while
  another is in flight. The Chromium protocol test proves the first save's
  acknowledgement cannot clear the later dirty revision; retry succeeds after
  the first save completes.
* Gateway save errors no longer expose arbitrary upstream bodies, and document
  downloads are bounded while reading. Unit tests cover a malformed HTTP-200
  page echoing the capability URL and an oversized content response.
* `POST /open/` now accepts a foreign Origin only when it matches configured
  `ARTCRAFT_SEAFILE_ORIGIN`; session mutations remain gateway-origin-only. The
  deployment docs now require Seahub and ArtCraft to be separate origins.
* GR-015 draft patches now scope save capabilities to the ArtCraft audience,
  original edit grant, repo allowlist and extension. Seahub uses a distinct
  `conditional-update-api` route exposed only by the proposed C patch; stock/Go
  route absence and source patches are checked, but binaries are not built or
  runtime-tested.
* SVG/XLSX evidence was corrected. The old GR-010/GR-012 PASS claims are marked
  superseded; the XLSX fixture now has a real `<f>` formula element. The local
  VectorCraft web bundle edited and reopened the expected pencil stroke in a
  browser (270 → 609 bytes); this is local editor evidence, not Seafile E2E.
* Reproduced local checks: `tests/test_gateway_unit.py`,
  `tests/test_hostpage_protocol.py`, `tests/test_gr015_authorization.py`,
  `tests/test_wordcraft_host_roundtrip.py`, `tests/test_gr012_svg_assertions.py`,
  `tests/test_vectorcraft_svg_local.py`, `tests/test_xlsx_fixture.py`, Python
  compilation, and both patch-application checks pass. `git diff --check` exits 2
  because the generated server patch contains one unified-diff context line
  flagged as trailing whitespace; patch applicability passes.
  `tests/test_integration.py` was not run because no Seafile URL/token, editor
  capability, or isolated patched Seafile deployment is available in the shell.
* No production Seafile, Proxmox service, ONLYOFFICE, or upstream repository was
  modified. Public deployment and upstream publication remain locked. A fresh
  Sol review is required on the new exact candidate SHA.

## 2026-10-22 — GPT-6.1 Sol remediation (local only)

The unauthenticated direct `/open` route was closed. Token sessions are writable
only with an explicit user-bound authorization hook, and saves require an
atomic upstream CAS hook; the stock Seafile client therefore fails closed.
WordCraft saves now carry and validate the original filename/type, with Save As
and PDF export rejected. Deterministic unit coverage was added for the CAS race
and refusal paths. The real Seafile Web DOCX and ONLYOFFICE checks remain
**NOT VERIFIED**. Evidence: `docs/reviews/GPT-LUNA-REMEDIATION.md`.

Running log. Newest first.


## 2026-10-22 — the fourth review, and the GR-012 proof hardened

* **REVIEW-04 (Nemotron) on GR-012: FAIL, remediated.** Four blockers, all right:
  the "document really changed" assertion compared the *length* of a
  `document.inspect` snapshot instead of the content; the save poll compared
  *sizes*, so an identical re-save was invisible; there was no `beforeunload`
  guard and no dirty state for VectorCraft; and `dispatch.json` claimed
  `?host=parent` for an application that does not speak it.
* The initial fixes: the test now reads the **bytes the editor produced** and
  asserts they differ from the original and form a valid SVG with a path
  element; the poll compared a **content fingerprint** and only a *stored* save
  became the new baseline; the host page warned on unload while a save was in flight; the
  dispatch entry no longer claims a contract VectorCraft does not implement; the
  adapter verifies the frame's **origin** before it drives it.
  A later Sol low review found the 32-bit fingerprint could collide; it has
  since been replaced by exact byte comparison (see the 2026-10-23 entry at the
  top of this file).
* Two bugs the remediation itself found: `api.readFile` is **synchronous** (it
  throws, it does not return a promise), and VectorCraft's SVG export writes a
  rectangle as a `<path>`, so an assertion looking for `<rect>` failed on a
  correct file.
* Final GR-012 run: **12/12 PASS**, including the strongest check — the bytes
  Seafile holds are **byte-identical** to what the editor produced.
* **GR-010** bundle written: the `.xlsx` round-trip, distinct from GR-005 (the
  mechanism) by being about the format and its conflict behaviour.
* The unit check on the dispatch table was corrected to match the truth: only
  the applications that speak the bridge name `?host=parent` in their URL.
* The architect sub-agent timed out a **second** time (GR-003), after cloning and
  reading all fourteen repositories for hours. Both GR-001 and GR-003 had already
  been completed independently by the owner, so nothing was lost. The lesson is
  recorded in `docs/AI-ROUTING.md`: a very long research brief is a bad fit for a
  single sub-agent call; research is now split into bounded questions, and the
  owner's own verification is the primary path.

## 2026-10-22 — GR-012, and the owner model retired mid-flight

* **GR-012** — proved a **non-Office** round-trip: an SVG opened from Seafile in
  **VectorCraft Web**, modified with the editor's own pencil tool in the browser,
  saved, and Seafile recorded a **new version**; the document reopened with the
  edit. `docs/reviews/GR-012/`.
* The first attempt (PdfCraft/PDF) **failed**, and the failure was the finding:
  the application was never dirty, so the Save handed the gateway unchanged bytes
  and the file server correctly created no new version. The lesson is that the
  modification must be driven deterministically, not by guessing where to click.
* VectorCraft was chosen because it exposes its own page API
  (`window.vectorcraft`), which is deterministic end to end. The host page gained
  a **second transport adapter** for it, documented as a gap in the common
  contract (VectorCraft has no `?host=parent` bridge).
* **The owner model was retired mid-flight**: MiniMax M3.1 Flash (free,
  OpenRouter) lost its endpoint during GR-012. The owner role moved to
  **GLM-5.3-Flash (thinking)**; no work was redone and no file rewritten — the
  state was reconstituted from `STATUS.md`, `HISTORY.md`, the GR queue,
  `docs/reviews/` and `git log`. `docs/AI-ROUTING.md` has the incident entry.
* `scripts/install-agents.sh` had a real bug, found while reinstalling: with
  `XDG_CONFIG_HOME` set it installed the agents to `~/.config/agents/` instead of
  `~/.config/opencode/agents/`. Fixed; the routing was verified through
  `/api/agent` afterwards.

## 2026-10-22 — Phases 1-6: research, the contract, and a working proof

* **GR-001** — read the *deployed* Seafile 12.0.14 Professional instance (read-only
  over SSH) and mapped the ONLYOFFICE contract exactly: the doc key, the token
  set, the callback statuses, the update call, the lock, and the fact that
  **the save is unconditional**. `docs/reviews/GR-001/DEPLOYED-INSTANCE-CONTRACT.md`.
* **GR-002** — found that Seafile already ships a **generic, configuration-only**
  third-party-editor hook (`seahub/thirdparty_editor/`), in the open-source upstream
  *and* in the Professional build. Established the shadowing problem (it wins over
  ONLYOFFICE per extension) and the read-only nature of the hook.
  `docs/SEAFILE-INTEGRATION-POINTS.md`.
* **GR-003** — **all 13 ArtCraft apps have a browser build**, and **3 of them
  already ship a `?host=parent` postMessage bridge** (GridCraft, PdfCraft,
  CADCraft) with a consistent vocabulary and a correct security model. The
  baseline audit was about the desktop packages and was silent about this.
  `docs/ARTCRAFT-WEB-CAPABILITIES.md`.
* **GR-004** — the host contract is the *existing* bridge, generalised, with one
  addition: the host must be able to tell the app how a save ended.
  `docs/HOST-CONTRACT.md`.
* **GR-008** — Seafile's file server has **no** compare-and-swap (`last_modify`
  only stamps the mtime; `head` is not a guard), so the conflict check is ours:
  compare the content id at save time. `docs/reviews/GR-008/`.
* **GR-005** — built the gateway (`integration/gateway/`), enabled the hook for
  **one extension that ONLYOFFICE does not claim and no real file uses** (`.xlsx`),
  and proved the whole flow **in a real browser**: GridCraft opened the Seafile
  workbook, the test edited a cell, the editor's own Ctrl+S produced the bytes, and
  Seafile created a **new version** containing the edit. Screenshot in
  `docs/reviews/GR-005/browser-proof.png`.
* **Two independent free reviews** (Nemotron), both **FAIL**, both remediated:
  `docs/reviews/REVIEW-01.md`, `docs/reviews/REVIEW-02.md`. The first caught a wrong
  generalisation about the save confirmation; the second caught a symlink escape, a
  TOCTOU window, a missing save answer, an account token leaking to the file
  server, and a dead dispatch entry.
* **GR-014** — wrote the **WordCraft `?host=parent` bridge** (the patch that
  unblocks the DOCX MVP) and it compiles. `docs/reviews/GR-014/DIFF.patch`.

### Decisions

| # | Decision | Rationale |
| --- | --- | --- |
| D-005 | The first proof uses **GridCraft + `.xlsx`** | `.xlsx` is in no other library and is not claimed by the deployed ONLYOFFICE configuration, so claiming it has **zero** blast radius; and GridCraft already ships the bridge, so no application had to be changed |
| D-006 | The first proof runs against the **existing instance**, not a new one | the change is one extension in one dict, backed up, with a documented rollback, and it touches nothing else |
| D-007 | The gateway **writes with its own credential** (option B) for the MVP | it needs no Seafile code change at all; the price — the version is attributed to the service account — is stated prominently, and the upstream patch (option A) is the production answer |
| D-008 | The host contract is the **existing `?host=parent` bridge**, not VectorCraft's `window.vectorcraft` API | the bridge is the shape a host platform needs; the page API is an automation surface with a much larger security cost |
| D-009 | The upstream patch is **one new file in `apps/wordcraft-web/`** | the smallest change that unblocks the MVP, and an alignment with the three apps that already have the bridge — not a new idea and not a multi-repo PR |
| D-010 | The browser test is part of the test suite, not a nicety | it found three real bugs the HTTP test could not see, including a JavaScript `ReferenceError` that left the page dead |

## 2026-10-22 — Phase 0: bootstrap

* Inspected the OpenCode installation (v2.1.0, V2 agent format: Markdown with
  YAML frontmatter under `~/.config/opencode/agents/<name>.md`, `mode:
  primary|subagent|all`, `model: provider/model#variant`).
* Discovered the **exact** model IDs available in this environment and recorded
  them in `docs/AI-ROUTING.md`.
* Created the five project agents and smoke-tested every one of them. All mapped
  to their expected model. `artcraft-deepseek-worker` timed out on the first
  attempt and succeeded on the second — recorded as a flakiness warning.
* Created the public repository skeleton, dual license, `AGENTS.md`, `README.md`,
  `STATUS.md`, `ROADMAP.md`.
* Read `~/ArtCraft-Audit.md` as baseline input evidence. It reports the 13 apps
  are **Rust-only, native egui/eframe + wgpu, explicitly not Tauri/Electron/webview**,
  and that the CI gate includes a `wasm` check. The Web/WASM story must be
  re-verified specifically for this project (GR-003).
* Located the Seafile reference host: `svc-seafile-host.tailb64fb1.ts.net`.
  No local Seafile/Docker runtime on this workstation. No production change made.

### Decisions

| # | Decision | Rationale |
| --- | --- | --- |
| D-001 | Agents are installed **globally** in `~/.config/opencode/agents/`, with the canonical copies versioned in `config/opencode/agents/` | Routing must work in every session, including ones started outside the project directory. `scripts/install-agents.sh` keeps the two in sync. |
| D-002 | Project-local `.opencode/agents/` is **not** used | It would shadow the global definitions and create two sources of truth. |
| D-003 | A reviewer's verdict is only `PROVISIONAL` until GPT passes | Hard gate required by the mission; free-model verdicts are not final. |
| D-004 | The Seafile test bed is the remote server, with a synthetic library | Production data and personal files must not be cloned into the project. |
