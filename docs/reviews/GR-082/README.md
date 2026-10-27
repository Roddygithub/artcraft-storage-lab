# GR-082 evidence — upstream refresh wave 1

This bundle tracks source provenance and qualification for the five apps
currently listed in `integration/config/dispatch.json`. It is isolated from the
GR-081 worktree and does not promote any route.

## Ongoing update loop

Run the read-only release scan with:

```sh
python3 scripts/check-artcraft-releases.py
```

The JSON report gives the latest non-prerelease GitHub release returned by
`/releases/latest`, its resolved commit,
and ahead/behind counts from each qualified source pin. The scanner never
changes source or pins. Transient network, rate-limit and server errors receive
at most two retries after the first request, with bounded exponential backoff
and `Retry-After` handling. A remaining `unknown` is an incomplete scan, never
a no-drift result. The weekly T3 task records scans, retries unknown apps on a
later run, resumes unfinished work before stopping, and deduplicates candidates
by app plus full release commit SHA using
[`release-candidate-state.json`](release-candidate-state.json). Each candidate
must pass the full app gates in the GR-082 report. Automation must never
promote the active dispatcher, deploy to Seafile, touch ONLYOFFICE, or publish
to upstream `storytold/*` before the repository's GPT review gate.

The recurring task is enabled/configured as
`scheduled-task:c297cae8-a56e-47a5-844c-bf52626b672a`, bound to this project
thread and scheduled every 7 days. Its next run is 2026-11-03 09:17:46 UTC; it
is configured to resume this in-progress wave before opening any new release
candidate. The scheduler currently reports `lastRunStatus: never`; unattended
execution remains **NOT VERIFIED**.
The full live prompt and update response are retained in
[`scheduler-prompt-20261027.md`](scheduler-prompt-20261027.md) and
[`scheduler-prompt-update-response-20261027.json`](scheduler-prompt-update-response-20261027.json);
the cadence/status snapshot is
[`scheduler-configuration-20261027.json`](scheduler-configuration-20261027.json).
The monitor R5 review and response are retained in
[`INDEPENDENT-MONITOR-REVIEW-R5.md`](INDEPENDENT-MONITOR-REVIEW-R5.md) and
[`RESPONSE-MONITOR-R5.md`](RESPONSE-MONITOR-R5.md). R5 was bounded PROVISIONAL
PASS with two LOW evidence findings, both addressed; unattended execution is
still **NOT VERIFIED**.
Pre-push review R1 and its response are retained in
[`INDEPENDENT-PREPUSH-REVIEW-R1.md`](INDEPENDENT-PREPUSH-REVIEW-R1.md) and
[`RESPONSE-PREPUSH-R1.md`](RESPONSE-PREPUSH-R1.md). R2 returned with one
MEDIUM and two LOW pre-push findings; its response and the R3 review are in
[`INDEPENDENT-PREPUSH-REVIEW-R2.md`](INDEPENDENT-PREPUSH-REVIEW-R2.md) and
[`RESPONSE-PREPUSH-R2.md`](RESPONSE-PREPUSH-R2.md). R3 found that R8 hashed
the build directory rather than the served copy. R9 reran the smoke and hashed
the actual served files before and after; R4 returned bounded PROVISIONAL PASS; see
[`INDEPENDENT-PREPUSH-REVIEW-R4.md`](INDEPENDENT-PREPUSH-REVIEW-R4.md) and
[`RESPONSE-PREPUSH-R4.md`](RESPONSE-PREPUSH-R4.md). A branch-only push to this
repository is allowed; Seafile remains NOT VERIFIED.

## Source references

Official tag lookup on 2026-10-27:

```sh
git ls-remote https://github.com/storytold/wordcraft.git 'refs/tags/v0.11.0*'
git ls-remote https://github.com/storytold/gridcraft.git 'refs/tags/v0.12.1*'
git ls-remote https://github.com/storytold/pdfcraft.git 'refs/tags/v0.14.0*'
git ls-remote https://github.com/storytold/vectorcraft.git 'refs/tags/v0.17.0*'
git ls-remote https://github.com/storytold/photocraft.git 'refs/tags/v0.16.0*'
```

Results are recorded in `docs/GR-082-UPSTREAM-REFRESH-WAVE-1.md`. WordCraft and
GridCraft compare results were obtained from the official GitHub API:

