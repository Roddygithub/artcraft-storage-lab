# GR-016 — Shared Rust host transport prototype

Status: **PROTOTYPE / NOT UPSTREAM-READY / NOT A GPT CANDIDATE.** The root
repository's candidate SHA remains the last frozen review history; this work is
a local experiment in scratch clones, plus the source audit record and browser
evidence.
No ArtCraft upstream repo, public Seafile instance, production service, or
upstream issue/PR was changed.

## Scope

The first slice tests one reusable browser transport in `craft-platform`, then
adapts the already existing WordCraft and GridCraft host seams to it. The shared
part owns same-origin parent/source validation, lifecycle-managed event
listeners, `postMessage` byte transfer, opaque string tickets, and bounded
pending-save bookkeeping. Each app keeps its own serializer, dirty state, and
saved-document snapshot rules.

The app sources were checked out at:

| Repository | SHA | Patch applied before common-transport refactor |
|---|---|---|
| `storytold/craft-libs` | `f180fc0d35d521c5d18e118c881d3efde1ec1eee` | none |
| `storytold/wordcraft` | `00bc6a4b028013b2dfb0e85e8b326aeed3ecff6d` | existing lab GR-014 bridge patch |
| `storytold/gridcraft` | `06920de8da609c19de7446945cfc62b844691efd` | existing lab GR-010 durable-ack patch |

All app checkouts and code changes are under `/tmp/artcraft-gr016-*`; they are
not commits or branches in the upstream repositories. The GR-016 `craft-platform`
source snapshot is now packaged independently at
[`integration/rust/craft-platform`](../../../integration/rust/craft-platform),
based on `craft-libs` SHA `f180fc0d35d521c5d18e118c881d3efde1ec1eee` plus the
recorded GR-016 working-tree changes. A minimal root Cargo workspace exposes
the nested package for later git dependencies without inheriting crate settings.
Its standalone metadata, native tests and
WASM browser feature can be checked with
[`scripts/check-craft-platform.sh`](../../../scripts/check-craft-platform.sh).
GPT-6.1 Sol low independently reviewed the package with no blocker/major; its
minor lockfile finding was fixed by adding `--locked` to metadata. See
[`REVIEW-PORTABLE-CRAFT-PLATFORM-20261024.md`](REVIEW-PORTABLE-CRAFT-PLATFORM-20261024.md).

The WordCraft and GridCraft patch manifests now pin the packaged transport to
the immutable repository revision `90c261de22ef75c4c7c5c5cd1c712d483be0bbc8`.
Both patches were applied to clean checkouts and passed Rust 1.95 WASM checks
with `--locked`. Exact patch hashes and commands are recorded in
[`PORTABLE-APP-PATCHES-20261024.md`](PORTABLE-APP-PATCHES-20261024.md).

The exact scratch diffs are preserved in [`patches/`](patches/):
`craft-libs-shared-transport.patch`, `wordcraft-shared-transport.patch`, and
`gridcraft-shared-transport.patch`. The app diffs include their pre-existing
lab GR-014/GR-010 bridge patches before the common transport refactor. They are
review artifacts with a pinned dependency on this repository; this verifies
build reproducibility, not upstream readiness or the remaining app integrations.

## Behavior preserved by the adapters

- **WordCraft:** app `AsyncSaves` keeps its own internal numeric ticket; the
  bridge maps it to an opaque `wordcraft:<id>` wire ticket. Unknown or duplicate
  acknowledgements are ignored. An app save is completed only after a matching
  host `saveResult`; serialization and editor dirty behavior remain in the
  existing WordCraft code. The current `Services.download` hook does not expose
  Save As, so this adapter sends `saveAs=false`; host-driven Save As semantics
  remain unresolved.
- **GridCraft:** each save keeps its original `(document uid, immutable workbook
  snapshot)` association. The source workbook becomes clean only on the matching
  successful host result. Export requests without a source snapshot cannot mark
  the workbook clean. Failed saves retain dirty state and display an error. Its
  `open_async` hook now sends `gridcraft:openRequest` so the parent can supply
  the selected workbook rather than invoking the browser picker.
- Both adapters use the same strict parent origin and `event.source` checks. The
  shared helper rejects nonmatching origins/sources and owns removal of the
  browser listener when its adapter is dropped.
- The shared pending-save table rejects duplicate tickets and refuses more than
  64 outstanding requests; the editor remains dirty when a new request cannot
  be tracked.

## Reproduced checks

Executed on 2026-10-24 with Rust/Cargo 1.97 and target
`wasm32-unknown-unknown`:

