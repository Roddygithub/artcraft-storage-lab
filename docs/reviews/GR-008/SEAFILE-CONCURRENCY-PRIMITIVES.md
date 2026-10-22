# GR-008 — Evidence: the concurrency and data-integrity primitives Seafile actually provides

Collected read-only on 2026-10-22 from:

* the **deployed** Seahub 12.0.14 Professional (`/opt/seafile/seafile-server-12.0.14/seahub/seahub/`), and
* the **open-source** file server, `haiwen/seafile-server` (the seafhttp server is
  written in Go and its source is public) — `fileserver/fileop.go`, `fileserver/http_code.go`.

**Question this answers:** does Seafile give us an optimistic-concurrency primitive
for "replace this file, but only if it has not changed since I opened it"?

**Short answer: no. Not natively. We must implement the check ourselves using the
content id (`obj_id`).**

---

## 1. The update endpoint, exactly

Seafile's file server exposes two update routes
(`haiwen/seafile-server`, `fileserver/fileserver.go`):

```go
r.Handle("/update-api/{.*}", appHandler(updateAPICB))   // API flavour
r.Handle("/update-aj/{.*}",  appHandler(updateAjaxCB))  // web flavour
```

Both call `doUpdate(rsp, r, fsm, isAjax)`, which:

1. parses the multipart body: exactly one `file` part, plus `target_file`,
   optionally `last_modify`, optionally `head`;
2. `checkParentDir(repoID, parentDir)` — the parent directory must still exist;
3. `checkTmpFileList(fsm)`;
4. `checkQuota(repoID, contentLen)` — returns `443` (`seafHTTPResNoQuota`) if over quota;
5. `putFile(...)` — the actual write.

### 1.1 The form fields

| Field | Meaning | Enforced as a concurrency check? |
| --- | --- | --- |
| `target_file` | absolute path of the file to replace | **yes, indirectly** — see 1.2 |
| `file` | the new content (exactly one part) | — |
| `last_modify` | RFC3339 timestamp | **NO** — see 1.3 |
| `head` | base commit id to write onto | **NO** — see 1.4 |

### 1.2 Deletion and rename *are* detected

```go
exist, _ := checkFileExists(repo.StoreID, headCommit.RootID, canonPath, fileName)
if !exist {
    msg := "File does not exist.\n"
    return &appError{nil, msg, seafHTTPResNotExists}   // HTTP 441
}
```

`checkFileExists` looks the name up in the **current** head commit's directory
listing. Consequences:

* the file was **deleted** while the editor was open -> `441`, no write;
* the file was **renamed** while the editor was open -> `441`, no write
  (the old name no longer exists);
* the **parent directory** was deleted -> `checkParentDir` fails, no write.

This is exactly the behaviour we want for those three cases, and it comes for
free from the file server. Our integration only has to surface the error
honestly instead of reporting success.

### 1.3 `last_modify` is NOT a conditional update — it only stamps the mtime

```go
lastModifyStr := normalizeUTF8Path(r.FormValue("last_modify"))
var lastModify int64
if lastModifyStr != "" {
    t, err := time.Parse(time.RFC3339, lastModifyStr)
    if err == nil {
        lastModify = t.Unix()
    }
}
...
mtime := time.Now().Unix()
if lastModify > 0 {
    mtime = lastModify
}
newDent := fsmgr.NewDirent(fileID, fileName, uint32(mode), mtime, user, size)
```

The parsed timestamp is only used as the **mtime of the new directory entry**. It
is **never compared** with the mtime or the content id of the existing file. A
stale `last_modify` therefore does **not** cause a rejection: the write goes
through and the file's mtime is silently rewritten to the supplied value.

**Do not build the conflict strategy on `last_modify`.** It is a trap: it looks
like an optimistic-lock token and is not one.

### 1.4 `head` is a base commit id, not a guard

```go
var headIDs, ok := r.Form["head"]
if ok { headID = headIDs[0] }
...
var base string
if headID != "" { base = headID } else { base = repo.HeadCommitID }
headCommit, err := commitmgr.Load(repo.ID, base)
```

The commit named by `head` is loaded and used as the parent of the new commit.
There is **no check that `head` is still the repository head**. Writing onto a
stale base would create a commit whose parent is not the current head, which
risks losing concurrent changes made to *other* files in the same library.
**Do not use `head` as a lock.** It is a low-level write primitive.

### 1.5 The only server-side "same content" case

```go
oldFileID, _, _ := fsmgr.GetObjIDByPath(repo.StoreID, headCommit.RootID, fullPath)
if fileID == oldFileID {
    // content is identical -> no new commit is created
    rsp.Write([]byte(fileID))
    return nil
}
```

If the new bytes hash to the same content id, **no new version is created** and
the response is the existing file id. This is the natural "no changes" signal and
it protects the file history from noise.

### 1.6 The only "conflict" the server reports

```go
if errors.Is(err, ErrGCConflict) {
    return &appError{nil, "GC Conflict.\n", http.StatusConflict}   // HTTP 409
}
```

`ErrGCConflict` is about **garbage collection** racing with the write, not about
content conflicts. It must not be reported to the user as "someone else edited
this file".

---

## 2. What Seafile gives us to build the check ourselves

### 2.1 Read the current content id

`GET /api2/repos/{repo_id}/file/detail/?p=/path`
(deployed: `seahub/api2/views.py:3319` `FileDetailView`)

Response fields that matter:

