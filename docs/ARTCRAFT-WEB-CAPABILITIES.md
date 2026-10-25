# ArtCraft Web / WASM / host-bridge capability matrix

Status: **PROVISIONAL — upstream capability inventory** · GPT REVIEW: FAIL on frozen candidate `0edbe524`; current remediation tip is not frozen or reviewed
GR-003 · Inspected 2026-10-22 against the live `storytold/*` repositories on `main`

> **Follow-up correction (2026-10-24):** the app seams were re-inspected at pinned
> revisions for GR-016. That report supersedes stale capability claims below,
> especially the statements that FigCraft has only `NoServices`, that FilmCraft
> has no host-callable open API, and that LightCraft's browser-local library is a
> document host bridge. See
> [`APP-SEAM-AUDITS-20261024.md`](reviews/GR-016/APP-SEAM-AUDITS-20261024.md).

## 0. Evidence base

* Repositories: the 13 `storytold/*` apps and `storytold/craft-libs`, cloned read-only
  (shallow) into a scratch directory. **No issue, no PR, no comment, no fork.**
* Method: the GitHub contents API and `raw.githubusercontent.com` for the survey, then a
  full clone for the per-app source reading.
* The baseline audit `~/ArtCraft-Audit.md` was read as input evidence. **It is about the
  AUR desktop packages and is silent about the browser builds** — the silence is the
  single most consequential finding of this phase.

| App | Commit inspected | Web build dir | Build command | Licence |
| --- | --- | --- | --- | --- |
| wordcraft | `00bc6a4b028013b2dfb0e85e8b326aeed3ecff6d` | `apps/wordcraft-web` | `trunk build --release` | MIT OR Apache-2.0 |
| gridcraft | `main` | `apps/gridcraft-web` | `trunk build --release` | MIT OR Apache-2.0 |
| deckcraft | `main` | `apps/deckcraft-web` | `trunk build --release` | MIT OR Apache-2.0 |
| pdfcraft | `main` | `apps/pdfcraft-web` | `trunk build --release` | MIT OR Apache-2.0 |
| vectorcraft | `main` | `apps/vectorcraft-web` | `trunk build --release` | MIT OR Apache-2.0 |
| photocraft | `main` | `apps/photocraft-web` (+ `photocraft-web-boot`) | `trunk build --release` | MIT OR Apache-2.0 |
| figcraft | `main` | `apps/figcraft-web` (+ `figcraft-server`) | `trunk build --release` | MIT OR Apache-2.0 |
| designcraft | `main` | `apps/designcraft-web` | `trunk build --release` | MIT OR Apache-2.0 |
| cadcraft | `main` | `apps/cadcraft-web` | `trunk build --release` | MIT OR Apache-2.0 |
| filmcraft | `main` | `apps/filmcraft-web` | `cargo xtask web` | MIT OR Apache-2.0 |
| lightcraft | `main` | `apps/lightcraft-web` | `cargo xtask web` | MIT OR Apache-2.0 |
| effectcraft | `main` | `apps/effectcraft-web` | `cargo xtask web` | MIT OR Apache-2.0 |
| soundcraft | `main` | `apps/soundcraft-web` | `trunk build --release` | MIT OR Apache-2.0 |
| craft-libs | `main` | — | — | MIT OR Apache-2.0 |

**The licence finding closes an open question in `docs/LICENSING.md`: all 13 apps and
`craft-libs` are dual MIT / Apache-2.0, which is exactly this repository's licence.**

## 1. The mandatory matrix

