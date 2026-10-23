# GR-015 — Per-library ArtCraft routing and conditional Seafile save

Status: **local draft; not built, not deployed, not reviewed, not published**.

This is the server-side work needed to make the gateway usable without taking
Office formats away from ONLYOFFICE globally.

## Exact source revisions

| Component | Release | Source SHA | Patch |
| --- | --- | --- | --- |
| Seahub | 12.0.14 Pro | `1e9bde801b4360c14d784d9681d4261abc233a8b` | [`seahub-12.0.14.patch`](seahub-12.0.14.patch) |
| Seafile Server | 12.0.14 | `32ed9c69594c9faa5cea28024403fcde362589ec` | [`seafile-server-12.0.14.patch`](seafile-server-12.0.14.patch) |

## Proposed behavior (not achieved by the current draft)

1. Seahub only dispatches to ArtCraft for repositories in an explicit
   `ARTCRAFT_REPO_IDS` allowlist, and only for configured extensions. This
   leaves ONLYOFFICE dispatch unchanged in every other library.
2. The existing third-party-editor capability provides the user, repository
   and path. The current local patch rechecks `can_preview` for the capability's
   user on each info/content request and binds content reads to the expected
   file id. `tests/test_gr015_authorization.py` executes the exact decorator
   with synthetic Seafile state; Django/Seafile runtime behavior remains
   **NOT VERIFIED**.
3. A save accepts no arbitrary repository or path. Seahub requires an
   `audience=artcraft` capability, its cached `permission.can_edit` grant, an
   allow-listed repository and extension, and the user's current web-edit
   permission. It validates the original filename and basic file signature,
   then mints an update token for that same user.
4. The fileserver receives the opened file id and repository head. Seahub calls
   the dedicated `conditional-update-api` route; the proposed C fileserver maps
   this route to its conditional handler. The stock C and Go routers do not
   expose that route, so the request must fail with 404 before an unconditional
   update can happen. The patch remains **unbuilt/uninstalled**; route behavior,
   proxy path preservation, and stale-save races need runtime tests.
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
| Patched Seahub syntax/helper checks | PASS for Python compilation and the synthetic AST harness, including capability audience/grant/allowlist and dedicated route checks; Django/Seafile runtime is **NOT VERIFIED** |
| Seafile Server C build | **NOT VERIFIED**; the attempted isolated configure failed on missing `libargon2`; the live server was not touched |
| Seahub deployment/import test | **NOT RUN** |
| Synthetic Seafile save and conflict test against patched binaries | **NOT RUN** |
| Browser click from the Seafile file list | **REPRODUCED: current route opens ONLYOFFICE**, observed on the synthetic library; ArtCraft gateway is not installed/configured |
| ArtCraft DOCX edit/save/reopen and ONLYOFFICE regression | **NOT VERIFIED**; no ArtCraft route is active and no document edit was made during this observation |

The live Seahub config was backed up at
`/root/seahub_settings.py.artcraft-rollback-20261022` on LXC 108. Its former
global `.xlsx -> http://127.0.0.1:8777/open/` mapping was removed and Seahub
restarted. `ENABLE_ONLYOFFICE` remains true, its 15 configured extensions were
left unchanged, and the third-party extension map is now empty. Read-only
inspection of LXC 108 shows Seahub, Nginx and `seaf-server` active on ports 8000,
80 and 8082; no ArtCraft gateway is installed there. A synthetic DOCX uploaded
through the Seafile browser file list opened the existing ONLYOFFICE editor
iframe and loaded `/onlyoffice/9.4.0-…` assets. No bytes were edited or saved.

Do not install these patches or enable ArtCraft routing until the current C
source builds, Seahub imports/routes, user-bound save, conflict behavior, and
ONLYOFFICE preservation are verified against the synthetic library with a
rollback plan. No patch was copied to or installed on Proxmox.
