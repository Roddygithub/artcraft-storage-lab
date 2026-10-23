# GPT Luna Independent Audit

Candidate: `71a7d82da9aa2e2fc8a1743e0c4c06635ae3bd89`
Branch: `main`
SHA: `71a7d82da9aa2e2fc8a1743e0c4c06635ae3bd89`
Date: 2026-10-23

The candidate is the local remediation after Sol's review of
`d9ef476e6fbcb04c9a9e23cfe235812167d1f27c`. It is not deployed or pushed. The
original Sol report remains at `docs/reviews/GPT-SOL-REREVIEW-D9EF476.md`.

## Reproduction

| Command / action | Result | Scope |
| --- | --- | --- |
| `git status --short`; `git rev-parse HEAD`; `git branch --show-current` | clean worktree; `71a7d82da9aa2e2fc8a1743e0c4c06635ae3bd89`; `main` | Exact candidate freeze |
| `python3 tests/test_gateway_unit.py` | PASS, all checks | Synthetic HTTP/upstream adapter, including fake CAS and error redaction |
| `/tmp/opencode/pwvenv/bin/python tests/test_hostpage_protocol.py` | PASS | Synthetic save/dirty protocol; no Craft or Seafile runtime |
| `ARTCRAFT_SEAHUB_SOURCE=/tmp/artcraft-seahub-review python3 tests/test_gr015_authorization.py` | PASS | Exact patched helper/decorator with synthetic Django/Seafile dependencies; not a Django runtime test |
| `/tmp/opencode/pwvenv/bin/python tests/test_wordcraft_host_roundtrip.py` | PASS | Real local WordCraft Web bundle edits/serializes a synthetic DOCX; storage/ack/reopen are in-memory |
| `python3 -m py_compile integration/gateway/*.py tests/*.py` | PASS | Python syntax only |
| `PATH=/home/roddy/.cargo/bin:/usr/bin:/bin cargo fmt --check --all` in `.work/wordcraft-patch` | PASS | Formatting only |
| `git apply --check` for both GR-015 patches against their recorded clean source trees | PASS | Patch applicability only; no build or runtime test |
| Seafile UI, logged-in Tailscale session: open synthetic library, click `synthetic.docx` | Opened `/lib/<synthetic-repo>/file/synthetic.docx`; browser loaded `/onlyoffice/9.4.0-…` assets in a new tab | Confirms the current route is ONLYOFFICE; no bytes were edited or saved |
| `opencode models` and installed role files | IDs present: `openai/gpt-5.6-luna`, `openai/gpt-6.1-sol`; configured agent files use these exact IDs | OpenCode routing verified; T3 uses its own provider model IDs |

An initial `cargo fmt` invocation through `mise` failed because no Rust shim
version was selected in that shell. The direct installed Cargo command above
passed. The browser integration tests requiring a Seahub-minted access token
were not run. No credentials were read or printed.

## Verified claims

- The current local gateway rejects cross-origin state-changing requests,
  redacts capability query values from errors, and has synthetic tests for the
  exercised cases (`integration/gateway/server.py`, `seafile.py`,
  `tests/test_gateway_unit.py`).
- The host page keeps its dirty state during a save and clears it only after the
  storage response and the editor's post-response acknowledgement, in the
  tested protocol (`integration/gateway/hostpage.py`,
  `tests/test_hostpage_protocol.py`).
- The WordCraft web build can edit and serialize the fixture and can reopen it
  from the test harness's in-memory store (`tests/test_wordcraft_host_roundtrip.py`).
- The proposed GR-015 changes are recorded as patch artifacts against exact
  Seafile 12.0.14 source trees, and both patches apply to those trees.
- The logged-in Seafile synthetic library is available. Its DOCX click still
  opens ONLYOFFICE. This observation did not verify OnlyOffice save/version
  behavior and did not modify the document.
- OpenCode's configured Luna and Sol model IDs are present in the model list;
  `config/opencode/agents/artcraft-gpt-auditor.md` and
  `artcraft-gpt-final-reviewer.md` name the corresponding IDs.

## Claims not reproduced

- The mandatory real workflow remains **NOT VERIFIED**: Seafile Web click →
  WordCraft opens the same DOCX → real edit → serialized bytes → user-authorized
  Seafile save → new history version → editor acknowledgement → close/reopen
  from Seafile with semantic edit preservation.
- GR-015 patches are not built, installed, or exercised in Django/Seafile.
  Patch applicability does not prove the C code compiles or that the deployed
  fileserver route enforces the preconditions.
- No actual Seafile history entry, read-back bytes, or editor reopen was
  produced by these runs. Gateway, host, authorization, and storage tests are
  synthetic at their respective boundaries.
- GridCraft workbook formulas/semantics and VectorCraft's expected SVG stroke
  after a real reopen were not freshly reproduced. The previous GR-012 claim
  is evidence to inspect, not a fresh result.
- OnlyOffice open was observed, but editing, save, new version, and reopen were
  not tested. The fact that the configuration stayed enabled does not establish
  regression safety.
- Read-only shares, permission revocation during a live editor session,
  cross-user access, external writer races, save retries, and network loss were
  not exercised against a running Seafile instance.
- The browser-required tests `tests/test_browser.py` and
  `tests/test_gr012_svg.py` were not run in this recovery because no Seahub
  capability token was supplied to the test process.

## Test-quality findings

- `tests/test_gateway_unit.py` proves gateway behavior against fake Seahub and a
  fake conditional writer. Its CAS result is not proof that Seafile's C
  fileserver route commits atomically.
- `tests/test_gr015_authorization.py` executes the patched permission logic with
  synthetic dependencies; it does not import the patched Seahub package into
  Django or invoke Seafile APIs.
