# GR-015 route-token remediation — independent narrow review

Date: 2026-10-23
Model: Nemotron 3 Ultra 550B A55B (`nvidia/nvidia/nemotron-3-ultra-550b-a55b`)
Effort/mode: medium / plan
Task: `artcraft-gr015-route-check-20261023-r1`
Remediation commit: `0da898f58d7f706acd321bd1bec34526deeb62cf`

## Verdict

**PASS for the route-prefix finding only.** The route rename matches the
existing `op=update` prefix check and does not remove or bypass that check.

## Evidence checked

* Seahub mints a token with operation `update` and calls
  `update-conditional-api` in `seahub-12.0.14.patch`.
* The C patch registers the same path to `conditional_update_api_cb` and uses
  the existing `upload_headers_cb`.
* The hook extracts the first path component and passes it to
  `check_access_token`, which checks the requested operation prefix.
* The route is distinct from ordinary `update-api`; the Go router does not
  implement it. A stock or Go fileserver therefore does not gain this
  conditional route.
* `tests/test_gr015_authorization.py` checks these exact source relationships.
  It is a useful static regression guard, not a C runtime test.

## Limits

After this narrow review, the exact patched C source was configured and the
modified object plus complete `server` subproject compiled and linked in an
isolated `/tmp` build using locally staged dependencies. No C runtime request,
Django route import, or Seafile save was executed. Authorization revocation,
concurrent writes, commit acknowledgement, and the DOCX editor workflow remain
unverified. This source-level PASS and compile/link evidence do not change the
overall GPT-6.1 Sol **FAIL** on candidate
`0edbe524b4fa321b0f73f8601afef390e7f785e6`.
