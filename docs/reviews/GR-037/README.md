# GR-037 — PhotoCraft save-byte provenance

This bounded follow-up closes the GR-036 evidence gap at the editor-to-gateway
boundary. A real PhotoCraft Web/WASM save in the isolated synthetic Seahub
session produced one ticketed save request and one gateway POST. The SHA-256
and size matched at the browser message, gateway request body, and Seafile
readback: **8,555 bytes**, SHA-256
`ea0121c1e465c753947005e1ff4452cc031f734baed3345400bcd3a96218c4ca`.

Seafile history increased from two to three versions. A fresh Seahub route
created a new editor session, fetched the file with HTTP 200, and PhotoCraft
reported `photocraft-gr035.pcraft (no changes)`. The reopened screenshot and
redacted API results are retained in [`runtime/`](runtime/).

| Artifact | SHA-256 |
|---|---|
| `runtime/seafile-readback.json` | `b9b223702de1517b3a0237248b98af85b5e00e43464d8822006fc4462401005b` |
| `runtime/photocraft-seafile-reopen.png` | `b0ce53b8c71a481d33e5061f64277be235ced2991f9972314a8d412b5f09442f` |
| `runtime/sanitized-runtime-transcript.txt` | `1765e824a7d94e1413e9860239f8470f5904879ab2a4d1afa799a49e1fb811b0` |

The temporary observer logged only the transferred byte count and SHA-256;
temporary gateway instrumentation logged only the request-body byte count and
SHA-256. Both source files were restored to their repository HEAD after the
run. The temporary dispatch was removed and the synthetic Seahub settings were
restored to their recorded pre-test SHA-256. No credentials, document bytes,
or session capabilities are in this bundle.

The reusable browser test harness now asserts one save message and one outgoing
browser request, and compares their sizes and hashes with Seafile readback.
Python syntax and `git diff --check` pass; the manual T3 Chromium run is the
runtime evidence for this update. The independent review record is
[`INDEPENDENT-REVIEW.md`](INDEPENDENT-REVIEW.md).

## Limits

- This is synthetic loopback evidence, not production deployment evidence.
- PhotoCraft remains excluded from the committed dispatcher.
- `wasm-opt=0`, cross-origin deployment, TLS/proxy/CSP/CSRF controls,
  ONLYOFFICE regression, and optimized production performance remain
  **NOT VERIFIED**.
- Independent bounded review returned PROVISIONAL ACCEPT without blocker or
  major; one wording MINOR was corrected but not separately re-reviewed.
  Project-level GPT review remains pending. This is not upstream authorization.
