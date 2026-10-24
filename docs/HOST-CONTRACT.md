# The Craft Web Host Contract

Status: **PROVISIONAL — local proposal; GR-016 prototype under review** · GPT REVIEW: FAIL on the frozen `0edbe524` candidate; current remediation tip is not frozen or reviewed
Owner: artcraft-owner · Architecture input: artcraft-architect (GR-003) ·
Feasibility: artcraft-owner · Independent review: artcraft-reviewer (pending)

> **Revision note (2026-10-24):** Sections below record the earlier bridge
> survey/proposal and contain stale app-count and capability claims. The current
> pinned-source inventory is [`docs/reviews/GR-016/APP-SEAM-AUDITS-20261024.md`](reviews/GR-016/APP-SEAM-AUDITS-20261024.md).
> A shared `craft-platform` Rust/WASM transport was prototyped with WordCraft
> and GridCraft in scratch clones; release-browser smoke tests used a synthetic
> `sessionStorage` host. See [`docs/reviews/GR-016/README.md`](reviews/GR-016/README.md).
> This does not establish Seafile persistence or suite-wide adoption. Do not
> treat the historical assertions below as current source findings.

## 0. Summary

> **The contract already exists, in two places, in the same shape.**
> GridCraft and PdfCraft each ship a `?host=parent` `postMessage` bridge with an
> identical message vocabulary. Our job is **not to invent a host API** — it is
> to **document the existing one as the suite-wide standard, extend it to the
> other eleven apps upstream, and implement the Seafile side against it.**

> **Caveat, verified in the source and confirmed by the independent review:**
> the two existing bridges are **not** identical in the one place that matters
> for data integrity — whether the Craft app learns that a save **failed**.
> GridCraft cannot (its `download` hook has no `Result`); PdfCraft can, but
> only synchronously; WordCraft can, asynchronously, through the `async_saves`
> machinery that already exists. The generalised contract therefore needs one
> extra message (§3.7) and the upstream patch needs to unify the three.
> See §3.5-§3.7.

This is the answer to the mission's question *"does a common host contract
already exist between several Craft web apps?"* — **yes, de facto, in 2 of 13,
with a clear and consistent shape for the open and dirty parts, and a
divergent shape for the save part.** We do not need to create `craft-host` from
scratch; we need to **generalise and upstream `host.rs`**, and to settle the
save-outcome semantics.

---

## 1. The existing contract, as implemented

Two independent implementations, byte-for-byte compatible in their message
vocabulary:

* `storytold/gridcraft` — `apps/gridcraft-web/src/host.rs` (166 lines)
* `storytold/pdfcraft` — `apps/pdfcraft-web/src/main.rs`, `mod host` (inline)

### 1.1 Activation

```text
?host=parent      the page is framed and must talk to its parent
?author=<name>    the host's name for the user (signs comments, notes)
```

`?host=parent` is the switch. Without it the app behaves exactly as it does
today (browser file picker to open, browser download to save).

### 1.2 Message vocabulary

| Direction | Type | Payload | Meaning |
| --- | --- | --- | --- |
| child → parent | `<app>:ready` | `{ version }` | the app is listening; send a file now |
| parent → child | `<app>:open` | `{ name, bytes }` | open this document (`bytes`: `ArrayBuffer` or `Uint8Array`) |
| child → parent | `<app>:save` | `{ name, bytes }` (+ `saveAs` in PdfCraft) | the app would otherwise have downloaded this file |
| child → parent | `<app>:dirty` | `{ dirty }` | unsaved changes appeared or went away |
| child → parent | `<app>:failed` | `{ error }` | the app could not start (e.g. no WebGL) |

`<app>` is the app's own name: `gridcraft:open`, `pdfcraft:open`, and so on.

`bytes` is a transferable `ArrayBuffer` on the way out
(`postMessageWithTransfer`), so the document is moved, not copied.

### 1.3 The security model (already correct, and we must keep it that way)

Both implementations do all three of these:

```js
// incoming
if (event.origin() !== origin) return;
if (!event.source().is_some_and(s => Object.is(s, parent))) return;

// outgoing
parent.postMessageWithTransfer(msg, origin, [buffer]);   // never "*"
```

