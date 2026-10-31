# GPT Handoff

> **2026-10-31 — superseded.** The GR series below describes the gateway + Seahub/fileserver patch
> architecture that `docs/REFOUNDATION-REPORT.md` retired. Current state: `README.md`, `ROADMAP.md`,
> `lab/real-seafile/results/`. This file is kept as history and is no longer updated.


A single document that lets a GPT session take over this project **without
trusting the summaries produced by the free models**.

Everything here can be checked against the repository, the upstream sources and
the reference instance. Where a claim was made by a free model and not
independently verified, it says so.

## Latest review event — 2026-10-23

GPT-6.1 Sol reviewed exact candidate
`0edbe524b4fa321b0f73f8601afef390e7f785e6` at medium effort/default service
tier and returned **FAIL**. The report is `docs/reviews/GPT-SOL-REREVIEW-0EDBE52.md`;
the earlier `afec19e` and `d9ef476e` FAILs remain preserved in their reports.
Sol found that the GR-015 route `conditional-update-api` fails Seafile's existing
`op=update` prefix token check. Commit `0da898f` changes it to
`update-conditional-api` and adds a source-level guard test; the exact header
hook and a built isolated runtime still need verification. The route/prefix
assertions pass against pinned source but are not a C runtime test. Nemotron
independently passed this single route/prefix finding at medium effort; that
narrow result is in `docs/reviews/GR-015/ROUTE-TOKEN-REVIEW.md` and does not
replace Sol's overall FAIL. GR-006's historical
free PASS claim and the RFC's capability handoff wording were also corrected.
The required Seafile DOCX file-list click/edit/version/close/reopen and
ONLYOFFICE save regression had not been reproduced at the time of that review.
No GPT PASS was granted; upstream is locked. No production service was changed
during that review.

The local remediation after `0edbe52` is not yet frozen for Sol. Record the exact
next review SHA after the final status/evidence commit.

### GR-016 all-app audit and transport prototype — 2026-10-24

The 13 ArtCraft Web apps now have a consolidated source seam inventory in
`docs/reviews/GR-016/APP-SEAM-AUDITS-20261024.md`. Six remaining audits that had
failed or returned unusable results were rerun as brief GPT-6 Luna high source
reads. These are not implementation reviews and do not prove runtime behavior.

A scratch prototype extends the pinned `craft-platform` browser feature with
same-origin/source validation, RAII message-listener cleanup, transferred byte
buffers, opaque string save tickets, and bounded pending-save tracking. The
pinned local GR-014 WordCraft and GR-010 GridCraft adapters were refactored to
use it. On Rust 1.97, `craft-platform` tests (6), strict clippy, its browser
WASM check, and both app `cargo check`s passed. The app checks used a temporary
local path to the scratch library; they do not validate a published dependency
revision. WordCraft and GridCraft release bundles then passed local Chromium
synthetic-host edit/save-ack/reopen smoke tests, including failed-save dirty
state. The harness used `sessionStorage`; this is not a Seafile E2E.

The prototype remains in scratch clones and is not ready to publish. The first
review found two GridCraft defects: in-app Open still used the browser picker,
and the declared 1.90 MSRV conflicted with dependencies requiring 1.95. The
adapter now routes Open through the host; a Rust 1.95 release-bundle browser
test observed a request and reopened the stored edit. GridCraft's scratch MSRV
is raised to 1.95 and its WASM check passes. GPT-6.1 Sol low independently
returned provisional PASS for these bounded remediations with three minor
notes; the full report is `docs/reviews/GR-016/REVIEW-SOL-LOW-R3.md`.
Full details and exact SHAs are in
`docs/reviews/GR-016/README.md`. The old Sol FAIL on `0edbe524` stands, public
deployment is not ready, and the upstream hard gate remains locked.

The root Seafile host page did not handle the shared transport's
`<app>:openRequest`. It now displays a safe instruction to choose another file
from Seafile and retains dirty state. The connector session remains bound to
the document selected in Seahub; it does not provide a library browser. A T3
Chromium synthetic-frame preview verified this message path. The documented
Playwright protocol test was updated but could not run in system Python because
the Playwright module is unavailable. This does not verify the refactored
WordCraft/GridCraft save flow against Seafile.

