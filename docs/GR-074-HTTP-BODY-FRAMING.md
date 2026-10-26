# GR-074 — reject malformed and oversized gateway request bodies

**Status:** R1–R4 findings are fixed. Independent R5 review returned a bounded PROVISIONAL PASS with no new findings. Project GPT remains **INCOMPLETE** and upstream publication **LOCKED**.

## Finding and change

The gateway uses HTTP/1.1 and reads request bodies itself. A too-large body was
previously left unread while the connection stayed reusable. More seriously,
`POST /session/{sid}/dirty` treated the `None` result from an oversized read as
an empty body, potentially clearing the host's unsaved warning. Negative or
malformed `Content-Length` could reach unbounded `rfile.read()` behavior, while
`Transfer-Encoding` was not decoded.

The shared body reader now rejects parser-reported malformed headers and any
unparsed header payload, trims only
HTTP SP/HTAB optional whitespace, accepts one ASCII decimal `Content-Length`,
rejects transfer encoding, rejects over-limit bodies, and treats truncated reads
as invalid. Error responses close the connection. Early Origin/session/route rejection paths also close when they
have not consumed the body; GET requests with bodies are rejected. `/dirty`
handles rejection before updating session state; `/open/` and `/save` use the
same rejection path.

## Verification

`python3 tests/test_gateway_unit.py` covers over-limit `/open/`, `/save`, and
`/dirty` requests; duplicate, comma-separated, negative, Unicode-whitespace,
and unrepresentably long Content-Length values; transfer encoding; truncated
bodies; rejected early routes; and pipelined requests. It confirms oversized or
malformed `/dirty` cannot clear an existing unsaved flag and rejected `/open/`
does not call the active Seafile fake. The suite also covers rate limits, origin
checks, sessions, save bounds, and static routing.

Independent R1 review reproduced a Unicode-whitespace bypass and a test checking
the wrong fake; both were fixed. R2 found that Python could omit malformed header
fields before the body reader inspected them; parser defects and unknown-route
bodies were covered. R3 found HTTP/0.9 header-object compatibility and
matrix-claim wording issues; both were fixed. R4 demonstrated that malformed
bytes can remain in `headers.get_payload()` with no parser defect, so the reader
now rejects either condition. New raw regressions cover both R4 inputs and
assert one 400 response, connection closure, and preservation of dirty state.
See [R1](reviews/GR-074/INDEPENDENT-REVIEW-R1.md),
[R2](reviews/GR-074/INDEPENDENT-REVIEW-R2.md), [R3](reviews/GR-074/INDEPENDENT-REVIEW-R3.md),
and [R4](reviews/GR-074/INDEPENDENT-REVIEW-R4.md). Independent R5 found no new
P1–P3 findings and exercised 36 additional raw loopback probes across the
affected routes. Its bounded result and limits are recorded in
[R5](reviews/GR-074/INDEPENDENT-REVIEW-R5.md). The current suite, Python
compilation, and `git diff --check` pass. No live service was accessed.

## Limits

This validates gateway HTTP request framing with loopback sockets. The gateway
configures no finite body-read deadline (`Handler.timeout` and the default
socket timeout are both `None`), so an incomplete body can retain a handler
thread indefinitely until EOF or external connection closure. Reverse-proxy framing, production suitability, and
Seafile/ONLYOFFICE runtime behavior remain **NOT VERIFIED**.
