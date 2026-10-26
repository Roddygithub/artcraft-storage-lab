# GR-074 evidence

Implementation: `integration/gateway/server.py` (`Handler._read_body` and its
GET/POST callers). Regression checks are in `tests/test_gateway_unit.py`.

Run from the repository root:

```sh
python3 tests/test_gateway_unit.py
python3 -m py_compile integration/gateway/server.py tests/test_gateway_unit.py
git diff --check
```

The HTTP checks use loopback and a synthetic `FakeSeafile`; they do not contact
Seafile. They cover over-limit `/open/`, `/save`, and `/dirty`; malformed lengths,
transfer encodings and truncated bodies; early rejection paths; and pipelined
requests. The `/dirty` state is preserved on rejection. R1 reproduced a Unicode
whitespace bypass, R2 a malformed-header parser bypass, R3 HTTP/0.9 handling and
matrix wording issues, and R4 parser-leftover header bytes that bypassed the
parser-defect check. All are fixed with retained regressions and accurate
claims. Independent R5 returned bounded PROVISIONAL PASS with no new P1–P3
findings after 36 raw route probes; see
[`INDEPENDENT-REVIEW-R5.md`](INDEPENDENT-REVIEW-R5.md). Proxy behavior,
production and ONLYOFFICE remain **NOT VERIFIED**.
Project GPT remains
**INCOMPLETE**, upstream publication **LOCKED**.
