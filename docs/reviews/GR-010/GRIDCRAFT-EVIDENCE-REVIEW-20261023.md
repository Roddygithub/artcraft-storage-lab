# Independent review — GR-010 fixture and runtime evidence

Date: 2026-10-23
Reviewer: Nemotron 3 Ultra 550B A55B, medium effort (`artcraft-reviewer`)
Scope: XLSX styles fixture/generator test, synthetic-Seafile GridCraft runtime
evidence, screenshots and updated status/matrix documentation. This is not a
full-project or GPT final review.

## Result

**PASS for this bounded evidence and fixture update.** No blocker or major
finding. This does not change the GPT-6.1 Sol FAIL on candidate
`0edbe524b4fa321b0f73f8601afef390e7f785e6`, does not complete GR-010 or the
all-Craft/multi-platform goal, and does not unlock upstream publication.

## Findings and disposition

| Finding | Disposition |
| --- | --- |
| Review suggested inconsistent indentation on the styles content-type entry. | Checked `tests/fixtures/make_fixtures.py:125`; it has the same two-space indentation as adjacent entries. No code change required. |
| Seafile history API returned HTTP 403 in the browser session. | Kept as an explicit evidence limitation. The committed-head acknowledgement and persisted content are verified, but a history-list count is not. GR-010 row 3.5 is marked `[~]` until that independent history check succeeds. |
| Full `gridcraft-ui-egui` integration suite did not run due to disk quota. | Already disclosed in `README.md:93-96`; the two affected targets passed individually. Full integration suite remains NOT VERIFIED. |
| Formula recalculation and GridCraft conflict behavior are not verified. | Retained as open items; no claim of complete GR-010. |

The reviewer also confirmed the regenerated fixture contains `xl/styles.xml`,
the workbook relationship and content-type override, and that the fixture test
passes. Both screenshots are valid PNGs. The corrected fixture opened from the
synthetic Seahub list without the missing-styles warning; its full edit/save/
reopen path has not yet been repeated.

## Reproduced checks

```text
python3 tests/test_xlsx_fixture.py                         PASS
python3 tests/fixtures/make_fixtures.py /tmp/test_fixtures  PASS
```

After returning this result, the reviewer briefly appended a follow-up table
despite the read-only brief. The parent removed that unadjusted append and
recorded the dispositions above. The reviewer made no source or test changes.
