# GR-076 evidence — bounded PhotoCraft host adapter

Read [the report](../../GR-076-PHOTOCRAFT-BOUNDED-HOST-ADAPTER.md) for scope,
guards and limits. All claims remain bounded by recorded checks. This evidence
was committed as `5637bf2` on `main`, matching its local `origin/main` tracking
ref. No Seafile,
Proxmox, ONLYOFFICE, production, deployment or dispatch was accessed or changed;
no upstream publication was made.

## Reproduction

Use a fresh checkout of `https://github.com/storytold/photocraft` at exactly
`a02f2ee41059d3312e7ff24a5af5edcac7b6435a`. The local source object was available
in `/home/roddy/.cache/artcraft-storage-lab/photocraft-audit`; a new detached
worktree was created from that object. Both original patch digests matched and
`git apply --check` succeeded before edits. The combined GR-076 patch includes
the GR-026 core, reused GR-032 adapter, missing test file repair and hardening;
apply it alone (do not apply prerequisites separately).

```sh
git checkout --detach a02f2ee41059d3312e7ff24a5af5edcac7b6435a
git apply --check /path/to/lab/docs/reviews/GR-076/photocraft-host-save.patch
git apply /path/to/lab/docs/reviews/GR-076/photocraft-host-save.patch
/path/to/lab/scripts/check-gr076-photocraft.sh "$PWD"
```

`pins.json` records every Git dependency resolved by Rust 1.95
`cargo metadata --locked --format-version 1`. The candidate adds only the existing workspace `photocraft-format` dependency
edge for the Web bounded decoder; all external locked versions/Git pins remain
unchanged. Registry dependencies are fully
pinned/checksummed in that lockfile. Cargo used the existing persistent global
target/temp configuration; no `/tmp` override was introduced.

## Check evidence

Final runnable script **PASS, exit 0**. Initial retained GR-032 locked WASM
check also passed; it is retained separately from final candidate results. The first fmt attempt
failed because retained patches omitted `saved_snapshot_tests.rs`; candidate
repairs that artifact defect as documented in the report.

## Independent review

R1 delegated to `artcraft-reviewer` role using configured free reviewer model
`nvidia/nvidia/nemotron-3-ultra-550b-a55b`, effort `thinking`, on provider
`acpRegistry_opencode`. The live catalog does not advertise the definition's
`#high` suffix as an effort value; used its supported `thinking` descriptor.
Reviewer did not author code and was instructed not to change source. R1 and
R2 returned **PROVISIONAL PASS**, no BLOCKER/MAJOR. R2 reviewed final combined
patch `b3375bc2e9f29a9624df0428df3916b2013ba9aa11be9b7e27825cd103c07d85`.
R2 used supported effort `high` after a live catalog change rejected `thinking`;
see `docs/AI-ROUTING.md`. Responses/corrections are retained separately; the
independent reports were not rewritten. Every free verdict is PROVISIONAL;
GPT review remains pending. These are source reviews, not independent runtime
or test execution. Some reviewer line references are inaccurate; authoritative
current anchors are in `source-evidence.txt` and the exact patch.

## Current demonstrated checks

| Command / observation | Result |
|---|---|
| `cargo +1.95.0 fmt --all -- --check` | PASS at start of runnable final check script |
| `cargo +1.95.0 test --locked -p photocraft-engine --lib saved_snapshot_tests` | PASS, 4 tests |
| `cargo +1.95.0 test --locked -p photocraft-ui-egui --lib host_` | PASS, 7 tests (5 host/core policy cases plus 2 existing workspace host-chrome tests) |
| `cargo +1.95.0 test --locked -p photocraft-ui-egui --lib file_open::tests::` | PASS, 47 tests including native path/open, local drag/drop, host lifecycle/guards/limits and standalone download baseline |
| `cargo +1.95.0 test --locked -p photocraft-web host_inbox::tests::` | PASS, 2 tests |
| `cargo +1.95.0 check --locked -p photocraft-web --target wasm32-unknown-unknown` | PASS, final candidate; retained baseline passed separately |
| `git apply --check`, apply and byte comparison in clean exact-base checkout | PASS, all 14 changed/new source files byte-identical; `patch-check.txt` |
| `git diff --check` / script syntax | PASS at current stage |

Final script output is `checks.log`. Original engine test command without
`--lib` also passed 4 selected tests and ran many integration binaries with zero
selected cases; retained in `initial-engine.log`. `initial-ui.log` records the
first host test run. `retained-gr032-base-wasm.log` is explicitly baseline
compilation, not evidence for the final candidate. `source-evidence.txt` and
`transport-source-evidence.txt` record exact source anchors at the pinned inputs.

## Final result and retained state

**GPT REVIEW PENDING** — committed lab candidate (`5637bf2`). R1/R2 are
PROVISIONAL source reviews. Runtime and memory limits
remain in the report; this is not a project PASS or deployment authorization.

- Combined patch SHA-256: `b3375bc2e9f29a9624df0428df3916b2013ba9aa11be9b7e27825cd103c07d85`.
- Cargo.lock SHA-256: `166c9984b3e3706eabd88400ab9bed50840cd146043e6dd4ac900a285cb4a3d0`.
- Final check script exit: `0`; see `check-result.json` and `checks.log`.
- `lock-check.txt`: every preexisting external dependency version/source/checksum unchanged.
- Parent checkout `/home/roddy/.t3/worktrees/artcraft-storage-lab/t3-96b37bb6`
  remains clean at `dc105220ae934f9779eb357a4cda901ee0aa0c0b`.
- Lab edits: `/home/roddy/.t3/worktrees/artcraft-storage-lab/gr-076-photocraft`.
- Product edits: `/home/roddy/.cache/artcraft-storage-lab/gr076-photocraft`.
- Clean apply-check copy retained: `/home/roddy/.cache/artcraft-storage-lab/gr076-photocraft-apply-check`.

Runnable check from the isolated lab worktree:

```sh
./scripts/check-gr076-photocraft.sh /home/roddy/.cache/artcraft-storage-lab/gr076-photocraft
```

Browser iframe/ACK/unload/repaint runtime, persistence/version/reopen, full
native desktop/visual/clippy/corpus checks and total serialization-memory bound
remain **NOT VERIFIED** (serialization peak is explicitly not bounded by the
post-serialization cap). No service was accessed for this slice.
