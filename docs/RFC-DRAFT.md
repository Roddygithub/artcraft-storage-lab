# RFC — a reusable ArtCraft Web host integration for embedded editors

Status: **DRAFT — NOT PUBLISHED** (the upstream hard gate: no RFC, issue or PR in
`storytold/*` before `GPT REVIEW PASS`)
Angle: **Reusable ArtCraft Web host integration for embedded editors.** Seafile
end-to-end validation is not yet complete; the mandatory DOCX flow is NOT VERIFIED.

## Problem

Each ArtCraft application has a browser build, and each of them is a complete
editor: a document model, an engine, a real UI, the file formats. What they do
**not** have is a way for a **host page** to open a document in them and take the
saved bytes back.

Today a browser build can only:

* open a file with the **browser's file picker** (or a drop), and
* save with a **browser download** (or the File System Access API).

That is fine for a person at a keyboard. It is useless for a page that embeds the
editor — a document management system, a wiki, a mail client, a file manager.
Those hosts want to say *"open this document"* and *"give me the saved bytes"*,
not *"please pick a file on your computer"*.

Three of the thirteen applications already answer a host page over `postMessage`
(GridCraft, PdfCraft, CADCraft), each with its own copy of the same ~200 lines.
The other ten cannot be embedded at all.

## Use case

A user is in a file platform's web interface. They click a document. The platform
opens the ArtCraft editor in an iframe, hands it the document, and takes the
saved bytes back and stores them as a new version. No download, no upload, no
desktop application, no local mount.

The platform may be self-hosted (Seafile, Nextcloud, ownCloud) or a web office
suite. The editor may be any ArtCraft application.

## Existing web architecture

Every application has a browser build:

```text
apps/<app>-web/          the browser shell
  Cargo.toml             eframe (wgpu, WebGL2 fallback), wasm-bindgen, web-sys
  Trunk.toml             or `cargo xtask web` for three of them
  index.html             a canvas, relative URLs, hashed assets
  src/web.rs             the browser platform layer
  src/main.rs            the entry point
  packaging/web/         the release packaging and the hosting guide
```

The build **runs the same application as the desktop app**, through eframe's web
runner. There is no second UI, no second document model, and no JavaScript
toolchain: the suite is Rust only, and the browser build is Rust compiled to
WebAssembly.

`packaging/web/README.md` (present in all thirteen) documents the hosting: a
static site, `application/wasm` for the module, gzip or Brotli, immutable caching
for the hashed assets, HTTPS for WebGPU, **no** `SharedArrayBuffer` and therefore
**no** COOP/COEP, and cross-origin embedding works for the application itself.

## Existing host bridges

Three applications already have one, and they agree:

```text
?host=parent      the page is framed and must talk to its parent
?author=<name>    the host's name for the user

child -> host    <app>:ready    { version }
parent -> child  <app>:open     { name, bytes }
child -> host    <app>:save     { name, bytes }
child -> host    <app>:dirty    { dirty }
child -> host    <app>:failed   { error }
```

The security model is the same in all three and is the part that must not be
weakened:

* the bridge only exists when the page is framed, and **refuses to exist** when
  the parent is on another origin (a message to a foreign origin is dropped by the
  browser *without an error*, while the document shows as saved);
* every incoming message is checked on **both** `event.origin` and `event.source`;
* every outgoing message names an **explicit `targetOrigin`** — never `"*"`;
* the bytes are transferred, not copied (`postMessageWithTransfer`).

**Three copies of the same 200 lines, already drifting.** PdfCraft adds `saveAs`;
GridCraft's copy cannot report a failed save; CADCraft's copy hooks the engine
rather than the services.

## Seafile reference integration

The reference implementation is still a prototype and has **not** passed its
required Seafile Web → WordCraft DOCX end-to-end acceptance test. Earlier GR
bundles report browser edits and saves, but Sol's independent review found that
the current tests inject a gateway page and inspect output bytes rather than
reopening the file in WordCraft. Patched Seahub/fileserver integration and the
ONLYOFFICE regression are also not run (`docs/reviews/GR-015/README.md`). Treat
those earlier reports as unverified leads, not proof.

