# HOST_PERMISSION_BOUNDARY — WOPI read-only tokens can write on the host

Status: **finding retained, host-side, zero-patch fix NOT possible.** The
bridge refuses read-only saves at its own endpoint; the unpatched host does
not.

```text
HOST_PERMISSION_BOUNDARY:

ROOT_CAUSE:
    Seahub's WOPI PutFile endpoint validates token existence but never
    consults the write permission it stored in the token itself.
    - Token minting records the action: `get_wopi_file_url(...,
      can_edit=(action_name == 'edit'))` caches
      `{'can_edit': bool, ...}` in the token value
      (`seahub/wopi/utils.py:63`, `:262`).
    - CheckFileInfo reads it and reports `UserCanWrite=False`,
      `ReadOnly=True` for view tokens (`seahub/wopi/views.py:348`,
      `:417-418`).
    - PutFile (`WOPIFilesContentsView.post`) reads only
      `request_user/repo_id/file_path` from the same cache entry and
      immediately mints a fileserver `update` token and overwrites the file
      (`views.py:661-687` in the c01d46b checkout; `:425-460` in
      `seahub-12.0.14`). `can_edit` is consulted exactly once in the whole
      file — in CheckFileInfo.
    - The fileserver side (`server/upload-file.c:2429 check_access_token`)
      validates token existence, repo status and op match only; the token is
      the capability, and per-user permission checking is Seahub's
      responsibility — which PutFile does not do.

AFFECTED_VERSIONS:
    Seafile CE 12.0.14 and CE 13.0.28. Confirmed by source inspection of both
    shipped `seahub-12.0.14` and a 2026-10-21 master checkout (`c01d46b`,
    post-13.x): the defect is present in both, identical structure.

REPRODUCIBLE:
    YES on CE 13.0.28 — empirically in the lab
    (`lab/real-seafile/results/2026-11-15-seafile-render-readonly/`: a direct
    PutFile with a read-only WOPI token succeeded).
    CE 12.0.14: verified by source inspection of the exact release checkout
    (same missing check, file:line above); NOT yet reproduced empirically on
    the pinned CE12 stack.

EXISTING_FIX:
    NONE FOUND. No WOPI setting (`ENABLE_OFFICE_WEB_APP`,
    `OFFICE_WEB_APP_EDIT_FILE_EXTENSION`, token TTL) restricts what a token
    may do after minting; they only control which actions get tokens. No
    host-side permission re-check exists in the PutFile path of either
    version.

ZERO_PATCH_FIX_POSSIBLE:
    NO.
    - Configuration: no option makes PutFile honor `can_edit`.
    - Reverse proxy: a rule blocking `POST /wopi/files/*/contents` would also
      block every legitimate editor save — the bridge's own save path uses
      the same endpoint. Per-token permission cannot be evaluated at proxy
      level.
    - Client-side UI checks (`UserCanWrite=False`, hidden save buttons) are
      not security controls.
    The bridge-side refusal is real and tested (`tests/bridge/` fault
    injection covers token-class checks) but it cannot constrain a client
    that bypasses the bridge and calls Seahub directly with the
    browser-visible token.

HOST_CHANGE_REQUIRED:
    YES — a small upstreamable host patch: in `WOPIFilesContentsView.post`,
    reject when `not info_dict.get('can_edit')` (401/403 per WOPI
    conventions). One line of substance, no schema or protocol change. A
    draft belongs in `docs/upstream-drafts/` and stays there under the
    upstream hard gate.

SAFE_DEPLOYMENT_SCOPE:
    - Edit workflows (the MVP loop) are unaffected: the user's token is
      minted for edit and is meant to write.
    - Read-only viewing routes (ODT/ODS/CSV/PPSX, `VIEW_SUPPORTED`) are NOT
      safe for untrusted users in production under the zero-patch constraint:
      any user who can open a view page holds a token that can overwrite that
      file. They remain acceptable in a trusted single-user deployment where
      the viewer is the owner, and in the lab.

REMAINING_RISK:
    Privilege escalation from viewer to writer on a per-file basis (no new
    file creation; the token is bound to one path). Locking does not help:
    the endpoint honors the caller's lock operations regardless of
    `can_edit`.
```

Consequence for the product matrix: `VIEW_SUPPORTED` formats must keep the
caveat "requires a trusted deployment or a one-line host patch; not safe for
untrusted viewers zero-patch" until the host change exists. This is recorded
in `docs/ONLYOFFICE-REPLACEMENT-MATRIX.md`.
