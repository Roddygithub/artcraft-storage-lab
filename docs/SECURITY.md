# Security

Status: **GPT REVIEW FAIL** (Sol, latest reviewed candidate `0edbe524b4fa321b0f73f8601afef390e7f785e6`)
GR-009 · Independent free review: `docs/reviews/REVIEW-01.md`, `REVIEW-02.md`

## Current implementation correction — 2026-10-23

This note supersedes older statements below when they conflict:

* The gateway uses the third-party-editor capability server-side; a stock
  Seafile account token is not required by the current path.
* Session-mutating POSTs require the gateway origin. `POST /open/` also accepts
  the exact configured `ARTCRAFT_SEAFILE_ORIGIN`, because Seahub submits its
  capability by form navigation. The gateway and Seahub must use distinct
  origins; behavior through Nginx Proxy Manager is not yet verified.
* Stock Seafile has no user-bound conditional-save endpoint. The gateway fails
  closed on the deployed version. The local GR-015 patch proposes a dedicated
  `update-conditional-api` route. Its `update-` prefix preserves the existing
  `op=update` token check while keeping the endpoint distinct from `update-api`.
  Stock C and Go fileservers do not expose it. The patches remain unbuilt and
  runtime behavior is **NOT VERIFIED**; see the latest Sol finding and local
  remediation in `docs/reviews/GPT-SOL-REREVIEW-0EDBE52.md`.
* The local Seahub patch rechecks current `can_preview` permission for each
  capability-backed read. The exact decorator passes a synthetic AST harness;
  Django/Seafile runtime authorization remains **NOT VERIFIED**.
* Capability-bearing URLs are redacted from gateway-facing errors in the local
  worktree and covered by a synthetic HTTP test, including malformed HTTP-200
  responses. Seafile document bodies are bounded while reading. The host refuses
  overlapping editor saves; a Chromium synthetic protocol test confirms an
  earlier acknowledgement cannot clear a later edit. This is not a real
  Seafile persistence test.
* The dynamic capability host page now sends a nonce-based CSP and restricts
  `frame-ancestors` to the configured Seahub origin (GR-039). The policy does
  not cover static Craft editor HTML or deployment proxy responses. GR-073 adds
  an in-process limit for `/open/`; behind a reverse proxy, clients may share
  the proxy's peer address. The system is not approved for public Internet
  deployment.

## 0. The threat model, in one picture

```text
   the browser                 the gateway                     Seafile
  ┌──────────────┐          ┌───────────────┐            ┌──────────────┐
  │  the Craft   │  postMsg │  the host     │ user-bound│  Seahub      │
  │  app (wasm)  │ ───────► │  page + the   │ capability│  + seafhttp  │
  │              │ ◄─────── │  service      │ ─────────► │              │
  └──────────────┘          └───────────────┘            └──────────────┘
        ▲                         ▲
        │ the user                │ editor capability stays server-side
   the user's own machine
```

* The **Craft application** is a third-party WebAssembly module running in the
  user's browser. It is trusted to the extent that it is the user's editor, but it
  is **not** trusted with credentials, and it is not trusted to decide that a save
  succeeded.
* The **gateway** is the browser-facing trust boundary. It holds the opaque
  third-party-editor capability server-side and ties save acknowledgements to
  Seafile's response. Seahub must re-check the actual user's current permission
  before every write.
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
| a Seahub session cookie | not used by the gateway | the gateway does not read or forward it; browser cookie scope depends on deployment origin |
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
| 3 | current read/write permission | local Seahub patch checks current `can_preview` on capability reads and current edit permission on saves | synthetic source harness only; runtime **NOT VERIFIED**; stock writes fail closed |
| 4 | the file still exists | local patch binds reads/saves to the opened file id | deletion/revocation runtime **NOT VERIFIED** |
| 5 | the file has not changed since it was opened | local C patch checks the file id and uses branch compare-and-update even for same-content saves | exact source patch only; build/runtime **NOT VERIFIED**; Go route remains unpatched |
| 6 | the document is not too large | `ARTCRAFT_MAX_BYTES` | 413 |
| 7 | request-body framing, size, and read time | GET/POST handlers reject parser defects and leftover header payload, require supported framing, enforce route limits and a 120-second total body-read deadline, and close on malformed/oversized/timed-out bodies; HTTP/0.9 is rejected | 400 / 408 / 413; `/dirty` state is unchanged |

**Check 2 deserves a note:** the path, the repository and the user are read from the
**session**, never from the request. A request cannot name a different file. This
is what makes the session id a *capability* rather than a parameter.

## 3. The message channel (browser ↔ Craft app)

