# GR-052 — Ambiguous upstream save response reconciliation

Status: IMPLEMENTED — bounded independent R1–R3 review PROVISIONAL PASS,
no blocker/major; GPT REVIEW PENDING. No project GPT PASS.
Base: local main `a7804a23183c3bc5680028b0a88ac24e4eeb3a86`.
The two nonblocking R2 notes (lock-contention evidence and stale counts) were
remediated and re-reviewed in R3.

| Decision | Evidence |
|---|---|
| Only a `SeafileError` with `status is None` raised by `thirdparty_file_save` starts reconciliation; receipt validation errors do not | `integration/gateway/server.py:227-236` |
| Re-read using the original session repo/path/user/token; the real client checks token identity against all three | `integration/gateway/server.py:268-269`; `integration/gateway/seafile.py:127-140` |
| Require current editable permission and nonempty string file/head IDs, then bounded user-token content read with that file ID and exact byte equality | `integration/gateway/server.py:270-282` |
| Recheck user-bound authorization and identical current file/head after content read | `integration/gateway/server.py:285-293` |
| Only confirmed reads reach normal success: advance session IDs, clear unsaved, create digest/length receipt | `integration/gateway/server.py:255-265` |
| Reconciliation performs no write; subsequent identical and contended concurrent retries follow existing current-head/permission receipt checks | `integration/gateway/server.py:216-226,267-294`; `tests/test_gr052_upstream_save_loss.py:67-112` |
| Failure retains session baseline, dirty state and receipt; generic upstream details never enter browser errors | `integration/gateway/server.py:237-254`; `tests/test_gr052_upstream_save_loss.py:44` |

## Safety and limits

This confirms that the submitted bytes exist at the observed current version,
with current user-bound editable authorization. It cannot establish which writer
produced identical bytes, or prove that a new version was created specifically by
the ambiguous request. It does not replay a write. Detail/content/detail reads
reject observed concurrent file/head or authorization changes; an external write
following the final read is still possible, as after any successful save. Future
writes retain upstream CAS, and receipt retries recheck freshness.

The existing user-bound API contract remains required: file info must return
current identity/permission/head, and content must honor expected file ID. Stock
Seafile availability and real deployed endpoint semantics are NOT VERIFIED by
these tests. No real Seafile, browser, production, ONLYOFFICE or upstream changes.
This is synthetic gateway behavior, not the complete MVP.

| Check | Result / evidence |
|---|---|
| GR-052 native synthetic tests | 10 tests PASS; includes simultaneous identical retry after reconciliation; `docs/reviews/GR-052/gr052-tests.txt` |
| GR-049 receipt regression | 6 tests PASS; `docs/reviews/GR-052/gr049-tests.txt` |
| GR-050 loopback HTTP retry | 1 test PASS; `docs/reviews/GR-052/gr050-tests.txt` |
| Existing gateway checks | ALL CHECKS PASSED; `docs/reviews/GR-052/gateway-tests.txt` |
| Syntax and diff | Re-run after concurrent-retry test addition; `docs/reviews/GR-052/checks.txt` |
| Independent review | PENDING; parent will arrange separately |

Reproduce from repository root: `python3 tests/test_gr052_upstream_save_loss.py`.
Rollback: discard the GR-052 working-tree diff; no external state changed.