- `tests/test_hostpage_protocol.py` uses synthetic messages and a synthetic
  durable-save response. It checks the intended ordering, but does not prove the
  actual Craft editor emits and consumes every message correctly.
- `tests/test_wordcraft_host_roundtrip.py` uses the real local WordCraft web
  engine, but in-memory storage stands in for Seafile. It is a useful editor
  serialization test, not an E2E storage test.
- The historical SVG suite needs adversarial review: Sol found that its open
  requests omitted the expected `Origin`, its shape assertion could pass for a
  rectangle-only path, and byte equality on reopen did not verify editor
  semantics. No fresh evidence here closes those issues.
- Tests requiring a live capability token were not run. A missing-token usage
  exit is not a product failure and is not counted as a pass.

## Architecture findings

- The common host idea still matches a reusable web-editor boundary, but the
  implementation's central Seafile path now depends on proposed GR-015 Seahub
  and C fileserver changes. This is not yet a stock-Seafile integration.
- The local C patch checks the opened file ID and disables the identical-content
  fast return for conditional writes, then requests no automatic concurrent
  merge. It also updates a separate legacy RPC call with a null precondition.
  Static inspection and `git apply --check` do not prove ABI/build or runtime
  correctness.
- The Go fileserver update route remains unsupported by this conditional-save
  patch. The recorded live Nginx `/seafhttp` route targets the C `seaf-server`,
  but the patched binary has not been installed there.
- The Seafile dispatcher draft uses an explicit repository allowlist so it can
  preserve ONLYOFFICE for other repositories. It has not been imported or
  exercised in the live Seahub process.
- The local WordCraft round-trip demonstrates editor serialization through the
  patched host bridge with fake storage; it does not resolve the absent live
  dispatch path.

## Security findings

- The current local gateway tests cover origin rejection and capability URL
  redaction. Reverse-proxy origin/scheme behavior remains unverified.
- The proposed Seahub capability checks re-evaluate current `can_preview` for
  reads and current web-edit permission for save, but only a synthetic source
  harness ran. Runtime authorization, permission revocation, and share behavior
  remain unverified.
- CSP, CSRF protections beyond the current Origin check, and rate limiting are
  still gaps. The prototype is not approved for public Internet exposure.
- Browser cookie, iframe, and message-origin behavior through the intended
  production origin has not been tested with the proposed deployment.

## Data-integrity findings

- The prior Sol blocker about the identical-content shortcut is addressed in
  the current C patch draft: it still compares `expected_file_id`, and
  conditional saves proceed to `gen_new_commit(..., handle_concurrent_update =
  false, ...)` rather than returning early. This is source-level reasoning only;
  no build or race test ran against Seafile.
- The Seahub draft checks repository head and current file ID before making the
  fileserver request. The C branch update is intended to close the TOCTOU window
  with compare-and-update. Actual request routing and behavior under
  simultaneous saves remain unverified.
- Network failure after server commit but before the editor receives the
  response, retries, duplicate commits, and remote delete/rename races were not
  tested against Seafile.
- The host dirty-state test is stronger than the prior pre-save clear test, but
  its positive save response is synthetic.

## Licensing findings

- `docs/LICENSING.md` now identifies the Seahub and Seafile Server patch-context
  revisions and their Apache-2.0 and AGPLv3-with-OpenSSL-exception licenses.
- Those patch artifacts contain upstream context. This repository's
  redistribution and compatibility treatment remains **NOT LEGALLY REVIEWED**;
  the report does not claim legal clearance. ArtCraft upstream contribution
  acceptance is also NOT VERIFIED.
- The reported ArtCraft repositories are dual MIT/Apache-2.0, but the original
  Sol report's provenance concern about copied upstream source context and
  notices should be independently resolved before publication.

## Upstream findings

- `docs/RFC-DRAFT.md` and GR-014/GR-015 artifacts remain local and unpublished.
- The RFC now references adjacent ArtCraft Host Mode work, but the host
  contract's overlap and maintenance scope still need maintainer feedback.
- The Seafile patches add a Seahub endpoint and C fileserver preconditions;
  their compatibility, tests, deployment/upgrade burden, and upstream ownership
  are not established. Do not publish them yet.
- GR-011 DeckCraft remains deferred pending an upstream bridge; this is not an
  implementation failure. No DeckCraft bridge was added in this review.

## Candidate findings

BLOCKER:
- The project's mandatory real Seafile Web → WordCraft → durable new version →
  acknowledgement → close/reopen workflow is not demonstrated.
- The conditional Seafile save code is an unbuilt, untested source patch; no
  server-side atomicity or save acknowledgement is verified in a real instance.

MAJOR:
- Read/write permission and revocation behavior has only synthetic
  source-harness coverage.
- OnlyOffice regression is not tested beyond confirming the existing synthetic
  DOCX still opens in OnlyOffice.
- GridCraft/VectorCraft semantic round-trips and historical SVG test quality
  remain unresolved.
- Public deployment security controls and patch licensing/provenance remain
  incomplete.

MINOR:
- `git diff --check` reports whitespace in blank context lines inside the
  generated GR-015 patch artifact; both patch files still pass `git apply
  --check`. No corresponding source whitespace failure was observed.
- Some historical GR bundle text overstated the DOCX MVP; the current queue and
  handoff now state that the E2E flow is unverified.

## Recommendation to Sol

READY FOR SOL REVIEW

The candidate SHA is exact and reviewable. Sol should decide whether the
synthetic-only evidence and unbuilt GR-015 patches are sufficient for any
prototype or upstream status. Luna does not grant a GPT PASS. Public deployment
is **NOT READY**; upstream publication remains **LOCKED** pending Sol's verdict
and separate user approval.
