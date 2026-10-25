# GR-051 evidence — synthetic browser committed-save retry

Date: 2026-10-25. Base: `5a1ceb66da4a6cdb6f77ee7fa9203b3a271e7efb`.
**INDEPENDENT FREE REVIEW: PROVISIONAL PASS; GPT REVIEW PENDING.** R1 found no
blocker/major; two P3 wording points were corrected. No project GPT PASS.

| Command | Captured evidence | Result |
|---|---|---|
| `uv run --with playwright --python 3.14 -- python -u tests/test_gr051_browser_save_retry.py` | `browser-tests.txt` | PASS, cached Chromium; GR-043 workflow |
| `python3 tests/test_gr049_save_retry.py` | `receipt-tests.txt` | PASS, 6 tests |
| `python3 tests/test_gr050_http_save_retry.py` | `http-retry-tests.txt` | PASS, 1 test |
| `python3 tests/test_gateway_unit.py` | `gateway-tests.txt` | PASS, existing gateway checks |
| Python compile and whitespace checks | `checks.txt` | PASS, including new files |

`tests/test_gr051_browser_save_retry.py` asserts every route observation rather
than relying on printed claims. The first internal HTTP 200 is deliberately
never sent; Chromium observes `net::ERR_EMPTY_RESPONSE`. The second save receives
HTTP 200. Ticket-1 fails, ticket-2 succeeds, one fake upstream write occurs, then
the editor's dirty=false signal confirms the host clean. Route multisets and exact per-save/ticket sequences are checked without
depending on response-event ordering across separate browser connections.

Loopback ephemeral ports only; synthetic parent form, synthetic same-origin
editor **not actual WASM**, valid synthetic DOCX bytes and in-memory
`RetrySeafile`/`FakeSeafile` **not real Seafile**. Browser and server cleanup is
asserted; environment restored. No build output or test assets under `/tmp`.
No production code changed and no production/ONLYOFFICE service accessed.

Independent R1 review reran the Playwright test and returned bounded
PROVISIONAL PASS; see `INDEPENDENT-REVIEW-R1.md`.

Only gateway-to-browser response loss after gateway receipt is proved.
**NOT VERIFIED:** upstream response loss before gateway receipt, actual
WordCraft runtime, real Seafile versions/reopen, restart persistence, TLS/proxy
behavior or the complete Seafile Web MVP. See `docs/GR-051-BROWSER-SAVE-RETRY.md`.

An exploratory run (`initial-assertion.txt`) failed an added assertion expecting
`session.unsaved=true` after the dropped response. Gateway.save marks committed
bytes saved; browser dirty state is separate. To avoid relying on concurrent
`/dirty` and `/save` ordering, the final synthetic editor has a separate Edit
button. The test waits for its dirty-route ACK before clicking Save, and retry
sends no new edit. It asserts gateway unsaved=false after commit alongside
browser/editor dirty=true. All requested checks remain exact.
