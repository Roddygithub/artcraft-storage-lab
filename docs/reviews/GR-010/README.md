# GR-010 — GridCraft: an `.xlsx` round-trips

Status: **GPT-6.1 Sol FAIL** on candidate `0edbe524b4fa321b0f73f8601afef390e7f785e6`; historical free-model PASS is
provisional and its E2E claim is not accepted. GridCraft durable save is not
verified with the current ticket/acknowledgement protocol.
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

## 2. The transport

The common contract, unmodified:

```text
child -> host   gridcraft:ready   { version }
host  -> child  gridcraft:open    { name, bytes }
child -> host   gridcraft:save    { name, bytes }
child -> host   gridcraft:dirty   { dirty }
child -> host   gridcraft:failed  { error }
```

**The one weakness of this application's bridge is documented and known:**
`Services::download` in GridCraft has the type `Fn(&str, &[u8])` — **no `Result`** —
so a failed save is only logged and the workbook is still marked saved
(`docs/HOST-CONTRACT.md` §3.5). The host page therefore keeps its own "not
persisted" state, and the upstream fix is A-3 in `docs/UPSTREAM-PLAN.md`.

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
| 3.5 save → a new Seafile version | **NOT VERIFIED**; old host event did not prove durable editor acknowledgement |
| 3.6 reopen, values and formulas preserved | **NOT VERIFIED**; earlier assertion inspected backend bytes, not a reopened editor |
| 3.7 concurrent edit → conflict, no silent overwrite | **SIMULATED** by the gateway's fake compare-and-swap test |
| 2.4 a double save | **NOT VERIFIED** against Seafile; identical-content shortcut is not evidence of a committed version |
| 2.12 an unsupported format | **PASS** for the gateway extension lookup unit check only |

GridCraft's upstream bridge has no save-result handler and marks its workbook
saved when handing bytes to the parent. It cannot currently satisfy the host's
durable acknowledgement contract. Formula semantics and editor reopen must be
tested after that bridge is repaired.

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
