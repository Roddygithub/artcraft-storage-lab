# GR-050 — HTTP response loss after committed save

**State: IMPLEMENTED; bounded independent R1 review PROVISIONAL PASS.** Base main
`fd6ae99e31e9f895fe35bbf324a85c6a7d43ba91`. This is a local lab change;
upstream publication remains locked. Independent R1 review: **PROVISIONAL PASS**, no
blocker/major. No project GPT verdict claimed.

| Proof | Evidence |
|---|---|
| Actual loopback TCP HTTP POST reaches the real `Handler.do_POST` and `Gateway.save` | `tests/test_gr050_http_save_retry.py:HttpSaveRetryTests.test_response_lost_after_commit_retry_writes_once`; inherited production route, synthetic session, matching Origin and filename |
| First save commits before response loss | Test-only `DropFirstSaveResponse._json` captures the successful route result after save returns, then shuts down/closes the socket without sending status, headers or body; client must raise `http.client.RemoteDisconnected` |
| Identical bytes retried over a new HTTP connection succeed | HTTP 200 with JSON equal to the first committed result |
| Only one synthetic upstream write/version | Before and after retry: `save_calls == 1`, `len(written) == 1`, file/head `bbbb`/`head-b`, stored content equals submitted bytes |
| Authorization/freshness remain unchanged | No production code edits; GR-049 authorization, identity, permission, freshness and failed-save regressions rerun |
| Isolation and cleanup | OS-assigned port on `127.0.0.1`, in-memory FakeSeafile and session, socket timeout, server shutdown and bounded serve-thread join in `finally`; no sleeps or timing race required |

Run `python3 tests/test_gr050_http_save_retry.py`. Results, existing-suite
output and syntax/diff checks are retained in `docs/reviews/GR-050/`.

This proves a deliberately injected gateway-to-client response loss after the
gateway receives a successful synthetic commit. It does not simulate an upstream
response lost before the gateway records its receipt. Real Seafile version
history, browsers, proxies/TLS, restarts, expired sessions and reopen/readback are
outside this regression. FakeSeafile records synthetic commits, not actual
Seafile versions. No Seafile, production, ONLYOFFICE or upstream repository was
accessed or changed. Independent review is left to the parent; no review PASS
or completed work-item status is inferred from these checks.
