# AI Routing

How work is routed between models in this project, and the **exact** model IDs
available in this environment.

Everything here was discovered by inspecting the live OpenCode installation
(`opencode v2.1.0`) and the `models` API — not assumed.

## Discovered model IDs

| Display name | Real OpenCode model ID | Variants | Provider |
| --- | --- | --- | --- |
| MiniMax M3.1 Flash (free) | `openrouter/minimax/minimax-m3.1-flash:free` | `low` `medium` `high` `xhigh` `max` | openrouter |
| GLM-5.3 | `nvidia/z-ai/glm-5.3` | `none` `thinking` | nvidia |
| GLM-5.3-Flash | `nvidia/z-ai/glm-5.3-flash` | `none` `thinking` | nvidia |
| Nemotron 3 Ultra 550B A55B | `nvidia/nvidia/nemotron-3-ultra-550b-a55b` | `none` `medium` `high` | nvidia |
| DeepSeek V4.1 Flash | `nvidia/deepseek-ai/deepseek-v4.1-flash` | `none` `low` `high` `max` | nvidia |

Related models that also exist and may serve as **fallback reviewers** (they must
not have participated in the work under review):

| Display name | Real OpenCode model ID | Variants |
| --- | --- | --- |
| Nemotron 3.5 Super VL 120B A12B | `nvidia/nvidia/nemotron-3.5-super-vl-120b-a12b` | `none` `thinking` |
| Nemotron 3.5 Lightning 30B A3B | `nvidia/nvidia/nemotron-3.5-lightning-30b-a3b` | `none` `thinking` |
| Nemotron 3 Nano Omni | `nvidia/nvidia/nemotron-3-nano-omni-30b-a3b-reasoning` | `none` `high` `max` |
| Muse Glimmer 30B | `nvidia/meta/muse-glimmer-30b` | `none` `minimal` `low` `medium` `high` `max` |
| Step 5 Preview | `nvidia/stepfun-ai/step-5-preview` | `none` `minimal` `low` `medium` `high` `xhigh` `max` |
| Qwen3.8 Omni Flash | `nvidia/qwen/qwen3.8-omni-flash` | `none` `low` `high` `max` |
| Qwen3.6 Flash | `nvidia/qwen/qwen3.6-flash` | `none` `thinking` |
| Granite 4.2 8B | `openrouter/ibm-granite/granite-4.2-8b` | `none` `low` `medium` `high` |
| Flint (free) | `openrouter/recursive/flint-v1.0:free` | — |

> A `thinking` variant is only meaningful on the models that expose it. Using
> `#thinking` on a model without that variant is a configuration error, not a
> silent no-op — check the table before assigning a model.

## The routing table

**Changed on 2026-10-22, during GR-012**: the MiniMax free endpoint was withdrawn,
so the owner role moved to GLM-5.3-Flash. See the incident log below.

| Role | Agent ID | Model | Variant | Since |
| --- | --- | --- | --- | --- |
| Owner / Orchestrator / **default implementer** | `artcraft-owner` | `nvidia/z-ai/glm-5.3-flash` | `thinking` | 2026-10-22 |
| Architect / Deep research | `artcraft-architect` | `nvidia/z-ai/glm-5.3` | `thinking` | start |
| Independent reviewer | `artcraft-reviewer` | `nvidia/nvidia/nemotron-3-ultra-550b-a55b` | `high` | start |
| Bounded worker / remediation | `artcraft-worker` | `nvidia/z-ai/glm-5.3-flash` | `thinking` | start |
| Optional worker (never critical) | `artcraft-deepseek-worker` | `nvidia/deepseek-ai/deepseek-v4.1-flash` | `max` | start |

**RETIRED**: `openrouter/minimax/minimax-m3.1-flash:free#max` — the free endpoint
was withdrawn. It is **not** replaced by a paid MiniMax model. The definitions in
`config/opencode/agents/` no longer name it, and `scripts/install-agents.sh`
installs the current ones.

The owner now implements directly (it is the *default implementer*), and delegates
only what is genuinely better delegated: hard architecture to the architect,
independent review to the reviewer.

## How the agents are defined

OpenCode V2 discovers agents from Markdown files with YAML frontmatter:

```text
~/.config/opencode/agents/<name>.md     # global, applies to every project
.opencode/agents/<name>.md               # project-local
```

Both `agent/` and `agents/` directory names are accepted by the loader, and
`mode:` accepts `primary`, `subagent` or `all`. The canonical definitions live in
[`../config/opencode/agents/`](../config/opencode/agents/) and are installed with:

```sh
./scripts/install-agents.sh
```

The script copies the definitions into `~/.config/opencode/agents/` so that the
routing works in any session, including sessions started outside this repository.
Project-local `.opencode/agents/` is deliberately **not** used: it would shadow the
global definitions and create two sources of truth.

### Owner delegation permission

The owner agent is allowed to launch any subagent:

```yaml
permissions:
  - action: subagent
    resource: "*"
    effect: allow
```

The reviewer agent is **denied** write access, so it cannot fix the code it is
reviewing:

```yaml
permissions:
  - action: edit
    resource: "*"
    effect: deny
```

## Smoke test results

Performed on 2026-10-22 against the live installation, with the installed
definitions and a trivial identity prompt. A subagent that silently inherits the
parent's model is a **FAIL**.

