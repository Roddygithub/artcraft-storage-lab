# GPT Review Queue

Every work item in this project ends here. GPT performs an **independent** review
and does not trust the free-model verdicts.

Nothing may be published upstream (issue, PR, RFC in `storytold/*`, Seafile or
Seafile docs) before an entry reaches `GPT REVIEW PASS`.

## Latest candidate result — 2026-10-23

```text
Candidate: afec19e63a6a4faec8a94f93651363dbe007e526
Reviewer: GPT-6.1 Sol
Verdict: FAIL
Report: docs/reviews/GPT-SOL-REREVIEW-AFEC19E.md
Prototype: operator-only local investigation; Seafile MVP not ready
Public deployment: NOT READY
Upstream RFC/patch: NOT READY
Upstream publication: LOCKED
```

The failed candidate remains immutable. Focused local remediation commits now
exist after it, but the resulting candidate has not yet received a fresh Sol
review and has not been deployed or pushed. Earlier failures remain in their
separate reports.

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
Decision:       The WordCraft ?host=parent bridge (the GR-014 patch) makes the
               DOCX MVP technically possible. The required Seafile Web →
               WordCraft edit → durable Seafile version → editor acknowledgement
               → close/reopen flow is NOT VERIFIED. The latest browser recovery
               opened the synthetic DOCX in ONLYOFFICE, not WordCraft. A local
               WordCraft harness uses in-memory storage and is not an E2E pass.
Files:          docs/reviews/GR-006/, docs/reviews/GR-014/
Tests:          test_gateway_unit.py and local host round-trip are synthetic;
               Seafile browser E2E is NOT VERIFIED
Free review:    historical review-03 PASS is provisional and superseded by Sol FAIL
Evidence:       docs/reviews/GR-006/ and docs/reviews/GPT-SOL-REREVIEW-D9EF476.md
Known risks:    The real Seafile Web click/close/save flow is NOT VERIFIED;
               the GR-015 C and Seahub patches are local drafts, unbuilt and
               undeployed; ONLYOFFICE preservation after routing is NOT VERIFIED.
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
Known risks:    GridCraft's bridge (not ours) cannot report a failed save; the
                upstream patch has to fix that.
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

Status: **GPT REVIEW FAIL** — durable save acknowledgement and semantic reopen
are not established. See `docs/reviews/GR-010/README.md`.

```text
Status:     GPT REVIEW FAIL (Sol); bridge lacks durable save acknowledgement
Branch/SHA: (filled at freeze time)

Requirements:  .xlsx open/edit/save/reopen/conflict via GridCraft Web.
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

Status: **GPT REVIEW FAIL** — the historical SVG run did not prove the intended
stroke after editor reopen. Revised local assertions are present; Seafile E2E is
not verified. See `docs/reviews/GR-012/README.md`.

```text
Status:     GPT REVIEW FAIL (Sol); Seafile persistence and dirty/commit acknowledgement remain unverified
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
