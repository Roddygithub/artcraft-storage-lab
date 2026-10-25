# GR-041 independent exact review — round 3

**Verdict: PROVISIONAL PASS, bounded to candidate ZIP ingestion.** No blocker or
major finding. This is not a project-level GPT verdict and does not approve an
asset for promotion or deployment.

## Review scope and checks

Reviewed the exact GR-041 changes against base
`1e94723ad967f5fdec384c938062fcf37daf092a`: `scripts/fetch-craft-web.sh`,
`scripts/craft_web_zip.py`, the focused tests, and related status/evidence docs.
The reviewer independently ran:

- `python3 tests/test_gr041_craft_zip_limits.py` — 8 passed.
- `bash -n scripts/fetch-craft-web.sh` — passed.
- `python3 -m py_compile scripts/craft_web_zip.py` — passed.
- `git diff --check` — passed.

## Prior findings and disposition

| Finding | Round 3 disposition |
|---|---|
| Download/extraction byte limits | Closed: bounded streaming download and extraction, with a declared-size precheck. |
| Entry-count exhaustion before `ZipInfo` allocation | Closed: EOCD entry-count preflight precedes `ZipFile`, with a second count check. |
| Duplicate normalized names | Closed: duplicate normalized paths are rejected before writing. |
| No timeout | Closed for this staging tool: 30-second socket timeout plus a 15-minute streaming deadline checked around reads. |
| ZIP64/multi-disk rejection lacked tests | Closed: synthetic sentinel, locator, and multi-disk records are tested. |
| Negative path/symlink cases lacked tests | Closed for traversal, absolute/backslash paths, duplicates, Unix symlink, multi-root and missing required assets. |
| R2 claimed there was no temp cleanup trap | Not a code finding: the shell already installs `trap cleanup EXIT` before staging. R3 confirmed it. SIGKILL or machine failure can still leave a stale temporary directory. |

## Reviewer observations and limits

- The ZIP64 locator check follows the standard placement immediately before the
  classic EOCD record. Unusual nonconforming archives may be rejected; live
  release asset compatibility was not tested.
- The total deadline is checked between reads. An in-progress socket operation
  can last up to the 30-second socket timeout; this was tested with a mocked
  clock, not a real network stall.
- Host-protocol compatibility, live GitHub release retrieval, and promotion
  remain **NOT VERIFIED**. The script stages only under
  `integration/static/candidates/` and does not touch active app trees.

The review is source/test based. No Seafile, ONLYOFFICE, production or upstream
state was touched.
