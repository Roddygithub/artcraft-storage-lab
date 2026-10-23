# GR-014 — the first ArtCraft upstream patch: the `?host=parent` bridge for WordCraft

Status: **PREPARED — NOT PUBLISHED** (the upstream hard gate: nothing goes to
`storytold/*` before `GPT REVIEW PASS`) · GPT REVIEW: PENDING

## 0. What this is

A patch that adds the browser host bridge to **WordCraft**, so that a page which
embeds WordCraft in an iframe can open a document in it and take the saved bytes
back — the same bridge **GridCraft, PdfCraft and CADCraft already have**.

* Target: `storytold/wordcraft`, branch `main` at
  `00bc6a4b028013b2dfb0e85e8b326aeed3ecff6d` (2026-10-22).
* The local prepared branch is at `9d46a47e4624546e9d193ef59e2939edcd47b40f`;
  [`DIFF.patch`](DIFF.patch) is the full diff from the target base — 4 files,
  +259 / −4.
* The branch in this workspace: `feature/host-bridge` in a local clone
  (`.work/wordcraft-patch`, gitignored).

## 1. Why this patch and not another

The mission's rule is *"prepare small contributions, not a huge multi-repo PR"*, and
the ArtCraft upstream rule is *"what belongs upstream in ArtCraft"*. This patch is
exactly the thing that belongs upstream:

* it is **generic** — it knows nothing about Seafile, about file servers or about
  storage platforms; it is a page-to-page protocol;
* it **reuses the existing convention** of three other apps in the suite, so it is
  an *alignment* of WordCraft with its siblings, not a new idea;
* it is **self-contained**: one new file in `apps/wordcraft-web/`, three small
  edits, and two extra `web-sys` features.

It is also the **blocker for GR-006** (the WordCraft DOCX MVP): without it there is
no way to open a DOCX in WordCraft from a page.

## 2. What the patch does

```text
apps/wordcraft-web/src/host.rs   NEW  the bridge
apps/wordcraft-web/src/web.rs     the host mode, the app's services, the failure path
apps/wordcraft-web/src/main.rs   the module declaration and the doc comment
apps/wordcraft-web/Cargo.toml    two web-sys features: MessageEvent, UrlSearchParams
```

### 2.1 The protocol

```text
HOST  -> CRAFT

  wordcraft:open        { name, bytes }        open this document
  wordcraft:saveResult  { ticket, ok, error }  how the parent's write ended

CRAFT -> HOST

  wordcraft:ready       { version }             the app is listening
  wordcraft:save        { name, bytes, ticket }  the app wants the bytes stored
  wordcraft:openRequest { purpose }             File › Open was asked for
  wordcraft:dirty       { dirty }               unsaved changes appeared or went away
  wordcraft:failed      { error }               the app could not start
```

The vocabulary follows the three existing bridges. The two additions are the
**ticket** on the save and the **`saveResult`** answer, and they are the point of
the patch: without them the app cannot know whether the host stored the file.
The prepared WordCraft patch currently encodes its internal `u64` ticket as a
JSON number, while the GridCraft patch encodes a namespaced string. These local
patches therefore do not yet share one ticket wire type; the common transport
proposal requires opaque strings and the WordCraft adapter must convert at its
boundary before the implementations are described as interoperable.

### 2.2 The security model, unchanged from the existing bridges

* the bridge only exists when the page is **framed**;
* it refuses to exist when the parent is on **another origin**
  (`parent.location().origin() != origin`);
* every incoming message is checked on **both** `event.origin` and `event.source`;
* every outgoing message names an **explicit `targetOrigin`** — the page's own
  origin, never `"*"`.

### 2.3 The save confirmation, using machinery that already exists

This is the part worth the maintainer's attention. WordCraft already has the right
mechanism, in `crates/ui-egui/src/async_saves.rs`:

```rust
let ticket = saves.start();                                  // the host's hook
saves.finish(ticket, SaveOutcome::Saved | Cancelled | Failed(error));
```

and the app already reacts to a failure by putting the document back in its dirty
state and showing the reason
(`crates/ui-egui/src/lib.rs:1286-1305`).

So the bridge does not invent anything: it starts a ticket, tells the parent which
ticket this save is, and finishes the ticket when the parent answers. **The
document is not marked saved until the host says it stored the file** — which is
the property the Seafile integration needs and which the browser's own download
path cannot offer (a browser cannot tell a page whether the user kept the file).

### 2.4 What the patch deliberately does not do

* it does not change the document model, the engine, the editor or the undo stack;
* it does not touch the desktop app;
* it does not add a dependency;
* it does not know what the host does with the bytes.

## 3. How it was verified

The editor reports `dirty=false` when it starts serialization, before the host
has written bytes. On `saveResult`, the bridge now clears its deduplication
state and re-emits the final dirty state. This gives the host an explicit
post-write event to confirm only after Seafile/storage has answered. The host
keeps its dirty guard set while the write is in flight.

| Check | Result |
| --- | --- |
| `cargo build --target wasm32-unknown-unknown -p wordcraft-web --release` | **compiles**, no new warning |
| `cargo clippy` on the new file | the crate's `deny` list (`unwrap_used`, `expect_used`, `panic`, …) is respected — the code uses `unwrap_or_else` on the poisoned inbox lock, like the rest of the file |
| `trunk build --release` | **done** — the site builds with the bridge |
| the bridge in a real browser | **PASS** — `tests/test_wordcraft_host_roundtrip.py` edits the real local WordCraft Web build, verifies changed DOCX bytes and the post-save dirty acknowledgement, then reopens the saved DOCX. Storage is an in-memory synthetic adapter, not Seafile. |
| the same bridge on the other apps | GridCraft and PdfCraft were exercised in a browser (GR-005); CADCraft was not |

## 4. What is NOT in this patch

* **the shared browser transport.** The existing upstream bridges have already
  drifted (PdfCraft adds `saveAs`; GridCraft cannot report a failed save). A
  shared layer in `storytold/craft-libs` is proposed in `docs/RFC-DRAFT.md`; the
  exact home (the current `craft-platform` browser module or a focused crate)
  and staged migration are still under review. This WordCraft patch remains a
  separate app adapter, not a shared transport implementation.
* **any mention of Seafile.** The patch is platform-agnostic on purpose.

## 5. The upstream hard gate

> **Nothing in this directory may be published before `GPT REVIEW PASS`.**
> No issue, no PR, no comment, no branch push to `storytold/wordcraft`.

The patch exists here, in this repository, for the GPT review to check.

## 6. The commit message, as it would be sent

```text
web: add the ?host=parent bridge to the browser build

The browser build opens files with the browser's picker and saves them with a
download. A page that embeds WordCraft in an iframe has to do both itself.

This adds the same bridge GridCraft, PdfCraft and CADCraft already have: the
page answers a same-origin parent, takes the document from it, and hands the
saved bytes back. The save carries a ticket and the parent answers with
'wordcraft:saveResult', so the document counts as saved only once the parent
has stored it, and stays unsaved when the parent refuses.
```
