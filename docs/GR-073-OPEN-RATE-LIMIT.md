# GR-073 — bound gateway open requests

**Status:** R1 findings resolved; R2 identified a stale security-table entry; it was corrected and independently verified in R3. R1–R3 bounded reviews are PROVISIONAL PASS. Project GPT remains **INCOMPLETE** and upstream publication **LOCKED**.

## Change

The gateway now applies a process-local fixed-window rate limit to capability-
bearing `POST /open/` requests. It allows 60 requests per 60 seconds per TCP
peer address, returns HTTP 429 with `Retry-After` when the peer exceeds the
limit, and rejects unknown peers while its 1,024-entry table is full. Expired
entries are pruned on request. The table is lock-protected and uses a monotonic
clock. The limiter runs before body parsing and before any Seafile request.

The gateway intentionally uses the socket peer address and ignores
`X-Forwarded-For`. When directly exposed, that address identifies the connecting
peer. Behind a reverse proxy, all clients may share the proxy address and its
rate bucket; the limit can therefore be shared across users. State is local to
one process and resets on restart. This reduces repeated opens but does not
replace proxy-level controls or establish public deployment readiness.

## Verification

`python3 tests/test_gateway_unit.py` passed. The focused checks cover permitted
requests, HTTP 429 and `Retry-After`, window expiry using an injected clock,
bounded peer state, refusal while the table is full, admission after expiry,
spoofed forwarding headers, and no Seafile call for a rejected request.

`python3 -m py_compile integration/gateway/server.py tests/test_gateway_unit.py`
and `git diff --check` passed. No Seafile, browser, deployment, or ONLYOFFICE
service was accessed or changed.

Independent R1 requested changes for unread request-body handling, clock sampling
under contention, and testing the configured threshold. The current patch closes
429 connections, samples time under the limiter lock, and tests admission of 60
requests followed by rejection of request 61. See the [retained R1
review](reviews/GR-073/INDEPENDENT-REVIEW-R1.md). R3 verified the
security documentation correction; see [R2](reviews/GR-073/INDEPENDENT-REVIEW-R2.md)
and [R3](reviews/GR-073/INDEPENDENT-REVIEW-R3.md).

## Limits

This is a single-process in-memory limit. It does not provide a distributed
quota, identify end users behind a proxy, or prevent a distributed source flood.
Reverse-proxy behavior, public deployment, production security, and upstream
publication remain **NOT VERIFIED** / **LOCKED**. See [the evidence record](reviews/GR-073/README.md).