The repository contains a gateway, draft Seahub/Seafile patches and synthetic
tests. The current deployed Seafile has not received those patches, and the
gateway writes fail closed until user-bound authorization and atomic
compare-and-swap are available. This RFC describes a proposal; it does not
claim that the integration or a reusable contract has been validated end to
end.

An adjacent upstream proposal, [Suite-wide Host Mode, issue #2420](https://github.com/storytold/artcraft/issues/2420),
describes a native Craft application as the authoritative host for remote UI
surfaces. This RFC addresses a different flow: Seafile remains the document
authority, a browser editor serializes document bytes, and the storage adapter
commits a new Seafile version. Any upstream contract proposal should state this
scope difference and coordinate with issue #2420 rather than duplicate its
native remote-surface work.

## Proposed common host contract

One crate, in `storytold/craft-libs`, used by the thirteen `apps/<app>-web`
crates.

```text
HOST  -> CRAFT

  <app>:open        { name, bytes }        open this document
  <app>:saveResult  { ticket, ok, error }  how the host's write ended

CRAFT -> HOST

  <app>:ready       { version }            the app is listening
  <app>:save        { name, bytes, ticket }  the app wants the bytes stored
  <app>:openRequest { purpose }            File > Open was asked for
  <app>:dirty       { dirty }              unsaved changes appeared or went away
  <app>:failed      { error }              the app could not start
```

The vocabulary is the one three applications already use. Two things are added:

1. **the ticket** on the save, and
2. **`saveResult`**, the host's answer.

### Why the ticket and the answer matter

A browser cannot tell a page whether the user kept the file it downloaded. A
**host can**: it knows whether the write succeeded, and it can refuse it. The
document must therefore not count as saved until the host says so.

WordCraft already has exactly the right machinery, in
`crates/ui-egui/src/async_saves.rs`: a host hook starts a ticket, the host
reports the outcome later, and the application puts the document back into its
dirty state and tells the user why when the outcome is a failure. The other
applications have equivalents (`Services::host_save` in PdfCraft) or need them.

**This is the difference between a bridge and an integration.** Without the
answer, the editor believes a save worked that the host refused — the worst
possible failure mode, because the user is told the opposite of the truth.

### Where the bridge belongs

`storytold/craft-libs` is where the suite already puts code that must be
identical across applications (`craft-ui`, `craft-window`, `craft-quit`,
`craft-docpath`, …), and it is dual MIT / Apache-2.0 like every application.

The crate would hold the message types and the transport; the per-application
`apps/<app>-web` would wire it to that application's own services.

## Open flow

```text
1. The user clicks a document in the host page.
2. The host creates an editing session and renders its editor page.
3. The page frames the Craft application (same origin) with ?host=parent.
4. The application starts and posts <app>:ready.
5. The host sends <app>:open { name, bytes }.
6. The application delivers the bytes to its own inbox — the same channel the
   browser's file picker and drag-and-drop use. Nothing in the document model,
   the engine or the editor changes.
```

The application starts with an **empty document** in host mode, not a sample.

## Save flow

```text
1. The user saves in the application.
2. The application hands the bytes to the host, with a ticket.
3. The host stores them, and answers <app>:saveResult { ticket, ok }.
4. The application marks the document saved — or puts it back in its dirty state
   and says why.
```

The host owns persistence, the version, the conflict check and the permissions.
The application owns the document.

## Permissions

The application is told whether it may write (`<app>:open` carries the mode, or
the host simply never sends a save path). **The host must enforce it anyway**:
the application's mode is a convenience, the host's check is the rule.

The read-only case is not "the editor has no save button". It is "the host
refuses the write".

## Authentication

The ArtCraft frame receives document bytes and an opaque gateway session id. A
short-lived Seafile third-party-editor capability is submitted by the browser to
the gateway, which stores it server-side; it is not exposed to the Craft frame.
No Seafile account token or fileserver access token is sent to the editor.

* The **gateway** holds the capability after the browser-mediated Seahub form
  handoff. The browser participates in that handoff, so origin isolation and
  redaction are part of the security boundary.
* The **application** never knows what platform it is in. It receives bytes and
  gives bytes back.
* The **session** between them is the host's own, opaque, single-document and
  short-lived.

## Security

* the bridge is **same-origin only**, and refuses to exist otherwise;
* both the origin **and** the source window are checked on every message;
* the `targetOrigin` is always explicit;
* the document bytes are transferred, not copied;
* the host is the trust boundary: it re-checks the permission on every write and
  never trusts the application's view of what is allowed.

## Conflict handling

The host owns it. It records the document's identity when it opens it and
compares it before it writes; if the document changed underneath, the write is
refused and the user is told.

The application is not involved: a conflict is a host decision, and the
application learns about it as a failed save.

## Incremental rollout

1. **A shared crate** in `craft-libs` with the message types and the transport,
   and **no behaviour change** anywhere.
2. **WordCraft** gains the bridge — it already has the richest set of services
   and the `async_saves` machinery the save answer needs. *(This is the patch
   prepared in `docs/reviews/GR-014/`, 4 files, +261/-4.)*
3. **PdfCraft, GridCraft and CADCraft** move to the shared crate, and GridCraft's
   copy gains the save answer it is missing.
4. The applications whose services are not browser-shaped yet — FigCraft
   (`NoServices`), FilmCraft and EffectCraft (`FsServices`) — get their seam
   first, then the bridge.

Each step is independent and shippable.

## Compatibility

* **Nothing changes for a person using the application on its own.** The bridge
  is off unless the page says `?host=parent`.
* **Nothing changes for the desktop application.** The bridge lives in
  `apps/<app>-web`.
* **The three existing bridges keep working.** Their message vocabulary is the
  one the shared crate implements; a host written against GridCraft works
  unchanged.
* **No new dependency.** The crate would use `wasm-bindgen` and `web-sys`, which
  the browser builds already use.
* **No second UI, no second document model.**

## Testing

* the crate's own tests: the message shapes, the origin and source checks, the
  transferables;
* per application: the bridge wires to that application's services — open,
  save, dirty, and the **failed save** path;
* end to end, against a real platform: open, edit, save, a new version, a
  refused stale save, and a read-only document.

The historical GR-006 bundle is not accepted as reproducible end-to-end
evidence for this candidate. The current tests do not demonstrate the complete
Seafile click → WordCraft edit → durable save/version → close/reopen path. That
test remains a release gate, along with an ONLYOFFICE regression.

## Adjacent upstream work

ArtCraft issue [#2420 — Suite-wide Host Mode](https://github.com/storytold/artcraft/issues/2420)
proposes a native Craft application as an authoritative remote UI/session host.
This RFC instead concerns browser/WASM editors embedded in an external file
platform, with Seafile authorizing and versioning document bytes. The scopes
are adjacent but not equivalent; any upstream proposal should explain that
boundary and check for shared protocol requirements before publication.

## Upstream split

| Part | Where it belongs |
| --- | --- |
| the message types, the transport, the origin checks | **ArtCraft** — `storytold/craft-libs` |
| the per-application wiring | **ArtCraft** — `apps/<app>-web` |
| the host contract document | **ArtCraft** — the documentation of the crate |
| the platform connector (the Seafile side) | **not** ArtCraft: it is a platform integration, and it lives in the platform's own ecosystem |
| a generic *write* endpoint in Seafile's third-party-editor hook | **Seafile** — it is editor-agnostic and useful to anyone embedding an editor |

## Open questions for the maintainers

1. Is `craft-libs` the right home, or should the bridge be a new repository?
2. Should the message vocabulary keep the per-application namespace
   (`wordcraft:open`) or become common (`artcraft:open`)? *Recommendation: keep it
   — it lets a host frame several applications, and it is what exists.*
3. Should the shared crate also hold the **desktop** control protocol
   (`docs/control-protocol.md`, present in twelve applications), so the browser
   and the desktop speak the same vocabulary? *Recommendation: a later phase.*
4. Should `?host=parent` carry a session descriptor, or stay dumb? *Recommendation:
   stay dumb — the application needs bytes, not a session.*
5. What is the rule for the applications that have no browser-shaped services
   yet?
