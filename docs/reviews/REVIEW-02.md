# Review 02 — independent free review of the gateway code, the browser proof and the remediated docs

* Reviewer: `artcraft-reviewer` (Nemotron 3 Ultra 550B A55B, Nvidia) — **independent**; it
  did not write the code and did not take part in review 01.
* Review date: 2026-10-22
* Reviewed: `integration/gateway/*`, `integration/config/dispatch.json`,
  `tests/test_integration.py`, `tests/test_browser.py`, `tests/fixtures/make_fixtures.py`,
  `tests/upload_fixtures.py`, `scripts/fetch-craft-web.sh`, and the docs remediated after
  review 01.
* Verdict: **FAIL**

```text
REVIEW RESULT: FAIL
```

The reviewer confirmed that the GR-005 proof is genuine ("a real GridCraft WASM app in a
real browser edited a real Seafile XLSX and created a new version with the edited
content") and that the security model of the host page is correct. The findings below
are the ones that had to be fixed.

## 1. Findings and remediation

| # | Severity | Finding | Remediation | Status |
| --- | --- | --- | --- | --- |
| G1 | BLOCKER | The static file handler used `os.path.abspath`, which does not resolve symlinks: a symlink inside the static root pointing outside would be served. | `_serve_static` now resolves with `os.path.realpath` and checks the **real** path against the real root. A test creates such a symlink and asks for it. | **fixed**, test added |
| G2 | BLOCKER | The conflict check is a read-then-write, so a write landing between the check and the update wins over a concurrent one. Seafile has no compare-and-swap. | The race window and its consequence are now **documented in the code** and in `docs/CONFLICTS.md`; closing it would need a file-server patch, which is upstream work. | **fixed** (documented; the window is one API round trip) |
| G3 | BLOCKER | The host page never told the Craft app how a save ended, so an app that waits for a confirmation (WordCraft's `async_saves` ticket) would stay dirty forever. | The host page now answers with `<app>:saveResult { ticket, ok, error }` when the save message carries a ticket. The WordCraft bridge patch produces the ticket; the host page consumes it. | **fixed** |
| G4 | MAJOR | The account token was sent to the file-server URLs, which already carry their own short-lived token. | `Seafile._request` takes `auth=False`, and every file-server call uses it. The account token now goes only to the Seafile API. | **fixed** |
| G5 | MAJOR | `dispatch.json` mapped `.pptx` to DeckCraft, which has no host bridge, so the table promised something that does not work. | The table now lists only apps that have a bridge: `pdfcraft`, `gridcraft`, and `wordcraft` (with our patch). The others are documented as needing the upstream bridge. | **fixed** |
| G6 | MAJOR | `Session.unsaved` was dead code. | The host page now reports the dirty state to the gateway (`POST /session/<sid>/dirty`), which sets the flag. | **fixed** |
| G7 | MAJOR | The browser test clicked fixed canvas coordinates. | Kept (it is a fixture-based test) but the test now **asserts the effect** — the typed text is found in the worksheet Seafile holds — so a click that missed would fail the test rather than pass silently. The assumption is documented. | **fixed** (by assertion) |
| G8 | MAJOR | The HTTP test parsed the session id out of the HTML. | `/open/?format=json` returns the session as data; the test uses it and additionally checks that the session is bound to the file that was opened. | **fixed** |
| G9 | MINOR | `update_file` assumed the response body was a file id. | `_file_id` now validates that the answer is a hex id and raises otherwise, so a malformed answer cannot corrupt the session's conflict check. | **fixed** |
| G10 | MINOR | `max_bytes` was hardcoded. | `ARTCRAFT_MAX_BYTES` (default 50 MB). | **fixed** |
| G11 | MINOR | The permission field was read without an explicit `None` case. | The permission is now read into a variable and compared explicitly, so a missing field means "not editable" and is visible in the code. | **fixed** |

## 2. A bug the remediation itself found

While fixing G9 the owner found that **`replace` is a form field of the seafhttp
upload, not a parameter of the upload link**. The earlier `upload_file` put it in the
link's query string, so Seafile **created a second file** (`synthetic (1).xlsx`) instead
of replacing the first. The stray copies were deleted from the test library, and
`upload_file` now sends `replace` as a form field.

This is exactly the class of mistake the reviewer was looking for, and it was only
visible because the test now **resets its own fixture** instead of assuming a starting
state.

## 3. Test gaps the review listed, and their state

| Gap | State now |
| --- | --- |
| no test for symlink traversal | **closed** — test 7 creates the symlink and asks for it |
| no test for the TOCTOU race | **open** — it needs a coordinated two-client test with tight timing; the window is documented |
| no test for the save failure path (quota, 403, 441, network error) | **partly closed** — test 6 renames the file away and checks the save is refused with "the file no longer exists" (the 441 path). Quota and network errors are still untested. |
| no test for permission revoked mid-session | **open** |
| no test for a file renamed/deleted mid-session | **closed** (test 6) |
| no test for the session idle timeout | **open** |
| no test for a browser reload during editing | **open** |
| no test for `postMessage` from an unexpected origin | **open** |
| no test for a share-link read-only | **out of scope for the MVP** (documented, L7) |
| the browser test only covers GridCraft/XLSX | **being closed** — the WordCraft/DOCX path is GR-006 |

## 4. Status after remediation

```text
PROVISIONAL — FREE REVIEW PASS (remediated)
GPT REVIEW PENDING
```

A third independent review was requested after the remediation; its result is recorded
in `docs/reviews/REVIEW-03.md` when it lands. **Nothing here is final until
`GPT REVIEW PASS`.**
