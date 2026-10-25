# GR-051 — Browser retry after lost gateway response

**State: IMPLEMENTED; bounded independent R1 review PROVISIONAL PASS; GPT REVIEW
PENDING.** Based on local main `5a1ceb66da4a6cdb6f77ee7fa9203b3a271e7efb`.
Production code is unchanged; no upstream publication.

| Claim | Evidence |
|---|---|
| Browser uses actual gateway and rendered host page | `tests/test_gr051_browser_save_retry.py:main`: loopback parent form POST to inherited `Handler._open`, real `Gateway`, `hostpage.render`, document GET; all HTTP 200 |
| First response is lost only after successful gateway save | `DropFirstSaveResponse._json`: inherited `Handler.do_POST` has completed `Gateway.save`; hook asserts successful 200 result and one synthetic save call, then closes the socket before sending any HTTP response. A later assertion checks exactly one recorded synthetic write. |
| Browser fetch fails and editor remains dirty | Exact Chromium `net::ERR_EMPTY_RESPONSE`; no browser save response; ticket-1 receives `ok:false` and sanitized error; synthetic editor dirty=true, no clean signal; host dirty/unconfirmed, not pending/in flight; gateway unsaved=false because bytes are committed |
| User retry uses same bytes and a fresh ticket | Second button click sends the same immutable synthetic edited DOCX bytes with ticket-2; real save route returns HTTP 200 equal to captured first result |
| GR-049 receipt avoids a second write | Two equal successful internal route results; `save_calls == len(written) == 1`, single original CAS expectation, stored bytes match, file/head `bbbb`/`head-b` |
| Editor confirms clean after positive result | Synthetic editor sends dirty=false only on `ok:true`; host clean/confirmed, pending/in-flight=false, visible `Saved — new version head-b`; dirty route acknowledges unsaved=false |
| Exact route observations and cleanup | Browser and server route multisets match open 200, editor 200, document 200, two dirty 200, and save DROP then 200; failed request and both ticket results exact. Browser closes in finally; servers shut down/close, request threads joined by server_close, serve threads joined/asserted stopped; origin environment restored |

The tiny same-origin editor is **synthetic, not actual WordCraft WASM**. The
in-memory `RetrySeafile` extends **FakeSeafile, not real Seafile**. “head-b” is a
synthetic commit acknowledgement, not evidence of a real Seafile version.
This extends GR-043's documented cached Playwright workflow and GR-050's
post-commit socket-loss injection; it does not replace real end-to-end MVP proof.

Only **gateway-to-browser response loss after gateway receipt** is covered.
Upstream response loss before gateway receipt, actual WordCraft, real Seafile
version history/readback/reopen, proxies/TLS, restart persistence and deployment
remain **NOT VERIFIED**. No production Seafile, ONLYOFFICE, SeaDrive or real
credentials/documents were accessed.

Independent R1 review reran the Playwright test and returned bounded
PROVISIONAL PASS; see `docs/reviews/GR-051/INDEPENDENT-REVIEW-R1.md`.

Run:

```sh
uv run --with playwright --python 3.14 -- python -u tests/test_gr051_browser_save_retry.py
python3 tests/test_gr049_save_retry.py
python3 tests/test_gr050_http_save_retry.py
python3 tests/test_gateway_unit.py
```

Commands, captured output and check results: `docs/reviews/GR-051/README.md`.
