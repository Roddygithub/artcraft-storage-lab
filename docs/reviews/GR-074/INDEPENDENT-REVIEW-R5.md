# GR-074 independent review R5 — final body-framing re-review

**Verdict:** bounded PROVISIONAL PASS. No new P1–P3 findings. This is not project GPT approval.

## R4 remediation

The review confirmed that Python 3.14.8 can leave malformed request-header bytes in `headers.get_payload()` while `headers.defects` is empty and `Content-Length` is absent. The shared body reader now rejects missing payload access, parser defects, or any nonempty parser payload before interpreting framing. Both R4 CR/LF cases have retained raw loopback regressions asserting one 400 response, `Connection: close`, and unchanged dirty state.

## Independent checks reported

- `PYTHONDONTWRITEBYTECODE=1 python3 tests/test_gateway_unit.py` — passed.
- Python compilation of both changed Python files — passed, with temporary output outside the repository.
- `git diff --check` — passed.
- 36 additional raw loopback probes across `/open/`, `/save`, `/dirty`, and GET returned one 400, connection closure, then EOF. Dirty state stayed true; the bound fake recorded no calls, writes, or session creation.
- Valid ordinary/SP/HTAB lengths, a synthetic save with exact-byte persistence, dirty clearing after successful save, and ordinary connection reuse passed.

The review found the earlier Unicode-whitespace, malformed/duplicate length, transfer-encoding, truncation, oversized-body, early-rejection, and HTTP/0.9 fixes intact. It also confirmed the matrix limits the no-Seafile-lookup claim to the oversized `/open/` case.

## Remaining limits

No body-read deadline is configured (`Handler.timeout` and the default socket timeout are `None`); a client can retain a handler thread indefinitely by keeping an incomplete body connection open. Reverse-proxy behavior, other Python versions, production suitability, and live Seafile/ONLYOFFICE behavior remain **NOT VERIFIED**. The independent reviewer made no edits and accessed no external services.
