# GR-012 — a non-Office format round-trips

Status: **GPT-6.1 Sol FAIL** on candidate `0edbe524b4fa321b0f73f8601afef390e7f785e6`; the later exact-byte remediation received a bounded Nemotron PASS, not an overall project review.
Date: 2026-10-23 · See `VECTORCRAFT-SEAFILE-E2E-20261023.md` for the reproduced run.

## 0. The verdict

> The historical test claim was rejected by GPT Sol: it omitted the required
> `Origin`, accepted a rectangle path as the drawn stroke, and called byte
> equality a reopen. A later manual run now reproduces a VectorCraft SVG
> edit/save/version/history/reopen in isolated Seafile. The run uses
> VectorCraft's private page API, so the common Craft host contract is still
> **NOT VERIFIED** for non-Office formats.

## 1. Why VectorCraft, and why not PdfCraft

The first attempt was PdfCraft, and it **failed**, for a reason worth recording:

```text
[PASS] the editor's own Save reached the host and was persisted
[FAIL] 3a. the editor reported unsaved changes after the edit  -- dirty = False
[FAIL] 4. a NEW Seafile version exists
[FAIL] 5. the file Seafile holds is the one the editor produced
```

The application was **never dirty**: the UI interaction did not produce a
modification, so the Save handed the gateway the *unchanged* bytes, and the file
server correctly created **no new version** (its "same content id" path). The
host page's "Saved" was therefore true and useless at the same time — which is
why the test asserts the *effect*, not the editor's word.

The lesson: **the modification must be driven deterministically, not by guessing
where to click.** The independent review had already flagged click coordinates as
a fragility (REVIEW-03, H1).

VectorCraft is the one application that answers it. It exposes its own page API —
`window.vectorcraft` — which is its **control protocol in the page**
(`docs/control-protocol.md`), so the whole flow is deterministic:

```js
api.request("ui.tool.list", {})                 // find a drawing tool
api.request("ui.tool.select", {tool: "pencil"})
api.request("ui.pointer", {events: [...]})      // drag in DOCUMENT space
api.request("app.save", {path: name, svg: {}})  // the editor's own save
api.files() / api.readFile(name)                // the bytes back
```

`ui.pointer` takes `space: "doc"`, so the drag does not depend on the zoom or the
window size.

## 2. The transport

VectorCraft does **not** speak the `?host=parent` protocol the other three
applications speak. It exposes its page API instead, so the host page gained a
**second transport adapter** — and the dispatch entry no longer claims
`?host=parent` for it, because it would be a lie (`docs/reviews/REVIEW-04.md`,
G4):

| | postMessage bridge (gridcraft, pdfcraft, wordcraft, cadcraft) | page API (vectorcraft) |
| --- | --- | --- |
| open | the host posts `<app>:open {name, bytes}` | the host calls `vectorcraft.openFile(name, bytes)` |
| save | the app posts `<app>:save {name, bytes, ticket}` and the host answers | the host **polls** `vectorcraft.files()` and reads the file with `readFile` |
| dirty | the app posts `<app>:dirty` | **no signal** — the host page does not report it |

The adapter lives in `integration/gateway/hostpage.py` and is selected by the
application name. The postMessage path is unchanged.

**Four gaps are recorded, not hidden** (the independent review, REVIEW-04, found
three of them):

1. the page API has **no save event and no dirty signal**. The host page polls
   `files()` every 700 ms and compares the serialized bytes exactly. It can
   observe changed output, but cannot observe a save event that produces bytes
   identical to the last committed output. Only a **stored** save becomes the
   new baseline, so a refused save is retried instead of lost. The earlier
   32-bit content fingerprint could collide; the local browser regression test
   now uses a deterministic collision pair to guard the exact-byte comparison.
   A post-fix Seafile-backed VectorCraft run is recorded in the runtime report;
   the exact collision pair remains a synthetic regression case;