### Isolated runtime update — 2026-10-23

The statements above about unbuilt/unrun patches and an unverified DOCX E2E are
historical and superseded for the local remediation by
`docs/reviews/GR-015/ISOLATED-RUNTIME-E2E-20261023.md`. The exact GR-015 patches
were built/run in an isolated synthetic rootless Podman stack; Seahub checks and
migrations passed. The browser clicked the synthetic file in Seahub, opened the
real WordCraft Web/WASM app, edited and saved, received a committed new Seafile
head/file ID, and reopened the saved sentence in a fresh WordCraft session.
Two concurrent conditional writes yielded one 200 and one 409. A later test
repeated the race through two real WordCraft editors: both made different edits
and sent Ctrl+S concurrently, one committed, the other stayed dirty with a 409,
and a fresh Seahub click/reopen rendered only the winner. Seafile readback
confirmed the current head/file ID and that the losing edit was absent.

This does not change Sol's FAIL on `0edbe52` and does not mark a new SHA reviewed.
The initial local browser test used a same-origin loopback proxy. A follow-up
used Seahub and gateway/Craft on separate loopback ports, saved a real WordCraft
edit, reloaded the file route, and verified the saved DOCX content from Seafile.
Production TLS/proxy/CSP/CSRF and adversarial-frame isolation remain unverified.
ONLYOFFICE regression, permission revocation, read-only bypass, and stock/Go
fileserver rejection remain open. GridCraft and VectorCraft now have separate
synthetic Seafile runtime results, documented below. VectorCraft uses its
private page API rather than the common contract. Production
services were not changed; upstream is still locked.

### GridCraft synthetic Seafile runtime update — 2026-10-23

On repository revision `e6c559e7d7ea6e207f9d539f996eade4f1dc6334`, a real
Seahub click opened the patched GridCraft Web/WASM app in the isolated
synthetic Seafile stack. A3 was edited to `GridCraftSeafileRoundTrip`, Ctrl+S
received a committed file/head acknowledgement, Seafile readback returned a
valid changed XLSX, and a fresh Seahub click/reopen rendered the edited cell.
Exact hashes, screenshots, and limits are in
`docs/reviews/GR-010/GRIDCRAFT-SEAFILE-E2E-20261023.md`. The history-list API
was not independently verified in that run (the browser request returned 403);
the host's committed-head acknowledgement and Seafile readback were verified.

The XLSX fixture was missing `xl/styles.xml`, which made GridCraft show a
warning. The generator/check now include a minimal styles part. The corrected
fixture opened in a new GridCraft session without that warning, but its
edit/save/reopen cycle has not yet been repeated. Formula recalculation,
GridCraft concurrency and the other Craft apps remain open. This runtime
result does not change the old Sol FAIL or authorize upstream publication.

Nemotron independently reviewed SHA `a4ecc8e1d0da44a12f7bd9c4e529ed4accdb4a0e`
and returned FAIL for candidate readiness, chiefly because ONLYOFFICE
regression and separate-origin/auth edge cases were still unverified. A real
two-editor concurrent save/reopen was then reproduced and documented; Nemotron
has not reviewed that later evidence. See
`docs/reviews/REVIEW-NEMOTRON-A4ECC8E.md`.

Nemotron then reviewed exact SHA `36c0bc0f2b534b34c52193519fbb422ac5c22948`
and returned FAIL for candidate readiness. It accepted the separate-origin
synthetic handoff/save evidence and retained blockers for ONLYOFFICE
preservation, authorization edge cases, production security topology, and
runtime validation against unsupported fileservers. Major findings remain for
GridCraft/VectorCraft acknowledgement and semantic reopen, save crash/retry
windows, and licensing. After that review, another fresh gateway session
reported `Saved — new version`, `dirty=false`, `confirmedSave=true`; a fresh
Seafile-backed WordCraft load read a valid DOCX with the edit marker. This
strengthens the local DOCX evidence only. Full report:
`docs/reviews/REVIEW-NEMOTRON-36C0BC0.md`.

