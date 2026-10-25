# GPT Review Queue

Every work item in this project ends here. GPT performs an **independent** review
and does not trust the free-model verdicts.

Nothing may be published upstream (issue, PR, RFC in `storytold/*`, Seafile or
Seafile docs) before an entry reaches `GPT REVIEW PASS`.

## Latest first-pass result — 2026-10-25

```text
Candidate: 95d89835b2b1d06fd098c586469ed03b8fd0549e
Reviewer: GPT-6.1 Sol (low)
Verdict: INCOMPLETE — GPT REVIEW PASS not granted
Report: docs/reviews/GPT-FIRST-PASS-95D8983.md
Synthetic DOCX MVP: demonstrated on isolated patched Seafile C-fileserver stack
Open gates: ONLYOFFICE regression, security/authorization cases, server compatibility,
            pinned editor assets/protocol check, distribution/licensing decision
Upstream publication: LOCKED
```

This result supersedes the old “no Seafile E2E” objection for the candidate's
remediation evidence; it does not erase the historical FAIL on `0edbe52` or
establish production readiness. The current test matrix corrects the stale
GridCraft formula-recalculation entries based on the later GR-016 runtime report.

## Latest candidate result — 2026-10-23

```text
Candidate: 0edbe524b4fa321b0f73f8601afef390e7f785e6
Reviewer: GPT-6.1 Sol
Verdict: FAIL
Report: docs/reviews/GPT-SOL-REREVIEW-0EDBE52.md
Prototype at review time: operator-only investigation; local DOCX E2E remediation is recorded below and awaits review
Public deployment: NOT READY
Upstream RFC/patch: NOT READY
Upstream publication: LOCKED
```

The failed candidate remains immutable. At review time, Sol found a defect in
the conditional route name: it did not satisfy Seafile's existing `op=update`
prefix check. Commit `0da898f` renames the route. Later isolated runtime work
verified the header hook and DOCX E2E; that work is recorded below and does not
change the reviewed candidate's verdict. Earlier failures remain in their
separate reports. The current worktree is not yet frozen or reviewed.

## Remediation evidence — 2026-10-23

An independent Nemotron review of exact SHA
`a4ecc8e1d0da44a12f7bd9c4e529ed4accdb4a0e` returned **FAIL for candidate
readiness**. It accepted the isolated DOCX click/edit/save/reopen and route-token
runtime evidence, but found ONLYOFFICE regression still unverified and retained
major findings for production origins, authorization edge cases, editor-level
concurrency, other Crafts, security controls and licensing. The two-real-editor
concurrency result below was reproduced after this review and has not itself
been independently reviewed. Full report:
`docs/reviews/REVIEW-NEMOTRON-A4ECC8E.md`.

After the reviewed `0edbe52` SHA, the exact pinned GR-015 Seahub and C server
patches were applied and run in a synthetic rootless Podman environment. Django
checks/migrations and the patched fileserver startup passed. The real synthetic
Seahub file-list click opened WordCraft Web/WASM; a text edit was saved, the
fileserver committed a new head/file ID, WordCraft confirmed success, and a
fresh Seafile click reopened the edit. A simultaneous pair of conditional
Seahub save requests produced one HTTP 200 and one HTTP 409; a fresh WordCraft
open showed the winning paragraph only. A further race used two actual
WordCraft editors: both made different edits and sent Ctrl+S concurrently. One
created a new version; the other remained dirty with HTTP 409. A fresh Seahub
click/reopen rendered only the winner. Detailed evidence and limits are in
`docs/reviews/GR-015/ISOLATED-RUNTIME-E2E-20261023.md`.

This is remediation evidence on the current local tip, not a new frozen GPT
candidate and not a Sol PASS. The initial browser test used a same-origin
loopback proxy; a follow-up on separate Seahub and gateway/Craft loopback origins
verified a WordCraft edit, durable save, and persisted content after a fresh
route load. Production TLS/proxy/CSP/CSRF, adversarial-frame isolation,
ONLYOFFICE regression, live read-only/revocation propagation, unsupported stock/Go
fileserver behavior, and the other Craft apps remain unverified. Public
deployment and upstream publication remain locked.

Nemotron independently reviewed the separate-origin evidence at exact SHA
`36c0bc0f2b534b34c52193519fbb422ac5c22948` and returned **FAIL for candidate
readiness**. It accepted the separate-origin browser handoff and durable-save
evidence but retained findings for ONLYOFFICE preservation, authorization edge
cases, production security topology, unsupported fileserver behavior, other
Crafts, concurrency windows, and licensing. After that review, a fresh gateway
session exposed `Saved — new version` with `confirmedSave=true`; the next fresh
Seafile-backed WordCraft load read a DOCX containing the edit. This is added
prototype evidence, not a new immutable candidate or independent review. Full
report: `docs/reviews/REVIEW-NEMOTRON-36C0BC0.md`.
The exact patched Seahub handler was also exercised with synthetic storage and
an ONLYOFFICE response double: allow-listed DOCX selected ArtCraft, while a
non-allow-listed DOCX selected Seahub's existing ONLYOFFICE template. This is
a routing guard only; Document Server edit/save/version/reopen remains untested.

A further isolated Django runtime check posts a valid synthetic DOCX through the
actual patched `thirdparty-editor/file-save` URL. A read-only permission and an
edit capability whose current permission changed from `rw` to `r` both returned
403 before update-token minting or fileserver transport. The test uses synthetic
Seafile RPC/cache/user dependencies; live revocation propagation and persisted
state remain NOT VERIFIED. See `tests/test_gr015_save_authorization_runtime.py`
and the GR-015 isolated runtime evidence.

## Queue

### GR-001 — Seafile online-editor integration contract

