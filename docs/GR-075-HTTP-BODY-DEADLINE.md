# GR-075 — bound gateway request-body read time

**Status:** R1/R2 test findings and R3/R4 documentation findings are fixed. Independent R1–R5 bounded reviews returned PROVISIONAL PASS with no remaining findings in scope. Project GPT remains **INCOMPLETE** and upstream publication **LOCKED**.

## Change

GR-074 rejected malformed and oversized bodies but left a stalled upload able to
hold a `ThreadingHTTPServer` handler indefinitely. The gateway now gives each
nonempty body a 120-second total read deadline. It reads at most 64 KiB at a
time with `read1`, recalculates the remaining monotonic deadline before every
read, and returns HTTP 408 with `Connection: close` when the deadline expires.
The total deadline prevents a slow client from resetting an inactivity timeout
by sending occasional bytes. A timed-out `/dirty` request does not update the
session's unsaved state.

The timeout is a fixed handler default (`BODY_READ_TIMEOUT_SECONDS`), currently
120 seconds. This allows a 50 MiB body to complete at roughly 0.42 MiB/s or
faster. The route's existing size limit is checked before body allocation/read.

## Check

Run `python3 tests/test_gateway_unit.py`. Its loopback regression temporarily
reduces the deadline, synchronizes with the first `read1` call after deadline
creation, and drip-feeds an incomplete `/dirty` body more frequently than the timeout would
allow by inactivity alone; the server still closes at the total deadline with
one 408 and preserves the dirty state. The override and socket are restored or
closed in `finally`. The full gateway unit script passes. R2's probe found the
previous event happened before deadline creation and socket creation was
outside cleanup protection; both are corrected. See
[R1](reviews/GR-075/INDEPENDENT-REVIEW-R1.md) and
[R2](reviews/GR-075/INDEPENDENT-REVIEW-R2.md),
[R3](reviews/GR-075/INDEPENDENT-REVIEW-R3.md), and
[R4](reviews/GR-075/INDEPENDENT-REVIEW-R4.md), and
[R5](reviews/GR-075/INDEPENDENT-REVIEW-R5.md). R3/R4 documentation findings
are corrected; R5 found no new issue in those remediations.

## Limits

This deadline begins after Python has parsed the request headers. Header-read
deadlines and reverse-proxy behavior are not covered. The 120-second policy has
not been validated against large uploads over slow client links. Production
suitability and live Seafile/ONLYOFFICE behavior remain **NOT VERIFIED**.
