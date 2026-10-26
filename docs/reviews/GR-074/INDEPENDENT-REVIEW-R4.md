# GR-074 independent review R4 — parser-leftover header bytes

**Verdict:** bounded PROVISIONAL FAIL; one P2 finding. No blocker identified.

## Finding

Python's `http.client` header parser can leave malformed bytes in
`headers.get_payload()` while `headers.defects` is empty. In the affected raw
requests, a stray CR or LF/CR sequence before `Content-Length` caused the body
reader to treat the length as absent. The pipelined GET was then parsed as a
second request, and a `/dirty` request could clear the unsaved flag.

The reviewer reproduced these headers after the normal Host and Origin fields:

- `X-Review: x\r\rContent-Length: N\r\n\r\n`
- `X-Review: x\n\rContent-Length: N\r\n\r\n`

## Remediation in the current working tree

`Handler._read_body` now rejects a missing header payload accessor, any
`headers.defects`, or non-empty `headers.get_payload()` before reading framing.
Two raw loopback regressions use the reported malformed sequences with a
pipelined `/dirty` body. They assert one HTTP 400 response, `Connection: close`,
and that the session's prior dirty flag remains set.

`python3 tests/test_gateway_unit.py` passes with both cases. Python compilation
and `git diff --check` also pass before the independent R5 review.

## Remaining limit

The reviewer also confirmed that neither `Handler.timeout` nor the default
socket timeout sets a body-read deadline. A client that sends an incomplete
body and leaves the connection open can retain a handler thread indefinitely.
This remains explicitly documented and is not fixed by this patch.