- [WordCraft base to v0.11.0](https://api.github.com/repos/storytold/wordcraft/compare/00bc6a4b028013b2dfb0e85e8b326aeed3ecff6d...v0.11.0)
- [GridCraft base to v0.12.1](https://api.github.com/repos/storytold/gridcraft/compare/06920de8da609c19de7446945cfc62b844691efd...v0.12.1)
- [PdfCraft base to v0.14.0](https://api.github.com/repos/storytold/pdfcraft/compare/57e531ccca0047597809748b5cb4276336d6051a...v0.14.0)
- [VectorCraft v0.14.0 to v0.17.0](https://api.github.com/repos/storytold/vectorcraft/compare/ad0566943ab9741e6356bbc9b53c3cc09895068d...v0.17.0)
- [PhotoCraft base to v0.16.0](https://api.github.com/repos/storytold/photocraft/compare/a02f2ee41059d3312e7ff24a5af5edcac7b6435a...v0.16.0)

The available WordCraft/GridCraft cache clones have incomplete shallow
history; local `rev-list` counts are not used as release distances. All five
compares were checked via the official compare API. Ahead/behind counts are
293/0, 175/0, 535/0, 1,174/0 and 77/0, respectively.

## Porting observations

- **WordCraft:** v0.11.0 contains an upstream host bridge and startup wiring
  that overlap the retained adapter. Port the durable ticket/acknowledgement
  behavior without dropping upstream save-format, preference or startup rules.
- **GridCraft:** the bridge still needs durable acknowledgement; engine save
  logic has changed and GR-016 test hunks moved under `tests/it/`.
- **PdfCraft:** upstream changed text-edit commit and unsaved-work/save-prompt
  behavior in `editing.rs`; reconcile the GR-017 durable-ACK patch while
  preserving the new text-commit behavior.
- **VectorCraft:** GR-058 used VectorCraft's page API and the gateway polling
  adapter, not a shared host-save patch. The Web entry point is unchanged, but
  engine load/save/export code changed, so a new actual-WASM and Seafile run is
  required.
- **PhotoCraft:** most existing GR-076 source hunk contexts remain, but lockfile
  hunks differ. Preserve upstream modal-workspace restrictions and new
  import/export bounds when applying the combined GR-076 patch.

These research notes informed four exact-release source patches; VectorCraft
has a source-only no-port assessment. See
[`ports/`](ports/) and [`port-manifest.json`](port-manifest.json).

## Patch and build status

| App | Exact-base patch | Locked WASM | Focused tests | Browser / Seafile |
|---|---|---|---|---|
| WordCraft v0.11.0 | PASS, packaged local transport included | PASS | Engine 2, UI 9; release bundle and actual-WASM memory-host edit/save/version/ACK/reopen pass | Seafile NOT VERIFIED |
| GridCraft v0.12.1 | PASS, includes pre-open native-XLSX check | PASS | Engine 3 and UI 2 pass | NOT VERIFIED |
| PdfCraft v0.14.0 | PASS, packaged local transport included | PASS | 30 `editing::` tests pass, including the 8 ACK tests | NOT VERIFIED |
| PhotoCraft v0.16.0 | PASS, packaged local transport included | PASS | One standalone confirmation test passes against final local-path tree; other final-tree test suites are NOT VERIFIED/cancelled | NOT VERIFIED |
| VectorCraft v0.17.0 | No source patch identified | PASS, Rust 1.95 locked WASM check | NOT RUN | NOT VERIFIED |

Patch application and transport-integrity command outputs are retained in
[`checks/`](checks/). GR-082 app-port review R1 findings and responses are in
[`INDEPENDENT-APP-PORT-REVIEW-R1.md`](INDEPENDENT-APP-PORT-REVIEW-R1.md) and
[`RESPONSE-APP-PORT-R1.md`](RESPONSE-APP-PORT-R1.md). R2 verified those
packaging corrections but identified incomplete final build/test records and
outstanding PdfCraft regression tests; the bounded responses and rerun evidence
are in [`INDEPENDENT-APP-PORT-REVIEW-R2.md`](INDEPENDENT-APP-PORT-REVIEW-R2.md)
and [`RESPONSE-APP-PORT-R2.md`](RESPONSE-APP-PORT-R2.md). The bounded R3 review
returned PROVISIONAL PASS with one low finding, now resolved in the manifest;
see [`INDEPENDENT-APP-PORT-REVIEW-R3.md`](INDEPENDENT-APP-PORT-REVIEW-R3.md)
and [`RESPONSE-APP-PORT-R3.md`](RESPONSE-APP-PORT-R3.md).

The first scan is retained at
[`upstream-scan-20261027.json`](upstream-scan-20261027.json). It resolved and
compared WordCraft and GridCraft; later requests for PdfCraft, VectorCraft and
PhotoCraft hit GitHub's unauthenticated API rate limit and are recorded as
`unknown`. This historical partial scan predates the `merge_base_commit`
parser fix: its two `merge_base: null` fields use the wrong key and provide no
merge-base evidence. The corrected scanner rejects responses without a valid
`merge_base_commit`.

A fresh scan on 2026-10-27T16:06:51Z resolved and compared all five apps with
exit code 0. Each remains on the same stable release and ahead/behind counts
listed above; every reported merge base equals its qualified base. Raw output
is retained at
[`upstream-scan-20261027T160651Z.json`](upstream-scan-20261027T160651Z.json),
with its exit status alongside it. No newer stable release was detected.

The checker
tests pass (8 tests), including all 5xx responses, conditional 403 rate-limit
handling, HTTP-date `Retry-After` parsing/capping, nonretryable errors,
error-body closure, and bounded network retry. The test run is retained in
`checks/monitor-tests-r2.txt`; the exact `py_compile` command and exit status
are in `checks/monitor-syntax-r2.txt`. These checks validate the monitor, not
any refreshed ArtCraft adapter.

## Current evidence boundary

The four patches apply to clean indexes initialized from their exact release
commits. WordCraft has a release bundle and bounded actual-WASM in-memory
edit/save/version/ACK/fresh-reopen evidence, but no refreshed Seafile run or
refusal-count evidence. GridCraft, PdfCraft and PhotoCraft still need release
bundles and browser qualification; VectorCraft still needs a release
asset/font build and browser capture/save. Synthetic Seafile durable
version/readback/fresh reopen remains **NOT VERIFIED** for every refreshed app.
Prior GR-055–058 and GR-076 results are historical evidence for their exact
older source revisions only. No credentials or production data belong in this
bundle.
