# Upstream plan

Two upstream contributions are prepared. **Neither is published.** The hard gate
holds: nothing goes to `storytold/*` or to Seafile before `GPT REVIEW PASS`.

| Contribution | Target | Licence of the target | Where the patch lives |
| --- | --- | --- | --- |
| the Craft Web host bridge | `storytold/wordcraft` (+ the other apps) | MIT OR Apache-2.0 | **in this repository**: `docs/reviews/GR-014/DIFF.patch` |
| per-library dispatch and conditional-save route | `haiwen/seahub` + `haiwen/seafile-server` | **verify at target revision** | **in this repository**: `docs/reviews/GR-015/` |

The split is a repository-boundary and maintenance constraint: this repository
does not copy or vendor Seafile/Seahub code. The exact target licence must be
verified at the revision selected for any upstream contribution
(`docs/LICENSING.md`).

---

## 1. ArtCraft — the host bridge

**Not ready for upstream.** Sol found incomplete runtime evidence, semantic
reopen proof, and licensing/provenance packaging. Keep publication locked.

* Target: `storytold/wordcraft`, branch `main` at
  `00bc6a4b028013b2dfb0e85e8b326aeed3ecff6d`.
* Size: 4 files, +261 / −4.
* What it adds: the `?host=parent` bridge that GridCraft, PdfCraft and CADCraft
  already have, plus the **save confirmation** they are missing.
* What it reuses: `crates/ui-egui/src/async_saves.rs` — the ticket mechanism the
  suite already has.
* Verified: the patch compiles and has a local WordCraft browser harness with
  synthetic storage. The real Seafile DOCX edit/save/version/close/reopen flow is
  **NOT VERIFIED** (`docs/reviews/GPT-SOL-REREVIEW-AFEC19E.md`).

### 1.1 The follow-ups, in order

| # | Change | Target | Why |
| --- | --- | --- | --- |
| A-1 | the shared crate: the message types, the transport, the origin and source checks | **new crate in `storytold/craft-libs`** | three copies of the same 200 lines have already drifted |
| A-2 | move GridCraft, PdfCraft and CADCraft onto it | their `apps/*-web` crates | one vocabulary instead of three |
| A-3 | give GridCraft's copy the **save answer** it cannot express today | `gridcraft/crates/ui-egui/src/lib.rs` | its `download` hook has no `Result`; the fix is a `Result` in the signature |
| A-4 | the bridge for the ten applications that have none | `apps/<app>-web` | one per app, each a few lines once A-1 exists |
| A-5 | the browser-shaped services for the four that have none | `figcraft` (`NoServices`), `filmcraft`, `effectcraft` (`FsServices`), and the others | the seam has to exist before a bridge can be wired to it |
| A-6 | the **desktop** control protocol in the shared crate | `docs/control-protocol.md`, 12 of 13 apps | a later phase; the browser and the desktop speaking one vocabulary |

### 1.2 What would make the maintainers say no, and the answer

| Objection | Answer |
| --- | --- |
| "three copies already work" | they have **already drifted** (PdfCraft adds `saveAs`, GridCraft cannot report a failed save, CADCraft hooks the engine). The drift is the argument for the shared crate. |
| "the bridge is only needed by one project" | the bridge is **platform-agnostic**: it carries bytes, and the host decides what to do with them. The reference integration is one host; the Nextcloud-style embedding is named in the existing bridges' own comments. |
| "it adds a dependency" | it does not. `wasm-bindgen` and `web-sys` are already there. |
| "it changes the app" | it does not, unless the page says `?host=parent`. The desktop app is untouched. |

---

## 2. Seafile — a write path in the third-party-editor hook

**Specified, not written into this repository.** The target patch remains an
external artifact; this repository does not vendor Seafile/Seahub code.

### 2.1 The problem it solves

Seafile's `seahub/thirdparty_editor/` is a **generic, configuration-only** hook
for third-party online editors. It is present in the open-source upstream and in
the Professional build. It:

