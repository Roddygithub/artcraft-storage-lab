# Security

Status: **PROVISIONAL — FREE REVIEW PENDING** · GPT REVIEW: PENDING
GR-009 · Independent free review: `docs/reviews/REVIEW-01.md`, `REVIEW-02.md`

## 0. The threat model, in one picture

```text
   the browser                 the gateway                     Seafile
  ┌──────────────┐          ┌───────────────┐            ┌──────────────┐
  │  the Craft   │  postMsg │  the host     │  account   │  Seahub      │
  │  app (wasm)  │ ───────► │  page + the   │  token     │  + seafhttp  │
  │              │ ◄─────── │  service      │ ─────────► │              │
  └──────────────┘          └───────────────┘            └──────────────┘
        ▲                         ▲
        │ the user                │ the account token lives HERE and nowhere else
   the user's own machine
```

* The **Craft application** is a third-party WebAssembly module running in the
  user's browser. It is trusted to the extent that it is the user's editor, but it
  is **not** trusted with credentials, and it is not trusted to decide that a save
  succeeded.
* The **gateway** is the trust boundary. It holds the Seafile credential and it
  performs **every** authorisation check. It is the most security-critical
  component in the project, and it is the only one that must be right.
* **Seafile** is the storage system. Its file server is reached with
  narrowly-scoped, short-lived tokens.

### 0.1 The one rule that carries the most weight

> **An `op=update` file-server token is library-wide, not file-scoped.**
> (`haiwen/seafile-server`, `fileserver/fileop.go`: the object id is only
> interpreted for non-update operations, and the parent-directory constraint is
> only enforced on the upload path.)
>
> There is therefore **no** Seafile-native token that is safe to hand to a
> browser. The gateway's checks are therefore **not** defence-in-depth — they are
> the only defence. A single missed check is a library-wide write primitive
> exposed to the browser.

Everything below follows from that.

## 1. What the browser holds

| Credential | In the browser? | Why |
| --- | --- | --- |
| a Seafile account token | **no** | it would give the whole account |
| a seafhttp access token | **no** | an update token is library-wide; a download token is a URL the browser could leak |
| a Seahub session cookie | **no** | the browser is on a different origin from Seahub |
| the ONLYOFFICE JWT secret | **no** | it is a server-side secret |
| **an opaque session id** | **yes** | it is the *only* thing the browser holds |

The session id is:

* unguessable (24 bytes from `secrets.token_urlsafe`),
* bound server-side to **one** (repo, path, user, permission, content id),
* short-lived (30 minutes absolute, 15 minutes idle),
* useless for anything but the one document it names,
* revocable (a restart drops every session; a lost permission drops the session's
  authority at the next request).

## 2. The checks the gateway makes, on **every** request

| # | Check | Where | Failure |
| --- | --- | --- | --- |
| 1 | the session exists, is not expired, is not idle | `sessions.SessionStore.get` | 404 |
| 2 | the request is for the session's own document | the path comes from the session, never from the request | — |
| 3 | the user still has write permission on the file | `GET /api2/repos/<id>/file/detail/` -> `permission` | 403 |
| 4 | the file still exists | the same call, 404 | 404 |
| 5 | the file has not changed since it was opened | the same call, `id` compared with the session's | 409 |
| 6 | the document is not too large | `ARTCRAFT_MAX_BYTES` | 413 |
| 7 | the request body is the document, not something else | the length limit and the content type | 413 |

**Check 2 deserves a note:** the path, the repository and the user are read from the
**session**, never from the request. A request cannot name a different file. This
is what makes the session id a *capability* rather than a parameter.

## 3. The message channel (browser ↔ Craft app)

The host page and the Craft app are **same-origin** (the gateway serves both).

**Incoming** (the host page listens on `window`):

```js
if (event.origin !== location.origin) return;
if (event.source !== frame.contentWindow) return;
```

Both checks are needed: the origin check alone would let another page on the same
origin inject bytes, and the source check alone would let any frame in the page
post.

**Outgoing** (the host page posts to the frame):

