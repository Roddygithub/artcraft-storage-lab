# The save protocol

Status: **PROVISIONAL — FREE REVIEW PENDING** · GPT REVIEW: PENDING
GR-007 · Evidence: `docs/reviews/GR-006/`, `docs/reviews/GR-005/`,
`docs/HOST-CONTRACT.md` §3.5-§3.7

## 0. The rule

> A save is successful when **Seafile has committed a new version**. Not when the
> bytes left the editor. Not when the editor says it is done. Not when the host
> received them.
>
> Every step that can fail must be able to say so, and a failure must leave the
> document **dirty** — in the editor and in the gateway.

## 1. The whole sequence

```text
  the Craft app                     the host page                    the gateway              Seafile
       │                                 │                              │                      │
       │ ── wordcraft:save ────────────>│                              │                      │
       │   { name, bytes, ticket }       │                              │                      │
       │                                 │ ── POST /session/<sid>/save >│                      │
       │                                 │   (the bytes)                │                      │
       │                                 │                              │ ── file/detail ─────>│  (1) the current
       │                                 │                              │ <── id, permission ──│      content id
       │                                 │                              │                      │
       │                                 │                              │   (2) id != session.file_id
       │                                 │                              │       -> 409 CONFLICT, nothing written
       │                                 │                              │                      │
       │                                 │                              │ ── update-link ─────>│
       │                                 │                              │ <── the write URL ───│
       │                                 │                              │                      │
       │                                 │                              │ ── POST the bytes ──>│  (3) the write
       │                                 │                              │ <── the new file id ─│
       │                                 │                              │                      │
       │                                 │ <── { ok: true, file_id } ───│                      │
       │                                 │                              │                      │
       │ <── wordcraft:saveResult ──────│                              │                      │
       │   { ticket, ok: true }         │                              │                      │
       │                                 │                              │                      │
       │  the document is now clean     │  "Saved - new version ..."    │                      │
```

And on a failure at any step:

```text
       │                                 │                              │                      │
       │                                 │ <── { ok: false, error } ────│                      │
       │ <── wordcraft:saveResult ──────│                              │                      │
       │   { ticket, ok: false, error } │                              │                      │
       │                                 │                              │                      │
       │  the document stays DIRTY      │  "Save failed: ..."          │                      │
```

## 2. Step by step

### 2.1 The editor asks for a save

The Craft application produces the bytes and hands them to the host. WordCraft
does this through its `Services::download` hook, and — this is the part that
matters — it **starts a ticket** so that the save is not confirmed until the host
says so:

```rust
let ticket = bridge.saves.start();
bridge.post_save(&name, bytes, ticket)?;
```

The ticket travels in the message: `wordcraft:save { name, bytes, ticket }`.

The application then claims the ticket itself (`AsyncSaves::take_started`), so the
host and the application talk about the same save.

### 2.2 The host page persists the bytes

The host page POSTs the bytes and emitted filename to the gateway's
`/session/<sid>/save`. It does **not** decide anything: it has no credential
and no rule.

### 2.3 The gateway checks, then writes

```text
1. the session exists, is not expired, is not idle
2. the original filename and document type match (Save As/export is rejected)
3. the actual editing user is authorized on every save
4. the bytes are within the size limit
5. an upstream atomic CAS save accepts the opened content id; otherwise the
   gateway fails closed
```

The order matters: **the checks come before the write**, and the write is the last
thing that happens. A refused save writes nothing.

### 2.4 The gateway answers

```json
{ "ok": true, "file_id": "1c526786...", "version": "2026-10-22T13:00:30+00:00" }
```

or

```json
{ "ok": false, "error": "this file was modified by someone else while you were editing it; your changes were not saved",
  "conflict": true, "expected": "...", "current": "..." }
```

### 2.5 The host page answers the editor

This step **does not exist** in the two bridges that shipped before ours, and its
absence is a real defect (REVIEW-01, finding F1):

```js
if (ticket !== undefined && ticket !== null) {
  toCraft("saveResult", { ticket: ticket, ok: ok, error: error });
}
```

Without it, an application that waits for a confirmation waits forever, and the
document stays dirty even when the save worked.

### 2.6 The editor marks the document clean — or dirty again

