# GR-073 independent review R2

**Result:** PROVISIONAL PASS for the bounded implementation, with one P3
documentation finding. This is not project GPT approval.

## R1 remediation verified

| R1 finding | R2 result |
|---|---|
| Denied POST body could remain on a reusable connection | Fixed: rate-limited response sets `Connection: close`; raw TCP probes confirmed 429 followed by EOF, no body-parser call, and no pipelined request execution. |
| Clock sampled before lock | Fixed: clock sampling, pruning and mutation run under the same limiter lock. |
| Configured 60-request threshold lacked a matching test | Fixed: test admits 60 calls with production defaults and rejects call 61. |

## R2 finding and remediation

**P3 — stale security documentation.** The threat table still said there was “no
per-IP rate limit.” The row now describes the 60/60 per-peer `/open/` limit and
its process-local and reverse-proxy limitations. R3 later verified this correction
with no remaining findings.

## Independent checks

The reviewer reports passing the full gateway unit script, Python compilation,
and `git diff --check`. Raw HTTP denial checks covered incomplete and malformed
body lengths; concurrency produced 60 admissions and 940 rejections; peer-map
capacity rejected overflow at 1,024 entries without evicting active peers.

No live services were accessed. Proxy deployment, live Seafile/ONLYOFFICE
behavior, and public readiness remain **NOT VERIFIED**.
