# GR-015 — Per-library ArtCraft routing and conditional Seafile save

Status: **local draft; not built, not deployed, not reviewed, not published**.

This is the server-side work needed to make the gateway usable without taking
Office formats away from ONLYOFFICE globally.

## Exact source revisions

| Component | Release | Source SHA | Patch |
| --- | --- | --- | --- |
| Seahub | 12.0.14 Pro | `1e9bde801b4360c14d784d9681d4261abc233a8b` | [`seahub-12.0.14.patch`](seahub-12.0.14.patch) |
| Seafile Server | 12.0.14 | `32ed9c69594c9faa5cea28024403fcde362589ec` | [`seafile-server-12.0.14.patch`](seafile-server-12.0.14.patch) |

## Intended behavior

1. Seahub only dispatches to ArtCraft for repositories in an explicit
   `ARTCRAFT_REPO_IDS` allowlist, and only for configured extensions. This
   leaves ONLYOFFICE dispatch unchanged in every other library.
2. The existing third-party-editor capability provides the current user,
   repository and path. File info additionally returns the current file id,
   repository head and permission. Reads are bound to that file id.
3. A save accepts no arbitrary repository or path. Seahub derives both from the
   cached user-bound token, checks the current user's web-edit permission,
   validates the original filename and basic file signature, and mints an
   update token for that same user.
4. The fileserver receives the opened file id and repository head. It compares
   the file id in that commit, then uses Seafile's branch compare-and-update
   operation without auto-merging a newer head. A concurrent update returns
   HTTP 409 instead of silently replacing the newer version.
5. A successful response is returned only after the fileserver returns a new
   file id and Seahub reads back the committed repository head.

The branch-head check is deliberately conservative: an unrelated file change
in the same library can produce a conflict. A narrower file-only merge would
need a separate design and test matrix.

## Current evidence and limits

| Check | Result |
| --- | --- |
| Exact deployed release sources checked out | PASS; SHAs above |
| Gateway unit checks after the client-side changes | PASS; `python3 tests/test_gateway_unit.py` |
| Patched Seahub Python syntax | PASS; `python3 -m py_compile` on the two changed Python files |
| Patch whitespace | PASS; `git diff --check` in both source trees |
| Seafile Server C build | PASS; exact patched 12.0.14 source compiled with `./configure --disable-fuse && make -j2` in a temporary Podman Ubuntu 22.04 container; build dependencies and `libsearpc` were installed only in that disposable container |
| Seahub deployment/import test | **NOT RUN** |
| Synthetic Seafile save and conflict test against patched binaries | **NOT RUN** |
| Browser click from the Seafile file list | **NOT VERIFIED**; browser session is logged out and the gateway is not installed on the Seafile container |
| ONLYOFFICE end-to-end preservation | **NOT VERIFIED**; configuration routing was restored, but no authenticated browser check ran |

The live Seahub config was backed up at
`/root/seahub_settings.py.artcraft-rollback-20261022` on LXC 108. Its former
global `.xlsx -> http://127.0.0.1:8777/open/` mapping was removed and Seahub
restarted. `ENABLE_ONLYOFFICE` remains true, its 15 configured extensions were
left unchanged, and the third-party extension map is now empty. No ArtCraft
service is currently listening on LXC 108; the two gateway processes are in the
development workspace only.

The patched Server C source compiled in an isolated temporary container, but
that is not an integration test. Do not install these patches or enable
ArtCraft routing until Seahub import/route checks, user-bound save, conflict
behavior and ONLYOFFICE preservation have been verified against the synthetic
library with a rollback plan. No patch was copied to or installed on Proxmox.