```text
Status:     GPT REVIEW FAIL (Sol); remediation pending re-review
Owner:      artcraft-owner
Reviewer:   artcraft-reviewer (free pass) -> GPT (final)

Branch:     main
SHA:        (filled at freeze time)

Requirements:  Document the real, current Seafile <-> ONLYOFFICE online-editor
               integration and extract the abstract contract Seafile expects from
               an external web editor. Every claim evidenced by Seafile source
               code (file:line) or public documentation.
Decision:       The contract is documented from the DEPLOYED instance (12.0.14 Pro),
               not only from upstream: the doc key, the three tokens, the callback
               statuses, the update call, the lock, and the fact that the save is
               UNCONDITIONAL. A generic, configuration-only third-party-editor hook
               exists upstream AND in Pro.
Files:          docs/reviews/GR-001/DEPLOYED-INSTANCE-CONTRACT.md
Tests:          Documentation review + citation spot-check; no runtime code.
Free review:    FAIL -> remediated (REVIEW-01 F1, F6, F8)
Evidence:       the deployed files, read over SSH, read-only
Known risks:    The ONLYOFFICE path is hardcoded per suite id; the generic hook
                is read-only by design.
```

### GR-002 — Seafile integration point

```text
Status:     GPT REVIEW PENDING
Owner:      artcraft-owner
Reviewer:   artcraft-reviewer (free pass) -> GPT (final)

Branch/SHA: (filled at freeze time)

Requirements:  Choose and justify the best insertion point for a third-party
               web editor (extension/plugin, custom online editor registration,
               external editing service, iframe host page, small integration
               gateway, or upstream patch). Answer the 10 questions of the
               mission, including "can we avoid a permanent fork of Seafile?"
Decision:       (filled at freeze time)
Files:          docs/SEAFILE-INTEGRATION-POINTS.md
Tests:          (filled at freeze time)
Free review:    FAIL -> remediated (REVIEW-01 F2, F5, F7)
Evidence:       docs/SEAFILE-INTEGRATION-POINTS.md; the deployed instance; the
                upstream seahub tree
Known risks:    The hook SHADOWS ONLYOFFICE per extension; the write is
                attributed to the service account, not the user; share links are
                not covered.
```

### GR-003 — ArtCraft Web capability matrix

```text
Status:     GPT REVIEW PENDING
Owner:      artcraft-owner
Reviewer:   artcraft-reviewer (free pass) -> GPT (final)

Branch/SHA: (filled at freeze time)

Requirements:  A verified verdict, per Craft app, on: web build, WASM, host
               bridge, programmatic open, programmatic save, iframe safety, origin
               requirements, browser limitations, maturity. The 13 apps must NOT
               be assumed equivalent.
Decision:       (filled at freeze time)
Files:          docs/ARTCRAFT-WEB-CAPABILITIES.md
Tests:          (filled at freeze time)
Free review:    FAIL -> remediated (REVIEW-01 F4)
Evidence:       docs/ARTCRAFT-WEB-CAPABILITIES.md, docs/reviews/GR-003/WEB-BUILD-SURVEY.md
Known risks:    All 13 apps HAVE a browser build; only 3 have a host bridge; the
                13 are NOT equivalent in their services seam. The baseline audit
                was about the desktop packages and was silent about the web ones.
```

### GR-004 — Common Craft Web Host Contract

```text
Status:     GPT REVIEW PENDING
Branch/SHA: (filled at freeze time)

Requirements:  A reusable, storage-agnostic host contract for embedding Craft
               web editors, reusing existing ArtCraft conventions where they
               exist. Must not embed Seafile concepts in the Craft side.
Decision/Files/Tests/Free review/Evidence/Known risks: (filled at freeze time)
```

### GR-005 — First host-integration technical proof

```text
Status:     GPT REVIEW FAIL (Sol); gateway simulation is not Seafile E2E
Branch/SHA: (filled at freeze time)

Requirements:  Smallest end-to-end proof: Seafile host -> Craft Web -> open ->
               edit -> save -> new Seafile version. Mocks allowed as intermediate
               steps, never as final evidence.
Decision:       GridCraft + .xlsx: .xlsx is in no other library and is not claimed
               by the deployed ONLYOFFICE configuration, so claiming it has ZERO
               blast radius; and GridCraft already ships the bridge, so no
               application had to be changed.
Files:          integration/gateway/, docs/reviews/GR-005/
Tests:          tests/test_integration.py (20 checks) + tests/test_browser.py
Free review:    FAIL -> remediated (REVIEW-02 G1, G4, G5, G6, G8, G9, G10)
Evidence:       docs/reviews/GR-005/ (with browser-proof.png)
Known risks:    The original service-account write path is closed; stock
                Seafile lacks user-bound authorization and atomic CAS, so the
                gateway is read-only until the upstream endpoint exists.
```

### GR-006 — WordCraft Seafile MVP

```text
Status:     GPT REVIEW FAIL (Sol); remediation pending re-review
Branch/SHA: (filled at freeze time)

Requirements:  The 12-step MVP checklist of ROADMAP.md, VERIFIED END-TO-END on
               synthetic DOCX files. Must cover: simple DOCX, text edit, simple
               formatting, save, reopen, Seafile version, read-only, save
               failure, editor close, concurrent modification.
Decision:       The WordCraft `?host=parent` bridge (the GR-014 patch) makes the
               DOCX MVP technically possible. The required synthetic local
               Seafile Web → WordCraft edit → durable version → editor
               acknowledgement → close/reopen flow is now REPRODUCED against
               patched isolated Seahub/C fileserver. It has not been accepted by
               Sol on a new candidate; production ONLYOFFICE regression and
               separate-origin security remain unverified.
Files:          docs/reviews/GR-006/, docs/reviews/GR-014/
Tests:          See `docs/reviews/GR-015/ISOLATED-RUNTIME-E2E-20261023.md`;
               isolated real browser/Seafile E2E reproduced, broader security
               and regression cases remain open
Free review:    historical review-03 PASS is provisional and superseded by Sol FAIL
Evidence:       docs/reviews/GR-006/ and docs/reviews/GPT-SOL-REREVIEW-D9EF476.md
Known risks:    Test used a local same-origin proxy; production origins,
               ONLYOFFICE preservation, permission revocation/read-only, public
               security controls and live deployment remain NOT VERIFIED.
```

### GR-007 — Save protocol

