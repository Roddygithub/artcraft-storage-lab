# GR-082 — ArtCraft upstream refresh, active dispatcher wave

Started 2026-10-27. Status: **PAUSED 2026-10-28** for physical transport.
This work is isolated on branch
`upstream-refresh/wave-1`, based on committed candidate `62d8845` in a separate
worktree. It does not change the current GR-081 candidate or its uncommitted
closeout evidence.

## Scope

Refresh only the five apps in the tracked dispatcher: WordCraft, GridCraft,
PdfCraft, VectorCraft and PhotoCraft. Each refreshed adapter is a new candidate
until its own source, build, browser and synthetic Seafile evidence is complete.
Existing GR-055–058/076 evidence remains attached to its original source and
bundle; it does not transfer to refreshed bases. No dispatch promotion,
production change, ONLYOFFICE change, or upstream issue/PR/RFC is part of this
work.

## Verified pins and starting state

Exact upstream tag objects and ahead/behind distances were independently
verified against the official `storytold` repositories. Commit distances use
GitHub compare API counters, not incomplete local shallow-cache traversal.

| App | Existing source base | Release tag | Release commit | Distance / initial state |
|---|---|---|---|---|
| WordCraft | `00bc6a4b028013b2dfb0e85e8b326aeed3ecff6d` | `v0.11.0` | `e31f2f06a5f8004ceaa88f68c00b47908e321aa4` | 293 ahead, 0 behind; verified |
| GridCraft | `06920de8da609c19de7446945cfc62b844691efd` | `v0.12.1` | `f86aec12dabc744b5f75e1033f87bfe685e78481` | 175 ahead, 0 behind; verified |
| PdfCraft | `57e531ccca0047597809748b5cb4276336d6051a` | `v0.14.0` | `5a78b223871add8e3883856205cc653d741e0e94` | 535 ahead, 0 behind; verified |
| VectorCraft | `ad0566943ab9741e6356bbc9b53c3cc09895068d` | `v0.17.0` | `43313f9451de7ab5b909801006b8881458f2bf04` | 1,174 ahead, 0 behind; verified |
| PhotoCraft | `a02f2ee41059d3312e7ff24a5af5edcac7b6435a` | `v0.16.0` | `b1794c6e0608ccfc887213dcf58398977c5cb75e` | 77 ahead, 0 behind; verified |

The tag refs were checked on 2026-10-27; all five official compare results are
linked in the evidence README. These are source pins, not yet refreshed or
validated candidates.

## Qualification gates

Each app must pass these gates independently, with exact source and artifact
hashes retained before it can be called refreshed:

1. Confirm the official tag resolves to the recorded full commit; record the
   merge base and ahead/behind counts from a complete upstream graph.
2. Apply the existing adapter patch in a clean checkout. Rebase only the
   required hunks, document conflicts and preserve upstream safety changes.
3. Run the app's Rust tests and locked WASM check; build the release WASM with
   the pinned toolchain and a new immutable candidate inventory.
4. Run the host-contract browser workflow, including ordinary Save, durable
   acknowledgement, failed-save retry, edits during an outstanding save,
   close and fresh reopen. Refused replacement/Save As must not serialize or
   upload.
5. On the synthetic Seafile library, verify open → edit → save → durable new
   version → readback → fresh reopen. Retain evidence that the bytes sent by
   the editor are the bytes committed by Seafile, and that the editor becomes
   clean only after the durable acknowledgement.
6. Obtain an independent review of that app's final patch and evidence. All
   verdicts remain PROVISIONAL; nothing promotes a dispatch route automatically.

Unavailable build dependencies or deployment evidence are recorded as
**NOT VERIFIED**; they do not count as passes. ONLYOFFICE preservation remains
an independent project gate and is not to be modified during this wave.

## Current status

The five official release tag commits and distances have been recorded. Four
release patches are now retained under
[`docs/reviews/GR-082/ports/`](reviews/GR-082/ports/); VectorCraft requires
rebuild/retest but no adapter source port was identified. Every app remains a
candidate, not a promoted route. Current bounded qualification:

| App | Source patch / checks | Still open |
|---|---|---|
| WordCraft v0.11.0 | Exact-base apply, locked WASM, engine 2/2 and UI 9/9 tests, release bundle, and actual-WASM synthetic memory-host edit/save/new-version/ACK/fresh-reopen smoke pass; copied reopened-editor text contains the marker. R9 records the test-source hash and hashes of the actual served files before and after the run. | Seafile version/history/readback/fresh reopen; browser refusal counts for replacement/Save As. |
| GridCraft v0.12.1 | Exact-base apply, local transport checksums, locked WASM check, and host engine 3/3 and UI 2/2 tests pass. The optimized release bundle and actual-WASM synthetic memory-host active-cell Ctrl+S/version/ACK/fresh-reopen smoke pass; R4 records actual served-file hashes before/after. Final patch includes native `.xlsx` name/content admission after the first test exposed generic text-open acceptance. | Seafile version/history/readback/fresh reopen and browser refusal counts for replacement/Save As. |
| PdfCraft v0.14.0 | Ported durable ACK patch; exact-base apply and local transport checksums pass. Locked WASM and 30 `editing::` tests pass; optimized release bundle and actual-WASM synthetic memory-host edit/save/ACK/fresh-iframe reopen pass, with the edited field visible in the retained capture. | Seafile workflow and replacement-refusal counts. Uses the legacy ticket protocol, not identity binding. |
| VectorCraft v0.17.0 | No adapter source port identified; locked WASM check and optimized release build pass. R2 actual-WASM page-API smoke captures, saves and reopens the edited SVG in a fresh browser using isolated memory storage; served asset hashes match the bundle. | Seafile version/readback/fresh reopen; Ctrl+S/menu-export dirty-marker and native host ACK behavior; broader format regressions. |
| PhotoCraft v0.16.0 | Exact-base apply and packaged transport checksums pass; optimized release bundle passes. Final-tree focused Web 6/6 and UI 8/8 host tests pass. Actual-WASM memory-host smoke creates a layer, Ctrl+S saves 6,890 bytes, ticketed ACK marks it clean, and a fresh editor iframe reopens the same native identity; no download. | Engine snapshot suite; Seafile version/history/readback/fresh reopen and gateway identity-mode enablement. The missing optional font manifest returns the expected 404. |