An additional Django-runtime guard now calls the pinned patched Seahub view:
the ArtCraft allowlist selects the ArtCraft handoff, and a non-allowlisted DOCX
falls through to Seahub's ONLYOFFICE view template. Storage and the OnlyOffice
response builder are synthetic doubles, so actual Document Server
edit/save/version/reopen remains unverified. See
`tests/test_gr015_dispatch.py` and the reproduction command in the GR-015
runtime report.

## 1. Repository

| Item | Value |
| --- | --- |
| Local path | `~/Projects/artcraft-storage-lab` |
| GitHub | `https://github.com/Roddygithub/artcraft-storage-lab` (public) |
| Default branch | `main` |
| Licence | dual MIT / Apache-2.0 |
| HEAD | see `git log -1` |

## 2. What the project is

A research and prototyping project that makes **ArtCraft's browser editors
usable from a self-hosted file platform**, the way ONLYOFFICE is usable from
Seafile today: click a file in Seafile Web, edit it in the browser, press Save,
and Seafile records a new version. No SeaDrive, no manual download, no manual
upload, no desktop application.

## 3. Architecture

```text
   the browser                    the gateway                    Seafile
  ┌───────────────┐             ┌────────────────┐          ┌──────────────┐
  │  the Craft    │  postMessage │  the host page  │ capability│ Seahub      │
  │  app (wasm)   │ ──────────► │  + the service  │ ───────► │ + seafhttp  │
  │  in an iframe │ ◄────────── │                 │ ◄─────── │              │
  └───────────────┘             └────────────────┘          └──────────────┘
```

* the **Craft app** is the upstream web build, unmodified except for the host
  bridge patch (`docs/reviews/GR-014/`). It knows nothing about Seafile.
* the **host page** is served by the gateway and frames the Craft app **from the
  same origin** (the `?host=parent` bridge requires it).
* Seahub posts a short-lived third-party-editor capability to the gateway; the
  gateway stores it server-side and binds one document session. The local GR-015
  draft scopes write capability to ArtCraft, one repository and extension, then
  rechecks current user permission and calls a dedicated conditional-save route.
* The GR-015 Seahub and Seafile Server patches were built and run only in the
  isolated local test container. They are **not installed in production**. The
  live instance has no ArtCraft route; its synthetic DOCX still opens
  ONLYOFFICE. The isolated synthetic browser flow is documented separately.

### 3.1 The two integration points

| Point | Where | What it does |
| --- | --- | --- |
| the file-type dispatcher | Seafile's `seahub/thirdparty_editor/` hook, configured by `THIRDPARTY_EDITOR_ACTION_URL_DICT` | maps an extension to the host page's URL, mints the access token, serves the bytes |
| the save | proposed Seahub endpoint + conditional fileserver update | reauthorize the Seafile user, check opened file ID and repository head, then commit |

The original gateway service-account write design was rejected. The current
local draft proposes a user-bound Seahub save endpoint plus a conditional
fileserver update. Its authorization, CAS behavior, and version attribution
remain unverified until built and exercised on an isolated synthetic Seafile
deployment. Do not treat the draft as deployed behavior.

## 4. The GR list

