# Independent runtime/docs review

## R1 result

Independent review by the configured `artcraft-reviewer` role, T3 task
`gr076-runtime-review-20261026-r1`, returned **MINOR / PROVISIONAL**, with no
BLOCKER or MAJOR. The reviewer checked runtime evidence, screenshots, hashes,
secret/PII exposure and cross-file status. Its report identified three minor
items: stale Seafile status wording, a suggested `[~]` matrix grade, and a
reported `gr077` rollback-path typo.

## Findings and dispositions

| Finding | Disposition |
|---|---|
| Stale “Seafile persistence/version/reopen NOT VERIFIED” in current status/history/queue | Not present in the current GR-076 entries: `STATUS.md` and `HISTORY.md` state the synthetic workflow completed; the GR-076 queue entry states that three versions exist and the current readback matches the newest. Older, separately scoped GR entries retain their own historical NOT VERIFIED statements. No change needed. |
| Test matrix should use `[~]` because evidence is synthetic | No change. The matrix row is specifically the synthetic Seafile click/open/edit/save/version/close/reopen scenario; that complete scenario passed. `[x]` records that bounded scenario, while production/proxy and other limitations are separately marked NOT VERIFIED. |
| Rollback path should say `gr076`, not `gr077` | The `gr077` staging label is retained verbatim for the Seafile backup created during that deployment attempt. The review exposed an inaccurate gateway path; corrected it to the existing `gr077-dispatch.base.json`. Its SHA-256 is `af3c4cbbb76f3583b0bb70118c48ebd7445bc2841e577658918edd7c43f83c2d`, exactly the pre-change dispatch hash in the evidence record. |

R1 also confirmed the recorded screenshot, fixture, bundle, history and
configuration hashes and found no retained secrets or personal data. Because
R1's status observations predated the completed edits, a second independent
round checked the final current tree. All free-review verdicts remain
**PROVISIONAL**; GPT review is pending.

## R2 final-state check

The same independent reviewer completed task
`gr076-runtime-review-20261026-r2` against the final tree and returned
**PASS / PROVISIONAL**, no BLOCKER/MAJOR/MINOR. It verified all three R1
findings closed: current status claims match the synthetic evidence, `[x]`
correctly records the completed synthetic-only matrix scenario while broader
gaps remain unverified, and the `gr077`-named baseline file is the real
pre-change dispatch snapshot with a matching hash. R2 also reconfirmed the
runtime screenshot/evidence hashes, cross-file consistency and absence of
secrets or personal data. GPT review remains pending.

## R3 post-allowlist regression evidence

After the WordCraft DOCX re-save/reopen evidence and the more precise
ONLYOFFICE API-path diagnostic were added, independent review task
`gr076-runtime-review-20261026-r3` returned **PASS / PROVISIONAL**, with no
BLOCKER/MAJOR/MINOR findings. It verified the PhotoCraft and WordCraft
history/version claims, screenshot and bundle hashes, rollback baseline hash,
ONLYOFFICE 404-vs-200 diagnostic, secret/PII redaction, and consistency across
status, history, test matrix, queue and runtime evidence. GPT review remains
pending.

## Dispatcher route promotion review

Independent review task `gr076-dispatch-route-review-20261026-r1` returned
**PROVISIONAL PASS**, with no BLOCKER or MAJOR. It confirmed that the tracked
`pcraft` → PhotoCraft mapping matches the deployed synthetic route, retains all
four prior tracked mappings, and is supported by the GR-076 runtime evidence.
It also confirmed the static bundle stays Git-ignored and that no test/build or
production/ONLYOFFICE change is claimed by this dispatcher follow-up. GPT review
remains pending.
