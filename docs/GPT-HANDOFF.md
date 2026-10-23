# GPT Handoff

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
The local browser test used a same-origin loopback proxy, so separate-origin
security remains unverified. ONLYOFFICE regression, permission revocation,
read-only bypass, stock/Go fileserver rejection, and GridCraft/VectorCraft E2E
remain open. Production services were not changed; upstream is still locked.

Nemotron independently reviewed SHA `a4ecc8e1d0da44a12f7bd9c4e529ed4accdb4a0e`
and returned FAIL for candidate readiness, chiefly because ONLYOFFICE
regression and separate-origin/auth edge cases were still unverified. A real
two-editor concurrent save/reopen was then reproduced and documented; Nemotron
has not reviewed that later evidence. See
`docs/reviews/REVIEW-NEMOTRON-A4ECC8E.md`.

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
| `storytold/craft-libs` | `main` | where a shared host crate would go |
| the other eight `storytold/*` apps | `main` | the capability matrix |

All of them are **public** and were read read-only. **Nothing was published
anywhere.**

## 6. The reference environment

| Item | Value |
| --- | --- |
| Seafile | **12.0.14 Professional**, LXC `108` (192.168.1.108) |
| Seahub | on `:8000`; the file server on `:8082` |
| reverse proxy | Nginx Proxy Manager, LXC `103` (192.168.1.103) |
| public name | `svc-seafile-host.tailb64fb1.ts.net` |
| ONLYOFFICE | Document Server 24.04, LXC `112` — **untouched** |
| test library | `c82cc792-389d-43e6-b963-0dab1a47a9a8` ("OnlyOffice"), folder `/artcraft-lab/` |
| the real data | library `46ea6c3c-8df3-48b6-bf95-fdc300dcf65c` ("Google Drive") — **never touched** |

### 6.1 Historical Seafile configuration and current state

An earlier `.xlsx` third-party-editor mapping was removed. ArtCraft is not
currently configured in live Seahub; the synthetic DOCX click opens ONLYOFFICE.
The ONLYOFFICE setting and extension list were left unchanged. The backup and
rollback details are in `docs/DEPLOYMENT.md`. No gateway or conditional-save
patch is installed on the live instance.

## 7. The commands

```sh
# the Craft web builds (upstream release artifacts)
./scripts/fetch-craft-web.sh

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
| 6 | the local dispatcher draft lists `.pdf`, `.svg`, `.xlsx` and `.docx`; GridCraft/SVG save readiness is not verified | `docs/FILE-DISPATCH.md` |
| 7 | the other ten Craft applications have no bridge; **VectorCraft is driven by its own page API instead** | `docs/ARTCRAFT-WEB-CAPABILITIES.md` §2.6 |
| 7b | VectorCraft's page API has **no dirty signal and no save event**; the host page polls `files()` with a content fingerprint | `docs/reviews/GR-012/README.md` §2 |
| 7c | VectorCraft keeps at most **16** saved files in the page | upstream: `apps/vectorcraft-web/src/saved_files.rs` |
| 8 | GridCraft's own bridge cannot report a failed save | `docs/HOST-CONTRACT.md` §3.5 |
| 9 | CSP and rate limiting are missing; origin enforcement is only locally tested, not verified behind the proxy | `docs/SECURITY.md` §7 |

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