where `origin = window.location().origin()`.

And PdfCraft additionally refuses to build a bridge at all when the parent is
on a different origin:

```rust
// Reading another origin's location throws, which is `None` too.
if parent.location().origin().ok()? != origin { return None; }
```

with the comment that explains *why* it matters:

> messages only go to this origin, so the browser would drop every save without
> an error while the document showed as saved (#2167).

**This is the correct shape and it satisfies the mission's hard requirement:
`targetOrigin` is never `"*"`.** Our Seafile side must keep it that way, and the
security review (GR-009) must verify that the *host* side applies the same
discipline in reverse.

### 1.4 Behavioural rules in host mode

* The app starts with an **empty document**, not the sample document.
* The parent is responsible for guarding against leaving the page
  (GridCraft: "the parent guards leaving the page").
* The host receives the bytes; **the host reports failures itself** — the app
  does not know whether the write succeeded.

### 1.5 What the app does with the bytes

Both implementations push `(name, bytes)` into the app's `Inbox`, the same
channel the browser file picker and drag-and-drop use. The document model, the
editor, the undo stack and the save machinery are **completely untouched** by
host mode.

That is the single most important property of this design:

> **Host mode is a different producer on an existing channel, not a new
> document pipeline.**

---

## 2. The contract, generalised

The generalised contract is the GridCraft/PdfCraft one, with the per-app
namespace made explicit. We do **not** invent new message names.

```text
HOST  ->  CRAFT

  <app>:open      { name: string, bytes: ArrayBuffer | Uint8Array }

CRAFT -> HOST

  <app>:ready     { version: string }
  <app>:save      { name: string, bytes: ArrayBuffer, saveAs?: boolean }
  <app>:dirty     { dirty: boolean }
  <app>:failed    { error: string }
```

### 2.1 Rules

| # | Rule | Rationale |
| --- | --- | --- |
| R1 | The host page and the Craft page are **same-origin** | already enforced by both implementations; makes the origin check exact and removes a whole class of attacks |
| R2 | The Craft page only ever talks to `window.parent` | not `opener`, not a wildcard |
| R3 | Every incoming message is checked on **both** `event.origin` and `event.source` | a page on the same origin could otherwise be tricked into injecting bytes |
| R4 | Every outgoing message names an **explicit `targetOrigin`**, never `"*"` | required by the mission |
| R5 | The parent is the **only** party that can open a document or receive bytes | the Craft app has no storage of its own in host mode |
| R6 | The Craft app reports `dirty`; it never decides that a save succeeded | the host owns persistence |
| R7 | The Craft app reports `failed` when it cannot start | the host must be able to show the error |
| R8 | The host must be able to detect **stale** documents | the contract carries the document name; the *version* is the host's business (GR-008) |
| R9 | **The host tells the Craft app whether the save succeeded** | the Craft app must not believe a save succeeded when the host refused it (§3.5). Ticketed local patches now implement this for WordCraft and GridCraft, with isolated synthetic Seafile runtime evidence; the shared behavior is not adopted upstream (§3.7). |

### 2.2 Deliberately **not** in the contract

| Not in the contract | Why |
| --- | --- |
| a Seafile repository id, path or token | the Craft side must stay storage-agnostic (mission §26) |
| the file id / obj_id | a **host-platform** concern; it belongs to the Seafile integration layer, not to the Craft contract |
| permissions, roles, share links | host concern |
| the "save" command from host → craft | the app owns when to save; the host only receives the result. (A host-initiated save can be added later if a need appears — e.g. a "save now" button in the host chrome.) |
| error codes | `failed` carries a message; a richer error model is a later refinement |

### 2.3 What the contract deliberately leaves to the host

The host is responsible for:

* deciding **which** document to open and **whether** it may be edited;
* keeping the document's **identity** (path, version) and deciding if it is stale;
* **persisting** the bytes and creating the new version;
* **acknowledging** the save and reporting a failure to the user;
* the **session**, the credentials and the browser's own state.

This is the boundary between the platform adapter and the Craft editor. The
platform adapter owns provider-specific authentication, permissions, file
identity, versioning, and API calls; the Craft host contract carries only the
document bytes, filename, dirty state, and save outcome.

```text
Seafile adapter ────┐
Nextcloud adapter ──┼──> common browser host/session ──> extension dispatcher
ownCloud adapter ───┘                                      │
                                           ┌───────────────┼─────────────┐
                                           ▼               ▼             ▼
                                       WordCraft         GridCraft    other Craft Web apps
```

Seafile is the first adapter under test. Nextcloud and ownCloud are target
platforms, but their web entry points, authorization, version semantics, and
save APIs are **NOT VERIFIED**. This project has not implemented those adapters.

---

## 3. The host side: the Seafile integration layer

### 3.1 Shape

```text
Seafile Web (Seahub page)
   |
   | the user clicks rapport.docx
   v
Seahub "Open with Craft" -> our host page (same origin as Seahub)
   |
   | <iframe src="/artcraft/wordcraft/?host=parent&author=...">
   v
WordCraft Web (static files, same origin, behind the reverse proxy)
   |
   | wordcraft:ready
   v
host page -> integration service -> Seafile   (fetch bytes, check permission)
   |
   | wordcraft:open { name, bytes }
   v
WordCraft edits
   |
   | wordcraft:save { name, bytes }
   v
host page -> integration service -> Seafile   (conflict check, update, new version)
   |
   | ack
   v
host page tells the user "saved"; the Craft app has already marked the
document clean (its own `async_saves` machinery, unchanged)
```

### 3.2 Where the Craft web build is served

`packaging/web/README.md` exists in **all 13** repos and gives the exact static
hosting recipe: relative URLs, `application/wasm` MIME type, gzip/Brotli for
`.wasm`, immutable caching for hashed assets, `no-cache` for `index.html`, HTTPS
for WebGPU, **no COOP/COEP needed** (no `SharedArrayBuffer`).

The deployment fits the existing reverse proxy as an **additive location**:

```nginx
location /artcraft/wordcraft/ {
    types { application/wasm wasm; text/javascript js; text/html html; }
    gzip on;
    gzip_types application/wasm text/javascript text/html;
    location ~* \.(wasm|js)$ { add_header Cache-Control "public, max-age=31536000, immutable"; }
    location ~* index\.html$ { add_header Cache-Control "no-cache"; }
    root /srv/artcraft/wordcraft;
}
```

**Same origin as Seahub** — which is required by the contract (R1) and which
removes any cross-origin messaging problem entirely.

### 3.3 The open flow

```text
1. The user clicks a .docx in Seafile.
2. Seahub (or our host page) creates an editing session:
   - repo id, path, the file id observed now, the user's permissions
   - the session id is opaque, short-lived, single-document
3. The host page renders <iframe src="/artcraft/wordcraft/?host=parent">.
4. The iframe posts wordcraft:ready.
5. The host page asks the integration service for the bytes, and posts
   wordcraft:open { name, bytes } to the iframe.
```

### 3.4 The save flow

```text
1. The iframe posts <app>:save { name, bytes }.
2. The host page POSTs the bytes to the integration service.
3. The service:
   a. checks the session (exists, not expired, not revoked);
   b. checks the user still may edit this file;
   c. re-reads the current file id and compares it with the one at open time
      -> CONFLICT if different;
   d. writes through the seafhttp update API;
   e. returns the new file id (or "no change" if the content is identical).
4. The host page shows "Saved" or the error.
5. The Craft app is told the outcome (see below).
```

### 3.5 Does the Craft app know that the save failed?

**This is not uniform across the suite, and the difference matters.** It was
verified in the source of the three apps that have a bridge or the services
they need.

| App | The service hook | Its type | Can the app learn that the write failed? |
| --- | --- | --- | --- |
| **WordCraft** | `Services::download` + `Services::async_saves` | `Fn(&str, &[u8]) -> Result<(), String>` | **Yes, and asynchronously.** The host calls `AsyncSaves::start()` to get a ticket, and later `AsyncSaves::finish(ticket, Saved \| Cancelled \| Failed(error))`. On `Failed` the app sets `session.dirty = true` again and shows *"Couldn't download {name}: {error}"*. |
| **PdfCraft** | `Services::host_save` (`HostSaveFn`) | `Fn(&str, &[u8], bool) -> Result<(), String>` | **Yes, but synchronously.** On `Err` the app does not mark the document saved and shows the error. |
| **GridCraft upstream baseline** | `Services::download` | `Fn(&str, &[u8])` — **no `Result`** | **No.** Upstream at the inspected revision marks the workbook saved optimistically. The local GR-010 patch adds ticketed exact-snapshot dirty handling and has an isolated synthetic Seafile save/reopen proof; formula recalculation, conflicts and upstream adoption remain open. |

Sources:

```text
storytold/wordcraft/crates/ui-egui/src/lib.rs:123-131   (download + async_saves fields)
storytold/wordcraft/crates/ui-egui/src/lib.rs:1286-1305 (settle_async_saves: Failed -> dirty = true)
storytold/wordcraft/crates/ui-egui/src/async_saves.rs   (start / finish / SaveOutcome)
storytold/pdfcraft/crates/ui-egui/src/lib.rs:635-636     (host_save: Option<HostSaveFn>)
storytold/pdfcraft/crates/ui-egui/src/editing.rs:670-685 (Err -> not marked saved)
storytold/gridcraft/crates/ui-egui/src/lib.rs:195-196    (download: Fn(&str, &[u8]), no Result)
storytold/gridcraft/apps/gridcraft-web/src/host.rs:60-66 (the error is only logged)
```

### 3.6 The consequence, and the correction to an earlier draft

An earlier draft of this document claimed that "the Craft app has already marked
the document clean as soon as the bytes leave the frame". **That is only true
for GridCraft** (and it is a defect there). It is **false for WordCraft**, whose
`async_saves` machinery exists precisely to keep the document dirty until the
save is confirmed, and whose `Failed` outcome puts `dirty` back.

That is good news, and it changes the shape of the upstream proposal:

* **The "Craft remains dirty on failure" requirement (mission §30) is
  implementable with the machinery the apps already have.**
* The existing five-message vocabulary is **not sufficient on its own** to
  guarantee it: it has no message for the save outcome.

### 3.7 The save-result extension (local patches; not adopted upstream)

```text
HOST  -> CRAFT

  <app>:saveResult  { ticket: "...", ok: true }                 (the host persisted it)
  <app>:saveResult  { ticket: "...", ok: false, error: "..." }  (the host refused or failed)

CRAFT -> HOST

  <app>:save        { name, bytes, ticket: "..." }
```

The proposed common wire ticket is an **opaque string**, echoed unchanged in
`saveResult`; do not put a JavaScript number on the wire. Each app may keep its
own internal ticket and snapshot type, adapting it at the boundary. This avoids
the current local WordCraft patch's numeric ticket and GridCraft patch's string
ticket from becoming two incompatible host protocols. WordCraft's internal
`AsyncSaves` ticket (`start()` / `finish(ticket, Saved | Failed(error))`) stays
app-owned; GridCraft's exact workbook snapshot also stays app-owned. PdfCraft's
current synchronous `Result` is not sufficient for a durable remote write and
needs an asynchronous outcome.

> This extension remains a proposal for a shared upstream contract. WordCraft's
> bridge patch (GR-014) and the GridCraft ticketed patch (GR-010) implement it
> locally. Real-browser saves and fresh editor reopens were reproduced against
> the isolated synthetic Seafile stack for both apps; neither patch is
> upstreamed and the broader suite has not adopted one shared implementation.
> Their current ticket encodings differ and must be normalized when they migrate
> to a shared transport.

Until it exists, the host page must keep **its own** "not persisted" state and
warn on close, because a GridCraft-style app will believe the document is
saved. **The integration layer must never pretend a save succeeded.**

---

## 4. Gaps that must be closed upstream

| App | `?host=parent` bridge | The save hook it has | What is needed |
| --- | --- | --- | --- |
| gridcraft | **yes** | upstream baseline: `download: Fn(&str, &[u8])`; local GR-010 patch adds ticketed `saveResult` and snapshot tracking | synthetic Seafile save acknowledgement and fresh editor reopen reproduced; formula recalculation and GridCraft conflict behavior remain open |
| pdfcraft | **yes** | `host_save: Fn(&str, &[u8], bool) -> Result<(), String>` — synchronous | reference for the save-failure part; would need to become asynchronous to match WordCraft |
| wordcraft | upstream baseline: no | `download: Fn(...) -> Result<(), String>` **+ `async_saves`** | local GR-014 bridge patch and isolated synthetic Seafile edit/save/version/reopen are reproduced; upstream adoption and broader failure/security coverage remain open |
| deckcraft | no | not surveyed in detail | port the bridge |
| vectorcraft | no | has a *different* mechanism (`window.vectorcraft`, a promise API) — see §6 | decide whether to port the bridge or adapt the page API |
| designcraft | no | `download` present, `open_async` present, no `async_saves` | port the bridge; check the save hook's signature |
| photocraft | no | `inbox` present, no `download` | port the bridge; the save hook may not exist yet |
| figcraft | upstream: no; local GR-019 prototype only | upstream `Services` is picker/download-only; local patch adds pathless `.figcraft` snapshot ACK | browser and Seafile E2E remain NOT VERIFIED; host Save As/branches/previews are out of first-slice scope |
| cadcraft | yes | existing bridge replaces the engine delivery hook | migrate to the shared crate and verify durable save-result semantics |
| filmcraft | no | no `Services` found in `ui-egui/src/lib.rs` | locate the seam first |
| lightcraft | no | `Services` present, no `open_async`/`inbox`/`download` | locate the seam first |
| effectcraft | no | no `Services` found in `ui-egui/src/lib.rs` | locate the seam first |
| soundcraft | no | `Services` present, no `open_async`/`inbox`/`download` | locate the seam first |

### 4.1 The upstream patch shape (GR-014 candidate)

```text
storytold/craft-libs
  crates/host/                <-- NEW: the shared bridge
      src/lib.rs              message helpers, no wasm dependency
      src/wasm.rs             the postMessage transport (wasm32 only)

storytold/<app>
  apps/<app>-web/src/host.rs  <-- NEW or ported: wires Services to the bridge
  apps/<app>-web/src/web.rs   <-- MODIFIED: choose browser mode or host mode
```

`craft-libs` is the right home: it is where the suite already puts code that
must be identical across apps, and it is `MIT OR Apache-2.0`, licence-clean for
this repository.

**Why not 13 copies?** Two implementations of the same contract already exist
and they have already drifted (PdfCraft adds `saveAs`; GridCraft does not).
A third and fourth copy would drift further. The upstream value of the change
is precisely that it is *one* contract.

### 4.2 The WordCraft patch, concretely

WordCraft's `Services` is the richest of the suite, and it already has
everything the bridge needs:

```rust
services.open_async  = Some(|what| host.request_open(what));   // instead of a file picker
services.inbox       = Some(inbox);        // the host's bytes land here (unchanged channel)
services.download    = Some(|name, bytes| host.send_document(name, bytes));
services.async_saves = Some(saves);        // reused unchanged
services.on_dirty    = Some(|dirty| host.set_dirty(dirty));
```

The `download` hook is the save path. WordCraft's `async_saves` machinery
already implements *"the document's save isn't confirmed until the save
finishes"* — which is precisely the semantics a host save needs. **The save
protocol (GR-007) is therefore mostly already in the Craft apps, and the host
only has to answer.**

One caveat: `download`'s documented contract is *"an error means no download
started (the browser can't tell the page whether the user then kept the file)"*.
For a host save the error semantics are **stronger**: the host *can* tell the
page whether the write succeeded. So the host bridge should ideally use a
different, explicit hook rather than overloading `download` — a question for
the upstream patch design (GR-014).

---

## 5. The Seafile side of the contract

The host contract above is storage-agnostic. The Seafile-specific behaviour
lives entirely in the integration layer:

| Concern | Where it lives | Document |
| --- | --- | --- |
| session, credentials | integration service | `docs/AUTHENTICATION.md` |
| the bytes to open | integration service -> seafhttp download | GR-002 |
| the write, the new version | integration service -> seafhttp update | `docs/SAVE-PROTOCOL.md` |
| staleness / conflict | integration service, obj_id comparison | `docs/CONFLICTS.md` |
| extension -> editor | dispatch table, configurable | `docs/FILE-DISPATCH.md` |
| browser security | both sides | `docs/SECURITY.md` |

---

## 6. The other existing mechanism: VectorCraft's `window.vectorcraft`

VectorCraft exposes a different surface (`apps/vectorcraft-web/src/api.rs`):

```js
await vectorcraft.execute("object.rectangle", {…})   // engine command
await vectorcraft.request("ui.inspect")
await vectorcraft.commands()
const {base64} = await vectorcraft.screenshot()
await vectorcraft.openFile("logo.svg", bytes)
vectorcraft.captureDownloads(true)
vectorcraft.files(); await vectorcraft.readFile("logo.png")
```

It is the **desktop control protocol** (`docs/control-protocol.md`, present in
12 of 13 apps) exposed as a promise API on the page, aimed at an agent driving
the app in a tab. It is powerful but it is a *different* shape: it is an
in-page API, not a parent/child protocol, and it is designed for automation
rather than for embedding.

**Decision: the host contract is the `?host=parent` postMessage bridge, not
VectorCraft's control API.** Reasons:

1. the bridge is the shape a *host platform* needs (a parent page owns the
   document lifecycle);
2. the control API is a much larger surface with a much larger security cost
   (it can execute arbitrary engine commands and synthesise input);
3. the bridge is already implemented twice, consistently.

The control protocol remains relevant for **QA automation** (mission §48) and
is already used by the MCP servers. It is not the browser-embedding contract.

---

## 7. Open questions for the reviewer and the upstream RFC

| # | Question |
| --- | --- |
| Q-1 | Should the generalised contract keep the per-app namespace (`wordcraft:open`) or move to a common namespace (`artcraft:open`)? The per-app namespace is what exists and it lets a host frame several apps. **Recommendation: keep it.** |
| Q-2 | Should the host be able to *request* a save (host -> craft)? Not needed now. |
| Q-3 | What is the right error model beyond `failed { error }`? |
| Q-4 | Should the bridge live in `craft-libs` (one crate) or in each app (13 copies)? **Recommendation: `craft-libs`.** |
| Q-5 | How should the bridge report a save the host *rejected*? Today the app has already marked the document clean. This is the "Craft remains dirty on failure" requirement and it needs an upstream answer — see §3.4. |
| Q-6 | Should `?host=parent` be replaced by a richer host descriptor (`?host=parent&session=...`)? The session id belongs to the host, not to the Craft app; the Craft app only needs the bytes. **Recommendation: no, keep the Craft side dumb.** |
| Q-7 | Cross-origin embedding: the packaging docs say cross-origin embeds *work* (the app renders fine), but the **bridge** is same-origin only. That is the right split — the app can be embedded anywhere, the *bridge* needs a same-origin parent. Confirm this is the upstream intent. |

---

## 8. Evidence index

| Claim | Source |
| --- | --- |
| GridCraft bridge | `storytold/gridcraft@main:apps/gridcraft-web/src/host.rs` (166 lines) |
| GridCraft wiring | `storytold/gridcraft@main:apps/gridcraft-web/src/web.rs:39-41` |
| PdfCraft bridge | `storytold/pdfcraft@main:apps/pdfcraft-web/src/main.rs:135-260` (`mod host`) |
| PdfCraft save delivery | `storytold/pdfcraft@main:crates/ui-egui/src/editing.rs:670-680` |
| `Services` seam | `storytold/wordcraft@main:crates/ui-egui/src/lib.rs:100-190` |
| Web build + Trunk | `storytold/wordcraft@main:apps/wordcraft-web/{Cargo.toml,Trunk.toml,index.html,src/main.rs}` |
| Web app behaviour | `storytold/wordcraft@main:apps/wordcraft-web/src/main.rs` (module doc) |
| Static hosting recipe | `storytold/<app>@main:packaging/web/README.md` (all 13) |
| Control protocol | `storytold/<app>@main:docs/control-protocol.md` (12 of 13) |
| VectorCraft page API | `storytold/vectorcraft@main:apps/vectorcraft-web/src/api.rs` |
