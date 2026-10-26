# GR-073 independent review R1

**Result:** PROVISIONAL changes requested. This bounded review is not a project
GPT verdict. The reviewer inspected the patch and ran the gateway unit suite,
Python compilation, and whitespace checks. No live services were accessed.

## Findings and remediation

| Finding | Remediation in the current patch | Check |
|---|---|---|
| **P2 — Rejected POST left its unread body on a persistent HTTP/1.1 connection.** A client could reuse the connection and have body bytes parsed as a subsequent request. | Rate-limit rejection marks the connection for closure and returns `Connection: close`. | HTTP regression asserts `429`, `Retry-After`, `Connection: close`, and no Seafile call. |
| **P2 — Clock sample was taken before acquiring the limiter lock.** A delayed thread could apply a stale timestamp after another thread advanced the window. | The monotonic clock is now sampled inside the same lock that prunes and mutates windows. | Deterministic injected-clock test verifies the clock is called while the lock is held. |
| **P3 — Threshold evidence did not match the documented default.** The route test used a one-request test limit while the matrix claimed the configured 60-request threshold was tested. | Added a direct boundary check using the production defaults. | Test admits 60 requests and rejects request 61; fractional retry delay is also checked for rounding up. |

The R1 reviewer did not independently reproduce the two source-derived P2
failures. R2 subsequently verified the code remediations, and R3 verified the
security documentation correction.

## Remaining limits

The implementation is process-local, resets on restart, and keys on the TCP
peer address. Clients behind a reverse proxy may share one bucket. Proxy
identity, multi-process coordination, public deployment suitability, live
Seafile behavior, and broader security remain **NOT VERIFIED**.
