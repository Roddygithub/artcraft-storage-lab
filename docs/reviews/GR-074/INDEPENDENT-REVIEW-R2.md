# GR-074 independent review R2

**Result:** PROVISIONAL changes requested. One P2 remains; this is not project
GPT approval.

## R1 results

The R1 whitespace fix and the corrected active-`FakeSeafile` assertion are
verified. R2 independently confirmed that valid SP/HTAB handling, ordinary dirty
reports, valid synthetic saves, connection reuse after a successful save, and
the added malformed-length/transfer/truncated-body cases behave as intended.

## P2 — parsed header defects bypassed the body reader

Python's HTTP header parser can silently omit a malformed field such as
`Content-Length : 67` and record `MissingHeaderBodySeparatorDefect`. The prior
reader treated the absent parsed header as zero length. R2 reproduced two 200
responses and `/dirty` state clearing when the apparent body contained a valid
pipelined GET. A tab before the colon or another malformed field before a valid
Content-Length had the same behavior.

The current patch rejects `self.headers.defects` before reading or accepting a
body. Raw regressions cover space/tab before the colon and a malformed field
before a valid Content-Length; each expects HTTP 400, connection closure, one
response, and unchanged dirty state. R3 verification is pending.

R2 also noted that the test suite did not retain the unknown-route early-reject
probe. A raw POST test now verifies that this rejection closes the connection
instead of processing pipelined bytes.

## Verification and limits

R2 reports the gateway suite, Python compilation, and `git diff --check` passing.
The review used loopback probes only. Incomplete bodies still have no explicit
read deadline; reverse-proxy behavior and live Seafile/ONLYOFFICE remain
**NOT VERIFIED**.
