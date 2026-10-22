# GR-001 — Evidence: the ONLYOFFICE contract as implemented in the *deployed* instance

This is the **ground truth for our test bed**, collected read-only from the running
Seafile Server the project owner owns. It complements (does not replace) the
upstream source analysis in `docs/SEAFILE-ONLYOFFICE-RESEARCH.md`.

* Inspected: 2026-10-22
* Instance: Seafile Server **12.0.14 (Professional)**, LXC `108`
* Source root: `/opt/seafile/seafile-server-12.0.14/seahub/seahub/`
* Method: read-only inspection over SSH. **No file on the server was modified.**
* Secrets: all values redacted. Nothing secret was copied into this repository.

Line numbers refer to the deployed files listed in the header of each section.

---

## 1. The host page is a *full page*, not an iframe

`seahub/templates/view_file_onlyoffice.html`

```html
<script type="text/javascript" src="{{ ONLYOFFICE_APIJS_URL }}"></script>
...
var docEditor = new DocsAPI.DocEditor("placeholder", config);
```

Seafile does **not** embed ONLYOFFICE in an iframe of a Seahub page. It renders a
whole Seahub page that hosts the editor, and the editor is given a callback URL
back into Seahub.

**Consequence for ArtCraft:** the pattern to copy is *not* "iframe the editor".
It is *"Seahub serves a host page, the editor runs on it, the editor calls back
to Seahub"*. That is friendlier to a WASM editor than a nested iframe, and it
avoids third-party-cookie / framing policy problems entirely.

## 2. The open flow

Entry point: `seahub/views/file.py` (around lines 940-970).

```text
1. get_office_feature_by_repo(repo)                 -> is ONLYOFFICE enabled for this library
2. gate on the file extension:
     fileext in ONLYOFFICE_FILE_EXTENSION            -> openable
     fileext in ONLYOFFICE_EDIT_FILE_EXTENSION        -> editable
     permission.can_edit_on_web                      -> may edit
3. get_onlyoffice_dict(request, username, repo_id, path, file_id,
                       can_edit, can_download, can_copy)
4. if can_edit and the file is not already locked:
       seafile_api.lock_file(repo_id, path, 'OnlineOffice', expire=...)
5. render view_file_onlyoffice.html
```

`seahub/onlyoffice/utils.py::get_onlyoffice_dict` builds the whole contract object.

### 2.1 Tokens actually issued

| Token | How it is built | What it authorizes |
| --- | --- | --- |
| `dl_token` | `seafile_api.get_fileserver_access_token(repo_id, file_id, 'download', username, use_onetime=False)` | The **file server** lets the holder download this *one file id*. The editor server fetches the bytes through it. |
| `file_key` | `jwt.encode({'repo_id', 'file_path'}, ONLYOFFICE_JWT_SECRET)` | Identifies the file to the editor. Sent as `referenceData.fileKey`; `referenceData.instanceId` = the site base URL. **It carries no content id**, so it cannot detect a concurrent modification on its own (see GR-008). |
| `onlyoffice_jwt_token` | `jwt.encode(config, ONLYOFFICE_JWT_SECRET)`, `config['exp'] = now + 3*24*3600` | Signs the whole editor configuration (document url, permissions, callback URL, user). Valid **3 days**. |

`config` contains:

```python
{
  "document": { "fileType", "key", "title", "url",
                "permissions": { "download", "edit", "copy", "print", "review" } },
  "documentType": "word" | "cell" | "slide",
  "editorConfig": { "callbackUrl", "lang", "mode": "edit"|"view",
                    "customization": { "forcesave", "anonymous" },
                    "user": { "id", "name", "image" } },
  "exp": now + 3 days
}
```

`file_id` is `seafile_api.get_file_id_by_path(repo_id, file_path)` — the
**content id (obj_id)** of the current version. This is the natural value to use
for conflict detection at save time. *(Gr-008 hypothesis: compare the `file_id`
observed at open with the `file_id` at save.)*

### 2.2 `document_type` mapping (the file-type dispatcher, as implemented)

`seahub/onlyoffice/utils.py`:

```python
if fileext in ('xls', 'xlsx', 'ods', 'fods', 'csv'):  document_type = 'cell'
elif fileext in ('pptx', 'ppt', 'odp', 'fodp', 'ppsx', 'pps'): document_type = 'slide'
else: document_type = 'word'
```

Note: **everything else falls through to `word`**, including `.pdf`. The wider
office-suite extension lists in `seahub/onlyoffice/settings.py`
(`EXT_DOCUMENT` includes `.pdf`, `.epub`, `.rtf`, `.djvu`, ...) belong to the
*Collabora* path, not to this mapping.

### 2.3 `doc_key` semantics (the editing session identity)

`seahub/onlyoffice/utils.py`:

