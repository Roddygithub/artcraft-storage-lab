# AGENTS.md

Instructions for AI agents (and humans) working in this repository.

## Mission

Make "open → edit → save → new version" work in the browser between Seafile Web and the Craft
web editors, with no patch to either side. The architecture is the stateless WOPI editor bridge
(`bridge/`), chosen by `docs/REFOUNDATION-REPORT.md`; the previous gateway + patches design under
`integration/` is legacy and is not extended.

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
6. **No Seafile patch, no editor patch.** Configuration on the Seafile side
   (`seahub_settings.py`), upstream release bundles on the editor side. A lab
   shim in `lab/real-seafile/static/` is acceptable as a stopgap and must say so
   in the bundle's `PROVENANCE.txt`.
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
11. **Keep Rust build artifacts off `/tmp`.** `/tmp` is a size-limited tmpfs on
    the development machine. Cargo is configured globally to use persistent
    cache/temp directories; do not override `CARGO_TARGET_DIR` or `TMPDIR` to a
    path under `/tmp`. If a test checkout lives under `/tmp`, use Cargo normally
    so it still writes build output to the persistent cache. Remove only stale
    generated target caches, never a directory that an active Cargo process is
    using.

## Process

* Change the bridge → run `python3 tests/bridge/test_bridge.py` (fake Seahub host).
* Change anything a real Seafile could see differently → run the lab
  (`lab/real-seafile/up.sh slice`, then `browser`) and commit `results/`.
* An editor bundle enters the lab only through `scripts/craft_web_zip.py` or
  `deploy/bridge/fetch-editors.sh`, with its SHA-256 in a `PROVENANCE.txt`.
* Anything meant for upstream goes to `docs/upstream-drafts/` and stays there
  until the gate passes and the owner approves.
* Implementation and review are different contexts. The reviewer never wrote
  the code it reviews.
* Push small, coherent commits to the public repository regularly; `main` is
  the integration branch.

## Definition of done for a change

1. Code or document written, with the smallest runnable check that proves it.
2. Lab evidence updated when runtime behaviour changed.
3. Report (`docs/REFOUNDATION-REPORT.md` §7) or ROADMAP updated when the plan changed.
4. Committed and pushed.

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