WordCraft's own machinery does this, and it is the reason the patch reuses
`AsyncSaves` instead of inventing something:

```rust
match &outcome {
    SaveOutcome::Saved => log::info!("saved {name} through the save picker", save.name),
    SaveOutcome::Cancelled | SaveOutcome::Failed(_) => {
        if save.marked_saved && save.document == current {
            self.session.dirty = true;      // the document is unsaved again
        }
    }
}
```

and the user is told why:

```rust
SaveOutcome::Failed(error) => {
    let msg = i18n::fmt(tl!("Couldn't download {name}: {error}"), ...);
    self.status(msg);
}
```

**The evidence that the loop closes**: the browser console of the GR-006 run
contains the application's own line

```text
info: [wordcraft_ui_egui] ui-egui/src/lib.rs:1293: saved synthetic.docx through the save picker
```

which is the `SaveOutcome::Saved` branch. The ticket was started by the bridge,
claimed by the application, and finished by the host's answer.

## 3. The states a save can be in

| State | The editor | The gateway | The file on the server |
| --- | --- | --- | --- |
| editing, not saved | dirty | `unsaved = true` | the old version |
| saving | dirty (until the answer) | `unsaved = true` | the old version |
| saved | clean | `unsaved = false` | **a new version** |
| refused (conflict) | **dirty again**, with the reason | `unsaved = true` | the other user's version, untouched |
| refused (no permission) | dirty again, with the reason | `unsaved = true` | untouched |
| refused (the file is gone) | dirty again, with the reason | `unsaved = true` | gone |
| the network died | dirty | `unsaved = true` | the old version |

**There is no state in which the editor is clean and the server does not have the
edit.** That is the whole point of the ticket.

## 4. What is *not* in the protocol

* **No "save now" command from the host.** The editor decides when to save; the
  host only receives the result. A host-initiated save can be added later if a
  need appears.
* **No partial saves.** A document is saved whole. An OOXML file is a zip, and a
  half-written zip is not a document.
* **No "save as a new name".** The document keeps its name and its place. The
  Craft application may offer Save As to the user, but in host mode the host
  decides what the file becomes; today it is refused (the file server's update
  path replaces one path).
* **No retry.** A refused save is not retried by the editor or by the gateway. The
  user decides.
* **No version negotiation.** The gateway does not ask Seafile to keep both
  versions: it writes, and Seafile's own history keeps the old one.

## 5. The same content twice

The file server compares the content id of the new bytes with the existing one and
**creates no new commit** when they are the same. So a second save of an unchanged
document is accepted and changes nothing:

```text
[PASS] 3. a second save of the same content is accepted (same content, no new version)
```

This is why the "no changes" case needs no special handling: the platform already
has it.

## 6. The race we cannot close

The check and the write are two requests. A write that lands between them wins.
Seafile has no compare-and-swap, so closing the window needs a file-server patch.
See `docs/CONFLICTS.md` §2.1. **The protocol does not pretend the window does not
exist; it states it.**

## 7. What is tested, and what is not

| Case | Test | Result |
| --- | --- | --- |
| a save creates a new version | `tests/test_integration.py` §2, `tests/test_browser.py` §4 | **PASS** |
| the content is what was saved | `tests/test_integration.py` §2, `tests/test_browser.py` §5 | **PASS** |
| the document reopened from Seafile has the edit | `tests/test_browser.py` §6 | **PASS** |
| the editor confirms only after the write | `tests/test_browser.py` §3 + the application's own log line | **PASS** |
| the same content twice creates no new version | `tests/test_integration.py` §3 | **PASS** |
| a stale save is refused and the file is left alone | `tests/test_integration.py` §3 | **PASS** |
| a file that is gone is refused | `tests/test_integration.py` §6 | **PASS** |
| the editor stays dirty when the save is refused | — | **not tested in the browser** (the code path is the app's own, and the HTTP test covers the refusal) |
| the browser's leave-page guard warns about unsaved work | — | **not tested** |
| a save interrupted by a network failure | — | **not tested** |
| a save larger than the limit | — | **not tested** |
| a double save from the editor | — | **not tested** |

The rows marked "not tested" are open in `docs/TEST-MATRIX.md`.
