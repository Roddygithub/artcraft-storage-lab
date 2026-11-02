# WordCraft typed-edit browser slice — code-stage evidence

> Historical code-stage assessment at `e53fe09`. A subsequent parent-operated isolated replay
> passed HTTP 48/48 and WordCraft browser 23/23 after the reviewed file-list/test-selection
> correction `e21c0b3`. See the [runtime evidence](../../lab/real-seafile/results/2026-11-02-wordcraft-pilot/README.md).
> Earlier NOT RUN statements below describe the original handoff, not this later replay.

Source implementation: `00957cef10c31a1fc9f88acfa70116516fd2eea3`, following the retained
failed candidate `c045b04ff23233108802dd88f7e69ebcb8c15cd5`; lab base `5b576de`.
This follow-up changes documentation only. Real Seafile replay remains **NOT RUN**.
Project GPT status: **INCOMPLETE**. Upstream: **LOCKED**.

## Changes and local evidence

| Location | Change / evidence |
| --- | --- |
| `lab/real-seafile/run_slice.py:298` | Stdlib `docx_text` extracts document text for marker assertions. |
| `lab/real-seafile/run_browser.py:118` | WordCraft-only flow types a fresh marker, saves through the editor, checks the emitted payload, stored content and attributed new version, closes the old page and opens a fresh Seafile context. |
| `lab/real-seafile/run_browser.py:240` | Reopen uses the production `wait_for_saved_response` helper; it pumps sync Playwright callbacks and accepts only nonempty HTTP-200 captured bytes. |
| `lab/real-seafile/run_browser.py:246` | Reopened editor must accept a second typed marker, save again and emit both full markers; storage must retain both. These assertions are coded, not proven against Seafile here. |
| `tests/test_wordcraft_reopen_wait.py` | Real Chromium with a disposable loopback HTTP fixture invokes that exact helper. Delayed response succeeds; empty/error captures time out; the former sleep-only loop demonstrably starves callbacks. It loads no Craft editor. |
| `ROADMAP.md` step 3 | WordCraft coded, runtime NOT RUN; other editors pending. |

Fresh checks on the unchanged source above: bridge **30/30**, Chromium regression **6 assertions
passed**, syntax compilation passed. The browser regression used cached Python **3.13.16** and
Playwright **1.64.1** via `uv run --offline --with playwright`; system `python3` alone lacks the
Playwright module. Exact commands and output: [local-checks.txt](evidence/2026-11-02-wordcraft/local-checks.txt).
No new package download was required for this rerun.

The cumulative change preserves editor interaction, both host save confirmations, full marker
checks, stored version/user checks, old-page closure and fresh-context reopen. No edited output
is injected or uploaded by a helper. The bridge and other editors' generic path are unchanged.
A successful local wait regression does not prove the real editor accepts the typed change.

## Runtime commands are separate — both NOT RUN

| Command | Coverage / remaining prerequisite |
| --- | --- |
| `lab/real-seafile/up.sh slice` | HTTP/WOPI/storage and ONLYOFFICE assertions in `run_slice.py`. NOT RUN for this implementation: the isolated Seafile lab must be available. |
| `lab/real-seafile/up.sh browser` | Actual editor open/edit/save/version/reopen in `run_browser.py`. NOT RUN for this implementation: requires the isolated stack and provenance-checked editor bundle. It does not run `slice`. |

The separate `slice)` and `browser)` arms in `lab/real-seafile/up.sh` invoke separate Compose
services. Local execution was unavailable (no Lima and Docker permission denied); provisioning
or accessing a live instance was excluded from the bounded pilot. Historical
`lab/real-seafile/results/{slice,browser}.json` predates this implementation and is not its runtime
evidence. Those files were not changed. ONLYOFFICE preservation is not re-proven by this pilot.

## Planning and review history

Aptarchy plan `plan-4f938657073b` covered 20 requirements in two slices. The first task failed
its final GPT review (one major, one minor) after two remediations. The callback follow-up
`artcraft-wordcraft-callback-20261102` obtained a zero-finding GPT task review at `00957cef10`;
its reviewer reported static diff inspection only, with filesystem tools unavailable and no
independent test execution. This is a limited task review, not project approval.

The second task `artcraft-wordcraft-coverage-20261102` remained blocked after one GLM and four
DeepSeek failures exhausted its configured writer budgets. The parent completed this
**documentation-only slice manually in a separate worktree**. It did not change the failed or
blocked task into an Aptarchy success. A sanitized [task snapshot](evidence/2026-11-02-wordcraft/task-snapshot.json)
retains the outcomes; the full private ledger/logs remain outside Git. The final independent review must identify the exact documentation commit; its outcome is
recorded separately in the handoff/PR.

## Coverage of the follow-up plan

| Requirement | Final location / observation |
| --- | --- |
| R1 preserve candidate | Source `00957cef10` descends from retained `c045b04`; documentation-only follow-up. |
| R2 bridge architecture | No `bridge/` diff; local fake-host tests 30/30. |
| R3 callback dispatch | Production wait helper and its call in `run_browser.py`. |
| R4 delayed response | Existing real Chromium regression, six assertions passed. |
| R5 distinct runtime commands | Two explicit NOT RUN rows above; `up.sh` arms inspected. |
| R6 coverage audit | This table; cumulative changed-file list inspected. |
| R7 interactive typing | `wordcraft_real_edit_flow`, initial and reopened typing; runtime NOT RUN. |
| R8 full markers | Save-payload and storage assertions for both markers; runtime NOT RUN. |
| R9 save confirmations | Both host-status assertions preserved; runtime NOT RUN. |
| R10 version/content/user | Both history checks, stored DOCX and reopen-byte checks; runtime NOT RUN. |
| R11 close/fresh session | `page.close`, new browser context and Seafile login preserved; runtime NOT RUN. |
| R12 bounded reuse | Existing DOCX helper and WordCraft branch; no other editor changes. |
| R13 no live services | Only loopback fake-host/fixture checks executed in this follow-up. |
| R14 no infrastructure changes | Cached offline test environment; no VM, permission or service changes. |
| R15 ONLYOFFICE untouched | No configuration changes; actual regression NOT RUN. |
| R16 local checks | Exact output in `local-checks.txt`. |
| R17 historical limits | Historical runtime results explicitly excluded and unchanged. |
| R18 preserve failure | Original failed and second blocked tasks retained in sanitized snapshot. |
| R19 gates | No upstream publication, main integration or project GPT promotion. |
| R20 two-slice plan | Planner completed two slices; first accepted, second manually completed; exact-commit final review is separate. |