| App | Web build | WASM | Host bridge | Open from host | Save to host | iframe | Origin requirements | Relevant API | Maturity | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **wordcraft** | **yes** | yes (`wasm-bindgen`, `web-sys`, `js-sys`; `wasm32-unknown-unknown` target) | no upstream parent bridge; `Services` has inbox, async open, download, async save outcomes, dirty callback | no upstream bridge | browser download | yes (documented) | same-origin for proposed bridge | `wordcraft_ui_egui::Services`, `async_saves::{AsyncSaves, SaveOutcome}` | alpha | `00bc6a4b`; `crates/ui-egui/src/lib.rs`; local GR-014 adapter |
| **gridcraft** | **yes** | yes | **yes** — `?host=parent`, `postMessage`; baseline lacks durable result | **yes** (`gridcraft:open`) | sends bytes, but upstream clears dirty before host storage result | yes | **same-origin only** (origin *and* source checked; explicit `targetOrigin`) | `gridcraft:ready\|open\|save\|dirty\|failed` | alpha | `06920de8`; `apps/gridcraft-web/src/host.rs`; local GR-010 ack patch |
| **deckcraft** | **yes** | yes | upstream: partial, byte serialization but no JS host bridge; lab GR-020: local ticketed bridge patch | engine open-bytes API; lab patch exposes parent-provided bytes | browser download upstream; host ACK in lab patch | yes (upstream) | same-origin transport in lab patch | `file.openBytes`, `file.saveBytes`, Web `Services` | alpha | `0f4fffcf`; `apps/deckcraft-web/`; `crates/ui-egui/src/lib.rs`; GR-020 is not upstream or Seafile E2E |
| **pdfcraft** | **yes** | yes | **yes** — same-origin `postMessage` bridge; no durable host acknowledgement | **yes** (`pdfcraft:open`) | sends bytes; app marks clean after synchronous handoff | yes | same-origin only | `pdfcraft:ready\|open\|save\|dirty\|failed`; `Services::host_save` | alpha | `57e531cc`; `apps/pdfcraft-web/src/main.rs`; `crates/ui-egui/src/editing.rs` |
| **vectorcraft** | **yes** | yes (also a WASM plug-in sandbox, `wasmi`) | **different shape**: a page-global promise API `window.vectorcraft` (`execute`, `request`, `commands`, `screenshot`, `openFile`, `captureDownloads`, `files`, `readFile`), the desktop control protocol in the page | **yes** (`openFile(name, bytes)`) | **yes** (`captureDownloads(true)` + `files()`) | yes | the page API is same-origin by nature | `window.vectorcraft` (promise API), `docs/control-protocol.md` | alpha | `apps/vectorcraft-web/src/api.rs`; `docs/control-protocol.md` |
| **photocraft** | **yes** (+ `photocraft-web-boot`) | yes | no host bridge found | picker/import only | browser download/unconfirmed write | yes | same-origin for a future bridge | byte import/export; local dirty tracking | alpha | `a02f2ee4`; `apps/photocraft-web/src/web.rs` |
| **figcraft** | **yes** (+ `figcraft-server`) | yes | upstream at `8d790607`: no host bridge; local GR-019 patch adds one | upstream byte-based open; local host patch accepts one `.figcraft` document | upstream browser download; local patch awaits durable host ACK | yes | same-origin parent via shared transport in local patch | `Services`, `file.open`, `FileSnapshot` | pre-alpha | upstream `8d790607`; local patch/evidence: `docs/reviews/GR-019/` |
| **designcraft** | **yes** | yes | upstream: no; local GR-021 prototype uses shared parent transport; exact app patch review pending after transport repin | host-provided native `.designcraft` bytes in local prototype | local ticketed save waits for matching durable ACK; no Seafile E2E | yes | same-origin transport in local prototype | `file.serialize`, `Session::host_save_snapshot`, `HostTransport` | pre-alpha | upstream `80d13911`; GR-021 reports under `docs/reviews/GR-021/`; R1 found transport P2, fixed and independently reviewed; app R2 pending |
| **cadcraft** | **yes** | yes | **yes** — existing parent bridge; optimistic save | **yes** (`cadcraft:open`) | sends save bytes and marks clean on `postMessage` success | yes | same-origin only | `cadcraft:ready\|open\|save\|dirty\|failed` | pre-alpha | `7bf5905a`; `apps/cadcraft-web/src/host.rs` |
| **filmcraft** | **yes** (`cargo xtask web`) | yes | private `window.filmcraft` API, not common bridge | `openProject(fileOrUrl)` | serialized `.fcproj` currently downloads; no durable host result | yes | same-origin API | `openProject`, `ui.inspect`, `Services::write_file` | alpha | `fa550ce2`; `apps/filmcraft-web/src/api.rs`; `crates/engine/src/commands.rs` |
| **lightcraft** | **yes** (`cargo xtask web --serve`) | yes | local photo library, not a document host bridge | picker/drop | browser download export; storage flush not a host save ack | yes | same-origin for a future bridge | `web.stats` is local-library state | alpha | `98702b5c`; `apps/lightcraft-web/src/web.rs` |
| **effectcraft** | **yes** (`cargo xtask web`) | yes | upstream private browser API primitives; local GR-022 ticketed bridge prototype under review | `window.effectcraft.addFile` upstream; local host prototype accepts a single `.ecproj` | local snapshot ACK path; Seafile E2E not run | yes | same-origin shared transport in local prototype | `project.summary`, `Session::host_save_snapshot`, `HostTransport` | alpha | upstream `049070d6`; local patch/tests in `/tmp/effectcraft-audit-049070d` pending review/evidence |
| **soundcraft** | **yes** | yes | partial `DeliverHook`, no parent bridge | picker/bytes path | download via synchronous function-pointer sink | yes | same-origin for future bridge | `.scraftz`, `set_deliver`, `open_session_bytes` | pre-alpha | `d47abe48`; `crates/engine/src/io.rs`; `apps/soundcraft-web/src/web.rs` |