| GR | Title | Artifact | Free review | GPT review |
| --- | --- | --- | --- | --- |
| GR-001 | Seafile online-editor contract | `docs/reviews/GR-001/DEPLOYED-INSTANCE-CONTRACT.md` | PASS (remediated) | PENDING |
| GR-002 | Seafile integration point | `docs/SEAFILE-INTEGRATION-POINTS.md` | PASS (remediated) | PENDING |
| GR-003 | ArtCraft Web capability matrix | `docs/ARTCRAFT-WEB-CAPABILITIES.md` | PASS (remediated) | PENDING |
| GR-004 | Common Craft Web Host Contract | `docs/HOST-CONTRACT.md` | PASS (remediated) | PENDING |
| GR-005 | First technical proof | `docs/reviews/GR-005/` | PASS (remediated) | PENDING |
| GR-006 | WordCraft DOCX MVP | `docs/reviews/GR-006/` | provisional PASS (superseded) | FAIL (Sol) |
| GR-007 | Save protocol | `docs/SAVE-PROTOCOL.md` | PASS (REVIEW-03) | PENDING |
| GR-008 | Data integrity and conflicts | `docs/CONFLICTS.md` + `docs/reviews/GR-008/` | PASS (remediated) | PENDING |
| GR-009 | Web integration security | `docs/SECURITY.md` | PASS (remediated) | PENDING |
| GR-010 | GridCraft (`.xlsx`) | `docs/reviews/GR-010/README.md` | provisional PASS (superseded) | FAIL (Sol) |
| GR-011 | DeckCraft | — | not started (needs the upstream bridge) | PENDING |
| GR-012 | Non-Office Craft integration (SVG/VectorCraft) | `docs/reviews/GR-012/` | provisional PASS (superseded) | FAIL (Sol) |
| GR-013 | ArtCraft upstream RFC | `docs/RFC-DRAFT.md` | PASS (REVIEW-03) | PENDING |
| GR-014 | First ArtCraft upstream patch | `docs/reviews/GR-014/` | PASS (REVIEW-03) | PENDING |

## 5. The relevant upstream repositories and SHAs

| Repository | SHA / version | Why |
| --- | --- | --- |
| `haiwen/seahub` | `c01d46bcaa0b2ce24c71561c6c61d15fea808d1a` (2026-10-21) | the open-source Seahub; the `thirdparty_editor` hook |
| `haiwen/seafile-server` | `master` (the Go file server) | the `update-api`, the `441`, the `last_modify` finding |
| `storytold/wordcraft` | `00bc6a4b028013b2dfb0e85e8b326aeed3ecff6d` (2026-10-22) | the patch target |
| `storytold/gridcraft` | `main` | the reference bridge |
| `storytold/pdfcraft` | `main` | the reference save-failure bridge |
| `storytold/cadcraft` | `main` | the third bridge |
| `storytold/vectorcraft` | `main` | the `window.vectorcraft` page API |
| `storytold/craft-libs` | `f180fc0d35d521c5d18e118c881d3efde1ec1eee` | current `craft-platform` already has an optional WASM browser feature; candidate home for shared host transport, not yet decided |
| the other eight `storytold/*` apps | `main` | the capability matrix |

All of them are **public** and were read read-only. **Nothing was published
anywhere.**

## 6. The reference environment

| Item | Value |
| --- | --- |
| Seafile | **12.0.14 Professional**, LXC `108` ([private LAN address omitted]) |
| Seahub | on `:8000`; the file server on `:8082` |
| reverse proxy | Nginx Proxy Manager, LXC `103` ([private LAN address omitted]) |
| public name | [private Seafile hostname omitted] |
| ONLYOFFICE | Document Server 24.04, LXC `112` — **untouched** |
| test library | Dedicated synthetic library; identifier omitted |
| production libraries | Not accessed; identifiers and names omitted |

### 6.1 Historical Seafile configuration and current state

An earlier `.xlsx` third-party-editor mapping was removed. ArtCraft is not
currently configured in live Seahub; the synthetic DOCX click opens ONLYOFFICE.
The ONLYOFFICE setting and extension list were left unchanged. The backup and
rollback details are in `docs/DEPLOYMENT.md`. No gateway or conditional-save
patch is installed on the live instance.

## 7. The commands

