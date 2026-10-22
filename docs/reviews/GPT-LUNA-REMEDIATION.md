# GPT-6.1 Sol remediation — local evidence

Original candidate: `c76a7594cc43ba2a6cf56de2232836f008a97863`  
Original verdict: [`GPT-SOL-FINAL-REVIEW.md`](GPT-SOL-FINAL-REVIEW.md) — **FAIL**

## Implemented

| Finding | Local remediation | Evidence |
| --- | --- | --- |
| Unauthenticated direct `/open` | HTTP opening now requires Seafile `access_token`; `repo_id` + `path` is rejected. The internal method is disabled too. | `integration/gateway/server.py`; unit check “direct repo/path opening is disabled” |
| Service-account authorization | `can_edit` requires a user-bound `user_file_detail` result. Stock `Seafile` raises 501, so writes fail closed. Save re-authorizes the editing user. | `integration/gateway/server.py`, `integration/gateway/seafile.py` |
| Lost-update race | Gateway no longer calls unconditional `update_file`; it requires `atomic_update_file(expected_id, ...)`. The stock client raises 501. A deterministic fake-CAS barrier proves one winner and one 409. | `tests/test_gateway_unit.py`; `docs/CONFLICTS.md` |
| WordCraft Save As/PDF export | Host sends the emitted filename; gateway requires the original name and validates known OOXML/PDF/SVG signatures. | `integration/gateway/hostpage.py`, `integration/gateway/server.py` |
| Weak tests | Added deterministic CAS race, Save As rejection, PDF-as-DOCX rejection, direct-open refusal, and explicit failure assertions. | `tests/test_gateway_unit.py` |
| Licensing / evidence claims | Corrected verified upstream license revisions and marked real DOCX/ONLYOFFICE browser evidence NOT VERIFIED. | `docs/LICENSING.md`, `docs/TEST-MATRIX.md`, `STATUS.md` |

## Checks run

```text
python3 tests/test_gateway_unit.py                         PASS
python3 -m py_compile integration/gateway/*.py tests/*.py   PASS
git diff --check                                            PASS
```

## Genuine blockers

The repository does not contain a verified Seafile endpoint that both checks
the actual editing user and atomically compares the opened content id at write
time. The prepared external patch is not treated as such: it is outside the
candidate, unexecuted against Seahub, and its concurrency semantics are not
CAS. Consequently the stock gateway is intentionally read-only and the real
Seafile Web DOCX MVP remains **NOT VERIFIED**. ONLYOFFICE preservation also
remains **NOT VERIFIED** because no isolated browser deployment was available.

## Follow-up source verification (2026-10-22)

Exact deployed release sources were fetched read-only: Seahub
`1e9bde801b4360c14d784d9681d4261abc233a8b` (`v12.0.14-pro`) and Seafile Server
`32ed9c69594c9faa5cea28024403fcde362589ec` (`v12.0.14-server`). The public
`update-api` still has no conditional file-id parameter, but core Seafile includes
transactional `seaf_branch_manager_test_and_update_branch()` and `gen_new_commit()`
uses it. `seaf_repo_manager_post_file()` retries concurrent branch movement, so a
conditional-save patch must re-check the target path's file id after every retry
and refuse stale bytes. This corrects the shorthand “no atomic CAS primitive”:
the internal branch primitive exists; the user-bound file-level save endpoint
does not.

The live Seafile configuration was inspected without changes: ONLYOFFICE is
enabled for DOC/XLSX formats and the third-party-editor mapping currently sends
`.xlsx` to `http://127.0.0.1:8777/open/`. Seahub 12.0.14 returns the third-party
editor page before the normal Office view. Do not extend or change this mapping
until a per-file dispatch path preserving ONLYOFFICE is tested with synthetic
data.
