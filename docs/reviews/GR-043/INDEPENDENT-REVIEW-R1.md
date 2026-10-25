# Independent Review — GR-043 expired-session save

Date: 2026-10-25

**Verdict: PROVISIONAL PASS (bounded).** No blocker, major or minor finding.

The reviewer inspected the latest working tree. The browser test exercises the
real gateway `/open/` and `/session/<sid>/save` handlers with a synthetic
editor and adapter, expires the in-memory session beyond its TTL, and verifies
an HTTP 404 with reopen guidance. The host remains dirty, the editor receives
`saveResult {ok:false}` with actionable guidance, and the synthetic Seafile
writer is never called.

The host-page `sessionUnavailable` flag is declared outside the `try`, assigned
while the parsed response is in scope, and used after the `catch`. Other
upstream failures continue to receive generic save-failure wording rather
than being mislabeled as an expired gateway session. Loopback-only setup and
cleanup are sound by inspection.

The reviewer reports all 69 gateway unit checks passing. The author also ran
the focused Chromium test, gateway unit suite, Python compilation, and
`git diff --check` successfully.

**Limits:** this verifies only the gateway's in-memory session TTL and its
negative acknowledgement path. Real Seafile access-token expiry, permission
revocation, production behavior, cross-origin proxy/CSP deployment, Seafile
version creation and close/reopen remain **NOT VERIFIED**. The project-level
GPT verdict remains **INCOMPLETE**; upstream publication remains locked.