| Field | Meaning |
| --- | --- |
| `id` | the **content id (obj_id)** of the current version |
| `mtime` / `last_modified` | modification time |
| `last_modifier_email` | who changed it last |
| `permission` | the caller's effective permission string |
| `size` | file size |

The same value is available internally as
`seafile_api.get_file_id_by_path(repo_id, path)`.

### 2.2 The content id is what the editor token is bound to

In the ONLYOFFICE open flow the download token is minted against the file id:

```python
dl_token = seafile_api.get_fileserver_access_token(repo_id, file_id, 'download', username, use_onetime=False)
```

So the "version we opened" is already identified by a value we can re-read at
save time. **The conflict check is therefore: compare the `file_id` observed at
open with the `file_id` observed at save.**

### 2.3 The cooperative lock

`seahub/utils/file_op.py:13` -> `ONLINE_OFFICE_LOCK_OWNER = 'OnlineOffice'`.
The lock is taken on open, refreshed from the browser
(`operation=refresh-lock`, `expire=2400` -> 40 minutes) and released on save or
close. It is a **lease**, it is **advisory**, and it **expires**. It cannot be
the only protection.

### 2.4 What the write capability looks like

`GET /api2/repos/{repo_id}/update-link/?p=/path&from=api`
(deployed: `seahub/api2/views.py:2031` `UpdateLinkView`)

```python
token = seafile_api.get_fileserver_access_token(repo_id, 'dummy', 'update', request.user.username, use_onetime=False)
url   = gen_file_upload_url(token, 'update-api')
```

Note the object id is the literal string `'dummy'`, and the ONLYOFFICE path uses
`{'online_office_update': True}`. The seafhttp server interprets these
well-known markers instead of a real object id, so **the resulting update token
is scoped to the *library* (repo) with the `update` permission, not to a single
file**. `seahub/seadoc/utils.py:119` shows a narrower form:

```python
obj_id = json.dumps({'online_office_update': True, 'parent_dir': parent_path})
```

which scopes the capability to a directory.

**Least-privilege consequence for our connector (GR-009):** we should mint our
own update token scoped as narrowly as the file server allows, and we should
**never** hand a Seafile account token to the browser. The browser-side
capability must be our own, short-lived, single-file, single-action.

---

## 3. The resulting conflict matrix

| Situation | Detected by | Where | User-visible result |
| --- | --- | --- | --- |
| file deleted while editing | file server | `441 NotExists` | "This file no longer exists. Your changes were not saved." |
| file renamed while editing | file server | `441 NotExists` | "This file was renamed or moved. Your changes were not saved." |
| parent folder deleted | file server | `checkParentDir` error | "The folder no longer exists." |
| content saved unchanged | file server | `fileID == oldFileID` | no new version, save reported as "no changes" |
| **another user saved a different version** | **we must implement it** | obj_id compare | "This file was modified by someone else. Save refused." |
| permission revoked | Seahub permission check on the write path | `403` | "You no longer have permission to edit this file." |
| session expired | our own session store | `401` | "Your editing session expired. Reopen the file." |
| over quota | file server | `443` | "Not enough storage space." |

## 4. The check we must implement

At **open** time, store with the editing session:

```text
session.repo_id
session.file_path
session.file_id        <- the content id observed at open (get_file_id_by_path)
session.mtime          <- optional, for diagnostics only
session.user
session.permissions    <- can_edit / can_download / can_copy
```

At **save** time, before writing:

```text
current_id = get_file_id_by_path(repo_id, file_path)   # via the API
if current_id is empty            -> 404-equivalent, "file no longer exists"
if current_id != session.file_id  -> CONFLICT, refuse, do not write
otherwise                          -> write, then confirm
```

After the write, the new content id is the response of the update call
(the file server returns the new file id, or the existing one when the content
is unchanged), so the session can be updated to the new id for a subsequent save
in the same session.

### 4.1 Why this is strictly better than the reference implementation

Seafile's own ONLYOFFICE callback performs an **unconditional** update. Our
check is a superset of the protections Seafile provides (deleted / renamed
detected by the server) plus the one it does not provide (concurrent
modification).

The cost is one extra API call per save. That is acceptable.

### 4.2 A note on the "same file, two editors" case

Two users opening the same file in our Craft integration get **different**
sessions (unlike ONLYOFFICE, where the shared `doc_key` creates one co-editing
session). The second save will therefore be refused as a conflict rather than
merged. That is a deliberate, safe choice: silent last-writer-wins is the
failure mode we are trying to eliminate. Real co-editing is out of scope for
this project and is a candidate for a later phase.

---

## 5. Reproduction commands

```sh
# the update handler and its form fields
git clone --depth 1 --filter=blob:none --sparse https://github.com/haiwen/seafile-server.git ss
cd ss && git sparse-checkout set fileserver
sed -n '3170,3200p' fileserver/fileop.go     # last_modify parsing
sed -n '3400,3420p' fileserver/fileop.go     # mtime stamping
sed -n '3340,3360p' fileserver/fileop.go     # existence check -> 441

# the deployed Seahub side
pct exec 108 -- sed -n '3319,3400p' \
  /opt/seafile/seafile-server-12.0.14/seahub/seahub/api2/views.py   # FileDetailView
pct exec 108 -- sed -n '2031,2080p' \
  /opt/seafile/seafile-server-12.0.14/seahub/seahub/api2/views.py   # UpdateLinkView
```

All commands are read-only.
