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

All checkouts and code changes are under `/tmp/artcraft-gr016-*`; they are not
commits or branches in the upstream repositories. App manifests currently use a
local path to the scratch `craft-platform` checkout solely to make these checks
reproducible. That path must be replaced by a coordinated, real git revision
before any patch series can be considered applicable.

The exact scratch diffs are preserved in [`patches/`](patches/):
`craft-libs-shared-transport.patch`, `wordcraft-shared-transport.patch`, and
`gridcraft-shared-transport.patch`. The app diffs include their pre-existing
lab GR-014/GR-010 bridge patches before the common transport refactor. They are
review artifacts with a temporary `/tmp` path dependency, not ready-to-apply
upstream patches.

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

1. **No Seafile E2E was run on these refactored adapters.** The browser tests
   above use `sessionStorage`; previous synthetic Seafile evidence is against
   prior app bridge patches, not this transport refactor. Re-run the Seafile
   workflow before claiming that the shared transport is wired to Seafile.
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
5. The configured Nemotron review lane was interrupted after an extended run
   without a result. A fresh independent GPT-6.1 Sol low review of this bounded
   remediation returned provisional PASS with three minor findings. The first
   same-model Luna review remains a provisional FAIL in the history and is not
   counted as independent. Full report:
   [`REVIEW-SOL-LOW-R3.md`](REVIEW-SOL-LOW-R3.md).
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
