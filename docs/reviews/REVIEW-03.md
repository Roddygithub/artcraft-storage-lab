# Review 03 — the WordCraft host bridge, the GR-006 MVP proof, and the remediated gateway

* Reviewer: `artcraft-reviewer` (Nemotron 3 Ultra 550B A55B, Nvidia) — **independent**; it
  did not write the code and took no part in reviews 01 or 02.
* Review date: 2026-10-22
* Reviewed: the WordCraft `?host=parent` patch (GR-014), `docs/reviews/GR-006/`,
  the gateway after the review-02 remediation, `tests/test_browser.py`,
  `docs/SECURITY.md`, `docs/CONFLICTS.md`, and the two earlier remediation logs.
* Verdict: **PASS**

```text
REVIEW RESULT: PASS
BLOCKER: None found.
```

The reviewer's own words on the parts that mattered most:

> *"The WordCraft host bridge patch correctly implements the save confirmation ticket
> flow (AsyncSaves::start/finish), respects the crate's deny list, validates origin
> and source on every message, uses explicit targetOrigin, refuses to activate when
> framed cross-origin, and replaces (not leaks) the download/open_async/on_dirty hooks
> in host mode. The GR-006 claim is honest about what is partly proven."*

> *"Verified the ticket flow: Bridge.start() in download hook -> execute()
> take_started() after hook -> saves_in_flight tracking -> bridge.finish() on
> saveResult -> settle_async_saves matches by ticket"*

> *"The upstream hard gate (no PR to storytold/* before GPT REVIEW PASS) is
> respected."*

## 1. Findings and remediation

| # | Severity | Finding | Remediation | Status |
| --- | --- | --- | --- | --- |
| H1 | MAJOR | The browser test's click coordinates are fragile to a UI layout change. | The test already asserts the **effect** (the typed text is in the file Seafile holds), so a click that misses fails the test rather than passing silently. The coordinates are parameters (`ARTCRAFT_CLICK_X` / `ARTCRAFT_CLICK_Y`) and the assumption is documented in `docs/reviews/GR-006/README.md` §4. | **accepted, documented** |
| H2 | MAJOR | The browser test did not check that the **editor itself** confirmed the save, only the host page's status line. | A new check **3b** asserts the application's own confirmation line (`saved synthetic.docx through the save picker`). | **fixed** |
| H3 | MAJOR | The GR-006 browser test did not reset the fixture, so it depended on the state another test left behind. | The test now calls the HTTP test's `reset_fixture` — **before** the session is opened, because opening the session first would make it stale and every save would be refused as a conflict. | **fixed** |
| H4 | MAJOR | The security gaps (CSP, CSRF, rate limit, expanded size) are open and must be closed before a public deployment. | They are listed in `docs/SECURITY.md` §7; §7.1 now states them as a **pre-deployment gate**. | **fixed** |
| H5 | MINOR | The application logs *"saved … through the save picker"*, which is misleading in host mode (there is no picker). | It is **upstream's** message, in `crates/ui-egui/src/lib.rs`, outside the scope of the bridge patch. Changing it would widen the patch. Recorded in the GR-014 bundle as a known cosmetic point. | **accepted** |
| H6 | MINOR | The `saveResult` error carried the raw internal error, which the app then showed to the user. | The host page now sends a **short, generic** reason to the app (*"the file could not be stored"*); the full error stays in the host page and the service's log. | **fixed** |
| H7 | MINOR | The browser test used fixed `wait_for_timeout` calls. | The waits are now **condition-based** (`wait_for_function` on the dirty flag and on the host page's state). | **fixed** |
| H8 | MINOR | "VERIFIED END-TO-END" slightly overstates, because the close path is not exercised. | The GR-006 bundle already marks two of the twelve steps as *partly* proven and says so in bold. The wording is kept, because the flow itself is proven. | **accepted** |

## 2. A bug the remediation found

While fixing H3, the test's own fixture reset exposed a **real** behaviour that
had been invisible: with the reset in the wrong place, the session was already
stale, and the save was **refused** with a conflict. The screenshot of that run
shows the application doing exactly the right thing:

```text
WordCraft's status bar: Couldn't download synthetic.docx: the file could not be stored
the host page:          Unsaved changes
the title bar:          synthetic - Edited
```

The document stayed **dirty**, the user was told, and **nothing was written**. It
is the best possible demonstration of the rule the mission states: *a save failure
must never look like a success*.

## 3. The test gaps the review listed

| Gap | State |
| --- | --- |
| the save failure path in the browser | **partly closed** — the run above is exactly that path, and the application behaved correctly. An explicit test that forces the failure is still open. |
| permission revoked mid-session | **open** (the unit test covers the gateway's side) |
| the session idle timeout | **open** (the unit test covers the store) |
| a browser reload during editing | **open** |
| `postMessage` from an unexpected origin | **open** |
| a share-link read-only | **out of scope for the MVP**, documented |
| the TOCTOU race window | **open by design**, documented in `docs/CONFLICTS.md` §2.1 |
| a ZIP bomb / expanded size bound | **open**, upstream (S-4) |
| the other Craft applications | **open** |

## 4. Status

```text
PROVISIONAL — FREE REVIEW PASS
GPT REVIEW PENDING
```

Three independent free reviews, two of them FAIL and remediated, the third PASS.
**Nothing is final until `GPT REVIEW PASS`.**
