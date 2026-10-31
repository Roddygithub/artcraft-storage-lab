# Seahub WOPI host: PutFile does not check `can_edit` (note for haiwen/seahub) — DRAFT, unpublished

Measured on stock Seafile CE **13.0.28** (`lab/real-seafile/run_slice.py`, check
`seahub_putfile_ignores_can_edit`, `results/slice.json`); the same code is in `seahub/wopi/views.py`
on 12.0 and master.

## What happens

1. A user with **read-only** permission on a library opens an office file. `view_lib_file` builds a
   WOPI access token with `can_edit = False`; `CheckFileInfo` correctly returns
   `UserCanWrite: false`, `ReadOnly: true`, `SupportsUpdate: false`.
2. The same token is accepted by `POST /api2/wopi/files/<id>/contents` (`X-WOPI-Override: PUT`):
   `WOPIFilesContentsView.post` reads the token's user/repo/path, calls the fileserver update API
   as that user, and returns 200. The file is overwritten and a new commit is attributed to the
   read-only user.
3. There is also no lock check (`X-WOPI-Lock` is ignored on PutFile) and no version precondition.

A compliant WOPI client (Collabora, Office Online) never sends PutFile for `UserCanWrite: false`,
so this is not exploitable through those clients. It is exploitable by anyone who obtains a view
token (it is in the page source of the file view) and speaks WOPI directly.

## Proposed change (minimal)

In `WOPIFilesContentsView.post`, after resolving the token:

```python
if not request_user_can_edit:   # the value stored with the token at mint time
    return HttpResponse(status=403)
```

and, optionally, honour `X-WOPI-Lock` as `LOCK` already does (409 with the current lock on mismatch).

## Why it matters to us

Our bridge enforces `UserCanWrite` itself (`bridge/app.py`, `_relay_save`), so the integration is
safe either way; the note is for Seahub's own benefit.
