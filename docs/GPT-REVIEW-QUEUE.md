# GPT Review Queue

Every work item in this project ends here. GPT performs an **independent** review
and does not trust the free-model verdicts.

Nothing may be published upstream (issue, PR, RFC in `storytold/*`, Seafile or
Seafile docs) before an entry reaches `GPT REVIEW PASS`.

## Queue

### GR-001 — Seafile online-editor integration contract

```text
Status:     GPT REVIEW PENDING
Owner:      artcraft-owner
Reviewer:   artcraft-reviewer (free pass) -> GPT (final)

Branch:     main
SHA:        (filled at freeze time)

Requirements:  Document the real, current Seafile <-> ONLYOFFICE online-editor
               integration and extract the abstract contract Seafile expects from
               an external web editor. Every claim evidenced by Seafile source
               code (file:line) or public documentation.
Decision:       (filled at freeze time)
Files:          (filled at freeze time)
Tests:          Documentation review + citation spot-check; no runtime code.
Free review:    PENDING
Evidence:       docs/SEAFILE-ONLYOFFICE-RESEARCH.md
Known risks:    Possible that Seafile's ONLYOFFICE path is hardcoded and needs a
                patch; possible that a more generic hook exists upstream.
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
Free review:    PENDING
Evidence:       (filled at freeze time)
Known risks:    (filled at freeze time)
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
Free review:    PENDING
Evidence:       (filled at freeze time)
Known risks:    Baseline audit suggests the apps are native-only; the entire
                "Craft Web" premise may need to be reframed as "build the web
                host". Must be stated explicitly.
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
Status:     GPT REVIEW PENDING
Branch/SHA: (filled at freeze time)

Requirements:  Smallest end-to-end proof: Seafile host -> Craft Web -> open ->
               edit -> save -> new Seafile version. Mocks allowed as intermediate
               steps, never as final evidence.
Decision/Files/Tests/Free review/Evidence/Known risks: (filled at freeze time)
```

### GR-006 — WordCraft Seafile MVP

```text
Status:     GPT REVIEW PENDING
Branch/SHA: (filled at freeze time)

Requirements:  The 12-step MVP checklist of ROADMAP.md, VERIFIED END-TO-END on
               synthetic DOCX files. Must cover: simple DOCX, text edit, simple
               formatting, save, reopen, Seafile version, read-only, save
               failure, editor close, concurrent modification.
Decision/Files/Tests/Free review/Evidence/Known risks: (filled at freeze time)
```

### GR-007 — Save protocol

```text
Status:     GPT REVIEW PENDING
Branch/SHA: (filled at freeze time)

Requirements:  Exact save semantics: dirty state -> serialization -> host
               delivery -> authorization/conflict check -> upload -> version
               committed -> acknowledgement -> clean. On failure the Craft
               stays dirty and the UI must not claim success.
Decision/Files/Tests/Free review/Evidence/Known risks: (filled at freeze time)
```

### GR-008 — Data integrity and conflicts

```text
Status:     GPT REVIEW PENDING
Branch/SHA: (filled at freeze time)

Requirements:  Concurrent edit, deleted file, renamed file, revoked permission,
               expired session, network loss, interrupted upload, double save,
               browser reload. Must use a mechanism Seafile really provides.
Decision/Files/Tests/Free review/Evidence/Known risks: (filled at freeze time)
```

### GR-009 — Web integration security

```text
Status:     GPT REVIEW PENDING
Branch/SHA: (filled at freeze time)

Requirements:  XSS, CSRF, CSP, iframe sandbox, postMessage origin validation,
               same-origin/cross-origin isolation, token leakage, replay, session
               fixation, SSRF, malicious/oversized document, ZIP bomb, path
               traversal, save forgery, cross-user access, read-only bypass,
               share-link permissions, expired sessions. `targetOrigin = "*"` is
               forbidden for sensitive messages without a very strong argument.
Decision/Files/Tests/Free review/Evidence/Known risks: (filled at freeze time)
```

### GR-010 — GridCraft Seafile integration

```text
Status:     GPT REVIEW PENDING
Branch/SHA: (filled at freeze time)

Requirements:  .xlsx open/edit/save/reopen/conflict via GridCraft Web.
Decision/Files/Tests/Free review/Evidence/Known risks: (filled at freeze time)
```

### GR-011 — DeckCraft Seafile integration

```text
Status:     GPT REVIEW PENDING
Branch/SHA: (filled at freeze time)

Requirements:  .pptx open/edit slide/save/reopen via DeckCraft Web.
Decision/Files/Tests/Free review/Evidence/Known risks: (filled at freeze time)
```

### GR-012 — Non-office Craft integration

```text
Status:     GPT REVIEW PENDING
Branch/SHA: (filled at freeze time)

Requirements:  .pdf via PdfCraft Web and .svg via VectorCraft Web, proving the
               integration is not reserved to Office formats.
Decision/Files/Tests/Free review/Evidence/Known risks: (filled at freeze time)
```

### GR-013 — ArtCraft upstream RFC

```text
Status:     GPT REVIEW PENDING
Branch/SHA: (filled at freeze time)

Requirements:  An RFC titled around "Reusable ArtCraft Web host integration for
               embedded editors, validated end-to-end with Seafile", with the
               mission's required sections. NOT PUBLISHED.
Decision/Files/Tests/Free review/Evidence/Known risks: (filled at freeze time)
```

### GR-014 — First ArtCraft upstream patch

```text
Status:     GPT REVIEW PENDING
Branch/SHA: (filled at freeze time)

Requirements:  The smallest justified upstream contribution (e.g. a common host
               API primitive). Prepared only; NOT PUBLISHED.
Decision/Files/Tests/Free review/Evidence/Known risks: (filled at freeze time)
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