| Agent | Expected | Actual | Result |
| --- | --- | --- | --- |
| `artcraft-owner` | `openrouter/minimax/minimax-m3.1-flash:free#max` | same (session model) | OK at the time — **the model has since been retired**, see the incident log |
| `artcraft-owner` (re-smoked after the retirement) | `nvidia/z-ai/glm-5.3-flash#thinking` | `nvidia/z-ai/glm-5.3-flash` | OK — verified through `/api/agent` |
| `artcraft-architect` | `nvidia/z-ai/glm-5.3#thinking` | `nvidia/z-ai/glm-5.3` | OK |
| `artcraft-reviewer` | `nvidia/nvidia/nemotron-3-ultra-550b-a55b#high` | `nvidia/nvidia/nemotron-3-ultra-550b-a55b` | OK |
| `artcraft-worker` | `nvidia/z-ai/glm-5.3-flash#thinking` | `nvidia/z-ai/glm-5.3-flash` | OK |
| `artcraft-deepseek-worker` | `nvidia/deepseek-ai/deepseek-v4.1-flash#max` | — (1st attempt timed out, 2nd OK) | OK, flaky |

### DeepSeek resilience

`artcraft-deepseek-worker` produced `Timed out waiting for response headers` on
the **first** smoke test and answered normally on the second. The provider is
**reachable but unreliable**.

Rules in force:

1. Before a DeepSeek delegation, run a one-line smoke prompt.
2. On timeout / repeated retry / rate limit / provider unavailable / no answer:
   stop the task, record it in this file (see the incident log below), and
   reroute to `artcraft-worker` or to the owner.
3. DeepSeek is never on the critical path. The project never waits for it.

### Incident log

| Date | Agent | Symptom | Action | Impact |
| --- | --- | --- | --- | --- |
| 2026-10-22 | `artcraft-deepseek-worker` | `Timed out waiting for response headers` on smoke test #1 | retried once, succeeded | none |
| 2026-10-22 | `artcraft-owner` (MiniMax) | the free endpoint was **withdrawn** mid-session, during GR-012 | the owner role moved to `nvidia/z-ai/glm-5.3-flash#thinking`; no work was redone, no file was rewritten; the project state was reconstituted from `STATUS.md`, `HISTORY.md`, `docs/GPT-REVIEW-QUEUE.md`, `docs/reviews/` and `git log` | the session continued from where it stood |
| 2026-10-22 | `artcraft-architect` (GLM-5.3) | `Timed out waiting for response headers` on the GR-001 research task, after a long run | the task was abandoned; GR-001 had already been completed **independently** by the owner from the deployed instance (`docs/reviews/GR-001/DEPLOYED-INSTANCE-CONTRACT.md`), so nothing was lost | none — the artifact existed before the timeout |
| 2026-10-22 | `artcraft-architect` (GLM-5.3) | the same timeout on the GR-003 capability audit, after cloning all 14 repositories and reading them for hours | abandoned; the owner had already completed GR-003 independently and verified it against the sources (`docs/ARTCRAFT-WEB-CAPABILITIES.md`, `docs/reviews/GR-003/WEB-BUILD-SURVEY.md`) | none — the artifact existed before the timeout |

> **A note on the architect.** Two long research tasks produced no artifact
> before the provider timed out. Both were already covered by the owner's own
> verified work, so nothing was lost — but the pattern is real: a **very long
> research brief** is a bad fit for a single sub-agent call. The fix, applied
> from here on, is to split research into bounded questions and to keep the
> owner's own verification as the primary path. The architect stays for
> **bounded** architectural questions, not for open-ended surveys.

### The model-ID table (as of 2026-10-22, after the retirement)

| Display name | Real OpenCode model ID | Variants | Role |
| --- | --- | --- | --- |
| GLM-5.3-Flash | `nvidia/z-ai/glm-5.3-flash` | `none` `thinking` | **owner** |
| GLM-5.3 | `nvidia/z-ai/glm-5.3` | `none` `thinking` | architect |
| Nemotron 3 Ultra 550B A55B | `nvidia/nvidia/nemotron-3-ultra-550b-a55b` | `none` `medium` `high` | reviewer |
| DeepSeek V4.1 Flash | `nvidia/deepseek-ai/deepseek-v4.1-flash` | `none` `low` `high` `max` | optional worker |
| ~~MiniMax M3.1 Flash (free)~~ | ~~`openrouter/minimax/minimax-m3.1-flash:free`~~ | — | **RETIRED** |

## Fallback review policy

* Primary reviewer: `artcraft-reviewer` (Nemotron 3 Ultra 550B A55B).
* If unavailable, use **another free model that did not participate in the work
  under review** (see the fallback table above).
* If no independent reviewer is available, the item is marked
  `INDEPENDENT FREE REVIEW PENDING`.
* A self-review is **never** presented as an independent review.

## Review status vocabulary

```text
PROVISIONAL — FREE REVIEW PASS
PROVISIONAL — FREE REVIEW FAIL
INDEPENDENT FREE REVIEW PENDING
GPT REVIEW PENDING
GPT REVIEW PASS
GPT REVIEW FAIL
```

Only `GPT REVIEW PASS` unlocks publication upstream.