The host page and the Craft app are **same-origin with each other**, but both
must be on an origin **different from Seahub**. This prevents the untrusted
editor frame from reading Seahub's hidden capability form or cookies. The
browser posts the capability to `/open/` by navigation; the gateway stores it
server-side before rendering the host page.

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
| **CSRF** on the gateway's own endpoints | session POSTs require gateway `Origin`; only `/open/` accepts the configured Seahub origin | implemented and unit-tested; NPM/browser verification pending |
| **CSRF** on Seafile's side | the gateway uses an `Authorization: Token` header, never a cookie, so Seafile's own CSRF protection is not bypassed | addressed |
| **CSP** | `/open/` host-page responses send a nonce-based policy with `default-src 'none'`, same-origin frame/connect restrictions, and `frame-ancestors` set to the configured Seafile origin (or `'none'` when missing/invalid) | **partial** — static Craft HTML and reverse-proxy responses are not covered; test policy compatibility for each pinned editor bundle before public deployment |
| **iframe sandbox** | the Craft app is framed by our own page, which we control; the app's own docs require `allow-scripts allow-same-origin allow-downloads allow-popups` for a *third-party* embed | n/a for our own frame; documented for third-party embeds |
| **postMessage origin validation** | both directions check the origin **and** the source | addressed |
| **the page-API transport (VectorCraft)** | VectorCraft exposes no postMessage bridge, so the host page calls `frame.contentWindow.vectorcraft` directly. It verifies the frame's **origin** first (`frameIsOurs()`), and re-verifies it on every poll; a cross-origin read throws, which the check treats as "not ours" | addressed (REVIEW-04, G9) |
| **targetOrigin "*"** | never used | addressed |
| **same-origin / cross-origin isolation** | the host and Craft frame are same-origin with each other and cross-origin from Seahub; the app needs no `SharedArrayBuffer`, so **no COOP/COEP** is required | required topology documented and gateway handoff tested; deployment not verified |
| **token leakage** | the browser holds only an opaque gateway session id; the gateway does not need a broad account token; file-server update tokens never leave Seahub | intended; live Seafile endpoint not deployed |
| **replay** | a session id is single-document and short-lived; the local C patch routes conditional saves through the branch precondition | **not runtime verified; stock writes fail closed** |
| **session fixation** | the session id is generated by the gateway with 192 bits of entropy and is not derived from anything the client sends | addressed |
| **SSRF** | the gateway fetches the file content from Seafile, whose URL it derives itself. It never fetches a URL a client supplied. (The ONLYOFFICE callback in Seafile *does* fetch a client-supplied URL — our design deliberately does not.) | addressed, and a design win |
| **malicious document** | the gateway treats payload bytes as opaque except for basic file-signature validation; Craft's parser processes the document | partially addressed — parser expansion/resource limits remain unverified |
| **oversized document** | `ARTCRAFT_MAX_BYTES` (50 MB default) on both the open and the save | addressed |
| **ZIP bomb** | gateway bounds expanded `[Content_Types].xml` reads; Craft parser has separate expansion risks | gateway bound has a synthetic test; parser limits remain **NOT VERIFIED** |
| **path traversal** | the path comes from the session, which the gateway filled from Seafile's own answer. The static file handler resolves symlinks and refuses anything outside the static root | addressed |
| **save forgery** | a save names a session bound to one document; local Seahub/fileserver patches check permission, file id and branch head | **NOT VERIFIED** against patched runtime |
| **cross-user document access** | direct repo/path opening is disabled; saves require current-user authorization from the GR-015 endpoint | blocked; endpoint not built or deployed |
| **read-only bypass** | stock server saves are disabled; local Seahub patch rechecks current write permission | blocked pending GR-015 build and runtime tests |
| **share-link permissions** | **out of scope for the MVP**: the third-party-editor hook only exists in `view_lib_file`, so a share link never reaches it. A read-only share link keeps working exactly as before | scoped out, documented |
| **expired sessions** | 30 minutes absolute, 15 minutes idle; an expired session id gets 404 | addressed |
| **symlink escape from the static root** | `os.path.realpath` on both the file and the root | addressed (REVIEW-02 G1) |
| **the account token reaching the file server** | the file-server calls send no `Authorization` header | addressed (REVIEW-02 G4) |
| **a session store flood** | Session store is capped at 256 entries with oldest-entry eviction; GR-073 also limits `/open/` to 60 requests per 60 seconds per observed TCP peer (1,024 peer entries per process) | **partially addressed** — process-local peer limits do not coordinate across workers, and proxy clients may share a bucket |
| **the TOCTOU window on the conflict check** | stock public API has no user-bound conditional file save; GR-015 binds the opened file id to Seafile's transactional branch compare-and-update | **blocked pending build and deployment** — see `docs/reviews/GR-015/` |

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
| S-1 | a `Content-Security-Policy` for gateway host and editor documents | `/open/` host HTML is covered; editor HTML and deployed proxy behavior remain unverified |
| S-2 | an `Origin` / `Referer` check on the state-changing endpoints | gateway Origin checks are implemented; behavior behind Nginx Proxy Manager remains unverified |
| S-3 | a rate limit on `/open/` | GR-073 limits requests by the gateway-observed TCP peer; reverse-proxy clients may share one bucket |
| S-4 | a bound on the **expanded** size of an OOXML document | a 50 MB limit on the compressed file is not a limit on what it expands to; the Craft app must bound its own expansion |
| S-7 | a formal abuse-case list per endpoint | GR-074 records body-framing cases; endpoint-wide abuse-case coverage remains open |

S-5 (the share-link path) and S-6 (read-only enforced by the gateway) are
different: S-6 is **done**, and S-5 is a **scope decision** rather than a hole —
a share link never reaches the hook, so it behaves exactly as it did before.

| # | Item | Priority |
| --- | --- | --- |
| S-1 | CSP for gateway host and editor documents | host page implemented in GR-039; editor documents and deployed proxy behavior before any public deployment |
| S-2 | Verify `Origin` behavior behind Nginx Proxy Manager | before any public deployment |
| S-3 | Validate `/open/` rate limit against deployment topology and expected client volume | GR-073 adds 60 requests per 60-second fixed window per observed TCP peer; 1,024 peer entries maximum per process. Behind a reverse proxy, clients may share one bucket; forwarded headers are not trusted |
| S-4 | A bound on the *expanded* size of an OOXML document | upstream (the Craft app) |
| S-5 | The share-link path | out of scope for the MVP; needs the upstream Seafile patch |
| S-6 | A read-only mode that is enforced by the gateway, not only by the Craft app | **done** (the write path checks the permission) |
| S-7 | A formal threat model with an abuse-case list per endpoint | GR-074 covers gateway body-framing abuse cases; complete per-endpoint register remains open before public deployment |
