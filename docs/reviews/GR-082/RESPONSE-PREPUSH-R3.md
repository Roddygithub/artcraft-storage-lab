# Response to GR-082 pre-push review R3

**Disposition: both R3 findings addressed locally; independent R4 recheck
pending. No commit or push yet.**

1. **Served-asset provenance (MEDIUM):** reran the actual-WASM WordCraft browser
   smoke as R9 against `wordcraft-v0.11.0-static/wordcraft`. The retained log
   `checks/wordcraft-browser-smoke-r9.txt` records the exact test-source SHA-256
   and hashes for `index.html`, the icon, JS glue, and WASM in that served
   directory both before and after the run. All four asset hashes are unchanged
   and match the release bundle manifest; the smoke exited 0 and the fresh
   editor's copied text contains the edit marker.
2. **Stale review wording (LOW):** the evidence README now records R2 as
   completed, R3's finding and R9 response, and R4 as pending.

The smoke uses synthetic in-memory storage. Seafile version/history/readback/
reopen, replacement-refusal counts, promotion, merge, and upstream publication
remain unverified or locked as documented.