```sh
# stage one exact Craft web release asset (does not install it)
./scripts/fetch-craft-web.sh wordcraft vX.Y.Z <asset-sha256>
# Verify the host protocol before manually promoting it; see docs/ASSET-INGESTION.md.

# the WordCraft build with the host bridge (needs a Rust toolchain)
rustup target add wasm32-unknown-unknown
cd .work/wordcraft-patch/apps/wordcraft-web && trunk build --release
cp -a ../../../dist/web/. ../../../../integration/static/wordcraft/

# the synthetic fixtures
python3 tests/fixtures/make_fixtures.py tests/fixtures

# a synthetic library
ARTCRAFT_SEAFILE_URL=... ARTCRAFT_SEAFILE_TOKEN=... \
  python3 tests/upload_fixtures.py <repo_id> artcraft-lab

# the gateway
cd integration && ARTCRAFT_SEAFILE_URL=... ARTCRAFT_SEAFILE_TOKEN=... \
  python3 -m gateway --host 127.0.0.1 --port 8777

# gateway simulation only; not a real Seafile integration test
ARTCRAFT_GATEWAY=http://127.0.0.1:8777 \
  python3 tests/test_integration.py <repo_id> /artcraft-lab/synthetic.xlsx
ARTCRAFT_GATEWAY=http://127.0.0.1:8777 \
  python3 tests/test_browser.py <repo_id> /artcraft-lab/synthetic.docx
```

The real Seafile tests also need a synthetic library, account token, a live
third-party-editor capability, the gateway, and the GR-015 server patches built
in isolation. The local browser and engine tests use synthetic storage only.

## 8. The integration flow

```text
1. Intended: the user clicks a supported file in an allow-listed Seafile library.
2. Patched Seahub renders a form that POSTs an ArtCraft-audience capability to
   the separate gateway origin; this route is not deployed.
3. The gateway reads file-info and file-content, creates a session, and serves the
   host page.
4. The host page frames the Craft app (same origin, ?host=parent).
5. The Craft app posts <app>:ready; the host page sends <app>:open with the bytes.
6. The user edits; the app posts <app>:dirty.
7. The user saves; the app posts <app>:save with the bytes and a ticket.
8. The host page POSTs the bytes to the gateway.
9. Patched Seahub calls the dedicated `update-conditional-api`; the patched C
   route was built and exercised in the isolated runtime. Stock and Go
   fileserver rejection remain **NOT VERIFIED** at runtime.
10. The host/editor becomes clean only after durable version confirmation.
11. Close and reopen the file in the editor; verify the semantic edit.
```

## 9. The security assumptions

* the Craft frame holds only an opaque one-document gateway session id; Seahub
  must use a separate origin from the gateway and Craft frame;
* an `op=update` file-server token is **library-wide**, so it is never given to
  the browser; the gateway's checks are the only defence;
* the host page and the Craft app are **same-origin**, and both check the origin
  **and** the source of every message; the `targetOrigin` is always explicit;
* the session id is unguessable, single-document, and short-lived (30 min
  absolute, 15 min idle);
* the path, the library and the user come from the **session**, never from the
  request;
* stock Seafile has no user-bound conditional file save; writes remain disabled
  unless the dedicated patched fileserver route is built and runtime-tested.

The full list, with what is still open, is in `docs/SECURITY.md`.

## 10. The known limitations

