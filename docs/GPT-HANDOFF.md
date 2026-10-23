# GPT Handoff

A single document that lets a GPT session take over this project **without
trusting the summaries produced by the free models**.

Everything here can be checked against the repository, the upstream sources and
the reference instance. Where a claim was made by a free model and not
independently verified, it says so.

## Latest review event — 2026-10-23

GPT-6.1 Sol reviewed exact candidate
`afec19e63a6a4faec8a94f93651363dbe007e526` and returned **FAIL**. The full
report is `docs/reviews/GPT-SOL-REREVIEW-AFEC19E.md`; the prior `d9ef476e`
FAIL remains in `docs/reviews/GPT-SOL-REREVIEW-D9EF476.md`. Local remediation
commits after `afec19e` address overlapping-save state, gateway error leakage
and response bounds, the cross-origin handoff, conditional-save routing, and
false-positive SVG/XLSX evidence. They have not yet been reviewed by Sol. The
required Seafile DOCX file-list click/edit/version/close/reopen and ONLYOFFICE
save regression remain **NOT VERIFIED**. No GPT PASS was granted; upstream is
locked. No service was changed during the latest review or remediation.

The local candidate currently contains remediation commits through the entries
in `HISTORY.md`; it is not yet frozen for Sol. Record the exact next review SHA
after the final status/evidence commit.

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
* The GR-015 Seahub and Seafile Server patches are **not built, installed, or
  runtime-tested**. The live instance has no ArtCraft route or gateway. The
  current deployed click on the synthetic DOCX still opens ONLYOFFICE.

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
9. Patched Seahub calls the dedicated `conditional-update-api`; stock and Go
   fileservers do not expose this route and must fail before writing. The C patch
   is unbuilt and runtime behavior is **NOT VERIFIED**.
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
| 1 | user attribution is proposed by the local patch but not runtime-verified | `docs/reviews/GR-015/README.md` |
| 2 | stock Seafile has no user-bound conditional save; patched C behavior is not built or tested | `docs/reviews/GR-015/README.md` |
| 3 | **share links** are not covered by the hook | `docs/SEAFILE-INTEGRATION-POINTS.md` L7 |
| 4 | the click in the Seafile file list is not driven by the automated test | `docs/reviews/GR-006/README.md` §5 |
| 5 | the gateway runs on the owner's workstation for the proof | `docs/DEPLOYMENT.md` |
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
| per-library routing and conditional save | `docs/reviews/GR-015/` | patch artifacts apply to exact source revisions; not built or executed against Seahub/fileserver |

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

1. `docs/reviews/GR-006/README.md` — is the "VERIFIED END-TO-END" claim honest?
   (Two of the twelve steps are marked *partly*: the click in the Seafile file
   list, and the user-facing close.)
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