```text
Status:     GPT REVIEW FAIL (Sol); overlapping saves produced a false clean state
Branch/SHA: (filled at freeze time)

Requirements:  Exact save semantics: dirty state -> serialization -> host
               delivery -> authorization/conflict check -> upload -> version
               committed -> acknowledgement -> clean. On failure the Craft
               stays dirty and the UI must not claim success.
Decision:       A save is successful when Seafile has committed a new version. The
               editor holds a ticket and stays dirty until the host answers.
Files:          docs/SAVE-PROTOCOL.md
Tests:          the ticket loop is closed by the application's own log line
Free review:    pending
Evidence:       docs/reviews/GR-006/, docs/reviews/GR-005/
Known risks:    Upstream GridCraft still has optimistic save semantics. The
                local GR-010 patch adds ticketed save results and now has an
                isolated synthetic Seafile save/reopen proof; formula
                recalculation, conflict testing and upstream adoption remain.
```

### GR-008 — Data integrity and conflicts

```text
Status:     GPT REVIEW FAIL (Sol); remediation pending re-review
Branch/SHA: (filled at freeze time)

Requirements:  Concurrent edit, deleted file, renamed file, revoked permission,
               expired session, network loss, interrupted upload, double save,
               browser reload. Must use a mechanism Seafile really provides.
Decision:       Seafile has NO compare-and-swap. The gateway requires an
               upstream atomic save and fails closed instead of using a
               read-then-unconditional-write sequence.
Files:          docs/CONFLICTS.md, docs/reviews/GR-008/
Tests:          tests/test_integration.py (conflict, file-gone, same content)
Free review:    FAIL -> remediated (REVIEW-02 G2: the TOCTOU window is documented)
Evidence:       the Go file server's source, read directly
Known risks:    External-writer concurrency is NOT VERIFIED until an upstream
                atomic CAS/lock endpoint is implemented and exercised.
```

### GR-009 — Web integration security

```text
Status:     GPT REVIEW FAIL (Sol); capability scope, origin isolation and resource controls
Branch/SHA: (filled at freeze time)

Requirements:  XSS, CSRF, CSP, iframe sandbox, postMessage origin validation,
               same-origin/cross-origin isolation, token leakage, replay, session
               fixation, SSRF, malicious/oversized document, ZIP bomb, path
               traversal, save forgery, cross-user access, read-only bypass,
               share-link permissions, expired sessions. `targetOrigin = "*"` is
               forbidden for sensitive messages without a very strong argument.
Decision:       The gateway is the trust boundary and the ONLY defence: an
               op=update file-server token is library-wide, so no Seafile-native
               token is safe in a browser. The browser holds one opaque session id.
Files:          docs/SECURITY.md
Tests:          symlink escape, unknown session, read-only, cross-session
Free review:    FAIL -> remediated (REVIEW-02 G1, G4)
Evidence:       the Go file server's source; the two reviews
Known risks:    CSP, a CSRF check on the state-changing endpoints, and a rate
                limit are still open (S-1, S-2, S-3).
```

### GR-010 — GridCraft Seafile integration

Status: **GPT REVIEW FAIL** on the earlier candidate; the pinned-source bridge
patch now has a reproduced GridCraft Web → isolated synthetic Seafile
save/version acknowledgement → fresh editor reopen path. The narrow bridge
patch received an independent Nemotron PASS with three minor follow-ups; the
runtime evidence does not complete GR-010 or the all-Craft/multi-platform
scope. See `docs/reviews/GR-010/README.md` and
`docs/reviews/GR-010/GRIDCRAFT-SEAFILE-E2E-20261023.md`.

```text
Status:     GPT REVIEW FAIL (Sol on 0edbe52); GridCraft runtime save/reopen now reproduced in synthetic Seafile, but formula recalculation, conflicts and broader app/platform coverage remain open
Branch/SHA: (filled at freeze time)

Requirements:  .xlsx open/edit/save/reopen/conflict via GridCraft Web; all Craft apps remain in the overall product scope.
Decision/Files/Tests/Free review/Evidence/Known risks: (filled at freeze time)
```

### GR-011 — DeckCraft Seafile integration

```text
Status:     NOT IMPLEMENTED — deferred for the upstream DeckCraft host-bridge capability gap
Branch/SHA: (filled at freeze time)

Requirements:  .pptx open/edit slide/save/reopen via DeckCraft Web.
Decision/Files/Tests/Free review/Evidence/Known risks: (filled at freeze time)
```

### GR-012 — Non-office Craft integration

Status: **GPT REVIEW FAIL on 0edbe52**; later local evidence reproduces a
VectorCraft SVG click/edit/save/version/history/reopen in synthetic Seafile.
This does not prove the common host contract or other Craft apps. See
`docs/reviews/GR-012/VECTORCRAFT-SEAFILE-E2E-20261023.md`.

```text
Status:     GPT REVIEW FAIL (Sol); VectorCraft SVG runtime reproduced, common contract/general Craft coverage remain unverified
Branch/SHA: (filled at freeze time)

Requirements:  .pdf via PdfCraft Web and .svg via VectorCraft Web, proving the
               integration is not reserved to Office formats.
Decision/Files/Tests/Free review/Evidence/Known risks: (filled at freeze time)
```

### GR-013 — ArtCraft upstream RFC

```text
Status:     GPT REVIEW FAIL (Sol); stale E2E and credential claims must be corrected
Branch/SHA: (filled at freeze time)

Requirements:  A reusable ArtCraft Web host-integration RFC with the mission's
               required sections. Do not claim Seafile end-to-end validation
               until the required live acceptance flow is proven. NOT PUBLISHED.
Decision:       One shared crate in craft-libs; the message vocabulary three apps
               already use; the ticket and the saveResult answer added; a
               four-step rollout that changes nothing for a person using the app.
Files:          docs/RFC-DRAFT.md
Tests:          (n/a - a document)
Free review:    pending
Evidence:       the three upstream bridges, the reference integration, the patch
Known risks:    The maintainers may prefer a different home than craft-libs.
```

### GR-014 — First ArtCraft upstream patch