```js
frame.contentWindow.postMessage(msg, location.origin);
```

**`targetOrigin` is never `"*"`.** Every message that carries document bytes or
names a file uses the explicit origin.

**In the Craft app** (the same discipline, from the three existing bridges):

```js
if (event.origin() != origin || !event.source().is_some_and(|s| Object.is(&s, &parent))) { return; }
parent.post_message_with_transfer(&msg, &origin, &[buffer]);
```

The Craft app also **refuses to have a bridge at all** when the parent is on
another origin, because messages to a foreign origin would be dropped by the
browser *without an error* while the document showed as saved.

## 4. The threats, and what answers them

| Threat | Answer | Status |
| --- | --- | --- |
| **XSS** in the host page | the page is generated by the gateway with `json.dumps` for every value interpolated into JavaScript and `html.escape` for every value interpolated into HTML | addressed; the browser test would have caught a quoting bug — it caught one |
| **CSRF** on the gateway's own endpoints | the gateway's endpoints are `POST /open/`, `POST /session/<sid>/save`, `POST /session/<sid>/dirty` and `GET /session/<sid>/document`. A cross-site form POST to `/open/` would be possible without a token | **open** — the session id is the only thing that protects `/save`, and it is in the URL, which a cross-site page cannot read but *can* guess only with 192 bits of entropy. `SameSite` cookies do not apply because there are no cookies. A `Origin`/`Referer` check on the state-changing endpoints would close it further |
| **CSRF** on Seafile's side | the gateway uses an `Authorization: Token` header, never a cookie, so Seafile's own CSRF protection is not bypassed | addressed |
| **CSP** | the gateway sends `X-Content-Type-Options: nosniff` and `Referrer-Policy: no-referrer`. A full `Content-Security-Policy` is **not** set by the gateway | **open** — the deployment (Nginx) should set it; see `docs/DEPLOYMENT.md` |
| **iframe sandbox** | the Craft app is framed by our own page, which we control; the app's own docs require `allow-scripts allow-same-origin allow-downloads allow-popups` for a *third-party* embed | n/a for our own frame; documented for third-party embeds |
| **postMessage origin validation** | both directions check the origin **and** the source | addressed |
| **targetOrigin "*"** | never used | addressed |
| **same-origin / cross-origin isolation** | the host page and the Craft app are same-origin; the app needs no `SharedArrayBuffer`, so **no COOP/COEP** is required | addressed |
| **token leakage** | the browser holds no token; the gateway's token is in its environment; the file-server tokens never leave the gateway | addressed |
| **replay** | a session id is single-document and short-lived; a save replays the same bytes, which is idempotent (identical content creates no new version) | addressed |
| **session fixation** | the session id is generated by the gateway with 192 bits of entropy and is not derived from anything the client sends | addressed |
| **SSRF** | the gateway fetches the file content from Seafile, whose URL it derives itself. It never fetches a URL a client supplied. (The ONLYOFFICE callback in Seafile *does* fetch a client-supplied URL — our design deliberately does not.) | addressed, and a design win |
| **malicious document** | the document bytes go to the Craft app, which is the thing that has to survive them. The gateway treats them as opaque bytes with a size limit | partially addressed — the Craft app's own robustness is its business |
| **oversized document** | `ARTCRAFT_MAX_BYTES` (50 MB default) on both the open and the save | addressed |
| **ZIP bomb** | the DOCX/XLSX/PPTX formats are zips. The gateway does not unpack them; the Craft app does. A limit on the *compressed* size is not a limit on the *expanded* size | **open** — the Craft app must bound its own expansion; this is an upstream concern |
| **path traversal** | the path comes from the session, which the gateway filled from Seafile's own answer. The static file handler resolves symlinks and refuses anything outside the static root | addressed |
| **save forgery** | a save must name a session that exists; the session is bound to one document; the content id is checked | addressed |
| **cross-user document access** | the session records the user; the write is performed with the gateway's credential, and the *permission* is re-checked on every write. A user who never had access cannot obtain a session for the file, because the session is created from Seafile's own answer to the hook | addressed |
| **read-only bypass** | `can_edit` comes from the real permission, and the write path checks it again. A read-only session cannot write even if the browser asks | addressed |
| **share-link permissions** | **out of scope for the MVP**: the third-party-editor hook only exists in `view_lib_file`, so a share link never reaches it. A read-only share link keeps working exactly as before | scoped out, documented |
| **expired sessions** | 30 minutes absolute, 15 minutes idle; an expired session id gets 404 | addressed |
| **symlink escape from the static root** | `os.path.realpath` on both the file and the root | addressed (REVIEW-02 G1) |
| **the account token reaching the file server** | the file-server calls send no `Authorization` header | addressed (REVIEW-02 G4) |
| **a session store flood** | 256 sessions maximum, oldest evicted; no per-IP rate limit | **open** — acceptable for a prototype, needed for production |
| **the TOCTOU window on the conflict check** | documented: the check is a read-then-write, the window is one API round trip, and Seafile has no compare-and-swap | **open by design** — see `docs/CONFLICTS.md` §2.1 |

