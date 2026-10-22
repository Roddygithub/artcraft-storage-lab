# Authentication and authorization

Status: **PROVISIONAL — FREE REVIEW PENDING** · GPT REVIEW: PENDING
Evidence: `docs/reviews/GR-001/DEPLOYED-INSTANCE-CONTRACT.md`,
`docs/reviews/GR-008/SEAFILE-CONCURRENCY-PRIMITIVES.md`

## 0. The rule

> The browser must never receive a credential that grants more than
> *read this one file* and *write this one file, once, for this session*.

Everything below is derived from Seafile's real token model, not from a generic
web-app pattern.

## 1. What Seafile actually offers

| Credential | Where it lives | Scope | Lifetime | Verdict for our use |
| --- | --- | --- | --- | --- |
| **Account token** (`POST /api2/auth-token/`, `Authorization: Token <t>`) | user / server | the whole account, all libraries | until revoked | **Never** in the browser |
| **Django session cookie** | browser | the Seahub web session | session | Only for the Seafile page that hosts the editor |
| **seafhttp access token** (36-char token in the URL path) | server-side DB row (`seafile_web_query_access_token`) | `repo-id` + `obj-id` + `op` + `username` | row lifetime | Server-side only |
| **Share-link token** (20 chars) | URL | one file/dir, optional password, optional expiry | configured | Server-side only |

### 1.1 The seafhttp access token, precisely

From `haiwen/seafile-server` (`fileserver/fileop.go`):

```go
webaccess, err := rpcclient.Call("seafile_web_query_access_token", token)
// fields: repo-id, obj-id, op, username
```

and the operation is checked against the token:

```go
if strings.Index(urlOp, op) != 0 {
    return "Operation does not match access token."   // 403
}
```

### 1.2 The operation that matters for writing: `update`

The permission check is **repo + user + op**, not file-scoped:

```go
perm := share.CheckPerm(repoID, user)
if perm == "r" && op == "upload" { /* 403 */ }
```

The object id is only interpreted for non-update operations:

```go
if op != "update" {
    obj := map[string]interface{}{}
    json.Unmarshal([]byte(id), &obj)
    parentDir := obj["parent_dir"]
    fsm.parentDir = parentDir
}
```

and the parent-directory constraint is only enforced on the **upload** path:

```go
// doUpload()
if !isParentMatched(fsm.parentDir, parentDir) {
    return "Parent dir doesn't match."   // 403
}
```

**Consequence, and it matters:**

| Token type | Path scoping | Safe to hand to a browser? |
| --- | --- | --- |
| `op=upload` with `parent_dir` in the obj id | enforced (403 on mismatch) | still no |
| `op=update` (obj id `'dummy'` or `{'online_office_update': True}`) | **not enforced** — grants update on any file of the library, for that user | **never** |

Seafile's own ONLYOFFICE callback keeps the update token on the server and
uses it in a server-to-server POST. We must do the same.

## 2. The design

```text
Browser                     Seafile page                Our integration service        Seafile
   |                            |                               |                        |
   |-- click file ------------->|                               |                        |
   |                            |--- POST /artcraft/session ---->|                        |
   |                            |    (Seahub session cookie)     |                        |
   |                            |                               |-- validate session --->|
   |                            |                               |<-- file id + perms -----|
   |<-- host page + iframe -----|                               |                        |
   |                            |                               |                        |
   |---- editor asks for bytes -|--> POST /artcraft/session/<sid>/open                  |
   |                            |                               |-- issue file-server      |
   |                            |                               |   download token ----->|
   |                            |                               |<-- bytes --------------|
   |<-- bytes ------------------|                               |                        |
   |                            |                               |                        |
   |---- editor returns bytes --> POST /artcraft/session/<sid>/save                   |
   |                            |                               |-- conflict check ------>|
   |                            |                               |<-- current file id -----|
   |                            |                               |-- write (update token,  |
   |                            |                               |   server-side) ------->|
   |                            |                               |<-- new file id --------|
   |<-- {ok:true, version} -----|                               |                        |
```

### 2.1 The browser-side credential is **ours**, not Seafile's

The browser holds:

* a **session id** for the editing session, bound server-side to
  (repo_id, file_path, file_id, user, permissions, expiry);
* nothing else. No Seafile token, no seafhttp token, no account token, no JWT secret.

The session id is:

* **unpredictable** (>= 128 bits of entropy),
* **single-document**,
* **short-lived** (proposed: 30 minutes, refreshed only while the editor is
  actively saving),
* **single-action-scoped** by the server-side record, not by the token's shape.

### 2.2 Why not a signed capability token in the browser?

A signed, self-contained token (JWT) would be stateless and attractive, but:

