# GR-010 — GridCraft: an `.xlsx` round-trips

Status: **GPT-6.1 Sol FAIL** on candidate `0edbe524b4fa321b0f73f8601afef390e7f785e6`; historical free-model PASS is
provisional and its E2E claim is not accepted. GridCraft durable save is not
verified against Seafile. A source patch now adds a ticketed host acknowledgement;
runtime integration and semantic reopen remain unverified.
Independent review of the ticketed acknowledgement patch: **PASS** for the
narrow bridge change, with three minor follow-ups; see
`GRIDCRAFT-ACK-REVIEW-20261023.md`. This does not verify GridCraft→Seafile
persistence or complete GR-010.
Date: 2026-10-22 · Library `c82cc792-389d-43e6-b963-0dab1a47a9a8` ·
`/artcraft-lab/synthetic.xlsx` (synthetic) · GridCraft 0.10.0 web build

## 0. The verdict

> Historical claim, rejected by independent GPT review: this bundle does not
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
part for GridCraft to parse; that change was made only in the temporary harness.

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

## 4. What is covered, and what is not

| Test-matrix row | State |
| --- | --- |
| 3.1 open an `.xlsx` inline | **SIMULATED** in the browser harness; Seafile route not verified |
| 3.2 edit a cell value | **SIMULATED** in the browser harness |
| 3.3 edit a formula | not yet exercised |
| 3.4 minimal formatting | not yet exercised |
| 3.5 save → a new Seafile version | **NOT VERIFIED**; source patch adds ticketed durable acknowledgement, but the patched bridge has not run through a Seafile save |
| 3.6 reopen, values and formulas preserved | **NOT VERIFIED**; earlier assertion inspected backend bytes, not a reopened editor |
| 3.7 concurrent edit → conflict, no silent overwrite | **SIMULATED** by the gateway's fake compare-and-swap test |
| 2.4 a double save | **NOT VERIFIED** against Seafile; identical-content shortcut is not evidence of a committed version |
| 2.12 an unsupported format | **PASS** for the gateway extension lookup unit check only |

The patch is recorded in `gridcraft-0.10.0-durable-save-ack.patch`, targeting
GridCraft `06920de8da609c19de7446945cfc62b844691efd`. It corrects the bridge's
early-clean behavior at source level. The E2E evidence above is historical and
does not exercise this patched bridge. Formula recalculation, a durable
acknowledgement tied to an actual Seafile commit, Seafile version creation, and
GridCraft editor reopen must still be tested before GR-010 can claim a
round-trip.

The independent review found no blocker or major issue in this narrow patch.
It flagged pending-ticket cleanup if a host disappears, the lack of protocol
version negotiation with older hosts, and a low-risk Save/Save As title race.
These are recorded as minor follow-ups; an old host fails safely by leaving the
workbook dirty. None changes the unverified Seafile persistence/reopen status or
the prior GPT FAIL.

## 5. What GR-010 adds beyond GR-005

Nothing new was built for this GR: the `.xlsx` path **is** the first technical
proof. This bundle exists so that the GR tracker names the format, and so that
the two are distinguishable when someone reads the queue:

* **GR-005** is about the *mechanism*: the gateway, the hook, the first end-to-end
  proof, in a browser.
* **GR-010** is about the *format*: an Office spreadsheet, round-tripped, with the
  conflict behaviour that Office documents actually need.

## 6. The follow-ups

| # | Item | Where |
| --- | --- | --- |
| 1 | GridCraft's bridge cannot report a failed save | upstream A-3 (`docs/UPSTREAM-PLAN.md`) |
| 2 | the shared host crate, so GridCraft's bridge is not its own copy | upstream A-1 |
| 3 | a formula and a formatting round-trip | needs a deterministic surface in GridCraft's web build |
| 4 | a concurrent edit driven from two real browsers | the HTTP test covers the conflict; the browser path does not |