## 5. The rules the code must never break

```text
NEVER   a Seafile account token in JavaScript, in a URL, or in the repository
NEVER   a seafhttp update token in the browser          (it is library-wide)
NEVER   a download token in the browser for a file the user cannot download
NEVER   a JWT secret, a session secret, or a password in the frontend
NEVER   a "Save" that reports success without a confirmed Seafile version
NEVER   a targetOrigin of "*" for a message that carries document bytes
NEVER   a path, a repository or a user taken from the request instead of the session
NEVER   a file served from outside the static root
```

## 6. What the independent reviews said

* **REVIEW-01** (Nemotron): the host contract's security model was confirmed
  correct — "the origin check and the source check, explicit `targetOrigin`, and
  same-origin embedding — correct in both existing bridges, and it satisfies the
  mission's hard rules". It required the gateway to be stated as the *only*
  defence, which §0.1 now does.
* **REVIEW-02** (Nemotron): found the symlink escape, the account-token leak, the
  missing save answer, and the TOCTOU window. All four are addressed or
  documented above.

## 7. Open security work

### 7.1 The pre-deployment gate

**None of these may be open when the gateway is exposed to anyone but the
operator.** They are the difference between a self-hosted prototype and a
service:

| # | Item | Why it blocks |
| --- | --- | --- |
| S-1 | a `Content-Security-Policy` for the gateway's own pages | the host page is the one page that frames a third-party WebAssembly module; a CSP pins what that module may load |
| S-2 | an `Origin` / `Referer` check on the state-changing endpoints | a cross-site form POST to `/open/` is possible without a token; the session id is the only thing protecting `/save` |
| S-3 | a rate limit on `/open/` | the session store's cap is a backstop, not a limit |
| S-4 | a bound on the **expanded** size of an OOXML document | a 50 MB limit on the compressed file is not a limit on what it expands to; the Craft app must bound its own expansion |
| S-7 | a formal abuse-case list per endpoint | the threat list above is a checklist, not a model |

S-5 (the share-link path) and S-6 (read-only enforced by the gateway) are
different: S-6 is **done**, and S-5 is a **scope decision** rather than a hole —
a share link never reaches the hook, so it behaves exactly as it did before.

| # | Item | Priority |
| --- | --- | --- |
| S-1 | A `Content-Security-Policy` for the gateway's own pages | before any public deployment |
| S-2 | An `Origin`/`Referer` check on the state-changing endpoints (CSRF) | before any public deployment |
| S-3 | A per-IP / per-user rate limit on `/open/` | before any public deployment |
| S-4 | A bound on the *expanded* size of an OOXML document | upstream (the Craft app) |
| S-5 | The share-link path | out of scope for the MVP; needs the upstream Seafile patch |
| S-6 | A read-only mode that is enforced by the gateway, not only by the Craft app | **done** (the write path checks the permission) |
| S-7 | A formal threat model with an abuse-case list per endpoint | recommended before the public deployment |
