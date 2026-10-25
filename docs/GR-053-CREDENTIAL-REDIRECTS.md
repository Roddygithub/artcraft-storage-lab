# GR-053 — Reject credential-bearing Seafile redirects

Implementation: bounded independent R1–R2 PROVISIONAL PASS, no blocker/major;
GPT REVIEW PENDING. Base: `0190518db7c7ec924f9da28a06f4c55da6f7cc26`.

## Evidence and policy

Parent incident evidence supplied in the task: two synthetic loopback servers,
real `Seafile._request`, 302 followed by urllib; target received Authorization
and synthetic access_token copied into Location. This historical reproduction
was not independently rerun before the fix. No real credentials/services.
Omarseafile/SECURITY.md precedent was supplied by parent, not independently
inspected here; no Qt code copied.

| Inspected callers | Credential/policy | Source |
|---|---|---|
| `_json` → file info, detail, history, download/update/upload link discovery | Account Authorization when present; file-info also access_token | `integration/gateway/seafile.py` `_json` and ordinary API methods |
| thirdparty_file_content/save | Authorization and/or access_token | Same file, third-party methods |
| download/update_file/upload_file | auth=False means no account header, NOT no bearer: file-server path/query can be capability | Same file, explicit allow_redirects=False at each signed-link request |
| Public `_request` | No Authorization, no recognized credential query, no explicit opt-out: retain urllib redirects | Same file, `_request`; `tests/test_gr053_redirects.py` |

The stdlib HTTPRedirectHandler refuses all supported redirects for Authorization
(case-insensitive through Request normalization), decoded Unicode-casefolded query
keys access_token/token/jwt/signature/password (including blank values), or
allow_redirects=False. Same-origin redirects are also refused. The response is
closed and a fixed SeafileError with redirect status is raised; no Location or
response body is placed in the error. No dependencies or global urllib changes.

Public requests retain stdlib behavior. Arbitrary capability path/query formats
are not inferred for general public calls; the three actual signed-link callers
explicitly prohibit redirects, covering unknown query names and path tokens.
Future signed-link callers must also opt out.

## Verification and operational limits

| Check | Evidence |
|---|---|
| Real urllib, two loopback HTTPServer instances; 301/302/303/307/308; account/header/query credentials; target receives zero requests | `docs/reviews/GR-053/focused.txt`, `tests/test_gr053_redirects.py` |
| Path-only signed download, update and upload redirects refused; public 302 query redirect succeeds without Authorization | Same test and log |
| Existing gateway suite | `docs/reviews/GR-053/gateway.txt` |
| py_compile and git diff --check | `docs/reviews/GR-053/checks.txt` |

Real Seafile redirect behavior **NOT VERIFIED**. No Seafile, production,
ONLYOFFICE, browser, or remote service was accessed. Operators must configure a
canonical base URL (correct scheme, host and endpoint paths) and canonical
file-server link generation: credential-bearing HTTP→HTTPS, slash, hostname or
storage redirects now fail closed. A refused save is not a confirmed save; do
not work around it by manually replaying credentials to Location. Existing
gateway status/error handling is retained. This slice does not prove the MVP.
Rollback: revert the GR-053 commit. Independent R1–R2 bounded reviews are
PROVISIONAL PASS; GPT review remains pending. This is not a project PASS.