2. because there is no dirty signal, the host page cannot warn about unsaved
   *edits*. It warns on `beforeunload` **while a save is in flight**. The editor
   itself keeps unsaved work in **recovery copies** in the browser: *"Your unsaved
   changes are kept in this browser: reload the page to get them back."* A dirty
   signal is upstream work (`docs/UPSTREAM-PLAN.md` A-2);
3. the page API is **not** the common contract. It is VectorCraft's own surface,
   and it is the reason this GR is a *proof of the integration*, not a proof that
   the common contract covers non-Office formats. That is GR-004's open question
   Q-2 and the RFC's rollout step;
4. the page keeps at most **16** saved files
   (`apps/vectorcraft-web/src/saved_files.rs`: `MAX_SAVED = 16`), oldest first, so
   a seventeenth save evicts the first. The 700 ms poll makes that window small,
   but the limit is upstream.

The adapter also checks the frame before it drives it: `frameIsOurs()` verifies
the frame's **origin** (REVIEW-04, G9) — a direct property read crosses no
boundary that `postMessage` would have checked, so the check is made here.

## 3. Historical run (not accepted as E2E)

The old run recorded changed bytes, a content id, and history growth. It did not
prove that the expected pencil stroke was present or that VectorCraft parsed and
rendered the bytes after reopening. The transcript below is preserved only as
historical output.

```sh
export ARTCRAFT_SEAFILE_URL=... ARTCRAFT_SEAFILE_TOKEN=...
export ARTCRAFT_SEAFILE_ACCESS_TOKEN=... # synthetic document capability; never commit it
export ARTCRAFT_GATEWAY=http://127.0.0.1:8777
export ARTCRAFT_SCREENSHOT=docs/reviews/GR-012/browser-proof-svg.png
python3 tests/test_gr012_svg.py c82cc792-389d-43e6-b963-0dab1a47a9a8 /artcraft-lab/synthetic.svg
```

```text
  (fixture restored: synthetic.svg, 270 bytes)
[PASS] 1. the host page opened the document through the page API  -- synthetic.svg opened
[PASS] 2. the editor lists a drawing tool  -- tool ~ 'pencil'
[PASS] 3. the drawing tool is selected  -- {"tool": "pencil"}
[PASS] 4. the tool drew in document space  -- {"key": null, "selection": [4], "tool": "pencil"}
[PASS] 5. the document really changed  -- 1579 -> 2121 bytes of inspect state
[PASS] 6. the editor's own save command ran  -- {"bytes": 609, "format": "svg", ...}
[PASS] 7. the host page took the bytes and stored them  -- Saved - new version 2026-10-22T15:06:09+00:00
[PASS] 8. a NEW Seafile version exists  -- content id fd8fd133431c…
[PASS] 9. the file history has more than one version  -- 2 version(s)
[PASS] 10. the document reopened from Seafile is the edited one  -- 270 -> 609 bytes

ALL CHECKS PASSED
```

The application's own account of what happened, from the browser console:

```text
info: [vectorcraft_web::web] vectorcraft-web/src/web.rs:114: vectorcraft-web: wgpu backend Gl
warning: [eframe::web::app_runner] ...: Title("synthetic.svg - VectorCraft")
warning: [eframe::web::app_runner] ...: Title("*synthetic.svg - VectorCraft")     <- the dirty marker
warning: [eframe::web::app_runner] ...: Title("synthetic.svg - VectorCraft")      <- saved
```

**The asterisk is the editor's own dirty flag, appearing and going away.**

## 3.1 Reproduced Seafile runtime flow (2026-10-23)

The previous statement that the revised test had not run against Seafile is
superseded by the manual runtime evidence in
[`VECTORCRAFT-SEAFILE-E2E-20261023.md`](VECTORCRAFT-SEAFILE-E2E-20261023.md).
The actual Seahub list click opened VectorCraft; the editor drew and serialized
a path; Seafile returned a new version/content ID; readback matched all 609
editor bytes; the Seafile History UI showed both the 270-byte and 609-byte
versions; and a fresh Seahub click opened VectorCraft with the path parsed.
This is a VectorCraft-specific transport proof, not proof of the common host
contract or support across Craft apps.