* maps a file extension to a URL (`THIRDPARTY_EDITOR_ACTION_URL_DICT`),
* mints an access token for the document and caches it for 12 hours,
* serves the document's metadata and bytes to the editor.

It is **read-only by design**: the token record carries
`permission: {'can_edit': False}` — the source says *"Only can preview file for
now"* — and there is **no write endpoint at all**.

So an editor that embeds into Seafile can read a document and cannot give it
back. The reference integration works around this by writing with **its own**
credential, which has two consequences:

* the new version is attributed to the **service account**, not to the person who
  edited the document — wrong in a document library's audit trail;
* the write is not checked against the *user's* permission at the moment of the
  write, only by our own service.

### 2.2 The patch, precisely

**A new view** in `seahub/thirdparty_editor/views.py`:

```text
POST /thirdparty-editor/file-save/?access_token=...
Content-Type: multipart/form-data
  file        the new content
  target_file the path, as the file server's update API wants it
```

It would do, in order:

1. the same `access_token_check` the other two views use — the token names the
   user, the library and the path;
2. a **permission check on the user's real permission** for that path
   (`check_folder_permission` + `parse_repo_perm(permission).can_edit_on_web`),
   which the current token record does not carry;
3. a **conflict check**: compare the file's current content id with the one the
   token was minted for, and refuse when they differ. The token record would have
   to carry that content id — it is available at the moment the token is created
   (`seafile_api.get_file_id_by_path`), and it is exactly what the file server's
   download token is already bound to;
4. the write, with a file-server access token for the `'update'` permission,
   minted **for the user** — so the new version is attributed to them;
5. the new content id, as the answer.

**A new route** in `seahub/thirdparty_editor/urls.py`.

**Two small changes** in `seahub/views/file.py`:

* the token record keeps the **real permission** instead of the hardcoded
  `{'can_edit': False}`;
* it also keeps the **content id** the document had when the session started.

### 2.3 Why it is a good upstream contribution

* it is **editor-agnostic**: the words "Craft", "Word", "Spreadsheet" do not
  appear in it;
* it **completes an existing, generic mechanism** rather than adding a new one;
* it is **small** — a view, a route, two fields in a dict;
* it fixes a real gap that the upstream code comments acknowledge
  (*"Only can preview file for now"*);
* the same shape would serve the Collabora path and any other third-party editor.

### 2.4 The share-link case

The hook only exists in `view_lib_file`. `view_shared_file` and
`view_file_via_shared_dir` have their own branches and no third-party path, so
**share links are not covered** by the hook, and would need the same patch
applied to them. That is stated as a limitation, not hidden.

### 2.5 Where the patch will live

Outside this repository, in a separate working directory, so that no upstream code
is committed here:

```text
~/Projects/seafile-thirdparty-save-patch/
  README.md        the full specification, in the patch's own words
  seahub.patch     the diff against haiwen/seahub (3 files, +90/-3)
  BASE_COMMIT.txt  the upstream commit it applies to
```

Base: `haiwen/seahub` at `c01d46bcaa0b2ce24c71561c6c61d15fea808d1a` (2026-10-21).

The patch is **prepared**, not applied to the reference instance, and not
published. It has been checked for syntax and for import cycles, but it has
**not** been executed against a running Seahub: that needs a test instance, and
it is the first thing to do once the GPT review has passed.

---

## 3. The publication plan, and the gate

```text
NOW      the patches are prepared and reviewed here
         GPT REVIEW PASS
THEN     a branch on the target, a focused pull request, one review cycle
         the issue, if one is needed, opens the discussion
```

The order is deliberate: the ArtCraft patch is the smaller and the less
controversial one, and it is the one that unblocks the reference integration's
own development. The Seafile patch is the one that changes the audit trail of a
document library, and it deserves its own discussion.

**Until `GPT REVIEW PASS`, none of this is published.**
