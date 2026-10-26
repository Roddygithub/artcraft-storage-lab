# GR-074 independent review R3

**Result:** PROVISIONAL PASS for the HTTP/1.1 framing fix, with two non-blocking
P3 findings. This is not project GPT approval.

## R1/R2 findings

The R1 Unicode-whitespace and false-positive test findings are resolved. R2's
malformed-header parser bypass is resolved by checking `self.headers.defects`
before accepting body framing. R3 found no residual HTTP/1.1 unread-body or
dirty-state bypass. Raw probes confirmed SP/HTAB compatibility, valid dirty and
save requests, and rejected malformed-header/pipelined cases.

## P3 findings and remediation

| Finding | Remediation | Check |
|---|---|---|
| HTTP/0.9 GET leaves `self.headers` as a plain dict, so checking `.defects` raised an exception. | `do_GET` now closes HTTP/0.9 before accessing the header map or dispatching a route. | Raw HTTP/0.9 GET closes cleanly; regression added. |
| Matrix wording implied every malformed-frame test asserted no Seafile lookup. | Matrix now scopes the no-lookup claim to the oversized `/open/` test, which checks the active fake; other framing rows describe their actual assertions. | Updated matrix wording and reran gateway checks. |

The reviewer also confirmed that no finite body-read deadline is configured; this
is retained as an explicit limit rather than presented as solved. Independent
R4 verification is pending.

## Validation and limits

R3 reports the gateway unit script, `py_compile`, and `git diff --check` passing.
Review and regression checks use loopback. A slow incomplete body can retain a
handler thread because the default socket timeout is `None`. Reverse-proxy
behavior, deployment suitability and live Seafile/ONLYOFFICE remain **NOT
VERIFIED**.
