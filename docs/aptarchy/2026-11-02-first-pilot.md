# First Aptarchy pilot — code-stage assessment

**Outcome: useful code produced, autonomous completion not achieved.** This is the first
bounded WordCraft slice of ROADMAP step 3, not a completed Seafile MVP or an overall project
verdict. Real editor/Seafile execution remains **NOT RUN**. Project GPT: **INCOMPLETE**;
upstream: **LOCKED**.

## Delivered and actually checked

| Item | Result / evidence |
| --- | --- |
| WordCraft genuine-edit scenario | Aptarchy-generated code types a marker before saving and requires a fresh reopened editor to save a second marker while retaining the first. [Source/evidence report](2026-11-02-wordcraft-browser-edit-slice.md). |
| Callback starvation correction | Follow-up source `00957cef10` pumps Playwright events; existing Chromium regression invokes the actual helper and fails with the former wait. Fresh local run: six assertions passed. |
| Existing bridge regression | Fresh local run: 30/30. No bridge or production configuration change. |
| Planning | `plan-4f938657073b`: 20 requirements, two slices, coverage gate passed. Parent manually coordinated slices because integration was disabled. |
| Independent task review | Follow-up source received a zero-finding GPT review. That reviewer reported diff-only inspection, no usable filesystem tools and no independent execution. The exact-SHA full-context final review is recorded separately in the handoff/PR. |
| Seafile version and semantic reopen | Assertions coded; actual Seafile/editor runtime NOT RUN. Historical lab results are not reused as current proof. |

Commands/output and sanitized task state are retained under
[evidence/2026-11-02-wordcraft](evidence/2026-11-02-wordcraft/). The snapshot records latest task
states and latest review summaries, not every earlier review. The full private ledger and raw
agent logs remain outside Git.

## What failed and required intervention

| Observation | Consequence / action |
| --- | --- |
| First launch was interrupted by a signal | Parent moved execution to persistent user services and reconciled the retained work. |
| Parent started `run` without a Planner role | Initial task never exercised planning. Parent added the Planner role and ran a real follow-up plan; the earlier omission remains part of this assessment. |
| Codex rejected Aptarchy's output schema | Parent fixed the adapter's strict-schema boundary in [Aptarchy PR21](https://github.com/Roddygithub/Aptarchy/pull/21), independently reviewed at `61b94bb`. The pilot then used that branch. |
| Original WordCraft task failed after two remediations | Final findings: callback starvation and a report conflating HTTP/browser commands. The failed task and its three candidates were retained. |
| Accepted callback follow-up | New bounded task produced `00957cef10`; checks/review passed. `integrate: none` kept its branch; Aptarchy's `integrated` state did not mean a main merge. |
| Documentation task exhausted its lanes | One GLM and four DeepSeek dispatches failed as provider unavailable. Aptarchy escalated and cooled down, then stopped at configured daily budgets. Parent completed documentation manually on a separate branch; blocked task remains blocked. |
| OpenCode 2 changed isolation semantics | Parent pinned the pilot to installed 1.19.0 and prepared [Aptarchy PR22](https://github.com/Roddygithub/Aptarchy/pull/22). Parser-only adaptation was unsafe because MCP disabling changed. |
| PR22 first review found a relative-path bypass | Parent fixed absolute executable pinning; fresh GPT review passed at `8d8538f`. Exact-head local suite: 405 tests, 403 passed, two skipped, no failures. One skip was a free-model no-answer check, so native live-agent denial was not established by that run. |
| CI runners repeatedly disconnected | GitHub annotations reported lost runner communication. PRs remain unmerged pending green CI; read-only runner checks and bounded retries were performed. |
| T3 PR watching repeatedly lost host access | Direct GitHub reads worked; watches were re-enabled on notifications. This is a separate monitoring failure, not evidence of an Aptarchy code failure. |

The retained [plan summary](evidence/2026-11-02-wordcraft/plan-summary.json) and
[policy snapshots](evidence/2026-11-02-wordcraft/policy-summary.json) record the planning
coverage, allowed free/subscription tiers and policy adjustments. The parent also raised its own initial GPT subscription dispatch cap from six to eight to finish
the planned sequence. This manual policy adjustment is recorded; it did not waive a verdict,
change the original two-remediation limit, authorize PAYG, or turn a failed task into success.
The dashboard's per-task Planner card reads task dispatches, while planning is recorded as
plan-scoped events: an empty card is not a reliable account of separate planning activity.

## Measured scope and limits

The retained snapshot contains **three tasks and 15 task dispatches**, plus one separately
recorded Planner call. Four task dispatches reported token usage; the rest are unknown, including
the failed schema call. Token counters are not an invoice. No monetary total, end-to-end speedup
or human time saved is inferred. The review/repair work outside Aptarchy is not silently included
in its ledger totals.

The pilot demonstrates bounded execution, exact-candidate validation, review/remediation,
provider escalation, budget enforcement and retained failure states. It also required substantial
parent orchestration, two Aptarchy fixes and a manual documentation takeover. The first task
failed, the second source task passed locally, and the third remains blocked. It is therefore
insufficient evidence that Aptarchy can complete this project unattended.

Next acceptance step: run `lab/real-seafile/up.sh slice` and then `browser` in an isolated lab
with provenance-checked editor bundles, retain the new results, and verify a real typed change,
version creation, confirmation, old-editor closure and semantic reopen. Production changes,
ONLYOFFICE reconfiguration and upstream publication are outside this pilot.