```text
Status:     GPT REVIEW FAIL (Sol); packaging/provenance and runtime evidence incomplete
Branch/SHA: (filled at freeze time)

Requirements:  The smallest justified upstream contribution (e.g. a common host
               API primitive). Prepared only; NOT PUBLISHED.
Decision:       One new file in apps/wordcraft-web/ (the bridge) plus three small
               edits; it reuses the async_saves machinery instead of inventing
               anything, so the document is saved only once the host stored it.
Files:          docs/reviews/GR-014/ (README.md + DIFF.patch)
Tests:          it COMPILES for wasm32; it was BUILT and run in a real browser
Free review:    pending (review 03 in flight)
Evidence:       docs/reviews/GR-006/
Known risks:    NOT PUBLISHED. The upstream hard gate holds until GPT REVIEW PASS.
```

### GR-016 — All-app seams and shared Rust transport

```text
Status:      PROTOTYPE IN PROGRESS; not a candidate; bounded Sol low review PASS with minor notes
Branch/SHA:  main / `bdbea5faa7e8b1cdd4c1e526cd3b212e712a0789` (gateway compatibility update pushed); source changes remain in scratch clones
Scope:       inventory all 13 ArtCraft Web app seams; standardize transport; adapt WordCraft and GridCraft first
Evidence:    docs/reviews/GR-016/APP-SEAM-AUDITS-20261024.md, README.md, REVIEW-PORTABLE-CRAFT-PLATFORM-20261024.md
Tests:       standalone craft-platform metadata, 6 native tests and WASM check pass; WordCraft/GridCraft/PdfCraft/CADCraft clean-checkout Rust 1.95 WASM checks pass with --locked against immutable transport revision 90c261de22ef75c4c7c5c5cd1c712d483be0bbc8
Open:        remaining app-specific seams and acknowledgement gaps; security/deployment coverage; single-file Open boundary; runtime/optimized-bundle evidence for the newly pinned PdfCraft/CADCraft builds
GPT review:  NOT REQUESTED; existing project verdict remains GPT REVIEW FAIL on 0edbe524
Publication: LOCKED; no upstream issue, PR, RFC or patch was published

Update 2026-10-24: WordCraft and GridCraft now each have synthetic Seahub/Seafile
edit → durable save → new version → readback → fresh editor reopen evidence after
the shared-transport refactor. The WordCraft run used an actual Seahub file-list
open; GridCraft used the Seahub file route. A GridCraft `SUM(B2:B2)` formula was
also recalculated after B2 changed to 1337 and verified after durable save and
fresh reopen. Exact editor-to-gateway payload hashing and optimized bundle
performance remain unverified. The bounded Nemotron re-review accepted the
updated evidence with minor qualifications; see
`docs/reviews/GR-016/REVIEW-NEMOTRON-GRIDCRAFT-E2E-R2-20261024.md`. Reports:
`docs/reviews/GR-016/SEAFILE-WORDCRAFT-SHARED-TRANSPORT-E2E-20261024.md` and
`docs/reviews/GR-016/SEAFILE-GRIDCRAFT-SHARED-TRANSPORT-E2E-20261024.md`.

Follow-up 2026-10-24: packaged transport revision
`90c261de22ef75c4c7c5c5cd1c712d483be0bbc8` is pinned by the WordCraft,
GridCraft, PdfCraft, and CADCraft patches. All four patches were applied to
clean upstream-source checkouts and pass locked Rust 1.95 WASM checks. This is
build-reproducibility evidence only; other Craft integrations, app runtime
behavior for PdfCraft/CADCraft, and project-level GPT readiness remain open.
See `docs/reviews/GR-016/PORTABLE-APP-PATCHES-20261024.md`.
The bounded independent Sol review returned PASS after two minor documentation/
patch-scope findings were corrected; details and round history are in
`docs/reviews/GR-016/REVIEW-PORTABLE-APP-PATCHES-SOL-LOW-20261024.md`.
```

### GR-017 — PdfCraft durable host-save acknowledgement

```text
Status:      BOUNDED PROTOTYPE REVIEW PASS (Sol low round 4); synthetic Seafile E2E accepted with minor qualifications by Nemotron Free; project GPT remains FAIL
Base:        storytold/pdfcraft `57e531ccca0047597809748b5cb4276336d6051a`
Transport:   storytold/craft-libs `f180fc0d35d521c5d18e118c881d3efde1ec1eee` scratch prototype
Scope:       reuse ticketed shared transport for PdfCraft's existing same-origin host bridge; preserve dirty state until durable result
Evidence:    docs/reviews/GR-017/README.md, SEAFILE-PDFCRAFT-E2E-20261024.md, and patches/pdfcraft-durable-host-ack.patch
Tests:       7 focused native acknowledgement tests, Rust 1.95 WASM check, formatting/diff checks, exact-revision release build, Chromium synthetic-host ACK/reopen smoke, and isolated synthetic Seafile save/version/readback/fresh-reopen reproduction
Open:        lifecycle test gaps remain MINOR for this bounded prototype; file-list click, exact editor-to-gateway payload hash, browser timeout/response loss, deployment security and optimized bundle are NOT VERIFIED
GPT review:  NOT REQUESTED; project remains GPT REVIEW FAIL on 0edbe524
Publication: LOCKED; no upstream issue, PR, RFC or patch was published

Update 2026-10-24: `craft-platform` is packaged with preserved MIT/Apache
notices and pinned at revision
`90c261de22ef75c4c7c5c5cd1c712d483be0bbc8`. PdfCraft's patch now uses that
revision and its clean-checkout locked WASM build passes; details are in the
GR-016 portable app report.
```

### GR-018 — CADCraft durable host-save acknowledgement