| Command | Result |
|---|---|
| `cargo test -p craft-platform` | PASS — 6 tests, including 4 host-protocol tests |
| `cargo clippy -p craft-platform --all-targets -- -D warnings` | PASS |
| `cargo check -p craft-platform --features browser --target wasm32-unknown-unknown` | PASS |
| `cargo check -p wordcraft-web --target wasm32-unknown-unknown` | PASS |
| `cargo check -p gridcraft-web --target wasm32-unknown-unknown` | PASS; one existing dead-code warning in `gridcraft-ui-egui::backstage::Modified` |
| `cargo +1.95.0 check -p gridcraft-web --target wasm32-unknown-unknown` | PASS after the GridCraft Rust-version bump; same existing warning |
| `cargo +1.95.0 fmt --all -- --check` in GridCraft | PASS |
| `trunk build --release` in WordCraft Web | PASS; built bundle loaded in Chromium/SwiftShader |
| `trunk build --release --minify false` in GridCraft Web on Rust 1.95 | PASS; rebuilt bundle loaded in Chromium/SwiftShader |
| `git apply --reverse --check` for all three preserved patch files | PASS against the corresponding modified scratch checkouts |

The first GridCraft compile caught a generic `Default` bound in the shared
pending-save type; the implementation was fixed with a manual `Default` and the
WASM check then passed. The first WordCraft test command mistakenly attempted
to run `craft-platform` tests as a nonmember of the app workspace; the tests
were rerun successfully in the `craft-libs` checkout above.

### Synthetic-host browser smoke tests

Both release bundles were served from local static HTTP servers and run in the
collaborative Chromium preview on 2026-10-24. Each parent harness used a
synthetic fixture and `sessionStorage` as its fake durable store; it accepted a
save only after writing the serialized bytes, then sent the matching
`saveResult`. This is browser/runtime evidence for the transport adapters, not
Seafile persistence or a production topology.

| App | Browser flow and checks |
|---|---|
| WordCraft | Opened `tests/fixtures/synthetic.docx`; typed `GR016HostAck`; observed `dirty=true`; Ctrl+S sent serialized DOCX; parent stored 5,287 bytes and acknowledged; editor became clean. A fresh iframe reopened the stored DOCX and rendered `GR016HostAck`. The extracted DOCX passes `unzip -t`; `word/document.xml` contains the edit. A second edit followed by a synthetic rejection surfaced the error and left the editor dirty. SHA-256: `bb2ac3a46dc234027049a7c6aeae9f18f9c26614007a565fed05b2c5c94d0f7f`. |
| GridCraft | Opened `tests/fixtures/synthetic.xlsx`; changed cell A1 to `HostAck`; observed `dirty=true`; Ctrl+S sent 4,132 bytes and the parent acknowledged; the source became clean. A fresh iframe reopened the stored workbook and displayed `HostAck`. The extracted XLSX passes `unzip -t`, retains the `SUM(B2:B2)` formula and cached value 42. A second edit followed by rejection displayed the host error and left the workbook edited/dirty. SHA-256: `2a53ca82774d961462b5125bc2ddf0772c6ba3c71c801376d8a9042c260c136c`. |

### WordCraft and GridCraft shared transport through synthetic Seafile

On 2026-10-24, the WordCraft GR-016 adapter was built from its pinned scratch
checkout and loaded through the real synthetic Seahub file route and local
Seafile gateway. The operator edited `synthetic.docx`, WordCraft showed dirty,
Ctrl+S produced a new Seafile head/file ID and history entry, and WordCraft
returned to Saved. An API download was a valid DOCX containing the edit; after
the editor was unloaded, a fresh Seahub file-list open rendered the edit. Full
IDs, hashes, build mode, and limits are in
[`SEAFILE-WORDCRAFT-SHARED-TRANSPORT-E2E-20261024.md`](SEAFILE-WORDCRAFT-SHARED-TRANSPORT-E2E-20261024.md).

The WordCraft and GridCraft shared-transport adapters have both now completed
synthetic Seafile save-version-reopen runs. GridCraft changed A1 and reopened
with the edit, then changed B2 from 42 to 1337 and verified that B3's
`SUM(B2:B2)` recalculated, was saved as a new version, and reopened at 1337.
The editor-to-gateway save-message bytes were not independently hashed. Both
functional release builds used scratch `data-wasm-opt="0"`; the optional
`wasm-opt -Oz` pass and production bundle performance remain unverified. No
production service, ONLYOFFICE setting, or upstream repository was changed.

After the first review, GridCraft's `open_async` adapter was changed to send an
`openRequest` to the parent. On the Rust 1.95 release bundle, Ctrl+O in the
editor produced one host request; the harness returned stored workbook bytes
and the fresh GridCraft view displayed the persisted `HostAck` edit. Screenshot:
[`runtime/gridcraft-in-app-open.png`](runtime/gridcraft-in-app-open.png). The
GridCraft WASM bundle SHA-256 was
`89912b61067952cc2206bbde9e164e90e883ad2e08a348979141e9609bcd6c3f`.

The reusable harnesses are in [`runtime/wordcraft-host.html`](runtime/wordcraft-host.html)
and [`runtime/gridcraft-host.html`](runtime/gridcraft-host.html). To rerun after
building the corresponding app bundle, place the HTML file and the existing
synthetic fixture beside the built `index.html` as `host-test.html` and
`synthetic.docx` / `synthetic.xlsx`, then serve that directory over HTTP. Open
`/host-test.html`, edit inside the app, and use Ctrl+S. The harness used only a
same-origin local iframe; it does not exercise cross-origin production
deployment, Seafile API authorization/versioning, network interruption, or real
concurrent writers. Extracted output files from this run remain under `/tmp`.

