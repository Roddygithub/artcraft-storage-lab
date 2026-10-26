# Project GPT review: candidate `70fa192`

**Verdict: FAIL.** This review applies to candidate
`70fa192ed5d414daf28087315f0f77f8312e98b5`. It is a review record, not a
project-level approval. Production readiness remains **NOT VERIFIED** and
upstream publication remains **LOCKED**.

The reviewer inspected source, patches, stored observations and screenshots
read-only. HEAD matched the requested SHA and the worktree was clean. No tests,
service access, browser use, edits or publication were performed.

## Findings

| Severity | Finding | Disposition |
| --- | --- | --- |
| MAJOR | WordCraft and GridCraft may overwrite the selected Seafile file when creating a new document or using same-format Save As. The host accepts same-extension names and submits the original storage filename; the adapters do not reliably distinguish Save As. | Requires a code fix that binds the editor document identity to the opened file and rejects replacement/Save As before save. Browser reproduction was **NOT VERIFIED**. |
| MAJOR | Current-route ONLYOFFICE preservation is unresolved. Earlier GR-040/GR-072 synthetic success does not establish behavior after later route changes; GR-076/GR-080 found the configured client API script returning 404, with no editor. | Remains **INCONCLUSIVE / NOT VERIFIED**. This does not establish ArtCraft caused the failure. A current-route synthetic edit/save/version/reopen is still required. |
| MAJOR | Some retained screenshots are attributed to later workflows they do not show. Two GR-015 concurrent screenshots are byte-identical and both display “Concurrent writer A”; GR-078 PhotoCraft screenshots are byte-identical to GR-076 captures and show the earlier Layer 1/2 state. | Correct attribution or explicitly disclose reuse; later observations without matching captures remain operator-recorded and **NOT VERIFIED** by those images. |
| MAJOR | `integration/README.md` says the gateway must share Seafile's HTTPS origin, conflicting with the required separate Seahub origin. The quickstart also omits `ARTCRAFT_SEAFILE_ORIGIN`. | Correct deployment topology and runnable environment instructions. |
| MINOR | `_serve_static` checks a requested directory before appending `index.html`, but does not resolve/recheck the final index path. | Resolve and confine the final target before opening it. Remote creation of a symlink was **NOT VERIFIED**. |
| MINOR | `scripts/verify-dispatched-candidates.sh` expects exactly four routes while the tracked dispatcher has five, including PhotoCraft. | Update the verifier to validate the current mapping without claiming absent assets are present. |
| MINOR | Documentation contains stale status and broken evidence links, including GR-030, GR-048 and GR-076 references. | Reconcile status with later evidence and link only retained artifacts. |

## Prior findings and remaining gates

The original real-Seafile WordCraft workflow blocker and conditional-route/token
mismatch were considered closed for the bounded synthetic workflow. This review
does not close remaining authorization/atomicity gaps: live revocation,
external-writer races, interrupted uploads and stock/Go runtime rejection remain
**NOT VERIFIED**. GridCraft evidence applies to the tested workbook. VectorCraft
still lacks the common dirty/save-result protocol. Production proxy/TLS/cookie
isolation, parser peak-memory bounds and broader packaging compatibility remain
**NOT VERIFIED**.

The historical GPT FAIL on `0edbe524b4fa321b0f73f8601afef390e7f785e6` remains
unchanged. This candidate also receives FAIL. Free-model reviews remain
PROVISIONAL and do not unlock upstream issues, pull requests or RFCs.
