# GR-010 — GridCraft: an `.xlsx` round-trips

Status: **GPT-6.1 Sol FAIL** on candidate `0edbe524b4fa321b0f73f8601afef390e7f785e6`; the failure remains in force.
The patched GridCraft Web build has now completed a synthetic local Seafile
click/edit/save/version-ack/reopen run. It is runtime evidence for this path,
not final GPT approval, full GR-010 completion, or verification of all Craft
apps/platforms.
Independent review of the ticketed acknowledgement patch: **PASS** for the
narrow bridge change, with three minor follow-ups; see
`GRIDCRAFT-ACK-REVIEW-20261023.md`. That review is narrow and does not complete
GR-010 by itself. Runtime evidence and limits:
`GRIDCRAFT-SEAFILE-E2E-20261023.md`.
An independent review of this fixture/runtime-evidence update also returned
**PASS** with no blocker or major finding; its history API and full-suite limits
are recorded in `GRIDCRAFT-EVIDENCE-REVIEW-20261023.md`.
Date: 2026-10-23 · Isolated synthetic library · `synthetic.xlsx` · GridCraft
0.10.0 web build from the pinned patched source

## 0. The verdict

> Original claim, rejected by independent GPT review: this bundle did not
> prove a durable GridCraft save or semantic editor reopen. Its host simulation
> accepts emitted bytes independently of GridCraft's save result.

This is the proof the project was built around, and it is the one that answered the
pivotal question early: **the Craft web builds exist, and one of them already spoke
the host protocol.**

## 1. Why GridCraft was first

Two facts, both verified before anything was written:

1. **`.xlsx` occurs nowhere in the reference instance's real data**, and the
   deployed ONLYOFFICE configuration does not claim it. Claiming it therefore had
   **zero** blast radius: no existing file changed behaviour, and the ONLYOFFICE
   integration was untouched.
2. **GridCraft already ships the `?host=parent` bridge**
   (`apps/gridcraft-web/src/host.rs`, 166 lines), so no application had to be
   changed and no Rust toolchain was needed: the web build is published in the
   GitHub release (`gridcraft-web-0.10.0.zip`, 7 MB).

That combination is what made a **zero-risk** first proof possible on the real
instance (`docs/reviews/GR-005/README.md` §1).

## 2. The historical transport and current patch

The common contract, unmodified:

```text
child -> host   gridcraft:ready   { version }
host  -> child  gridcraft:open    { name, bytes }
child -> host   gridcraft:save    { name, bytes, ticket }
host  -> child  gridcraft:saveResult { ticket, ok, error }
child -> host   gridcraft:dirty   { dirty }
child -> host   gridcraft:failed  { error }
```

The pinned GridCraft bridge previously marked the active workbook clean as soon
as it handed bytes to the host. The prepared source patch adds a unique ticket,
keeps the exact immutable workbook snapshot with that ticket, and only updates
the matching document's saved snapshot after a successful `gridcraft:saveResult`.
An edit made while the save is pending remains dirty; exports carry no workbook
snapshot and cannot mark the source clean. This behavior has a focused engine
unit test and the patched web crate passes a WASM `cargo check`; the patch has
not yet been exercised against the gateway/Seafile runtime.

### Browser smoke of the patched bridge

The patched release build was loaded as a real GridCraft Web application in
headless Chromium with a temporary same-origin parent. The parent opened a
synthetic XLSX, accepted the app's emitted bytes into in-memory test storage,
and sent a failed result for the first save and a successful result for retry.
GridCraft stayed dirty after the failure and became clean only after the success
acknowledgement. The serialized XLSX was a valid ZIP package and contained the
actual cell edit (`A3` changed from `sum` to `Bk`). The test parent/storage were
synthetic: this did **not** call Seafile, create a Seafile version, or prove
formula recalculation/reopen semantics. The fixture needed a minimal styles
part for GridCraft to parse; the committed fixture generator now emits that
minimal styles part. A fresh Seahub click opened the regenerated fixture in
GridCraft without a missing-styles warning; see
`gridcraft-styled-fixture-open.png`. The corrected fixture has not yet repeated
the edit/save/reopen sequence.

