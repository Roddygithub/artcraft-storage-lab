# GR-077 — independent review R1 and response

**R1 verdict:** PROVISIONAL PASS; no BLOCKER or MAJOR. Ten MINOR wording and
reference findings. R1 reviewed the GR-077 docs read-only and did not access
services or run application tests.

| Finding | Response |
|---|---|
| M1 — `Tracked route` column showed app names | Renamed the column to `Tracked app`; extension keys remain explicit in the first column. |
| M2 — WordCraft primary run vs later re-check unclear | Clarified GR-059 is the primary synthetic roundtrip and GR-076 re-verified it after the allow-list change. |
| M3 — byte-identity scope omitted GR-037 | Added the GR-037 8,555-byte editor/gateway/readback hash match; stated GR-076 compares readback with history, not the editor payload. |
| M4 — optimized PhotoCraft smoke vs GR-076 low-opt bundle unclear | Added the GR-035 optimized browser-smoke reference and clarified GR-076 Seafile used the low-optimization bundle. |
| M5 — separate GR-071 test root omitted | Clarified GR-071 used a separate test static root, which does not establish active assets in this checkout. |
| M6 — active-static-assets expected result ambiguous | Reworded the matrix expectation as the condition required to pass the combined replay. |
| M7 — production-gate expected result ambiguous | Reworded it as a production-readiness gate, not a statement of current status. |
| M8 — incorrect `seafile-readback.json` path | Changed it to `docs/reviews/GR-076/runtime/seafile-readback.json`. |
| M9 — ONLYOFFICE script 404 could be confused with GR-072 editor result | Clarified that the configured client `api.js` request returned 404, the post-change attempt did not instantiate the editor, and GR-072's earlier synthetic regression is separate. |
| M10 — ONLYOFFICE diagnostic detail absent from STATUS | Added the configured client 404 and direct Document Server API/healthcheck 200 observations, with the post-change attempt still marked inconclusive. |

No finding changed the bounded evidence or acceptance claims. All free-review
results remain PROVISIONAL; R2 must verify these responses against the final
tree.