**Reading the table**

The capability descriptions that follow this paragraph under §2 are the
2026-10-22 baseline. If they conflict with the pinned-revision follow-up in
GR-016, use the 2026-10-24 report for current app seams; the baseline remains
for historical context only.

The app rows describe the inspected upstream revisions, not every local patch.
GR-010 and GR-014 add local bridges/save-result handling and have synthetic
Seafile runtime evidence; those changes are not upstream releases.

* **All 13 have a browser build.** Every one runs the *same* application as the desktop
  app, through eframe's web runner (wgpu: WebGPU where available, WebGL2 otherwise).
* **3 of 13 have a host bridge today**: GridCraft, PdfCraft, CADCraft. All three use
  the same `?host=parent` + `postMessage` shape and the same message vocabulary.
* **The 13 are not equivalent.** The seams differ: `Services` with browser hooks
  (wordcraft, gridcraft, deckcraft, vectorcraft, designcraft, photocraft,
  cadcraft, lightcraft, soundcraft), reduced or app-specific APIs (PDF, Vector,
  Film, Effect), and filesystem-oriented serializers. FigCraft has a real
  `Services` trait; LightCraft's current browser storage is a photo library.
* **`wordcraft` is the one with the most complete seam** — `open_async`, `inbox`,
  `download`, `async_saves` and `on_dirty` — which is why it is the right MVP target
  even though it has no bridge yet.

## 2. Per-app findings

The template: what the web build is, what the seam is, what is missing, and the
evidence.

### 2.1 wordcraft — the MVP target

* `apps/wordcraft-web/` — a Trunk build, `eframe` with `wgpu` + `accesskit`,
  `wasm-bindgen`, `wasm-bindgen-futures`, `js-sys`, `web-sys` (the feature list already
  includes `Blob`, `Url`, `HtmlIFrameElement`, `File`, `Storage`, `Idb*`).
* The app is the **same `WordApp`** as the desktop app. The web-specific differences
  are in `apps/wordcraft-web/src/main.rs`: no TCP control channel, the browser file
  picker for Open, and a download for Save.
* The seam (`crates/ui-egui/src/lib.rs:100-190`) is the richest of the suite and
  already has `open_async`, `inbox`, `download`, `async_saves` and `on_dirty`.
* **Missing:** the bridge. **Added by our patch** — see `docs/reviews/GR-014/`.

### 2.2 gridcraft — the reference bridge

`apps/gridcraft-web/src/host.rs` (166 lines) is the cleanest reference:

* `?host=parent` selects the mode; `?author=` names the user.
* `gridcraft:ready` / `:open` / `:save` / `:dirty` / `:failed`.
* The origin **and** the source window are checked on every incoming message; the
  outgoing `targetOrigin` is the page's own origin, never `"*"`.
* **Upstream baseline save is optimistic**: `Services::download` has the type
  `Fn(&str, &[u8])` — **no `Result`** — so a failed `postMessage` is only logged and
  the workbook is still marked saved. The local GR-010 patch adds ticketed durable
  acknowledgements and has an isolated synthetic Seafile edit/save/reopen runtime
  proof; formula recalculation, conflicts and upstream adoption remain open.

### 2.3 pdfcraft — the reference for a save that can fail

`apps/pdfcraft-web/src/main.rs:135-260` has the same vocabulary plus `saveAs`, and
`Services::host_save` is `Fn(&str, &[u8], bool) -> Result<(), String>`: a **synchronous**
result, so the app knows a save failed and does not mark the document saved. The
bridge also refuses to exist when the parent is on another origin, and says why:
*"messages only go to this origin, so the browser would drop every save without an
error while the document showed as saved"*.

### 2.4 cadcraft — a third implementation of the same shape

`apps/cadcraft-web/src/host.rs`, same vocabulary, and the doc comment says the save
*"replaces the engine's delivery hook"* — CADCraft does not use the `Services`
struct for it.

### 2.5 vectorcraft — a different, larger surface

`apps/vectorcraft-web/src/api.rs` exposes `window.vectorcraft`, a promise API that is
the **desktop control protocol** (`docs/control-protocol.md`) in the page: engine
commands, UI inspection, synthetic input, screenshots, `openFile`, `captureDownloads`,
`files`, `readFile`.

