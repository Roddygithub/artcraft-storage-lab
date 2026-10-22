# AGENTS.md

Instructions for AI agents (and humans) working in this repository.

## Mission

Produce a rigorous, evidence-based answer to: **how do ArtCraft web editors plug
into a self-hosted file platform (Seafile first) so that "open → edit → save →
new version" works in the browser, with no manual download and no manual upload?**

## Non-negotiable rules

1. **The MVP is real or it is not done.** Success means: a user in Seafile Web
   clicks a DOCX, WordCraft Web opens it, the user edits, the user saves, Seafile
   creates a new version, the editor confirms the save, the file is closed and
   reopened with the edit intact. A browser download is **not** a save. A manual
   `curl` upload is **not** a save.
2. **Never break ONLYOFFICE.** The existing Seafile ↔ ONLYOFFICE integration stays
   functional throughout development. Do not uninstall, disable, or reconfigure it.
3. **Never touch production Seafile destructively.** Read-only inspection first.
   Keep a rollback path for every change. Use a synthetic library and synthetic
   documents for tests.
4. **No SeaDrive.** It is out of scope for the main workflow and must not be used
   as evidence that the web integration works.
5. **No premature generalization.** A generic host contract is a goal, but the
   Seafile MVP comes first. Generalize only what is demonstrably common.
6. **One connector, not N plugins.** Prefer a single Seafile integration layer
   with a file-type dispatcher over one plugin per Craft app.
7. **Upstream hard gate.** Do **not** open issues, PRs or RFCs in `storytold/*`,
   Seafile, or Seafile docs before `GPT REVIEW PASS`. Preparing the artifacts in
   this repository is allowed.
8. **No secrets in Git.** No passwords, tokens, JWT secrets, cookies, private
   keys, personal files or production data. No credentials hardcoded in the
   frontend.
9. **Provisional until GPT.** All free-model verdicts are `PROVISIONAL`. Never
   present a free-review PASS as final.
10. **Evidence over assertion.** Every non-obvious claim needs a source
    (file:line, URL, command output). Unverified claims are marked
    `NOT VERIFIED`.

## Agent routing

Use the `subagent` tool with the agent that matches the task. Never ask the human
which model to use. The definitions live in [`config/opencode/agents/`](config/opencode/agents/)
and are installed into `~/.config/opencode/agents/` by
`scripts/install-agents.sh`.

| Task | Agent |
| --- | --- |
| deep research, architecture, contracts | `artcraft-architect` |
| independent review (code, security, licensing) | `artcraft-reviewer` |
| bounded implementation, tests, scripts, docs | `artcraft-worker` |
| optional extra coding capacity | `artcraft-deepseek-worker` |

`artcraft-deepseek-worker` is never on the critical path. On timeout or provider
failure: abandon the task, note it in `docs/AI-ROUTING.md`, reroute.

The reviewer must not have written the code it reviews. An auto-review is never an
independent review.

## Definition of done for a work item (GR-XXX)

1. Artifact written under `docs/`.
2. Evidence bundle under `docs/reviews/GR-XXX/`.
3. Independent free review performed and recorded, findings remediated.
4. Test matrix updated (`docs/TEST-MATRIX.md`).
5. `STATUS.md`, `HISTORY.md`, `docs/GPT-REVIEW-QUEUE.md` updated.
6. Small, coherent commit(s), pushed to the public repository.
7. Status set to `GPT REVIEW PENDING`.

## Commit style

```text
docs: map Seafile online-editor integration
docs: audit ArtCraft web host capabilities
docs: define host integration contract
feat: add Seafile Craft integration prototype
feat: wire WordCraft host open flow
feat: implement host save callback
test: cover concurrent Seafile update
docs: prepare ArtCraft host integration RFC
```

## Style

* Lazy and concrete: reuse what exists, no new dependency without a reason, no
  abstraction nobody asked for, shortest diff that is actually correct.
* Tables over prose. Conclusions and evidence over chain-of-thought.
* Leave one runnable check behind for any non-trivial logic.