## Open issues before broader adoption

1. WordCraft and GridCraft now both have bounded synthetic Seafile E2E evidence
   after the shared-transport refactor. One GridCraft `SUM(B2:B2)` formula was
   recalculated after B2 changed from 42 to 1337 and verified after Seafile
   save/reopen; broader formula compatibility remains NOT VERIFIED. Concurrent
   external writes, public security controls, and runtime authorization edge
   cases remain NOT VERIFIED.
2. **GridCraft MSRV:** the audited base declared Rust 1.90, while the current
   dependency graph requires 1.95. A Rust 1.90 WASM check failed on those
   dependency MSRV declarations; the scratch patch raises GridCraft to 1.95 and
   its WASM check and release bundle build pass on 1.95. Sol low reviewed this
   compatibility correction as part of the bounded remediation review.
3. **Only WordCraft and GridCraft are adapted.** The app audit matrix explains
   why remaining bridges cannot be handled by copying these adapters. In
   particular, some apps lack host-driven open, some serialize projects with
   assets, and several mark clean synchronously after a download or browser
   storage write.
4. The tests do not yet exercise wrong-source browser events, listener teardown,
   timeout/retry, concurrent saves within one app, permission revocation, or
   response loss.
5. The earlier configured Nemotron remediation lane was interrupted after an
   extended run without a result. A separate free Nemotron evidence review
   accepted the WordCraft runtime record with minor qualifications; the supplied
   numeric metadata was independently corrected against Seafile. GridCraft is
   outside that review scope. See `REVIEW-NEMOTRON-E2E-20261024.md`. A fresh
   independent GPT-6.1 Sol low review of the bounded GridCraft Open/MSRV/ack
   remediation returned provisional PASS with three minor findings. The first
   same-model Luna review remains a provisional FAIL in the history and is not
   counted as independent. Full report:
   [`REVIEW-SOL-LOW-R3.md`](REVIEW-SOL-LOW-R3.md).
   The combined WordCraft/GridCraft E2E evidence review first returned
   PROVISIONAL FAIL on payload-hash, formula-recalculation and optimizer gaps.
   A follow-up runtime save/reopen exercised the formula; Nemotron's second
   round accepted the bounded evidence with minor qualifications. The payload
   hash and optimized bundle remain open limitations. Reports:
   [`REVIEW-NEMOTRON-GRIDCRAFT-E2E-20261024.md`](REVIEW-NEMOTRON-GRIDCRAFT-E2E-20261024.md)
   and
   [`REVIEW-NEMOTRON-GRIDCRAFT-E2E-R2-20261024.md`](REVIEW-NEMOTRON-GRIDCRAFT-E2E-R2-20261024.md).
6. The gateway's editing session is scoped to the single file selected in
   Seahub. It handles an app `openRequest` by telling the user to return to
   Seafile and select another document; it does not browse the library or
   reuse the current file capability for another path. A T3 Chromium preview
   with a synthetic same-origin frame verified the message and that dirty state
   stays set. A Seafile-backed file picker remains a separate,
   authorization-sensitive feature.

See [`APP-SEAM-AUDITS-20261024.md`](APP-SEAM-AUDITS-20261024.md) for the full
13-app source seam inventory. These audits are evidence for planning, not proof
that the general Seafile/Nextcloud/ownCloud integration already works.

## Adversarial review feedback

The first bounded review used a separate task but the same GPT-6 Luna model as
the implementation owner, so it is **not counted as an independent free
review** under the repository policy. It returned **FAIL** and found that GridCraft's host
adapter did not replace `Services::open_async`, so the in-app Open action still
used the browser picker instead of requesting a file from the parent. The
adapter now sends `gridcraft:openRequest`; a release-bundle Chromium retest
observed the request, returned the stored fixture bytes, and rendered the saved
`HostAck` edit.

The reviewer also flagged the declared GridCraft Rust 1.90 MSRV versus
`craft-libs` 1.95. A direct Rust 1.90 WASM check confirmed the current GridCraft
dependency graph is already marked incompatible: `craft-ui` and egui 0.36.2
components require 1.95. The scratch GridCraft manifest now declares 1.95; a
full Rust 1.95 WASM check and release bundle build passed. This is a proposed
compatibility correction in the scratch patch, not an upstream change; the
original declaration was not validated by a successful Rust 1.90 build.

The review also noted that unknown acknowledgements could accumulate in
GridCraft's results queue and a synchronous `postMessage` failure was only
logged. The adapter now consumes only matching pending tickets when the browser
event arrives, bounding queued acknowledgements by the 64-pending-save limit;
immediate send failures are queued for a visible app error. The build and
in-app Open browser check passed. GPT-6.1 Sol low independently returned a
provisional PASS with no blockers/majors and three minor notes; see
`REVIEW-SOL-LOW-R3.md`.

The bounded independent GPT-6.1 Sol low review passed with minor findings. This
is not the final Sol candidate review; Seafile E2E and all other-app adapters
remain open.
