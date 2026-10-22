# Review 04 — the GR-012 bundle, the VectorCraft transport and its test

* Reviewer: `artcraft-reviewer` (Nemotron 3 Ultra 550B A55B, Nvidia) — **independent**;
  it took no part in reviews 01-03.
* Review date: 2026-10-22
* Reviewed: `docs/reviews/GR-012/README.md`, the VectorCraft transport adapter in
  `integration/gateway/hostpage.py`, `tests/test_gr012_svg.py`,
  `integration/config/dispatch.json`, and the VectorCraft sources.
* Verdict: **FAIL**

```text
REVIEW RESULT: FAIL
```

The reviewer confirmed the core result is real (*"the core claim … is likely true
based on the browser console log showing the dirty asterisk appearing and
disappearing, and the screenshot showing the pencil stroke"*) and called the page
API *"a solid deterministic surface for automation — much better than click
coordinates"*. The findings are about the **strength of the proof**, and every one
of them was right.

## 1. Findings and remediation

| # | Severity | Finding | Remediation | Status |
| --- | --- | --- | --- | --- |
| G1 | BLOCKER | The "document really changed" assertion compared the **length of the `document.inspect` JSON** — UI state, not content. An unrelated selection change would satisfy it. | The test now reads the **bytes the editor produced** (`vectorcraft.readFile`) and asserts (a) they differ from the original and (b) they are a valid SVG document containing a path element. The inspect comparison is kept as a secondary signal and labelled as such. | **fixed** |
| G2 | BLOCKER | The save poll compared **sizes**, so a second save producing the same size was silently ignored — and a refused save followed by a good one could be missed. | The poll now reads the bytes and compares a **content fingerprint**, and only a **stored** save becomes the new baseline: a refused one is retried on the next poll instead of being lost. | **fixed** |
| G3 | BLOCKER | No `beforeunload` for VectorCraft, and `/session/<sid>/dirty` is never called, so the gateway's unsaved state is never updated. | The host page now warns on unload **while a save is in flight** — the window in which closing the tab would lose bytes the editor already handed over. The **edit** warning is still impossible: VectorCraft's page API has **no dirty signal**. That is stated in the bundle, with the note that the editor itself keeps unsaved work in **recovery copies** in the browser ("Your unsaved changes are kept in this browser: reload the page to get them back"). | **fixed as far as the API allows; the rest is an upstream gap** |
| G4 | BLOCKER | `dispatch.json` gave VectorCraft a `?host=parent` URL while the host page ignores that parameter — the URL claims one contract, the code implements another. | The URL no longer claims it. The dispatch entry is `/artcraft/vectorcraft/`. | **fixed** |
| G5 | MAJOR | Check "a NEW Seafile version exists" compared two ids **both read after the save**, so it could not fail. | The content id and the version count are captured **before** the edit and compared after. | **fixed** |
| G6 | MAJOR | `MAX_SAVED = 16` in VectorCraft's `saved_files.rs`: a seventeenth save evicts the first. | Documented in the bundle as an upstream limit, with the mitigation that the host page polls every 700 ms. | **documented** |
| G7 | MAJOR | The history check expected `>= 1`, which a fresh file satisfies with no new version. | It now asserts `after_count > before_count` against the real before-count. | **fixed** |
| G8 | MAJOR | `svg: {}` was not explained: it means *"the document's own SVG options"*, which makes the save run directly instead of opening the SVG Options dialog. | Stated in the test and in the bundle, with the note that the lossiness is **SVG as an interchange format**, not an integration bug. | **fixed** |
| G9 | MAJOR | The adapter called `frame.contentWindow.vectorcraft` with **no** origin check, unlike the postMessage path. | `frameIsOurs()` verifies the frame's origin before the API is touched, and the check is repeated on every poll. | **fixed** |
| G10 | MINOR | `len(json.dumps(...))` is a weak change detector. | Kept as a secondary signal; the primary one is the byte comparison (G1). | **fixed** |
| G11 | MINOR | A 700 ms poll is also a correctness concern: a save just before the tab closes could be missed. | The `beforeunload` guard now covers the in-flight window (G3). The remaining window is the poll interval, which is a latency concern. | **fixed** |
| G12 | MINOR | The bundle quoted the editor's warning but the test did not assert it. | The warning comes back in the **save result's `warnings`**, and the test now asserts it: *"SVG keeps the artwork but not everything a VectorCraft document holds (editable effects, symbols, swatches, styles): save as VectorCraft to keep it all editable"*. | **fixed** |
| G13 | MINOR | The dispatch URL again (same as G4). | Same fix. | **fixed** |

## 2. Two bugs the remediation found

1. **`api.readFile` is synchronous.** The test called `.then()` on it and failed
   with *"readFile(...).then is not a function"*. VectorCraft's page API returns
   the bytes and **throws** on a miss; it does not return a promise.
2. **VectorCraft's SVG export writes a rectangle as a `<path>`.** The first
   assertion looked for a `<rect>` and failed on a file that was correct. The
   assertion is now about the document being a valid SVG with a path element.

Both are the kind of thing only running the test finds.

## 3. The final run

```text
  (fixture restored: synthetic.svg, 270 bytes)
[PASS] 1. the host page opened the document through the page API  -- synthetic.svg opened
[PASS] 2. the editor lists a drawing tool  -- tool ~ 'pencil'
[PASS] 3. the drawing tool is selected  -- {"tool": "pencil"}
[PASS] 4. the tool drew in document space  -- {"key": null, "selection": [4], "tool": "pencil"}
[PASS] 5. the document state moved  -- 1579 -> 2121 bytes of inspect state
[PASS] 6. the editor's own save command ran  -- {"bytes": 609, "format": "svg", …}
[PASS] 7. the editor produced NEW bytes  -- 270 -> 609 bytes
[PASS] 7a. the new bytes are an SVG document that holds the drawn stroke
[PASS] 8. the host page took the bytes and stored them  -- Saved - new version 2026-10-22T17:15:01+00:00
[PASS] 8a. the editor said what SVG does not keep  -- SVG keeps the artwork but not everything …
[PASS] 9. a NEW Seafile version exists  -- b8f7677f8fd1... -> fd8fd133431c...
[PASS] 10. the history grew  -- 7 -> 8 version(s)
[PASS] 11. the document reopened from Seafile is the edited one  -- the stored bytes are the editor's bytes

ALL CHECKS PASSED
```

Check **11** is the strongest one: the bytes Seafile holds are **byte-identical**
to the bytes the editor produced.

## 4. The test gaps the review listed

| Gap | State |
| --- | --- |
| a double save with identical bytes | **closed by design** — the fingerprint makes an identical re-save visible |
| a save during a network partition | **partly** — a refused save is retried on the next poll |
| 17+ rapid saves (eviction) | **documented**, upstream limit |
| the browser closed before the poll runs | **partly** — the `beforeunload` guard covers the in-flight window |
| a concurrent Seafile edit on this path | covered by the gateway's conflict check (`docs/CONFLICTS.md`); not re-driven here |
| read-only enforced on the VectorCraft path | covered by the unit test and the gateway; not driven in this browser test |
| SVG options other than the document's own | open |
| the leave-page warning | **fixed** for the in-flight window; the *edit* warning needs an upstream dirty signal |
| the other applications | open |

## 5. Status

```text
PROVISIONAL — FREE REVIEW PASS (remediated)
GPT REVIEW PENDING
```

Four independent free reviews: 01 FAIL → remediated, 02 FAIL → remediated,
03 PASS, 04 FAIL → remediated. **Nothing is final until `GPT REVIEW PASS`.**