| Mode | Key derivation | Consequence |
| --- | --- | --- |
| read-only (`can_edit=False`) | `md5(repo_id + file_path + file_id)[:20]` | changes with every new content version |
| editable (`can_edit=True`) | looked up by `md5(repo_id + file_path)` in `OnlyOfficeDocKey` (unique on `repo_id_file_path_md5`), else created | **stable across content versions and across concurrent users** -> the same editing session, i.e. co-editing |

> **Note, added after the independent review.** This "one key per document"
> property is what makes ONLYOFFICE's co-editing possible. **Our integration
> does not want that property**: the ArtCraft gateway gives every user their
> own session, so two people editing the same file are two sessions, and the
> second save is refused as a conflict rather than merged. The stable key is a
> **session-isolation tool** for us, not a co-editing enabler. Real
> co-editing is out of scope for this project.

`OnlyOfficeDocKey` (`seahub/onlyoffice/models.py`) stores
`doc_key`, `username`, `repo_id`, `file_path`. On save/close the row is deleted
and the mapping is cached for 24 h.

## 3. The save flow (callback)

`seahub/onlyoffice/views.py::onlyoffice_editor_callback` (line 49, `@csrf_exempt`).

* Endpoint: `POST /onlyoffice/editor-callback/`
* Body: JSON `{key, status, url, users, actions, history, changesurl, lastsave, notmodified}`
* Response: `{"error": 0}` on success, `{"error": 1}` on failure. **The editor
  server shows an error message when `error: 1`.**

### 3.1 Status codes handled by Seafile

| Status | Meaning | Seafile behaviour |
| --- | --- | --- |
| 1 | user connected / disconnected | log only, return `{"error": 0}` |
| 2 | document ready for saving | **save**, then delete doc key, cache 24 h, unlock |
| 3 | save error | not handled -> `{"error": 1}` |
| 4 | closed with no changes | delete doc key, cache 24 h, unlock, no write |
| 6 | force save | **save**, same as 2 except the key is not deleted |
| 7 | force-save error | not handled -> `{"error": 1}` |

### 3.2 How the bytes get back into Seafile

```python
url = post_data.get('url')
onlyoffice_resp = requests.get(url, verify=VERIFY_ONLYOFFICE_CERTIFICATE)   # pull bytes from the editor server

fake_obj_id = {'online_office_update': True}
update_token = seafile_api.get_fileserver_access_token(repo_id, json.dumps(fake_obj_id), 'update', username)

files = {'file': (os.path.basename(file_path), onlyoffice_resp.content)}
data  = {'target_file': file_path}
update_url = gen_inner_file_upload_url('update-api', update_token)
resp = requests.post(update_url, files=files, data=data)
```

Two observations:

1. **The editor server is pulled from**, not pushed to. The editor must expose
   the saved bytes at a URL that the *Seafile host* can reach. Our Craft
   integration must either do the same (serve the bytes) or flip the direction
   (the browser posts the bytes to Seafile) — flipping avoids a server-to-server
   round trip and removes a whole class of SSRF/URL-fetch concerns.
2. **The write is authorised by a capability token**, not by a user session:
   `get_fileserver_access_token(repo_id, {'online_office_update': True}, 'update', username)`.
   The `'update'` permission on the repo is what allows replacing the file.

## 4. Locking

* `seahub/utils/file_op.py:13` -> `ONLINE_OFFICE_LOCK_OWNER = 'OnlineOffice'`
* Lock taken when the editable document is opened:
  `seafile_api.lock_file(repo_id, path, ONLINE_OFFICE_LOCK_OWNER, ...)`
* Refreshed from the browser while the editor is open
  (`seahub/templates/view_file_onlyoffice.html`):

```javascript
url: '{% url "api-v2.1-file-view" repo_id %}?p=...'
type: 'PUT'
data: { 'operation': 'refresh-lock', 'expire': 2400 }     // 40 minutes
```

  For share links: `api-v2.1-share-link-online-office-lock` with the same
  `expire`.
* Unlocked on save (status 2) and on close-without-changes (status 4), Pro only.
* Other editors are blocked from the same file while the lock is held.

**This is a lease, not a compare-and-swap.** It prevents two *Seahub* editors
from working on the file at once, but it does **not** detect a stale write.

## 5. Concurrency: what Seafile does and does not do

**Verified in the deployed code: there is no version check on save.**

* The `file_id` is captured at open time and used for the download token and for
  the read-only `doc_key`.
* On save, the callback performs an **unconditional** `update-api` write.
* The only guard is the cooperative `OnlineOffice` lock.

Consequences:

* Two users inside the *same* Seafile+ONLYOFFICE stack are safe, because they
  share one `doc_key` and therefore one co-editing session inside ONLYOFFICE.
* A save from a **stale session** (browser asleep, lock lease expired, the file
  changed through another route such as a sync client or the WebDAV/API path)
  **silently overwrites** the newer content.
* The file is replaced by the editor's bytes; a history entry is created by
  Seafile's normal version mechanism, so the previous content is recoverable
  from the file history, but the overwrite itself is not prevented.

