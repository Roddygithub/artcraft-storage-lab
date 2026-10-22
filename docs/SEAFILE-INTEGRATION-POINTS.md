# Seafile integration points

Status: **PROVISIONAL — FREE REVIEW PENDING** · GPT REVIEW: PENDING
GR-002 · Owner: artcraft-owner · Architecture: artcraft-architect (GR-001/GR-003)

## 0. The short answer

> **Seafile already ships a generic, configuration-only hook for third-party
> online editors: `seahub/thirdparty_editor/`.** It is present in the open-source
> `haiwen/seahub` **and** in the deployed Professional 12.0.14 build.
>
> With it, the whole ArtCraft integration can be built **without touching
> Seafile's code**: one `seahub_settings.py` entry maps file extensions to the
> URL of our host page, and the hook takes care of the session, the
> permissions and the file-content delivery.
>
> The catch: the hook is **read-only by design** ("Only can preview file for
> now"), and it **shadows ONLYOFFICE** for any extension it claims. Both are
> addressed below, and both lead to one small, generic, upstreamable patch.

---

## 1. The candidates, evaluated

| Candidate | Verdict | Why |
| --- | --- | --- |
| **Seahub "third-party editor" hook** (`ENABLE_THIRDPARTY_EDITOR` + `THIRDPARTY_EDITOR_ACTION_URL_DICT`) | **CHOSEN for the MVP** | exists upstream *and* in Pro; configuration-only; already implements the session, the permission record and the content delivery; no fork |
| Custom online-editor integration in `seahub/views/file.py` | rejected for now | it is what the third-party hook already is, only worse (a hard fork) |
| External editing service (our own, on our own URL) | **CHOSEN, as a component** | this is the "action_url" the hook points at; it hosts the Craft app and owns the write |
| Iframe host page | **CHOSEN, as a component** | the Craft `?host=parent` bridge needs a same-origin parent page |
| Seahub app (`seahub/<app>/` with `urls.py`) | rejected for now | the third-party hook already gives the URLs; a full app is more moving parts and would still need the file-list change |
| Small integration gateway | **CHOSEN, as a component** | it is the "external editing service"; it holds the Seafile credential and applies the conflict check |
| Upstream Seahub patch | **CHOSEN, deferred** | needed for (a) the write path and (b) not shadowing ONLYOFFICE. Prepared, not published (GPT gate) |

---

## 2. How the third-party editor hook works

### 2.1 The configuration

```python
# seahub_settings.py
ENABLE_THIRDPARTY_EDITOR = True
THIRDPARTY_EDITOR_ACTION_URL_DICT = {
    'pdf': 'https://<host>/artcraft/pdfcraft/',
    'svg': 'https://<host>/artcraft/vectorcraft/',
}
THIRDPARTY_EDITOR_ACCESS_TOKEN_EXPIRATION = 12 * 60 * 60     # default
```

Keys are **file extensions without the dot**, lowercase
(`get_file_type_and_ext()` returns `os.path.splitext(name)[1][1:].lower()`).

### 2.2 The flow, in the actual code

`seahub/views/file.py::view_lib_file` (line 642 upstream, line 594 in the
deployed 12.0.14):

```python
if ENABLE_THIRDPARTY_EDITOR:
    filename = os.path.basename(path)
    filetype, fileext = get_file_type_and_ext(filename)
    action_url = THIRDPARTY_EDITOR_ACTION_URL_DICT.get(fileext, '')
    if action_url:
        user_repo_path_info = {
            'request_user': request.user.username,
            'repo_id': repo_id,
            'file_path': path,
            'permission': { 'can_edit': False },     # "Only can preview file for now"
        }
        uid = uuid.uuid4()
        access_token = uid.hex
        cache.set('thirdparty_editor_access_token_' + access_token,
                  user_repo_path_info, THIRDPARTY_EDITOR_ACCESS_TOKEN_EXPIRATION)
        editor_dict = {'filename': filename, 'action_url': action_url,
                       'access_token': access_token,
                       'access_token_ttl': int(time.time()) + THIRDPARTY_EDITOR_ACCESS_TOKEN_EXPIRATION}
        return render(request, 'view_file_thirdparty_editor.html', editor_dict)
```

`seahub/templates/view_file_thirdparty_editor.html`:

```html
<form id="office_form" target="office_frame" action="{{action_url}}" method="post">
    <input name="access_token" value="{{access_token}}" type="hidden"/>
    <input name="access_token_ttl" value="{{access_token_ttl}}" type="hidden"/>
</form>
<iframe id="office_frame" name="office_frame"></iframe>
<script>document.getElementById('office_form').submit();</script>
```

So the browser **POSTs the access token to our URL**, and the response is
rendered **inside the iframe**. The editor is therefore a *separate document*,
in an iframe, on **our** origin — not a same-origin child of the Seahub page.

### 2.3 The API the editor uses

`seahub/thirdparty_editor/urls.py`:

```text
GET /thirdparty-editor/file-info/?access_token=...    -> { username, repo_id, file_name, file_size, file_path }
GET /thirdparty-editor/file-content/?access_token=...  -> application/octet-stream
```

Both are guarded by `access_token_check`, which:

* looks the token up in the Django cache;
* validates that the user still exists and the library still exists;
* **re-reads the current object id** and 404s if the file is gone.

`file-content` mints a file-server access token for the object id with the
`'view'` permission and proxies the bytes.

---

## 3. The ten questions of GR-002, answered

### Q1 — Can a new online editor be registered cleanly?

**Yes, by configuration** — `THIRDPARTY_EDITOR_ACTION_URL_DICT` maps an
extension to a URL. No code change, no fork, no plugin install.

**But** it is a *preview* hook: it grants the editor a read-only session
(`'can_edit': False`, "Only can preview file for now"), and it offers no way to
write back. Writing is our job (see Q4) and it is the one thing that needs an
upstream patch if we want the write to happen *as the user*.

### Q2 — Can extensions be associated by type?

**Yes.** The dispatcher is `THIRDPARTY_EDITOR_ACTION_URL_DICT`, keyed by
extension. It is a plain dict in `seahub_settings.py` — editable without
touching the code, and readable by our gateway so both sides can agree on the
mapping.

Contrast with ONLYOFFICE, whose extension lists are three different settings
(`ONLYOFFICE_FILE_EXTENSION`, `ONLYOFFICE_EDIT_FILE_EXTENSION`, and per-type
lists `ONLYOFFICE_EXT_WORD/CELL/SLIDE/PDF/DIAGRAM`), all global and not
per-library.

### Q3 — How does Seafile provide the file?

Two ways, both server-side:

1. **The hook's own API** — `GET /thirdparty-editor/file-content/?access_token=…`
   returns the bytes, using a file-server token minted for the current object
   id with the `'view'` permission. The token is bound to (repo, path, user)
   by the cache entry.
2. **Our own seafhttp call** — our gateway can mint its own download token via
   `GET /api2/repos/{repo_id}/file/detail/` + the file server.

Option 1 is the natural one for the MVP: it needs no Seafile credential at all
on our side, because the access token *is* the credential.

### Q4 — How must a save be returned?

Today: **it cannot.** The hook has no write endpoint.

Two ways forward:

| Option | Mechanism | Pros | Cons |
| --- | --- | --- | --- |
| **B — our gateway writes** | our gateway calls `GET /api2/repos/{repo_id}/update-link/` and POSTs the bytes to the seafhttp `update-api` | **no Seafile code change at all**; works on both editions; full control over the conflict check | the new version is attributed to the **service account**, not the user; the gateway holds a Seafile credential |
| **A — a new endpoint in `thirdparty_editor`** | `POST /thirdparty-editor/file-save/?access_token=…` with the bytes | the write happens **inside Seahub as the user**: correct attribution, correct permission check, correct lock handling, correct history | requires a **Seafile patch** (upstreamable, but gated on GPT) |

**Recommendation: B for the MVP, A prepared as the upstream patch (GR-014).**
B gets the whole flow working with zero Seafile changes, which is the
strongest possible demonstration; A is the better long-term shape and is a
small, generic, defensible contribution.

### Q5 — How is a new version created?

By writing through the file server's update endpoint, which creates a new
commit in the library — the normal Seafile versioning mechanism. The file
history then shows the new version, attributed to whoever the write token was
minted for.

### Q6 — How are permissions and sharing preserved?

* The **read** path is already correct: the access token is bound to
  `request_user`, `repo_id` and `file_path` by the cache entry, and the
  `file-content` view re-checks that the library and the file still exist.
* The **write** path must be checked by our gateway, every time, against the
  *current* permission — not the permission recorded when the session opened.
  `GET /api2/repos/{repo_id}/file/detail/?p=…` returns the caller's
  `permission` string, which is the cheapest way to re-check.
* **Share links are not covered**: the third-party hook only exists in
  `view_lib_file`. `view_shared_file` and `view_file_via_shared_dir` have their
  own branches and no third-party-editor path. Share-link editing would need
  the upstream patch (A) to cover it, or a separate design.

### Q7 — How is read-only handled?

* The hook hardcodes `'can_edit': False` in the token record — it is a preview
  hook.
* Our gateway therefore decides the mode, from the *real* permission, and
  enforces it server-side on every write.
* The Craft app is told "view" by simply not sending a save path, or by
  sending the document with `can_edit: false`; the server refuses a write
  regardless.

### Q8 — What part needs a Seahub modification?

| Change | Size | Needed for |
| --- | --- | --- |
| a write endpoint in `thirdparty_editor` | ~60 lines | writing as the user, share-link support |
| `can_edit` taken from the real permission instead of `False` | ~5 lines | the editor knowing it may write |
| an `artcraft` office-suite id in `get_office_feature_by_repo` | ~20 lines | per-library selection, so ONLYOFFICE keeps the other libraries |
| the third-party hook in the share-link views | ~20 lines | share-link editing |

None of these is required to reach the MVP. All are small and generic.

### Q9 — Can we avoid a permanent fork of Seafile?

**Yes.** The MVP needs **zero** Seahub code changes: configuration only.

The upstream patch (option A) is *optional* and, if accepted, is a small
additive change to an existing generic app — not a fork.

### Q10 — What architecture would be acceptable upstream?

The patch that upstream would most likely accept is the one that makes the
**existing generic hook** able to write:

```text
seahub/thirdparty_editor/views.py   + a save endpoint
seahub/thirdparty_editor/urls.py    + one route
seahub/thirdparty_editor/settings.py+ a per-extension "editable" map
seahub/views/file.py                + the real permission in the token record
```

That is small, generic, editor-agnostic, and useful to anyone embedding a
third-party editor (Nextcloud-style integrations, Collabora-style, and the
ArtCraft suite). It does **not** mention ArtCraft — that stays on our side.

---

## 4. The shadowing problem (and why it decides the roadmap)

In `view_lib_file`, the third-party-editor branch is at line **642** and the
ONLYOFFICE branch at line **875** — the third-party branch is **first**:

```python
if ENABLE_THIRDPARTY_EDITOR:            # 642
    ... return render(request, 'view_file_thirdparty_editor.html', ...)
...
elif (... ENABLE_ONLYOFFICE and fileext in ONLYOFFICE_FILE_EXTENSION):   # 875
    ... return render(request, 'view_file_onlyoffice.html', ...)
```

**Consequence: an extension present in `THIRDPARTY_EDITOR_ACTION_URL_DICT`
stops being handled by ONLYOFFICE.** The two integrations compete per
extension, and the third-party one wins.

This directly collides with the project rule *"the existing Seafile ↔ ONLYOFFICE
integration must stay functional"*.

### 4.1 The deployed configuration, and the free extensions

The deployed `seahub_settings.py` has:

```python
ONLYOFFICE_FILE_EXTENSION = ('doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx',
                             'odt', 'fodt', 'odp', 'fodp', 'ods', 'fods',
                             'csv', 'ppsx', 'pps')
ONLYOFFICE_EDIT_FILE_EXTENSION = ('docx', 'pptx', 'xlsx')
```

Extensions **not** claimed by the deployed ONLYOFFICE configuration, and
therefore free for the first proof:

```text
pdf   svg   odg   fodg   wps   wpt   pages   txt   md   html   rtf   epub ...
```

**`.pdf` and `.svg` are free.** And **PdfCraft already ships a `?host=parent`
bridge** — so the very first end-to-end proof needs:

* no Seahub code change,
* no ArtCraft code change,
* no extension that ONLYOFFICE claims.

That is the **GR-005 first technical proof**: PDF via PdfCraft.

### 4.2 The WordCraft MVP (GR-006) needs a decision

`.docx` **is** claimed by the deployed ONLYOFFICE configuration, so
`THIRDPARTY_EDITOR_ACTION_URL_DICT['docx']` would take `.docx` away from
ONLYOFFICE. Options:

| Option | ONLYOFFICE impact | Assessment |
| --- | --- | --- |
| (a) claim `docx` in the third-party dict | `.docx` no longer opens in ONLYOFFICE | **rejected**: it degrades the existing integration |
| (b) use a **dedicated synthetic library** for the ArtCraft proof, and accept that only *that* library's `.docx` goes to ArtCraft | ONLYOFFICE keeps every other library | **acceptable for the MVP**, but the per-extension dict is global, so `.docx` would be taken from *every* library — so this needs (c) or (d) |
| (c) add an `artcraft` office-suite id upstream (option A, extended) | per-library choice; ONLYOFFICE remains the default | **the right long-term answer** |
| (d) claim `docx` only in a **separate Seahub deployment** (a test instance with its own `seahub_settings.py`) | production untouched | **acceptable for the MVP**; needs a test Seafile (mission §42) |

**Recommendation:** GR-005 on `.pdf`/`.svg` against the existing instance
(zero risk), and GR-006 (WordCraft `.docx`) against a **dedicated test Seahub
instance** with its own settings, so the production ONLYOFFICE configuration is
never touched. The upstream patch (c) is prepared in parallel and is the
production answer.

---

## 5. The chosen architecture

```text
                    Seafile Web (Seahub)
                            |
                            | click rapport.docx
                            v
              view_lib_file -> thirdparty_editor branch
                            |  (config only, no code change)
                            |  POST access_token + access_token_ttl
                            v
     +----------------------------------------------+
     |  our host page  (our origin, our service)    |
     |                                              |
     |  1. GET /thirdparty-editor/file-info/        |
     |  2. GET /thirdparty-editor/file-content/     |
     |  3. checks permission, size, lock            |
     |  4. renders <iframe src="...?host=parent">   |
     |                                              |
     |  <Craft app> -- wordcraft:ready              |
     |  host       --> wordcraft:open {name,bytes}  |
     |  <Craft app> -- wordcraft:save {name,bytes}  |
     |  5. conflict check (obj_id)                 |
     |  6. seafhttp update-api -> new Seafile version
     |  7. host tells the user "saved"              |
     +----------------------------------------------+
                            |
                            v
                    Craft web build (static files)
```

### 5.1 What is in Seafile, what is in our service, what is in the Craft app

| Concern | Where | Why there |
| --- | --- | --- |
| extension -> editor | `THIRDPARTY_EDITOR_ACTION_URL_DICT` (Seafile) + the same map in our service | the dispatcher must be one table, and Seafile's is the entry point |
| the session | Seafile's cache (the access token) | already implemented, already bound to the user |
| the credentials | **our service only** | the browser never sees a Seafile credential |
| the write | our service -> seafhttp | no Seafile code change for the MVP |
| the conflict check | our service | needs the obj_id, which only the service can compare |
| the document bytes | Seafile -> our service -> the browser | the browser never gets a Seafile URL with a token |
| the editor protocol | the Craft app | storage-agnostic by construction |

### 5.2 Why the Craft app is served by our service and not by Seafile

The Craft `?host=parent` bridge requires the parent page and the Craft page to
be **same-origin**. In the third-party hook the parent of the Craft app is
**our host page**, not the Seahub page. So the Craft static files must be
served from **our origin**, next to the host page. The reverse proxy then has
two additive locations: `/artcraft/<app>/` (static) and `/artcraft/open/`
(our service).

This also keeps the Seahub page and the Craft app in **different origins**,
which is better: the Craft app cannot read the Seahub DOM, and the
`postMessage` bridge is scoped to the Craft app's own origin, with the parent
identity checked.

---

## 6. Known limitations of the chosen path

| # | Limitation | Consequence | Mitigation / plan |
| --- | --- | --- | --- |
| L1 | the hook is **read-only** | we must write ourselves | option B (our gateway) for the MVP; option A (upstream patch) for the production shape |
| L2 | the hook **shadows ONLYOFFICE** per extension | `.docx` cannot be claimed without taking it from ONLYOFFICE | GR-005 on `.pdf`/`.svg`; GR-006 on a dedicated test instance; upstream patch (c) for production |
| L3 | **share links** are not covered by the hook | share-link editing is not available | upstream patch; documented as out of scope for the MVP |
| L4 | the write is attributed to the **service account** | the file history shows the service account, not the user | option A fixes it; otherwise documented |
| L5 | the hook does not check the **file lock** or the **online-preview size limit** | we must check them ourselves | our gateway does |
| L6 | the access token lives 12 h in the Django cache | a leaked token is valid for 12 h | our gateway uses it only to fetch the content, never as a bearer credential for the browser; the session we hand to the browser is short-lived and opaque |
| L7 | the hook does not know the file's **object id** | no conflict check is possible from the hook's data alone | our gateway reads the obj_id itself via `file/detail` |

---

## 7. What we are NOT going to do

* **Not** fork Seafile.
* **Not** patch the production `seahub_settings.py` in a way that takes an
  extension away from ONLYOFFICE.
* **Not** reimplement Seafile's file view.
* **Not** build 13 separate Seafile plugins — one gateway, one dispatcher.
* **Not** publish anything upstream before `GPT REVIEW PASS`.

---

## 8. Evidence index

| Claim | Source |
| --- | --- |
| the hook exists upstream | `haiwen/seahub@c01d46bcaa0b2ce24c71561c6c61d15fea808d1a` (2026-10-21): `seahub/thirdparty_editor/{__init__,settings,urls,views}.py` |
| the hook exists in the deployed Pro build | `/opt/seafile/seafile-server-12.0.14/seahub/seahub/thirdparty_editor/`, `seahub/urls.py:230` |
| the open branch | `seahub/views/file.py:642` upstream, `:594` deployed |
| the template | `seahub/templates/view_file_thirdparty_editor.html` |
| the API | `seahub/thirdparty_editor/urls.py` + `views.py` |
| the shadowing | order of the branches in `seahub/views/file.py` (642 before 875 upstream) |
| the deployed ONLYOFFICE extension list | `/opt/seafile/conf/seahub_settings.py` |
| the write primitives | `haiwen/seafile-server` `fileserver/fileop.go`; `docs/reviews/GR-008/SEAFILE-CONCURRENCY-PRIMITIVES.md` |
| the ONLYOFFICE contract | `docs/reviews/GR-001/DEPLOYED-INSTANCE-CONTRACT.md` |
