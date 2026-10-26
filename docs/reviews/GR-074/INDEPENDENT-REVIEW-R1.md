# GR-074 independent review R1

**Result:** PROVISIONAL changes requested. This bounded review is not project GPT
approval. The reviewer ran the gateway suite, Python compilation, and
`git diff --check`, and performed additional loopback probes. No external
services were accessed.

## Findings and remediation

| Finding | Remediation | Regression evidence |
|---|---|---|
| **P2 — Unicode whitespace bypassed `Content-Length` validation.** Unrestricted `.strip()` normalized NBSP/NEL bytes into valid lengths; raw requests could clear `/dirty` state and execute a pipelined request. | Trim only HTTP SP/HTAB optional whitespace; reject all remaining non-ASCII/non-decimal values. | Leading NBSP and trailing NEL raw requests each return 400, close the socket, execute no pipelined GET, and preserve `unsaved=true`. |
| **P3 — “No Seafile lookup” assertion inspected the wrong fake.** The assertion could pass without observing the fake attached to the active gateway. | Keep a reference to the exact `FakeSeafile` passed to the HTTP test gateway. | Over-limit `/open/` assertion compares its `open_info_calls` before/after the request. |
| **Coverage gap — early route rejections left bodies unread.** This included Origin denial, missing session and GET/unknown paths. | Close the connection for early rejections that do not consume a body; reject GET bodies through the same bounded reader. | Pipelined raw requests for cross-origin POST, expired session, and GET body yield one rejection response then EOF. |
| **Coverage gap — malformed framing cases were not retained.** | Added regressions for duplicate and comma-separated Content-Length, Transfer-Encoding (including empty and TE+CL), huge decimal length, truncated dirty/save bodies, exact 64-byte dirty body, and oversized save connection closure. | All cases run in `tests/test_gateway_unit.py`; save rejection is checked against the active synthetic Seafile fake. |

The R1 reviewer independently reproduced the Unicode whitespace issue and
identified the false-positive-prone fake assertion. It also recommended
preserving additional framing probes in the test suite; those cases are now
retained. Independent R2 review of the remediation is pending.

## Limits

The tests are loopback-only. Proxy normalization/framing, read deadlines for
slow incomplete bodies, production deployment, and live Seafile/ONLYOFFICE
behavior remain **NOT VERIFIED**.