Commands/checks run against the pinned patched source checkout:

| Command/check | Result | Scope |
| --- | --- | --- |
| `cargo test -p gridcraft-engine --lib` | **391 passed** | engine unit suite, including the exact-snapshot acknowledgement test |
| `cargo test -p gridcraft-ui-egui --lib` | **151 passed** | UI library unit suite |
| `cargo test -p gridcraft-ui-egui --test file_menu` | **12 passed** | integration target whose download callback signature changed |
| `cargo test -p gridcraft-ui-egui --test text_box_editing` | **4 passed** | integration target whose download callback signature changed |
| `cargo check -p gridcraft-web --target wasm32-unknown-unknown` | **PASS** | WASM target and bridge type-check |
| `trunk build --release` | **PASS** | optimized patched GridCraft Web artifact |
| Chromium edit → fail ack → retry → success ack | **PASS** | real GridCraft editor; synthetic parent and in-memory storage, not Seafile |

`cargo test -p gridcraft-ui-egui` was also attempted as the full crate suite, but
the environment hit `Disk quota exceeded` while compiling unrelated integration
test binaries. The two integration targets affected by this API change passed
individually; the full integration suite is therefore **NOT VERIFIED**.

## 3. Historical runs — evidence scope corrected by GPT Sol

### 3.1 The Seafile side, without a browser

`tests/test_integration.py` uses fake in-memory storage. Its PASS result checks
gateway behavior only; it is **not a Seafile integration test**:

```text
1. the host page is rendered
1. the host page asks for a document over the session
1. the session is described as data
1. the session is bound to the file that was opened
1. the document is delivered
2. the save is accepted
2. a NEW version exists
2. the history grew
2. the new content is what we saved          B2 = '<is><t>1337</t></is>'
3. a second save of the same content is accepted (same content, no new version)
3. a save with unchanged content is accepted
3. the second editor saves first
3. the STALE save is REFUSED                 HTTP 409
3. the refusal names the conflict
3. the file on the server was NOT overwritten  B2 = '<is><t>4242</t></is>'
4. an unknown session cannot write           HTTP 404
5. a known session can still write
6. a save of a file that is gone is REFUSED  HTTP 404
7. a symlink out of the static root is refused  HTTP 400
```

### 3.2 Browser host simulation

`tests/test_browser.py` injects a gateway page in a browser. It does not perform
the Seafile file-list click, commit a real Seafile version, or reopen GridCraft
from Seafile. Its earlier PASS transcript is preserved as historical evidence,
not an E2E result.

```text
[PASS] 1. the Craft app loaded and the document was delivered  -- synthetic.xlsx opened
[PASS] 2. the Craft app rendered a canvas
[PASS] 3a. the editor reported unsaved changes after the edit  -- dirty = True
[PASS] 3. the editor's own Save reached the host and was persisted
[PASS] 4. a NEW Seafile version exists
[PASS] 4. the history grew
[PASS] 5. the typed text is in the file Seafile now holds  -- the worksheet contains 4242: True
[PASS] 6. the document reopened from Seafile still has the edit
```

Screenshot: `docs/reviews/GR-005/browser-proof.png` — GridCraft with its ribbon,
the edited cell, and the host page's `Saved — new version …` line.

## 4. Seafile runtime round-trip

The earlier evidence below is historical and simulated. A subsequent run used
the actual Seahub file list, patched local Seafile fileserver, gateway and real
GridCraft Web/WASM, then saved and reopened the synthetic workbook through a new
Seahub click. The editor showed the saved edit, and the fetched XLSX bytes
contained it. See `GRIDCRAFT-SEAFILE-E2E-20261023.md` and
`gridcraft-seafile-reopen.png` for captured details and limits. This was a
local synthetic stack, not production Seafile. Formula recalculation, GridCraft
concurrency, deployment security, and other Craft apps remain unverified.

## 5. What is covered, and what is not