**Design consequence for ArtCraft (GR-008):** our integration should compare the
`file_id` / `obj_id` observed at open time with the current `file_id` at save
time and refuse to overwrite silently. This is strictly better than the
reference implementation and is achievable with primitives Seafile already
exposes (`get_file_id_by_path` / file history API).

## 6. The multi-office-suite mechanism (Professional) — the key GR-002 input

`seahub/views/file.py::get_office_feature_by_repo` (line 156) resolves, in order:

1. an explicit per-library `RepoExtraConfig` row (`config_type='office'`),
2. a role default from `ROLES_DEFAULT_OFFCICE_SUITE`,
3. the entry of `OFFICE_SUITE_LIST` whose `is_default` is true.

The shipped list (`seahub/settings.py:1023`):

```python
OFFICE_SUITE_LIST = [
    {"id": "onlyoffice",   "name": "OnlyOffice",     "is_default": True},
    {"id": "collabora",    "name": "CollaboraOnline", "is_default": False},
]
```

**The dispatcher is hardcoded to those two ids:**

```python
if default_suite.get('id') == 'onlyoffice': enable_onlyoffice = True
if default_suite.get('id') == 'collabora':  enable_office_app  = True
```

So the "add another office suite" idea is **not** configuration-only. Adding an
`artcraft` suite requires changing `seahub/views/file.py` and adding editor
views — i.e. a **patch**, not a plugin.

Per-library selection is exposed by
`seahub/api2/endpoints/repo_office_suite.py::OfficeSuiteConfig`
(`GET`, Pro-only via `IsProVersion`, `can_choose_office_suite()`).

## 7. Share links and anonymity

* `share_link_token` presence switches the lock refresh to
  `api-v2.1-share-link-online-office-lock`.
* When the request is not authenticated, the editor config carries
  `customization.anonymous = {request: True, label: "Guest"}` and no `user` block.
* `get_onlyoffice_dict` receives `can_edit`, `can_download`, `can_copy` and
  propagates them into `document.permissions` and `editorConfig.mode`
  (`edit` vs `view`).

## 8. What the browser actually loads

```text
GET /onlyoffice/...            ->  the Seahub page (full page, not an iframe)
  <script src="<ONLYOFFICE_APIJS_URL>">   -> same origin as Seahub (via the reverse proxy)
  <script src="js/base.js">                -> Seahub's own JS
  -> new DocsAPI.DocEditor("placeholder", config)
```

Because ONLYOFFICE is reverse-proxied under the **same origin** as Seahub
(`/onlyoffice/` on the same vhost), the editor frame is same-origin with the
host page. The saved bytes are fetched server-to-server over the internal
network, and the `document.url` points at the public vhost.

## 9. Summary of the contract, in one table

| Aspect | Seafile's ONLYOFFICE contract | Implication for ArtCraft |
| --- | --- | --- |
| Host surface | a full Seahub page hosting the editor | our Craft host can be a page too; a nested iframe is optional |
| Open | Seahub issues a download token for the file id and a signed config | we need an equivalent "open" capability: bytes + identity + permissions |
| Identity of the session | `doc_key` (stable per repo+path for editable files) | we need a session id mapping to (repo, path, user, permissions) |
| Save direction | editor server is pulled by the Seafile host | we can let the **browser** deliver the bytes, which is simpler and safer |
| Save authorisation | file-server access token with `'update'` permission on the repo | a per-session, per-file update capability |
| Write semantics | unconditional replace, new version created | **improve**: compare obj_id at save time, refuse silent overwrite |
| Concurrency guard | cooperative `OnlineOffice` lock with a 40-minute lease | keep the lock, add the obj_id check |
| Read-only | `editorConfig.mode = "view"`, `permissions.edit = false` | must be enforced server-side, not only in the editor |
| Editor errors | callback answers `{"error": 1}` | our save endpoint must answer an explicit failure the editor can show |
| Extensibility | hardcoded to `onlyoffice` / `collabora` | adding `artcraft` needs a patch (GR-002) |

## 10. Reproduction commands

```sh
# module layout
pct exec 108 -- ls -la /opt/seafile/seafile-server-12.0.14/seahub/seahub/onlyoffice

# the contract builder
pct exec 108 -- cat /opt/seafile/seafile-server-12.0.14/seahub/seahub/onlyoffice/utils.py

# the save callback
pct exec 108 -- sed -n '49,213p' \
  /opt/seafile/seafile-server-12.0.14/seahub/seahub/onlyoffice/views.py

# the host page
pct exec 108 -- cat \
  /opt/seafile/seafile-server-12.0.14/seahub/seahub/templates/view_file_onlyoffice.html

# the suite dispatcher
pct exec 108 -- sed -n '150,200p' \
  /opt/seafile/seafile-server-12.0.14/seahub/seahub/views/file.py
```

All commands are read-only (`cat`, `sed -n`, `ls`, `grep`).
