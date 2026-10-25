# GR-043 browser evidence — expired session save

Date: 2026-10-25

Command:

```sh
uv run --with playwright --python 3.14 -- python -u tests/test_gr043_expired_session_browser.py
```

Environment: cached Playwright Chromium, loopback-only parent and gateway
servers, a synthetic editor iframe, synthetic DOCX bytes, and a fake
Seafile adapter. The test moves the opened session timestamps beyond the
gateway TTL; it does not contact a Seafile service.

Output:

```text
PASS: actual POST /open/ created the session; synthetic editor opened the document
PASS: expired actual /session/<sid>/save returned HTTP 404 with reopen guidance
PASS: host UI stayed dirty; editor received saveResult ok:false; synthetic Seafile save calls=0
```

The test also asserts that `SessionStore.get` expires and removes the aged
session, that the host's failure result names the expired/unavailable session,
and that no synthetic upstream save was attempted. The existing gateway unit
check script also passed in the same run.

No production Seafile or ONLYOFFICE service, document or credential was used.
Real Seafile token expiry, permission changes, production deployment and
version history are **NOT VERIFIED**.