```text
Status:      BOUNDED LOCAL PROTOTYPE REVIEW PASS (GPT-6.1 Sol low round 4); no project-level GPT change
Base:        storytold/cadcraft `7bf5905ac97316a7896de8cbc12d243f57b09bd8`
Transport:   `craft-platform` pinned at `56c5e16d79b77751106173c13111ef4fe0a2c0ec`; repin exact review found no blocker/major
Scope:       ticketed save/saveResult adapter; dirty state follows host durable acknowledgement
Evidence:    docs/reviews/GR-018/README.md, cadcraft-host-save.patch, REVIEW-SOL-LOW-R2.md through REVIEW-SOL-LOW-R4.md, REVIEW-TRANSPORT-REPIN-R1.md, CADCRAFT-BROWSER-ACK-SMOKE-20261024.md, CADCRAFT-SEAFILE-E2E-20261024.md
Tests:       Rust 1.95 WASM check; 8 focused acknowledgement tests; 344 engine library tests; fmt/diff checks; local Chromium synthetic-host and isolated synthetic-Seafile edit/save/history/fresh-reopen runs
Open:        Synthetic CADCraft Seafile version/reopen is reproduced; browser failure/timeout/security paths remain NOT VERIFIED; exact editor-to-gateway byte hash and optimized bundle remain open
GPT review:  NOT REQUESTED as a project candidate; project remains GPT REVIEW FAIL on 0edbe524
Publication: LOCKED; no upstream issue, PR, RFC or patch was published
```

### GR-019 — FigCraft shared host-save adapter prototype

```text
Status:      local prototype; focused tests and WASM compile pass; not Seafile E2E
Base:        storytold/figcraft 8d790607ff1ad40e32343ca2116d8fdcf3244c8d
Transport:   craft-platform pinned at 56c5e16d79b77751106173c13111ef4fe0a2c0ec; exact repin review found no new blocker/major
Scope:       one pathless .figcraft file per iframe; ticketed snapshot save ACK; no host Save As
Evidence:    docs/reviews/GR-019/README.md and figcraft-shared-host-save.patch
Tests:       3 engine tests, 1 synthetic-host UI test, Rust 1.95 locked WASM check, patch apply check, fmt/diff checks
Open:        browser postMessage runtime, Seafile dispatch/version/reopen, timeout runtime, and deployment security NOT VERIFIED
Independent: Sol low rounds 1 and 2 returned FAIL; round 3 returned bounded PASS for the original implementation; transport repin R1 scope objection was closed in R2 after comparison against the accepted patch. Full-patch SHA `954850ba5aff7362e776b2331a5a5ff54bf9d71374d7b29bc856c2b7a47c4798`; one MINOR remains for retrying failed dirty-state reports; no project GPT PASS, Seafile E2E, or upstream authorization
GPT review:  NOT REQUESTED as a project candidate; project remains GPT REVIEW FAIL on 0edbe524
Publication: LOCKED; no upstream issue, PR, RFC, or patch published
```

### GR-020 — DeckCraft host-save acknowledgement prototype

```text
Status:      bounded local prototype review PASS (GPT-6 Luna high round 2 on exact current patch); no project-level GPT change
Base:        storytold/deckcraft `0f4fffcf6c71ffa16029d07ac23752fedd783547`
Transport:   `craft-platform` pinned to `56c5e16d79b77751106173c13111ef4fe0a2c0ec`
Patch SHA:   `8d7f98468ce446add5357e10ed8e10e729eb3306fee359d320f09805acc3ee4a`
Scope:       one host-bound presentation; ticketed serialized snapshot save; clean only after matching durable ACK; no host Save As
Evidence:    docs/GR-020-DECKCRAFT-HOST-SAVE.md and docs/reviews/GR-020/
Tests:       2 engine tests, 4 UI lifecycle tests, locked WASM check on 56c5e16, fmt, assets and layers checks pass; full workspace tests did not complete
Open:        browser messaging and Seafile dispatch/version/fresh-reopen NOT VERIFIED; no Seafile route added
CI:          `xtask ci` stops at pre-existing workspace Clippy finding in untouched `crates/matroska/src/demux.rs:726`; `assets`, `layers`, `wasm` and non-strict targeted Clippy pass; workspace test suite remains incomplete
GPT review:  NOT REQUESTED as a project candidate; project remains GPT REVIEW FAIL on 0edbe524
Publication: LOCKED; no upstream issue, PR, RFC, or patch was published
```

### GR-021 — DesignCraft host-save acknowledgement prototype

```text
Status:      bounded local prototype; project GPT verdict remains FAIL on 0edbe524
Base:        storytold/designcraft 80d13911b2d20fbb5cd9398696627bb3a715417b
Transport:   craft-platform `91836a9ebad5ffcd8f1966fb4f36dc84387f2cdd`
Patch:       `1333c9d24f19cbc458a436fac77a94f15924f5c9d1ec428c630fbadd0b2cbb30`
Scope:       one pathless native .designcraft document; serialized snapshot save with durable ticket ACK; no Save As
Tests:       five focused Rust 1.95 tests, locked WASM check, formatting and diff checks PASS
Independent: Luna high R1 found pre-copy transport gap; package fixed/reviewed. Luna high R3 PROVISIONAL: no code blocker/major; R2 P3 peak-serialization-memory qualification is documented
Open:        browser messaging, Seafile version/reopen, and production security NOT VERIFIED; 64 MiB serialized payload cap is after allocation
GPT review:  not a project candidate; project remains GPT REVIEW FAIL on 0edbe524
Publication: LOCKED; no upstream issue, PR, RFC, or patch published
```

### GR-021 — shared transport Open admission

```text
Status:      bounded local transport remediation; project GPT verdict remains FAIL on 0edbe524
Base:        craft-platform package revision d59c3ace80140fa20672131c5ae7c4e6392f8da6
Change:      incoming Open bytes share a cumulative 256 MiB and 64-message budget across same-origin/app transports in one WASM runtime; repeat Open remains supported
Review:      Luna high R2 found one-open compatibility and per-listener state defects; latest bounded review R4 found no functional findings, one wording nit corrected
Tests:       7 native package tests, WASM `--tests` compile, 19 checksums, formatting and diff checks pass; browser tests were not run
Open:        DesignCraft/EffectCraft/FilmCraft app patches need this new transport pin and exact-patch reviews; browser and Seafile runtime remain NOT VERIFIED
Publication: no upstream publication; project and public deployment readiness unchanged
Evidence:    `docs/reviews/GR-021/TRANSPORT-OPEN-ADMISSION-REVIEW.md`
```