* it cannot be revoked, and Seafile permission changes must take effect
  immediately (the "permission revoked while editing" test case);
* the "file was modified by someone else" check needs server-side state anyway
  (or at least a round trip to compare the file id);
* a JWT in the browser is a bearer token that leaks through logs, `Referer`,
  and browser history.

A server-side session record is the smaller, safer thing. The cost is one
session store; the benefit is immediate revocation and a single place to enforce
the conflict rule.

*Decision: server-side session record. Revisit if a stateless design becomes
necessary — it does not for this project.*

## 3. Authentication of the *host* to Seafile

The integration service authenticates to Seafile with an **account token** that
is:

* stored **server-side only** (environment/secret store), never in the repo,
* ideally **a dedicated service account** with access only to the libraries it
  serves,
* rotatable without touching the frontend.

Better still, the service should authenticate with the **user's own** identity
when the flow starts from a Seahub page, using the session cookie that the
browser already has, and only fall back to a service account for headless
operations. Seafile's Seahub pages accept both `SessionAuthentication` and
`TokenAuthentication` on the same views (verified: `seahub/api2/views.py`
`UpdateLinkView`, `FileDetailView`), so a same-origin `fetch` from the host
page can carry the session cookie.

*Decision to be confirmed at GR-002: cookie-forwarding (per-user identity,
no stored secret) vs service account (simpler, but a shared identity).*

## 4. Authorization checks that must happen server-side

The Craft editor runs in a frame the user controls the content of. **Every**
check below must be repeated by the integration service on each request. Nothing
may rely on the editor behaving.

| Check | When | How |
| --- | --- | --- |
| the session exists, is not expired, is not revoked | every request | session store |
| the session is bound to this file path | every request | session record |
| the user still has `can_edit` on the library/folder | every request | Seafile permission check |
| the user still has `can_download` (for the open step) | open | Seafile permission check |
| the file still exists and has the same content id | save | `get_file_id_by_path` comparison |
| the library still exists and is not read-only / frozen | save | Seafile repo status |
| the request body is the expected document, not something else | save | content type + size limits + optional hash pinning |

**Read-only must be enforced here.** A read-only session must never be able to
reach a write path, even if the editor sends a save request. The test matrix
row 2.18 ("read-only bypass attempt") exists for exactly this.

## 5. Sharing and anonymous access

Seafile's share links are a first-class case:

* the share link may be **read-only** — then the editor opens in view mode and
  the integration refuses to create a write session;
* the share link may have a **password** and an **expiry** — the integration
  must not create a session longer-lived than the link;
* the share link may point to a **sub-folder** — the session must be scoped to
  that scope.

The ONLYOFFICE implementation handles the share-link case by switching the lock
refresh endpoint (`api-v2.1-share-link-online-office-lock`) and by emitting an
`anonymous` customization block. We mirror the behaviour but keep the
authorization on our side.

## 6. What must never happen

```text
NEVER   a Seafile account token in JavaScript, in a URL, or in the repo
NEVER   a seafhttp update token in the browser          (it is repo-wide)
NEVER   a download token in the browser for a file the user cannot download
NEVER   a JWT secret, a session secret, or a password in the frontend
NEVER   a "Save" that reports success without a confirmed Seafile version
NEVER   a targetOrigin of "*" for a message that carries document bytes
```

## 7. Session lifetime

| Phase | Proposed value | Rationale |
| --- | --- | --- |
| editing session | 30 min, refreshed on each save | long enough for a work session, short enough that a leaked id is not useful for long |
| open token (file-server download) | server-side, minted per open, `use_onetime=True` if the endpoint allows it | one file, one use |
| update token (file-server update) | server-side, minted per save, discarded immediately | shortest possible exposure |
| our session id | 30 min, revoked on save-failure loops and on permission loss | |

`use_onetime=False` is what Seafile's own ONLYOFFICE flow uses for the download
token, because the editor server may fetch the document more than once. Our
integration controls the fetch, so a one-time token is preferable **if** the
endpoint supports it — to be verified.

## 8. Open questions

| # | Question | Resolution |
| --- | --- | --- |
| A-1 | Can the file-server download token be one-time for our flow? | to verify against `get_fileserver_access_token(..., use_onetime=True)` behaviour in the Go file server |
| A-2 | Does a *file-scoped* update token exist? | probably not (see 1.2); if not, our service must own the token and apply the path check itself |
| A-3 | Cookie forwarding vs service account | GR-002 |
| A-4 | Share-link expiry semantics | GR-002 / GR-009 |
| A-5 | Are the account-token scopes narrowable per library? | to verify in the Seafile API docs |
