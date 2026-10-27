# GR-082 release-monitor independent review R5

**Verdict: bounded PROVISIONAL PASS; two LOW evidence findings, closed by response.**

Read-only review of the R4 monitor remediation in the Wave 1 worktree. The
review did not run tests or access the scheduler, browser, network, or services.

## R4 findings and R5 verification

| R4 finding | R5 result |
|---|---|
| Candidate ledger retained only one SHA per app | **Closed.** Five candidate keys use `app@fullSHA`; `current_candidate_by_app` points separately. Older candidate entries remain in the ledger. Unknown apps remain pending, and missing observations are null rather than invented successes. |
| Scheduler evidence omitted the actual prompt/update response | **Closed.** The retained prompt text exactly matches the prompt in the captured update response. Both artifact hashes are recorded in `scheduler-configuration-20261027.json`. |
| Retry branches were under-tested; only selected 5xx codes retried | **Closed.** Implementation retries 429, all 500–599, and 403 only with rate-limit headers. Eight unit tests cover these branches, HTTP-date/numeric `Retry-After`, cap, nonretryable errors, retried-body closure, network retry and unknown results. |

## R5 LOW findings and response

1. **Syntax-check evidence was not retained.** The README pointed to the unit-test
   log for a `py_compile` claim. The exact command and exit status are now
   recorded separately in `checks/monitor-syntax-r2.txt`.
2. **Prompt did not explicitly preserve historical candidate entries.** The
   live prompt now instructs the task never to delete or overwrite old
   `candidates[app@fullSHA]` records and to update the separate
   `current_candidate_by_app` pointer. The exact updated prompt and scheduler
   response were retained and hash-checked.

The reviewer did not independently rerun these post-review corrections. Local
verification after the corrections confirmed the prompt/response match, prompt
and response hashes, valid candidate key/pointer structure, JSON parsing,
`git diff --check`, and eight passing monitor tests. Unattended scheduler
execution remains **NOT VERIFIED** (`lastRunStatus: never`). The review does not
approve candidate release promotion or project GPT status.
