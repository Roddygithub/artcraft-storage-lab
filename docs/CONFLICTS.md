# Conflicts and data integrity

Status: **PROVISIONAL — FREE REVIEW PASS** (remediated) · GPT REVIEW: PENDING
Evidence: `docs/reviews/GR-008/SEAFILE-CONCURRENCY-PRIMITIVES.md`

## 0. The rule

> A save must never silently overwrite somebody else's work, and a failed save must
> never be reported as a success.

Both are enforced **server-side**, in the gateway. The browser and the Craft
application are never trusted for either.

## 1. What Seafile gives us, and what it does not

| Mechanism | Exists? | Notes |
| --- | --- | --- |
| Content id (`obj_id`) of the current version | **yes** | `GET /api2/repos/<id>/file/detail/?p=` returns it; it is what the download token is minted against |
| File history | **yes** | `GET /api2/repos/<id>/file/history/?p=` — every write creates a version |
| "the file is gone" | **yes** | the file server answers `441` when the name is not in the current head commit |
| "the content did not change" | **yes** | the file server creates **no new commit** when the new bytes hash to the same id |
| Conditional update (ETag / `If-Match` / compare-and-swap) | **no** | `last_modify` only stamps the mtime; `head` is not a guard (GR-008 §1.3-§1.4) |
| Advisory lock | **yes** | Seafile's own `OnlineOffice` lock; a 40-minute lease, refreshed from the browser |

So: **the check has to be ours**, and it has to be a read-then-write.

## 2. The check

At **open** time the session records the content id:

```text
session.file_id = the obj_id observed when the document was opened
```

At **save** time the gateway:

```text
1. the session must exist, be unexpired and be bound to this file   (else 404/403)
2. the user must still have write permission on the file            (else 403)
3. the current obj_id is read again
     - no file            -> 404 "the file no longer exists"
     - a different obj_id -> 409 CONFLICT, nothing is written
4. the bytes are written through the file server's update API
5. the session's file_id becomes the id the file server answers with
```

### 2.1 The race window

Steps 3 and 4 are **two separate HTTP requests**. A write that lands in between wins
over the concurrent one: the second writer's content is silently replaced by the
first's.

* The window is **one API round trip** to Seafile (tens of milliseconds).
* Seafile offers no primitive that closes it (GR-008 §1.3-§1.4).
* Closing it would need a **file-server patch** that takes the expected content id
  and refuses the write when it no longer matches — an upstream change, tracked with
  the other upstream work (GR-014).

Until then the behaviour is stated plainly: **a conflict is detected and refused
except for a write that lands inside that window.** The gateway does not pretend
otherwise.

### 2.2 What the user sees

| Case | HTTP | Message |
| --- | --- | --- |
| somebody else saved first | 409 | "this file was modified by someone else while you were editing it; your changes were not saved" |
| the file was deleted or renamed | 404 | "the file no longer exists" |
| the permission was revoked | 403 | "you no longer have permission to edit this file" |
| the session expired | 404 | "unknown or expired session" |
| Seafile refused the write | 502 | "Seafile refused the write: …" |

None of them is a success. The Craft application is told the outcome
(`<app>:saveResult`, `docs/HOST-CONTRACT.md` §3.7), so an application that waits for
a confirmation — WordCraft's `async_saves` ticket — puts the document back in its
dirty state instead of believing the save worked.

## 3. Two editors on the same file

Seafile's own ONLYOFFICE integration gives every editor of a document **the same
`doc_key`**, which is how it gets co-editing: the document server serialises the
edits.

**We do not do that.** Each editor gets their own session, so:

* two people editing the same file are two sessions;
* the second save is **refused as a conflict** rather than merged.

That is deliberate. Silent last-writer-wins is the failure mode this project exists
to remove. Real co-editing is out of scope, and is a candidate for a later phase
(per-app co-editing would need a shared session key, i.e. the `doc_key` idea).

## 4. What the Craft application must not do

* It must not report a save as successful before the host has confirmed it.
* It must not retry a refused save on its own.
* It must keep the document dirty until the host says the write happened.

The third one is what the `async_saves` machinery in WordCraft already does
(`docs/HOST-CONTRACT.md` §3.5), and what the GridCraft bridge **does not** do — the
upstream patch has to fix that.

## 5. Tested

| Case | Test | Result |
| --- | --- | --- |
| a second editor saves first; the first is then refused | `tests/test_integration.py` §3 | **PASS** — HTTP 409, and the file on the server still holds the second editor's content |
| the file is renamed away under the editor | `tests/test_integration.py` §6 | **PASS** — HTTP 404 "the file no longer exists" |
| a save of unchanged content | `tests/test_integration.py` §3 | **PASS** — accepted, and the file server creates no new version |
| an unknown session | `tests/test_integration.py` §4 | **PASS** — HTTP 404 |
| the write race inside the window | — | **not tested** — see §2.1 |
| the permission revoked mid-session | — | **not tested** |
| the session idle timeout | — | **not tested** |
| a browser reload during editing | — | **not tested** |
| a `postMessage` from an unexpected origin | — | **not tested** |

The rows marked "not tested" are in `docs/TEST-MATRIX.md` and stay open until they
are.
