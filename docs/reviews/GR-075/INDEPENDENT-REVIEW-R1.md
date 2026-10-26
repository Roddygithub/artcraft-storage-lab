# GR-075 independent review R1 — total body deadline

**Verdict:** bounded PROVISIONAL PASS with one MINOR test determinism finding.
No blocker or major finding. This is not project GPT approval.

## Finding

The slow-drip test began sending without synchronizing with entry into
`Handler._read_body`. If handler startup were delayed by about 70 ms, all body
bytes could arrive inside the 250 ms test budget and the correct implementation
could accept the request, making the test flaky. The test also needed guaranteed
restoration of the class override and socket cleanup.

## Remediation

The test temporarily wraps `_read_body` with a gate for the target `/dirty`
request. It signals when the handler enters the reader, waits while the client
sends the first byte, then releases the handler so its deadline begins before
the remaining bytes are dripped. The remaining four bytes arrive at 90 ms
intervals: each gap is shorter than the 250 ms timeout, while total delivery
exceeds it. A `finally` block releases the gate, restores `_read_body` and the
timeout override, closes the socket, and joins the sender thread.

R1 independently confirmed the 120-second implementation behavior, the
`BufferedReader.read1` deadline reasoning, and the existing gateway suite. The
test synchronization remediation is pending independent R2 review.
