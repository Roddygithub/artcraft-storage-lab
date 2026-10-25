# GR-043 — expired editing session during browser save

## Scope

A loopback-only Chromium test opens the real gateway `/open/` host page with a
synthetic Seafile adapter and synthetic WordCraft-like iframe. After the
gateway opens the document, the test ages its in-memory session past the
configured `SessionStore` TTL and asks the iframe to save.

## Result

The actual `POST /session/<sid>/save` returns HTTP 404 with guidance to return
to Seafile and reopen the file. The host stays dirty, the iframe receives
`saveResult {ok:false}` with the actionable reason, and the synthetic Seafile
write method is never called. The gateway therefore does not report success
for an expired editor session.

Run:

```sh
uv run --with playwright --python 3.14 -- python tests/test_gr043_expired_session_browser.py
python3 tests/test_gateway_unit.py
python3 -m py_compile tests/test_gr043_expired_session_browser.py integration/gateway/server.py integration/gateway/hostpage.py
git diff --check
```

The browser run and gateway unit suite passed. Evidence output is in
`docs/reviews/GR-043/README.md`.

## Limits

The test uses a synthetic editor, token, document and adapter; it does not
contact Seafile. It validates the gateway's in-memory TTL and error/ack path,
not real token expiry, permission revocation, browser reload recovery, or
Seafile version creation. Production behavior and deployment remain
**NOT VERIFIED**. Work-item state: **GPT REVIEW PENDING**; project-level GPT
verdict remains **INCOMPLETE**.
