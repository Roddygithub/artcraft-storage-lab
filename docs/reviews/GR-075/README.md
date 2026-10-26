# GR-075 evidence

Implementation: `integration/gateway/server.py`, with a loopback slow-drip
regression in `tests/test_gateway_unit.py`.

Run from the repository root:

```sh
python3 tests/test_gateway_unit.py
python3 -m py_compile integration/gateway/server.py tests/test_gateway_unit.py
git diff --check
```

The slow-drip test uses a synthetic session and a loopback socket. It shortens
the handler deadline for the test, synchronizes with the first `read1` call
after deadline creation, and drips an incomplete `/dirty` body at 90 ms
intervals. It asserts one 408 response,
connection closure, and unchanged dirty state. The handler override and socket
are restored or closed in `finally`. No Seafile, proxy, or production service
is contacted. R1 found a timing race; R2 showed synchronization still preceded
deadline creation and socket setup was outside cleanup protection. The test now
synchronizes at `read1` and wraps setup in `try/finally`. R3 returned a bounded
PROVISIONAL PASS with one stale-matrix-status minor, now fixed. R4 returned a
bounded PROVISIONAL PASS and found stale R3-pending wording in two summaries;
those statements are corrected. R5 returned bounded PROVISIONAL PASS with no
new findings in the status remediation. The
120-second production default, header-read timing,
reverse-proxy behavior, and large-file behavior on slow links remain
**NOT VERIFIED**. Project GPT remains **INCOMPLETE** and upstream publication
**LOCKED**.