It is powerful and it is aimed at an agent driving a tab, not at a host platform
embedding an editor. It also carries a much larger security cost: it can execute
arbitrary engine commands. **Recommendation: the host contract is the
`?host=parent` bridge, not this API** (`docs/HOST-CONTRACT.md` §6). The control
protocol stays relevant for QA automation.

### 2.6 The nine without a bridge

deckcraft, photocraft, figcraft, designcraft, filmcraft, lightcraft, effectcraft,
soundcraft — and wordcraft, which we are patching.

For each, the seam differs (see the table). Two of them (`figcraft`, and the
`FsServices` pair `filmcraft`/`effectcraft`) do not have a browser-shaped seam at
all, so "porting the bridge" is not a copy-paste job for them.

## 3. Is there already a common host abstraction?

`storytold/craft-libs` (MIT OR Apache-2.0) holds the code that must be identical
across the apps:

```text
crates/ai-core  atomic  cms  docpath  i18n  media  pdf  print  quit  settings  ui  window
```

* `crates/ui` — buttons, docking, icons, layout, printing, tabs, theme: a shared
  **widget** crate.
* `crates/window` — the window-frame policy (desktop).
* `crates/quit` — the close handling.
* `crates/docpath`, `crates/print`, `crates/settings`, `crates/i18n`, `crates/cms`,
  `crates/media`, `crates/atomic`, `crates/ai-core`, `crates/pdf`.

**There is no host, embedding or bridge crate.** Nothing equivalent to a host
contract exists today, so creating one is justified — and `craft-libs` is where the
suite puts code that must be identical across apps.

## 4. The other protocol that exists

`docs/control-protocol.md` is present in **12 of 13** apps (all but PdfCraft). It is a
line-delimited JSON protocol over a **loopback TCP port**, with a 256-bit key written
to a file, used by `<app>-cli mcp --connect` and by the desktop control server.

It is a well-designed protocol, and it is **not** the browser contract: a browser
cannot open a TCP socket. VectorCraft is the only app that ports it to the page
(`window.vectorcraft`).

It remains relevant for **QA automation** of the browser build — the mission's §48 —
and for the MCP servers.

## 5. Browser constraints a Rust→WASM host faces

From `packaging/web/README.md` (present in all 13):

* the site is **static**; there is no server-side code;
* `.wasm` **must** be served as `application/wasm`;
* gzip/Brotli on `.wasm` (13 MB → 5 MB);
* **HTTPS** for WebGPU and the clipboard; over plain HTTP the app falls back to
  WebGL2;
* **no COOP/COEP needed** — no `SharedArrayBuffer`;
* **cross-origin embeds work** for the app itself; only the *bridge* is same-origin;
* a sandboxed iframe needs `allow-scripts allow-same-origin allow-downloads
  allow-popups`;
* `X-Frame-Options: DENY` and a `frame-ancestors` CSP must not exclude the host page.

## 6. The recommendation

1. **WordCraft is the MVP already exercised.** It has the richest seam, and the
   local bridge has an isolated synthetic Seafile open/edit/save/reopen proof.
   Continue app-by-app through the other Craft editors; this does not complete the
   full suite.
2. **The contract is the `?host=parent` bridge**, generalised from the three existing
   implementations, with **one addition**: the host must be able to tell the app
   how a save ended (`docs/HOST-CONTRACT.md` §3.7).
3. **The common code belongs in `craft-libs`**, in a new crate, so the 13 apps do not
   grow 13 drifting copies of the bridge — which is what has already happened with
   the three that exist.
4. **VectorCraft's page API stays out of the host contract**; it is an automation
   surface, not an embedding one.

## 7. Open questions

| # | Question |
| --- | --- |
| Q-1 | What host-save seam remains in apps whose browser `Services` are picker/download-only? FigCraft has a local GR-019 adapter; FilmCraft and EffectCraft also have bounded local host-save prototypes (GR-022/023). Their browser/Seafile persistence remains unverified. |
| Q-2 | Do the `?host=parent` bridges in GridCraft, PdfCraft and CADCraft differ in any way beyond the save semantics? (A line-by-line diff of the three is the natural next step.) |
| Q-3 | What is `photocraft-web-boot` and `figcraft-server`? `figcraft-server` is a hosted-server precedent worth understanding. |
| Q-4 | Are any of the web builds deployed publicly (a profile comment mentions Cloudflare Pages)? If so, their origin matters for the embedding model. |
| Q-5 | Do the three apps that build with `cargo xtask web` produce the same static site shape as the Trunk ones? (The deployment recipe assumes Trunk's `index.html` + hashed assets.) |
