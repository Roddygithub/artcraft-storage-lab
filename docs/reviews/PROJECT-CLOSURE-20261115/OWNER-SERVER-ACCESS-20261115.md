# Owner Seafile test access — 2026-11-15

Sanitized record of access preparation for the owner's synthetic-library tests.
Exact account address, private hostnames, repository ID, and credentials are
omitted.

## Verified

- Seafile ping and HTTPS login page respond successfully.
- Live server release is Seafile 12.0.14, older than the isolated CE 13.0.28
  validation target. The current stateless WOPI bridge is not configured;
  `ENABLE_OFFICE_WEB_APP` is false and its extension list is empty.
- The corrected owner-provided account exists and is active in Seahub/CCNet.
- The existing `ArtCraft GPT Review Synthetic` library was found. Its root has
  11 synthetic entries; its owner is a separate synthetic identity.
- Before the change, the library had no direct user shares. Under the owner's
  prior authorization to use this test library, Seafile's `share_repo` RPC was
  called with read-write permission for the corrected account. The RPC
  returned success; both the account's share list and the library's shared-user
  list confirmed the resulting share. `check_permission` and
  `check_permission_by_path` both returned `rw` for the account and library root.
- A headless browser reached the HTTPS login form but did not authenticate.

## Pre-existing legacy route found

Further read-only inspection found that this server still has a custom,
repository-scoped ArtCraft route from the retired third-party-editor design:

- The installed Seahub `views/file.py` and `thirdparty_editor/views.py` do not
  match the corresponding files in the adjacent Seafile 12.0.14 release
  archive. They contain custom `ARTCRAFT_*` dispatch and cached editor-token
  code.
- The active settings have one ArtCraft repository allowlist entry; the
  synthetic library is in it. An ArtCraft action URL is configured and the
  extension list includes office formats. The values and URL are intentionally
  omitted.
- Proxmox CT 114 has an active `artcraft-gateway.service` described as the
  synthetic Seafile gateway.
- Historical GR-059 records a real browser WordCraft edit, Seafile version
  creation and fresh-session reopen on the owner's Seafile 12.0.14 through the
  earlier gateway. That evidence belongs to the retired third-party-editor
  path; it was not replayed here and does not validate the current WOPI bridge.
- The stock WOPI branch routes by configured file-extension tuples and does
  not scope by repository. The active allowlisted route is custom and does not
  use the project's stateless WOPI bridge.

This is pre-existing infrastructure, not a result of the current test. Its
current runtime behavior and security were not tested in this session; see the
historical GR-059 scope above. It was not changed or stopped.
The limited authorization to test one synthetic library does not authorize
replacing this route or enabling a global WOPI extension route. A current-bridge
test needs an isolated Seafile instance unless the owner separately approves a
broader live-server routing change.

## Scope and limits

Only the synthetic library's permission changed. No document content, other
library, user file, or server configuration was modified. No password was
submitted through the HTTP login URL. The browser has not opened an editor;
authenticated open/edit/save/reopen against this server remains **NOT VERIFIED**.
The absence of a configured bridge and the older Seafile release prevent this
from being evidence for the isolated CE 13.0.28 workflow or for production
readiness.

## Reproduction summary

From the Seafile server's own Seahub Python environment, the read-only checks
used `ccnet_api.get_emailuser`, `seafile_api.search_repos_by_name`,
`seafile_api.get_share_in_repo_list`, `seafile_api.get_shared_users_by_repo`,
`seafile_api.list_dir_by_path`, `seafile_api.check_permission`, and
`seafile_api.check_permission_by_path`. The one authorized mutation used
`seafile_api.share_repo(repo_id, synthetic_owner, corrected_account, "rw")`.
No credential values or private identifiers were retained.
