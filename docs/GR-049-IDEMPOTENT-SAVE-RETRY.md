# GR-049 — Acknowledge the last committed save retry

**State: IMPLEMENTED; bounded independent review PROVISIONAL PASS.** Based on
local main `7238bc85b3816a6acfc1230c3cb1fb3172e1b696`. No project GPT PASS.

| Finding / behavior | Evidence |
|---|---|
| Previously, every valid save called upstream CAS, even after the same bytes had committed and advanced session IDs | Base `7238bc85:integration/gateway/server.py:181-230`; current `integration/gateway/server.py:197-259` |
| Validate local authorization, original filename, size and format before receipt lookup | `integration/gateway/server.py:197-208`; `tests/test_gr049_save_retry.py:test_replay_revalidates_payload_and_local_authorization` |
| Retain only the last successful SHA-256 digest (32 bytes), length and result, never document bytes | `integration/gateway/sessions.py:25-26`; `integration/gateway/server.py:248-259` |
| Identical retry rechecks token-bound user/document identity, edit permission and current file/head IDs; returns a copy of the original result without a save call | `integration/gateway/server.py:213-226`; `integration/gateway/seafile.py:127-140`; retry tests |
| Changed payload uses the existing atomic upstream CAS with updated session IDs; errors never create a successful receipt | `integration/gateway/server.py:227-259`; changed-payload and failed-save tests |
| Response is sent after `Gateway.save` returns, so a failed gateway-to-browser response can leave a successful receipt | `integration/gateway/server.py:335-349`; direct-call discarded-response test; GR-050 adds a real loopback HTTP route/socket regression |

## Concurrency and boundaries

`ThreadingHTTPServer` can execute routes concurrently. `SessionStore` locks its
map and lifetime bookkeeping, not the fields of a returned session
(`integration/gateway/sessions.py:71-116`). A per-session lock now covers save
validation, lookup, upstream operation and the file/head/receipt update. Document
fetch, session serialization and dirty-route mutation use that same lock
(`integration/gateway/server.py:171-184,354-361`;
`integration/gateway/sessions.py:51-69`). The store lock is released before taking
the session lock; save does not take the store lock. Separate sessions still
rely on upstream atomic CAS; existing two-session race checks remain passing.
Dirty notifications remain ordered by handler lock acquisition, not editor edit
generation; this change adds no document-generation protocol. A replay does not
clear a newer dirty notification.

The same-origin POST check and live session lookup still precede route save
handling (`integration/gateway/server.py:322-349`). No route, credential or
permission bypass was added. Reauthorization failure maps to the existing safe
403/404/502 responses. If the current file or library head differs, replay returns
409 and makes no write. The freshness read is a snapshot: external changes after
it are possible, but replay never writes. This lock does not replace server-side
atomic CAS for changed content.

Only the most recent successful payload is remembered in this process/session.
Restarts, session expiry, older out-of-order payloads, and commit outcomes whose
upstream response never reached the gateway are outside this guarantee. SHA-256
collision resistance is assumed. An identical intentional save is indistinguishable
from a retry and is acknowledged without creating another version. Existing
server-side atomic API is unchanged; unavailable upstream operations fail closed.

## Validation and claim limits

| Check | Result / evidence |
|---|---|
| `python3 tests/test_gr049_save_retry.py` | 6 tests pass; `docs/reviews/GR-049/retry-tests.txt` |
| `python3 tests/test_gateway_unit.py` | ALL CHECKS PASSED; `docs/reviews/GR-049/gateway-tests.txt` |
| `python3 -m py_compile integration/gateway/server.py integration/gateway/sessions.py tests/test_gr049_save_retry.py` | Exit 0; `docs/reviews/GR-049/checks.txt` |
| `git diff --check` | Exit 0; `docs/reviews/GR-049/checks.txt` |
| Independent review | PROVISIONAL PASS; no blocker/major/minor/actionable P3. Review did not run tests or services; see `docs/reviews/GR-049/INDEPENDENT-REVIEW-R1.md` |
| Actual socket response loss | Verified in synthetic loopback HTTP by GR-050: real save route commits through FakeSeafile, response socket closes before any status/headers/body, identical HTTP retry returns the original success with one fake write/version; see `docs/GR-050-HTTP-SAVE-RETRY.md` |
| Browser retry, real Seafile versions/readback/reopen | **NOT VERIFIED**; GR-050 uses a stdlib HTTP client and synthetic upstream only |
| Production / ONLYOFFICE | Untouched; no deployment or regression-runtime claim |
| Independent review / GPT review | Pending; no independent or project GPT verdict claimed |

No Seafile service, upstream repository, production data, or Rust build was used.