### GR-024 — ignore malformed host save acknowledgements

```text
Status:      bounded shared-transport parser fix, pushed at `56c5e16`; project GPT verdict remains FAIL on 0edbe524
Base:        local main `ee140f37be49517e2e35a542fec0fa9453cba27b`
Change:      ignore `saveResult` with missing/non-boolean `ok`; keep valid true/false behavior and public API unchanged
Review:      independent read-only review verified exact diff/hash; no functional issue; test-coverage follow-up for valid true was closed
Tests:       7 native tests, WASM `--tests` compile, all 19 checksums, formatting and diff checks pass; browser tests not run
Open:        active app patches must pin immutable revision `56c5e16d79b77751106173c13111ef4fe0a2c0ec`; browser and Seafile runtime remain NOT VERIFIED
GPT review:  not a project candidate; project remains GPT REVIEW FAIL on 0edbe524
Publication: LOCKED; no upstream issue, PR, RFC or patch published
Evidence:    `docs/reviews/GR-024/`
```

### GR-022 — EffectCraft host-save acknowledgement prototype

```text
Status:      bounded local prototype; project GPT verdict remains FAIL on 0edbe524
Base:        storytold/effectcraft `049070d65c66a73f322b496b22521816e0018f14`
Transport:   craft-platform `56c5e16d79b77751106173c13111ef4fe0a2c0ec`
Patch SHA:   `4e0a1799e36209e1234a1b3ff504ab5ed647cf3bd066af6dec90dacd46ab7407`
Review:      independent exact review found no blocker/major; tests/builds not rerun by reviewer
Tests:       engine 2/2; UI 4/4; Rust 1.95 locked WASM, fmt and diff checks pass per implementer
Open:        browser messaging, host authorization, Seafile version creation and fresh reopen NOT VERIFIED; not in dispatch
GPT review:  not a project candidate; project remains GPT REVIEW FAIL on 0edbe524
Publication: LOCKED; no upstream issue, PR, RFC or patch published
Evidence:    `docs/reviews/GR-022/`
```

### GR-023 — FilmCraft host-save acknowledgement prototype

```text
Status:      bounded local prototype; project GPT verdict remains FAIL on 0edbe524
Base:        storytold/filmcraft `fa550ce2d07bdfee6b1d7b6835e8abc8c6913d00`
Transport:   craft-platform `56c5e16d79b77751106173c13111ef4fe0a2c0ec`
Patch SHA:   `16158f500b2ec12f93c8fcb14867e0b452030dbb338b2d4d7fa8612850a694d4`
Review:      independent bounded R2 source review found no blocker/major; tests/builds were not rerun by reviewer
Tests:       engine 4/4; UI 3/3; Rust 1.95 locked WASM; fmt/diff checks pass per implementer
Open:        browser messaging, authorization, Seafile version creation and fresh reopen NOT VERIFIED; not in dispatch
GPT review:  not a project candidate; project remains GPT REVIEW FAIL on 0edbe524
Publication: LOCKED; no upstream issue, PR, RFC or patch published
Evidence:    `docs/reviews/GR-023/`
```

### GR-025 — SoundCraft host-save acknowledgement prototype

```text
Status:      PROVISIONAL source review; R1 local-open bypass fixed; WASM blocked by pinned-base API mismatch
Base:        storytold/soundcraft `d47abe484d4f9ef0cc9f8e872e0b3880a61a4588`
Transport:   `craft-platform` `56c5e16d79b77751106173c13111ef4fe0a2c0ec`
Patch SHA:   `f8f9da024b80b3292cca1a60ee69eaf4e19c450d7582fac582596fd11aebc331`
Review:      R1 found local picker/drop replacement bypass; R2 confirms guard closes it, no new blocker/major by inspection
Tests:       2 host-save ledger tests and the focused UI regression pass; full WASM passes with GR-027/028/029 overlays (unpatched-base failures are historical)
Open:        GR-027 ports Symphonia, GR-028 addresses CPAL; full WASM passes with GR-029 overlays; browser/Seafile version/reopen NOT VERIFIED; output cap after allocation
GPT review:  not a project candidate; overall project remains GPT REVIEW FAIL on 0edbe524
Publication: LOCKED; no upstream issue, PR, RFC or patch published
Evidence:    `docs/GR-025-SOUNDCRAFT-HOST-SAVE.md`, `docs/reviews/GR-025/`
```

### GR-027 — SoundCraft Symphonia 0.6.1 compatibility

```text
Status:      PROVISIONAL PASS, bounded audio-crate patch; exact independent R5 review found no findings
Base:        storytold/soundcraft `d47abe484d4f9ef0cc9f8e872e0b3880a61a4588`
Patch SHA:   `e4a63489cfdfc0fd3cfc347a1998347bd92bb0b682ac9a25d1051f887e357e6b`
Tests:       57 soundcraft-audio-io tests; locked native/WASM crate checks pass
Open:        full SoundCraft Web WASM now passes with local GR-029 compatibility overlays; browser/Seafile NOT VERIFIED
Publication: LOCKED; no upstream changes
Evidence:    `docs/reviews/GR-027/`
```

### GR-028 — SoundCraft CPAL 0.18.2 playback compatibility

```text
Status:      local patch candidate; independent R1 incomplete (no semantic API finding; exact base/builds not verified)
Base:        storytold/soundcraft `d47abe484d4f9ef0cc9f8e872e0b3880a61a4588`
Patch SHA:   `ff1ced58251397b8077f92ee9b92c7cae1ada25a8a7fe9068c50ba7cdad5901c`
Tests:       implementer reports 36 soundcraft-playback tests and locked native/WASM checks pass; independent reproduction unavailable
Open:        full SoundCraft Web WASM now passes with local GR-029 overlays; browser/Seafile NOT VERIFIED
Publication: LOCKED; no upstream changes
Evidence:    `docs/reviews/GR-028/`
```