## 3.2 Bounded independent review of the polling fix

Nemotron returned **PASS for the exact-byte remediation only**. It independently
checked the deliberate FNV collision pair, synthetic browser regression, and
post-fix Seafile readback/reopen evidence. It also recorded remaining minor
gaps: VectorCraft cannot signal all dirty edits, save-failure retry and
concurrent saves remain untested, and iframe sandbox/CSP controls are absent.
The complete bounded review is in
[`REVIEW-NEMOTRON-VECTORCRAFT-EXACT-BYTES.md`](../REVIEW-NEMOTRON-VECTORCRAFT-EXACT-BYTES.md).
This result does not clear the historical GPT FAIL or establish common-contract
coverage.

## 4. The screenshot

`browser-proof-svg.png`:

* **VectorCraft** running in the browser, with its full interface (File, Edit,
  Object, Type, Select, Effect, View, Window, Help; the toolbar; the Properties,
  Layers and Libraries panels);
* the document tab **`synthetic.svg @ 408.5 % (RGB/Preview)`** — the Seafile file;
* the canvas: the original blue rectangle and its "ArtCraft Lab" text, **with the
  new pencil stroke crossing it**;
* the Properties panel showing the new path's geometry — X 120 px, Y 90 px,
  W 120 px, H 60 px, exactly the drag the test performed in document space;
* VectorCraft's status bar: **"Saved synthetic.svg with 1 note(s): SVG keeps the
  artwork but not everything…"**;
* the host page's status: **"Saved — new version 2026-10-22T15:06:09+00:00"**.

## 6. The save warning, and why it is correct

VectorCraft's save returned, in its `warnings`:

```text
SVG keeps the artwork but not everything a VectorCraft document holds
(editable effects, symbols, swatches, styles): save as VectorCraft to keep it
all editable
```

That is the editor being honest about its own format, not the integration losing
data: the document was **opened from SVG**, so it is saved back as SVG, and SVG
cannot hold everything a VectorCraft document can. The same warning appears in
the desktop application.

`svg: {}` in the save call means *"the document's own SVG options"* and makes the
save run **directly** instead of opening the SVG Options dialog
(`docs/control-protocol.md`: "With `svg: {…}` (the `document.formats` SVG options)
they run directly").

It is also a useful reminder for the dispatcher (`docs/FILE-DISPATCH.md`): a
round trip through an interchange format is lossy by nature, and the editor says
so.

## 6. What this GR does and does not claim

| Claim | Status |
| --- | --- |
| a non-Office format round-trips through Seafile and a Craft web editor, with semantic reopen | **REPRODUCED for one synthetic SVG in VectorCraft**; see the 2026-10-23 runtime report |
| the **common contract** (`?host=parent`) covers non-Office formats | **NOT PROVEN** — VectorCraft has no bridge; CADCraft has one but its web build exposes no automation surface |
| PdfCraft handles a PDF round-trip | **NOT PROVEN** — the modification could not be driven; see §1 |
| VectorCraft's page API can edit and serialize the synthetic SVG locally | **REPRODUCED** locally and in the Seafile-backed runtime run |
| the page API is a second, supported transport | **implemented**, but lacks editor dirty/commit acknowledgement and is not the common contract |

## 7. The follow-ups

| # | Item | Where |
| --- | --- | --- |
| 1 | a `?host=parent` bridge for VectorCraft, so the page API is not needed | upstream, with the shared crate (RFC rollout step 4) |
| 2 | a save event and a dirty signal on the page API | upstream (VectorCraft's `api.rs`) |
| 3 | the PDF round-trip: drive a real modification in PdfCraft | needs either a deterministic surface in PdfCraft's web build, or a UI-driving helper that is not click coordinates |
| 4 | CADCraft + a synthetic DXF: the non-Office proof **through the common contract** | the bridge exists; the fixture is a text format, so it is easy to synthesise; the modification needs the same deterministic surface |

Number 4 is the cleanest way to make the *contract* (not just the integration)
cover a non-Office format, and it is the natural continuation.