| # | Limitation | Where |
| --- | --- | --- |
| 1 | positive user-bound save was exercised on the synthetic local Seahub stack; revocation/read-only behavior still needs runtime tests | `docs/reviews/GR-015/ISOLATED-RUNTIME-E2E-20261023.md` |
| 2 | patched C conditional route built and ran; unsupported stock/Go server fail-closed behavior needs runtime verification | `docs/reviews/GR-015/ISOLATED-RUNTIME-E2E-20261023.md` |
| 3 | **share links** are not covered by the hook | `docs/SEAFILE-INTEGRATION-POINTS.md` L7 |
| 4 | the synthetic file-list click and DOCX save/reopen are reproduced in the isolated test; the production instance still routes to ONLYOFFICE | `docs/reviews/GR-015/ISOLATED-RUNTIME-E2E-20261023.md` |
| 5 | the gateway ran in the isolated local container for the proof; no production deployment was made | `docs/reviews/GR-015/ISOLATED-RUNTIME-E2E-20261023.md` |
| 5b | a **leave-page warning about unsaved edits** is impossible for VectorCraft without an upstream dirty signal; the editor itself keeps unsaved work in recovery copies in the browser | `docs/reviews/GR-012/README.md` §2 |
| 6 | GridCraft `.xlsx` and VectorCraft `.svg` save/reopen are reproduced in the synthetic stack. One GridCraft `SUM(B2:B2)` recalculation and conflict path are also recorded; this does not establish broad formula compatibility. VectorCraft uses its private page API, not the common host contract, and lacks dirty/save events. | GR-010, GR-012 and GR-016 bundles |
| 7 | The inspected upstream baseline still lacks host integration in most Craft apps; local WordCraft/GridCraft patches do not complete the all-app contract. **VectorCraft is driven by its own page API.** | `docs/ARTCRAFT-WEB-CAPABILITIES.md` §2.6 |
| 7b | VectorCraft's page API has **no dirty signal and no save event**; the host polls `files()` and compares exact serialized bytes. Identical output cannot signal an editor save. The synthetic collision regression and post-fix isolated Seafile save/readback/reopen both pass. | `docs/reviews/GR-012/VECTORCRAFT-SEAFILE-E2E-20261023.md` |
| 7c | VectorCraft keeps at most **16** saved files in the page | upstream: `apps/vectorcraft-web/src/saved_files.rs` |
| 8 | GridCraft's upstream baseline cannot report a failed save; the local GR-010 ticketed patch addresses it and has an isolated runtime save/reopen proof | `docs/HOST-CONTRACT.md` §3.5 |
| 9 | GR-039 adds a nonce CSP to dynamic `/open/` host HTML; static editor HTML, browser bundle compatibility, proxy origin behavior and rate limiting remain unverified | `docs/SECURITY.md` §7 and `docs/GR-039-HOSTPAGE-CSP.md` |

## 11. The prepared upstream patches

| Patch | Where | State |
| --- | --- | --- |
| the WordCraft `?host=parent` bridge | `docs/reviews/GR-014/DIFF.patch` (in this repository; the target is Apache-2.0) | compiles and has a local browser harness; durable Seafile E2E not verified |
| per-library routing and conditional save | `docs/reviews/GR-015/` | exact patches built/run in isolated stack; synthetic DOCX E2E reproduced; security, compatibility and regression gaps remain |

**Neither has been published.** No issue, no PR, no comment, no branch push, no
RFC sent anywhere.

## 12. The free-model review record

| Review | Verdict | Remediation |
| --- | --- | --- |
| REVIEW-01 (GR-001/002/004) | **FAIL** | `docs/reviews/REVIEW-01.md` — 1 blocker, 4 majors, 3 minors, all fixed |
| REVIEW-02 (the gateway) | **FAIL** | `docs/reviews/REVIEW-02.md` — 3 blockers, 6 majors, 3 minors, all fixed |
| REVIEW-03 (the WordCraft bridge, GR-006/007/013/014) | **PASS** | `docs/reviews/REVIEW-03.md` — 4 majors, 4 minors, all fixed or accepted |
| REVIEW-04 (GR-012, the VectorCraft transport) | **FAIL** | `docs/reviews/REVIEW-04.md` — 4 blockers, 5 majors, 4 minors, all fixed or documented |

| Model incident | Where |
| --- | --- |
| MiniMax free withdrawn mid-session; the owner role moved to GLM-5.3-Flash | `docs/AI-ROUTING.md` |
| the architect timed out twice (GR-001, GR-003); both artifacts existed already | `docs/AI-ROUTING.md`, incident log |
| DeepSeek timed out once on the smoke test, succeeded on the retry | `docs/AI-ROUTING.md` |

**The reviews were performed by an independent agent that did not write the code
under review.** Their verdicts are `PROVISIONAL`.

## 13. The instruction for the GPT review

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

### 13.1 Where to look first

1. `docs/reviews/GR-006/README.md` — the historical free-review “VERIFIED
   END-TO-END” claim is superseded; Sol found no accepted real Seafile DOCX E2E
   evidence. See `docs/reviews/GPT-SOL-REREVIEW-0EDBE52.md`.