### GR-029 — SoundCraft egui 0.37 compatibility

```text
Status:      local compatibility patches; Sol low R3 bounded PROVISIONAL PASS, no findings; GPT REVIEW PENDING
Bases:       SoundCraft `d47abe484d4f9ef0cc9f8e872e0b3880a61a4588`; craft-libs `5c874d51eeb3de70e735c8ce87a59a7dedd47675`
Patch SHA:   craft-ui `5cf2728d20ed74d9fe0521543280d77ce9ef1a5efd3b6f3db3862b6363b06292`; SoundCraft `af31ccc5d69ea1e9577e0a7f989077ccafd9e40cfe3643a2e8c8f934cc6fa098`; lock `d86d74198de55f7f98a4a381d1d18183013f9195c046dd0f56667cbc305f0743`
Checks:      exact GR-025→027→028→029 sequence replays; locked full SoundCraft Web WASM check passes; focused host-save UI test 1/1 passes
Open:        browser screenshot/gutter-scroll runtime and Seafile version/reopen NOT VERIFIED
Publication: LOCKED; no upstream changes
Evidence:    `docs/GR-029-SOUNDCRAFT-EGUI-WASM.md`, `docs/reviews/GR-029/`
```

### GR-030 — SoundCraft browser host-save smoke

```text
Status:      browser protocol smoke reproduced; bounded evidence, GPT REVIEW PENDING
Base:        SoundCraft `d47abe484d4f9ef0cc9f8e872e0b3880a61a4588` with local GR-025/027/028/029 overlays
Transport:   craft-platform `56c5e16d79b77751106173c13111ef4fe0a2c0ec`
Evidence:    Chromium Open → UI edit → ticketed save/ACK → clean → fresh iframe reopen; 66,203,163-byte payload SHA-256 recorded
Open:        in-memory parent only; Seafile version/reopen NOT VERIFIED; payload exceeds gateway's default 50 MiB cap; wasm-opt=0 build is not optimized
Dispatch:    SoundCraft remains excluded
Evidence:    `docs/GR-030-SOUNDCRAFT-BROWSER-SMOKE.md`, `docs/reviews/GR-030/`
```

### GR-031 — SoundCraft Seafile save/version/reopen evidence

```text
Status:      reproduced on isolated synthetic Seafile; Luna High R1/R2 bounded PROVISIONAL PASS; project GPT review pending
Base:        SoundCraft `d47abe484d4f9ef0cc9f8e872e0b3880a61a4588` with local GR-025/027/028/029 overlays
Transport:   craft-platform `56c5e16d79b77751106173c13111ef4fe0a2c0ec`
Evidence:    Seahub file-list click → add Audio 2 → host save ACK → new Seafile file ID/head → 6,877-byte user-bound readback → fresh Seahub reopen showing all three tracks
Readback:    SHA-256 `895bce8fa565730ded872bbf1dd1746ddddc0345e72d9485279e3d987a5a3aff`; exact outgoing message bytes were not separately hashed
Limits:      `wasm-opt=0`; loopback synthetic stack; ONLYOFFICE regression, deployment security and optimized bundle NOT VERIFIED
Dispatch:    SoundCraft remains excluded until review and remaining readiness gaps are addressed
Evidence:    `docs/GR-031-SOUNDCRAFT-SEAFILE-E2E.md`, `docs/reviews/GR-031/`
```

### GR-026 — PhotoCraft host integration assessment

```text
Status:      bounded pathless-open/snapshot-ACK core PROVISIONAL PASS; no browser adapter yet
Base:        storytold/photocraft `a02f2ee41059d3312e7ff24a5af5edcac7b6435a`
Transport:   future app dependency must pin `56c5e16d79b77751106173c13111ef4fe0a2c0ec`
Finding:     `open_file(path, bytes)` binds the name as a local path; browser download uses `write_unconfirmed: true`; pathless binding and revision ACK require app-layer seams and route guards
Tests:       4 engine tests, 1 pathless-open UI test, Rust 1.95 locked PhotoCraft Web WASM check pass
Open:        browser messaging, async UI save lifecycle, Seafile version creation and fresh reopen NOT VERIFIED
GPT review:  not a project candidate; overall project verdict unchanged
Publication: LOCKED; no upstream issue, PR, RFC or patch published
Evidence:    `docs/GR-026-PHOTOCRAFT-HOST-SAVE.md`, `docs/reviews/GR-026/`
```

### GR-032 — PhotoCraft host-save adapter

```text
Status:      GPT REVIEW PENDING — bounded source prototype; R1 findings remediated; R2/R3 independent PROVISIONAL PASS
Base:        storytold/photocraft `a02f2ee41059d3312e7ff24a5af5edcac7b6435a` plus GR-026 core patch
Patch:       `docs/reviews/GR-032/photocraft-host-save.patch`; SHA-256 `487935d8f6db33cf82c85f8d9c8aa0686016612510f15cf34f6b3f05a2c53fe7`
Transport:   `craft-platform` exact rev `56c5e16d79b77751106173c13111ef4fe0a2c0ec`, locked in Cargo.lock
Review:      R1 found unbounded SaveResult enqueue and a swallowed listener-registration error. R2 verified the included fixed-slot inbox and listener failure handling; R3 verified documentation of the 50 MiB/serialization limit. Both are bounded provisional reviews, not project GPT PASS.
Tests:       UI lifecycle test 1/1, inbox/listener tests 2/2, Rust 1.95 locked Web WASM check, clean-base patch apply and diff checks pass
Open:        browser message execution, Seafile durable version/readback/fresh reopen, ONLYOFFICE regression NOT VERIFIED; gateway default is 50 MiB and serialization occurs before rejection, so oversized payload peak memory/compatibility is NOT VERIFIED
Publication: LOCKED; no upstream issue/PR/RFC, commit or push
Evidence:    `docs/GR-032-PHOTOCRAFT-HOST-SAVE.md`, `docs/reviews/GR-032/`
```

### GR-033 — PhotoCraft browser host-protocol smoke

