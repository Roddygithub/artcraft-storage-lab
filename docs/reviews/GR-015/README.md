# GR-015 — Per-library ArtCraft routing and conditional Seafile save

Status: **Sol FAIL on `0edbe524b4fa321b0f73f8601afef390e7f785e6`; after that reviewed SHA, the route-token correction and full synthetic DOCX click/edit/save/version/close/reopen flow were exercised against patched Seahub and a patched C fileserver in an isolated local container. The later tip has not had a full Sol re-review.** See [`ISOLATED-RUNTIME-E2E-20261023.md`](ISOLATED-RUNTIME-E2E-20261023.md).

This is the server-side work needed to make the gateway usable without taking
Office formats away from ONLYOFFICE globally.

## Exact source revisions

| Component | Release | Source SHA | Patch |
| --- | --- | --- | --- |
| Seahub | 12.0.14 Pro | `1e9bde801b4360c14d784d9681d4261abc233a8b` | [`seahub-12.0.14.patch`](seahub-12.0.14.patch) |
| Seafile Server | 12.0.14 | `32ed9c69594c9faa5cea28024403fcde362589ec` | [`seafile-server-12.0.14.patch`](seafile-server-12.0.14.patch) |

## Draft behavior and runtime evidence

1. Seahub only dispatches to ArtCraft for repositories in an explicit
   `ARTCRAFT_REPO_IDS` allowlist, and only for configured extensions. This
   leaves ONLYOFFICE dispatch unchanged in every other library.
2. The existing third-party-editor capability provides the user, repository
   and path. The current local patch rechecks `can_preview` for the capability's
   user on each info/content request and binds content reads to the expected
   file id. The patched Django app passed checks and migrations in the isolated
   Seafile runtime, and the synthetic browser flow opened through this
   capability. Permission revocation, read-only bypass, and expiry/replay
   behavior remain **NOT VERIFIED** end to end.
3. A save accepts no arbitrary repository or path. Seahub requires an
   `audience=artcraft` capability, its cached `permission.can_edit` grant, an
   allow-listed repository and extension, and the user's current web-edit
   permission. It validates the original filename and basic file signature,
   then mints an update token for that same user.
4. The fileserver receives the opened file id and repository head. Seahub calls
   the dedicated `update-conditional-api` route. Its name starts with `update`
   so the existing Seafile `op=update` token check accepts it; the patched C
   fileserver maps this distinct route to its conditional handler. The stock C
   and Go routers do not expose that route, so the request must fail with 404 before an unconditional
   update can happen. The C handler also rejects requests missing either
   precondition. The exact patched fileserver now runs in an isolated container.
   Runtime token-prefix and concurrent conditional-save results are recorded in
   `ISOLATED-RUNTIME-E2E-20261023.md`. Stock/Go server rejection,
   external-writer races, and production proxy behavior remain **NOT VERIFIED**.
5. A successful response is returned only after the fileserver returns a new
   file id and Seahub reads back the committed repository head.

The branch-head check is deliberately conservative: an unrelated file change
in the same library can produce a conflict. A narrower file-only merge would
need a separate design and test matrix.

Sol found an XLSX signature mismatch in the reviewed patch. The local
remediation now checks `spreadsheetml.sheet`; the exact patch applies to the
recorded Seahub base, and a synthetic test executes the exact helper against a
real XLSX fixture and rejects a DOCX mislabeled as XLSX. This is not a Django
runtime test.

## Current evidence and limits

| Check | Result |
| --- | --- |
| Exact deployed release sources checked out | PASS; SHAs above |
| Gateway unit checks after the client-side changes | PASS; `python3 tests/test_gateway_unit.py` |
| Exact-source patch application | PASS for both patches against clean recorded base SHAs; source tree diff matches the patch artifact |
| License/provenance inventory | PASS for exact source SHAs and license-file references; legal compatibility/distribution is **NOT VERIFIED** (`THIRD-PARTY-NOTICES.md`) |
| Patched Seahub syntax/helper checks | PASS for Python compilation and the synthetic AST harness. Django checks and migrations also passed in the isolated runtime. A Django URL-level save test rejects read-only and revoked cached edit capabilities before token minting/fileserver calls; Seafile RPC and persistence are synthetic for this check. |
| Seafile Server C build and runtime | PASS for the pinned patched source build and an isolated running C fileserver. The actual `upload_headers_cb` accepts `op=update` on `update-conditional-api` and rejects `op=view` with 403. |
| Synthetic conditional save and conflict test | PASS for real WordCraft sessions: two independent editors changed the same DOCX and sent Ctrl+S concurrently; one committed 200 and one refused 409 while remaining dirty. A fresh WordCraft reopen rendered only the committed edit. External writers and Go/stock server behavior remain **NOT VERIFIED**. |
| Browser click from the Seafile file list | **REPRODUCED in isolated synthetic Seahub:** the allow-listed DOCX opened the real WordCraft Web/WASM app. The production instance still routes its synthetic DOCX to ONLYOFFICE. |
| ArtCraft DOCX edit/save/version/reopen | **REPRODUCED in isolated local stack** with the new head/file ID, semantic content readback, WordCraft post-save confirmation, and fresh editor reopen recorded in `ISOLATED-RUNTIME-E2E-20261023.md`. |
| ONLYOFFICE regression | **NOT RUN**. ONLYOFFICE was not configured in the isolated stack; the production integration was not changed. |

The live Seahub config was backed up at
`/root/seahub_settings.py.artcraft-rollback-20261022` on LXC 108. Its former
global `.xlsx -> http://127.0.0.1:8777/open/` mapping was removed and Seahub
restarted. `ENABLE_ONLYOFFICE` remains true, its 15 configured extensions were
left unchanged, and the third-party extension map is now empty. Read-only
inspection of LXC 108 shows Seahub, Nginx and `seaf-server` active on ports 8000,
80 and 8082; no ArtCraft gateway is installed there. A synthetic DOCX uploaded
through the Seafile browser file list opened the existing ONLYOFFICE editor
iframe and loaded `/onlyoffice/9.4.0-…` assets. No bytes were edited or saved.

The isolated test does not authorize installation on the live instance. The
production Seafile/ONLYOFFICE services remain untouched. Before any deployment,
verify the intended separate-origin topology and security controls, permission
revocation/read-only behavior, unsupported fileserver rejection, ONLYOFFICE
edit/save/version/reopen preservation, rollback, and resource limits. Upstream
publication remains locked.