2. `.work/wordcraft-patch` — is the ticket flow right? (The application claims the
   ticket the bridge started; the bridge finishes it. If they are not the same
   ticket, the document never gets marked saved. REVIEW-03 verified this.)
3. `integration/gateway/server.py` — is any check missing?
4. `docs/reviews/GR-008/SEAFILE-CONCURRENCY-PRIMITIVES.md` — is the conflict
   analysis right against the Go file server?
5. `docs/reviews/REVIEW-01.md` … `REVIEW-04.md` — is the remediation real, and
   did it introduce anything new?
6. `docs/reviews/GR-012/README.md` §2 — is the VectorCraft transport divergence
   (a page API, not the common contract) stated honestly, and are its gaps?

### GR-017 PdfCraft durable host acknowledgement — 2026-10-24

PdfCraft is the next bounded adapter after the all-app seam audit. On pinned
source SHA `57e531ccca0047597809748b5cb4276336d6051a`, the scratch patch reuses
the GR-016 `craft-platform` transport and adds ticketed save results. PdfCraft
keeps its snapshot dirty until a matching host response confirms persistence;
failed, duplicate or stale acknowledgements do not mark newer edits clean.
The first bounded Sol low review returned FAIL: UI form drafts could be lost on
an older save acknowledgement, overlapping same-document saves could lose a
close callback, and unanswered tickets could retain capacity indefinitely. The
patch now commits typing before comparing generations, coalesces and queues
same-document requests, adds a 120-second ticket timeout, bounds retained bytes,
and releases pending snapshots when tabs close. Round 3 found no blocker/major,
but found callback-cap bypass through wrapped follow-up callbacks. The current
patch propagates retained callback counts and the 64-callback regression test
passes. Seven focused native tests, Rust 1.95 WASM check, formatting and diff
checks pass. Release/browser smoke used `sessionStorage` and predates the
callback-accounting-only change; Seafile persistence/versioning is not claimed.
Sol low round 4 returned bounded prototype PASS, with no blocker/major and one
non-blocking lifecycle-test minor. After that review, the exact current patch
passed a fresh Rust 1.97 release build and Chromium synthetic-host
edit/save/ACK/fresh-reopen smoke using `sessionStorage`. See
`docs/reviews/GR-017/RUNTIME-SMOKE-R4.md` and `REVIEW-SOL-LOW-R4.md`. The
project's prior GPT-6.1 Sol FAIL remains in force; PdfCraft Seafile
persistence/version/reopen is not verified, and this work does not unlock
upstream publication.

### GR-018 CADCraft durable host-save acknowledgement — 2026-10-24

On pinned CADCraft base `7bf5905ac97316a7896de8cbc12d243f57b09bd8`, a local
patch adds correlated `cadcraft:save` / `cadcraft:saveResult` handling. The
engine holds the drawing dirty until a positive host acknowledgement, preserves
newer edits and SaveAs destination after stale success, tracks exports without
clearing the source drawing, and expires tickets on the earliest deadline.
Sol low bounded rounds 1–4 culminated in PASS for the local prototype; each
round-1/2 finding was remediated and round 3's export-timeout message was
corrected. Rust 1.95 WASM check, eight focused acknowledgement tests and 344
engine tests pass. Full evidence is in `docs/reviews/GR-018/`.

The local build still depends on the GR-016 transport at an absolute `/tmp`
path and used `wasm-opt=0`; standalone reproducibility and optimized bundle
performance remain unverified. A later isolated synthetic Seafile runtime run
did reproduce Seahub file-list click → CADCraft circle edit → save confirmation
→ new Seafile history entry/file ID → fresh Seahub click and CADCraft reopen
with the circle visible. The API readback hash is recorded, but the exact
editor-to-gateway message bytes were not independently hashed. See
`docs/reviews/GR-018/CADCRAFT-SEAFILE-E2E-20261024.md`. Project GPT remains
FAIL on `0edbe524`; public deployment and upstream publication remain locked.