```text
Status:      browser Open/edit/save/ACK/fresh iframe reopen reproduced; bounded independent evidence review PROVISIONAL ACCEPT
Scope:       same-origin Chromium; parent retains bytes in JavaScript memory
Save bytes:  4,995; SHA-256 cbaa7b458588780210d1da7a267d2d5223d6808e0b15ea9e80e84d23ea980f34
Evidence:    screenshot, static host harness and synthetic fixture in docs/reviews/GR-033/runtime/
Limits:      no Seafile write/version/readback, optimized bundle, deployment security or ONLYOFFICE regression
Dispatch:    PhotoCraft remains excluded; no project GPT PASS or upstream publication approval
Review:      Nemotron 3 Ultra PROVISIONAL ACCEPT; no blocker/major; reviewer did not rerun browser or builds
```

### GR-034 — PhotoCraft gateway payload validation

```text
Status:      gateway-only validation; Nemotron 3 Ultra R2 bounded PROVISIONAL PASS
Base:        repository main at 39b6944; native format source storytold/photocraft a02f2ee41059d3312e7ff24a5af5edcac7b6435a
Change:      `.pcraft` validation requires exactly one nonempty exact root `manifest.json` in ZIP central-directory metadata; no decompression
Tests:       `python3 tests/test_gateway_unit.py` passes; malformed ZIP, missing/nested/duplicate/empty manifest, native fixture acceptance and invalid save-before-write are covered
Limits:      shape check only; no manifest JSON/CRC/semantic validation; Seafile runtime unavailable and NOT VERIFIED
Dispatch:    unchanged; `.pcraft` intentionally not added to integration/config/dispatch.json
Review:      R1 MINOR test gap (duplicate/empty manifest) fixed; R2 confirmed coverage by source inspection, no tests rerun
Publication: no upstream action, service/config change or Seafile access
Evidence:    `docs/GR-034-PHOTOCRAFT-GATEWAY-VALIDATION.md`
```

### GR-035 — PhotoCraft optimized Web host smoke

```text
Status:      bounded optimized-bundle browser smoke; Nemotron PROVISIONAL ACCEPT, no blocker/major
Base:        PhotoCraft a02f2ee41059d3312e7ff24a5af5edcac7b6435a + GR-032 host adapter patch
Build:       Trunk 0.22.0 `trunk build --release`; `wasm-opt -Oz` completed; WASM 26,342,447 bytes
Flow:        real PhotoCraft WASM opens a 4,000-byte synthetic fixture in the GR-033 same-origin harness; UI edit; 4,984-byte ticketed save; exact ticket ACK; fresh iframe reopen shows Layer 1 and dirty=false
Save hash:   `92e93c2b993b7de073a2c870aba522d7f9112647d9d1181d2b8592df665936b3`
Limits:      parent retains bytes in JS memory; no gateway/Seafile call, version, or storage-backed reopen; `.pcraft` remains out of dispatch
Review:      PROVISIONAL ACCEPT; screenshot does not identify loaded WASM resource hash
Evidence:    `docs/GR-035-PHOTOCRAFT-OPTIMIZED-BROWSER-SMOKE.md` and `docs/reviews/GR-035/`
```

### GR-037 — PhotoCraft exact save-byte provenance and Seafile reopen

```text
Status:      synthetic Seafile E2E; exact bytes match at editor message, gateway body and Seafile readback; independent review PROVISIONAL ACCEPT, final wording MINOR corrected but not re-reviewed
Base:        PhotoCraft GR-032 adapter + GR-036 repaint fix; no app source patch in this follow-up
Flow:        Seahub open → PhotoCraft edit → Ctrl+S → version 2→3 → byte-identical Seafile readback → fresh Seahub route/new editor session
Bytes:       8,555 at all three boundaries; SHA-256 ea0121c1e465c753947005e1ff4452cc031f734baed3345400bcd3a96218c4ca
Limits:      synthetic loopback; wasm-opt=0; deployment/security and ONLYOFFICE regression NOT VERIFIED; PhotoCraft remains out of dispatch
Evidence:    `docs/reviews/GR-037/`
```

### GR-036 — PhotoCraft synthetic Seafile save/version/reopen

```text
Status:      bounded synthetic Seafile E2E; independent R2 PROVISIONAL ACCEPT, no blocker/major; GPT REVIEW PENDING
Base:        PhotoCraft a02f2ee41059d3312e7ff24a5af5edcac7b6435a + GR-032 adapter + GR-036 repaint fix
Build:       `trunk build --release`, wasm-opt=0; loaded WASM 35,820,040 bytes, SHA-256 d4f339df6312429fa15de653a37b3ef156cee84a3c58eee1358caee34523324c
Flow:        Seahub open → PhotoCraft host Open → add Layer 1 → Ctrl+S → host confirmation → Seafile history 1→2 → fresh Seahub route/session reopens Layer 1
Readback:    4,984 bytes, SHA-256 92e93c2b993b7de073a2c870aba522d7f9112647d9d1181d2b8592df665936b3
Limits:      synthetic loopback only; temporary `.pcraft` route not committed; exact browser-message bytes not independently hashed; security, ONLYOFFICE and optimized production bundle NOT VERIFIED; see independent R1/R2 evidence review
Dispatch:    committed `integration/config/dispatch.json` unchanged; PhotoCraft remains excluded
Evidence:    `docs/GR-036-PHOTOCRAFT-SEAFILE-E2E.md`, `docs/reviews/GR-036/`
```

## GPT review instruction (for the future session)

```text
Do not trust previous free-model PASS verdicts.

Independently inspect and verify:

- Seafile integration assumptions
- OnlyOffice reference analysis
- ArtCraft Web capability matrix
- Host Contract
- browser messaging
- authentication
- authorization
- Save protocol
- version creation
- concurrency handling
- data integrity
- security
- licensing
- deployment
- source code
- diffs
- tests
- upstream RFC
- proposed ArtCraft patches

Return:

BLOCKER
MAJOR
MINOR

Only GPT REVIEW PASS may unlock upstream publication.
```