| Test-matrix row | State |
| --- | --- |
| 3.1 open an `.xlsx` inline | **REPRODUCED** in isolated synthetic Seafile; real Seahub click opened GridCraft Web |
| 3.2 edit a cell value | **REPRODUCED** in GridCraft Web; saved cell displayed after a fresh Seahub click/reopen |
| 3.3 edit a formula | not yet exercised |
| 3.4 minimal formatting | not yet exercised |
| 3.5 save → a new Seafile version | **PARTIALLY REPRODUCED** in isolated synthetic Seafile; patched route returned a committed head/file ID and host acknowledged the version, but the history-list increment was not independently queried |
| 3.6 reopen, values and formulas preserved | **PARTIALLY REPRODUCED**; fresh GridCraft session displayed the edit; formula XML/cached value survived, but recalculation after input change is unverified |
| 3.7 concurrent edit → conflict, no silent overwrite | **SIMULATED** by the gateway's fake compare-and-swap test |
| 2.4 a double save | **NOT VERIFIED** against Seafile; identical-content shortcut is not evidence of a committed version |
| 2.12 an unsupported format | **PASS** for the gateway extension lookup unit check only |

The patch is recorded in `gridcraft-0.10.0-durable-save-ack.patch`, targeting
GridCraft `06920de8da609c19de7446945cfc62b844691efd`. It corrects the bridge's
early-clean behavior at source level. The isolated Seafile runtime E2E now
exercises this patched bridge through a durable acknowledgement and fresh
editor reopen. Formula recalculation, GridCraft conflict behavior, deployment
hardening and the broader Craft/platform scope remain open before release or
GPT PASS.

The independent review found no blocker or major issue in this narrow patch.
It flagged pending-ticket cleanup if a host disappears, the lack of protocol
version negotiation with older hosts, and a low-risk Save/Save As title race.
These are recorded as minor follow-ups; an old host fails safely by leaving the
workbook dirty. None changes the unverified Seafile persistence/reopen status or
the prior GPT FAIL.

## 6. What GR-010 adds beyond GR-005

Nothing new was built for this GR: the `.xlsx` path **is** the first technical
proof. This bundle exists so that the GR tracker names the format, and so that
the two are distinguishable when someone reads the queue:

* **GR-005** is about the *mechanism*: the gateway, the hook, the first end-to-end
  proof, in a browser.
* **GR-010** is about the *format*: an Office spreadsheet, round-tripped, with the
  conflict behaviour that Office documents actually need.

## 7. The follow-ups

| # | Item | Where |
| --- | --- | --- |
| 1 | Upstream GridCraft baseline still has optimistic save; local ticketed patch is not upstream | upstream A-3 (`docs/UPSTREAM-PLAN.md`) |
| 2 | A shared Craft host crate/implementation is not upstream | upstream A-1 |
| 3 | Recalculate a formula after editing an input and verify formatting round-trip | needs deterministic GridCraft Web interaction |
| 4 | Exercise a GridCraft concurrent save conflict through real editor sessions and Seafile | current runtime conflict test is fake-CAS only |

## 8. Independent evidence-review findings and disposition

| Finding | Disposition |
| --- | --- |
| Browser history-list request returned HTTP 403; no version-count comparison was captured. | GR-010 rows 3.5 are marked `[~]`; committed-head acknowledgement plus changed persisted bytes are recorded, with the history-query limit explicit. |
| Reviewer flagged styles XML indentation. | Checked `tests/fixtures/make_fixtures.py:125`; the entry has two leading spaces, matching adjacent entries. No correction was needed. |
| Full `gridcraft-ui-egui` integration suite was blocked by disk quota. | Kept explicitly NOT VERIFIED at lines 93–96; the two affected integration targets passed individually. |

The independent review returned PASS with no blocker or major finding. Its narrow
scope does not complete GR-010 or the full all-Craft/multi-platform project.
Formula recalculation, GridCraft conflicts, full integration-suite execution,
and the history-list count remain open. Sol's prior FAIL and the upstream lock
remain unchanged.