The R1–R3 pre-push reviews and responses are retained in the review bundle; R3’s served-file provenance finding was addressed by R9. R4 returned bounded PROVISIONAL PASS for a commit and branch-only push to
this repository; GridCraft release-evidence R1 returned one LOW queue-wording finding; R2
verified its correction with no new findings. PdfCraft release-evidence R1's two
LOW findings were addressed; R2 returned bounded PROVISIONAL PASS. These reviews
do not close Seafile or project GPT gates. The complete snapshot review R1's
duplicate-matrix finding was fixed; R2 returned bounded PROVISIONAL PASS. The
R1 port review and R2 independent
app-port findings are also retained. Final evidence includes retained
WordCraft/GridCraft logs, PdfCraft's 30 editing regression passes (including its 8 ACK tests), optimized bundle and actual-WASM memory-host edit/save/ACK/fresh-reopen smoke, PhotoCraft final-tree Web 6/6 and UI 8/8 focused host tests, its optimized release and actual-WASM memory-host save/ACK/fresh-iframe reopen smoke, and VectorCraft's optimized bundle and actual-WASM page-API capture/save/fresh-browser reopen smoke. PhotoCraft's engine snapshot suite remains **NOT VERIFIED**; its earlier 19-test result is only pre-local-path historical evidence. R2's
source-port findings have a response. The source/app-port R3 review returned a
bounded PROVISIONAL PASS with one LOW manifest-status finding; that field and
overlapping test-count wording were corrected and recorded. Separately,
PhotoCraft/VectorCraft release-smoke reviews R1–R3 returned bounded PROVISIONAL
PASS after two R1 and one R2 LOW documentation findings were corrected.
The final snapshot R4 found a duplicate VectorCraft test-matrix row; it was
consolidated and R5 returned bounded PROVISIONAL PASS.
Free-model reviews remain PROVISIONAL. See
[`docs/reviews/GR-082/README.md`](reviews/GR-082/README.md).

## Automatic maintenance

The read-only stable-release scanner is
[`scripts/check-artcraft-releases.py`](../scripts/check-artcraft-releases.py),
driven by [`integration/config/artcraft-upstream.json`](../integration/config/artcraft-upstream.json).
It resolves the latest non-prerelease release returned by GitHub's
`/releases/latest` endpoint to a commit and reports ahead/behind counts against
the qualified upstream source pin. It never changes source or pins. The scanner
retries transient request failures twice with bounded backoff and
`Retry-After` handling; every HTTP 5xx code is retryable, and 403 is retried
only when rate-limit headers indicate throttling. An unresolved `unknown` marks the scan incomplete and
cannot be treated as no drift. Candidate records are retained by app plus full
release SHA; per-app current pointers do not replace or delete prior records.
Candidate identities and progress are retained in
[`docs/reviews/GR-082/release-candidate-state.json`](reviews/GR-082/release-candidate-state.json).
The first run is retained at
[`docs/reviews/GR-082/upstream-scan-20261027.json`](reviews/GR-082/upstream-scan-20261027.json).
That first run was partial. A fresh scan on 2026-10-27T16:06:51Z completed for
all five apps with exit 0 and retained valid `merge_base_commit` values; it
found no release change. See
[`upstream-scan-20261027T160651Z.json`](reviews/GR-082/upstream-scan-20261027T160651Z.json).

A weekly T3 maintainer was configured with a 7-day interval (next run would
have been 2026-11-03 09:17:46 UTC). The user requested a project pause for
transport, so the task was disabled on 2026-10-28; `nextRunAt` is null. The
disabled state is retained in
[`docs/reviews/GR-082/scheduler-pause-20261028.json`](reviews/GR-082/scheduler-pause-20261028.json).
When re-enabled, its live prompt resumes incomplete work without a manual
trigger, treats unknown scans as incomplete, and deduplicates candidates by
app and full release SHA. It starts separate `upstream-refresh/` candidates
when later release drift appears. After candidate checks and independent review
it may commit and push that reviewable branch to this project's origin; it does
not open a PR or merge. It must not promote routes, alter Seafile or ONLYOFFICE,
push to ArtCraft upstream repositories, open upstream issues/PRs/RFCs, or skip app tests,
browser checks, synthetic Seafile version/readback/reopen, and independent
review. If a gate cannot run, the task must mark it **NOT VERIFIED**. It had
not run unattended before the pause; unattended execution remains
**NOT VERIFIED**.
The complete live prompt and update response are retained in
[`scheduler-prompt-20261027.md`](reviews/GR-082/scheduler-prompt-20261027.md)
and
[`scheduler-prompt-update-response-20261027.json`](reviews/GR-082/scheduler-prompt-update-response-20261027.json).
The cadence/status snapshot is
[`scheduler-configuration-20261027.json`](reviews/GR-082/scheduler-configuration-20261027.json).
