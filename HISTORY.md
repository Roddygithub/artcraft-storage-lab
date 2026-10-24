# HISTORY

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
* The patch still references `craft-platform` through an absolute `/tmp` path.
  The transport must become a pinned distributable dependency before the patch
  is portable or publishable. The overall project GPT FAIL and upstream lock
  remain unchanged. Details: `docs/reviews/GR-018/`.

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
