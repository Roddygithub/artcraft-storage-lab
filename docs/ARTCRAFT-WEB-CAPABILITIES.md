# ArtCraft Web / WASM / host-bridge capability matrix

Status: **PROVISIONAL — upstream capability inventory** · GPT REVIEW: FAIL on frozen candidate `0edbe524`; current remediation tip is not frozen or reviewed
GR-003 · Inspected 2026-10-22 against the live `storytold/*` repositories on `main`

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
| **wordcraft** | **yes** | yes (`wasm-bindgen`, `web-sys`, `js-sys`; `wasm32-unknown-unknown` target) | **none** — but the `Services` seam has every hook needed (`open_async`, `inbox`, `download`, `async_saves`, `on_dirty`) | no | no | yes (documented) | same-origin for the bridge | `wordcraft_ui_egui::Services`, `async_saves::{AsyncSaves, SaveOutcome}` | alpha, ~60 % ready | `apps/wordcraft-web/{Cargo.toml,Trunk.toml,index.html,src/main.rs,src/web.rs}`; `crates/ui-egui/src/lib.rs:100-190`; `crates/ui-egui/src/async_saves.rs` |
| **gridcraft** | **yes** | yes | **yes** — `?host=parent`, `postMessage` | **yes** (`gridcraft:open`) | **yes** (`gridcraft:save`) | yes | **same-origin only** (origin *and* source checked; explicit `targetOrigin`) | `gridcraft:ready\|open\|save\|dirty\|failed` | alpha | `apps/gridcraft-web/src/host.rs` (166 lines); `apps/gridcraft-web/src/web.rs:39-41`; `crates/ui-egui/src/lib.rs:195-196` |
| **deckcraft** | **yes** | yes | none | no | no | yes (documented) | same-origin for a bridge | `deckcraft_ui_egui::Services` (`open_async`, `inbox`, `download` present) | alpha | `apps/deckcraft-web/`; `crates/ui-egui/src/lib.rs` |
| **pdfcraft** | **yes** | yes | **yes** — `?host=parent`, `postMessage` | **yes** (`pdfcraft:open`) | **yes** (`pdfcraft:save`, with `saveAs`) | yes | **same-origin only** (the bridge refuses a parent on another origin) | `pdfcraft:ready\|open\|save\|dirty\|failed`; `Services::host_save` | alpha | `apps/pdfcraft-web/src/main.rs:135-260` (`mod host`); `crates/ui-egui/src/lib.rs:630-636`; `crates/ui-egui/src/editing.rs:670-685` |
| **vectorcraft** | **yes** | yes (also a WASM plug-in sandbox, `wasmi`) | **different shape**: a page-global promise API `window.vectorcraft` (`execute`, `request`, `commands`, `screenshot`, `openFile`, `captureDownloads`, `files`, `readFile`), the desktop control protocol in the page | **yes** (`openFile(name, bytes)`) | **yes** (`captureDownloads(true)` + `files()`) | yes | the page API is same-origin by nature | `window.vectorcraft` (promise API), `docs/control-protocol.md` | alpha | `apps/vectorcraft-web/src/api.rs`; `docs/control-protocol.md` |
| **photocraft** | **yes** (+ `photocraft-web-boot`) | yes | none | no | no | yes | same-origin for a bridge | `Services` present, `inbox` present, **no `download`** | alpha, ~45 % | `apps/photocraft-web/`; `crates/ui-egui/src/lib.rs` |
| **figcraft** | **yes** (+ `figcraft-server`) | yes | none | no | no | yes | same-origin for a bridge | `NoServices` — a **placeholder**, no services at all | pre-alpha | `crates/ui-egui/src/lib.rs:382`; `apps/figcraft-server/` |
| **designcraft** | **yes** | yes | none | no | no | yes | same-origin for a bridge | `Services` with `open_async`, `inbox`, `download`; **no `async_saves`** | pre-alpha | `apps/designcraft-web/`; `crates/ui-egui/src/lib.rs` |
| **cadcraft** | **yes** | yes | **yes** — `?host=parent`, `postMessage` | **yes** (`cadcraft:open`) | **yes** (`cadcraft:save`) | yes | **same-origin only** | `cadcraft:ready\|open\|save\|dirty\|failed`; the save "replaces the engine's delivery hook" | pre-alpha, 38 % | `apps/cadcraft-web/src/host.rs`; `apps/cadcraft-web/src/main.rs` |
| **filmcraft** | **yes** (`cargo xtask web`) | yes | none | no | no | yes | same-origin for a bridge | `FsServices` in `crates/engine/src/lib.rs:161` — a **filesystem** shape, not a browser one | alpha | `apps/filmcraft-web/`; `docs/web.md` |
| **lightcraft** | **yes** (`cargo xtask web --serve`) | yes | none | no | no | yes | same-origin for a bridge | `Services` present; **no `open_async`/`inbox`/`download`** | alpha | `apps/lightcraft-web/`; `docs/web.md` |
| **effectcraft** | **yes** (`cargo xtask web`) | yes | none | no | no | yes | same-origin for a bridge | `FsServices` in `crates/engine/src/lib.rs:138` | alpha | `apps/effectcraft-web/`; `docs/web.md` |
| **soundcraft** | **yes** | yes | none | no | no | yes | same-origin for a bridge | `Services` present; **no `open_async`/`inbox`/`download`** | pre-alpha | `apps/soundcraft-web/`; `crates/ui-egui/src/lib.rs` |

**Reading the table**

The app rows describe the inspected upstream revisions, not every local patch.
GR-010 and GR-014 add local bridges/save-result handling and have synthetic
Seafile runtime evidence; those changes are not upstream releases.

* **All 13 have a browser build.** Every one runs the *same* application as the desktop
  app, through eframe's web runner (wgpu: WebGPU where available, WebGL2 otherwise).
* **3 of 13 have a host bridge today**: GridCraft, PdfCraft, CADCraft. All three use
  the same `?host=parent` + `postMessage` shape and the same message vocabulary.
* **The 13 are not equivalent.** The seams differ: `Services` with browser hooks
  (wordcraft, gridcraft, deckcraft, vectorcraft, designcraft, photocraft,
  cadcraft, lightcraft, soundcraft), a reduced one (pdfcraft: `inbox` + `host_save`
  only), a placeholder (`figcraft`: `NoServices`) and a filesystem shape
  (filmcraft, effectcraft: `FsServices`).
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
| Q-1 | Where exactly is the seam in the nine apps without a browser-shaped `Services`? (`figcraft`: `NoServices`; `filmcraft`/`effectcraft`: `FsServices`.) |
| Q-2 | Do the `?host=parent` bridges in GridCraft, PdfCraft and CADCraft differ in any way beyond the save semantics? (A line-by-line diff of the three is the natural next step.) |
| Q-3 | What is `photocraft-web-boot` and `figcraft-server`? `figcraft-server` is a hosted-server precedent worth understanding. |
| Q-4 | Are any of the web builds deployed publicly (a profile comment mentions Cloudflare Pages)? If so, their origin matters for the embedding model. |
| Q-5 | Do the three apps that build with `cargo xtask web` produce the same static site shape as the Trunk ones? (The deployment recipe assumes Trunk's `index.html` + hashed assets.) |
