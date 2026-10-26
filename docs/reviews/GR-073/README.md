# GR-073 evidence

The implementation is in `integration/gateway/server.py`; deterministic
coverage is in `tests/test_gateway_unit.py`.

Run from the repository root:

```sh
python3 tests/test_gateway_unit.py
python3 -m py_compile integration/gateway/server.py tests/test_gateway_unit.py
git diff --check
```

The gateway unit run passed, including all GR-073 rate-limit checks. No browser,
Seafile, production, proxy, or ONLYOFFICE service was accessed. The results are
local code evidence only. Reverse-proxy client identity and multi-process
behavior remain unverified. Independent R1 requested two P2 and one P3 changes;
those remediations are recorded in [the review](INDEPENDENT-REVIEW-R1.md), and
R2 found one stale security-table entry, corrected and verified in R3. R1–R3
are bounded PROVISIONAL PASS reviews; they do not grant project GPT approval.
Project GPT remains **INCOMPLETE** and upstream publication **LOCKED**.
