# GR-003 / GR-004 — Owner's independent verification: the web builds exist, and the host seam already exists

* Verified 2026-10-22 against the **live** `storytold/*` repositories on GitHub
  (default branch `main`), read-only, via the GitHub contents API and `raw.githubusercontent.com`.
* This document is the owner's own verification. The architect's full per-app
  capability matrix is `docs/ARTCRAFT-WEB-CAPABILITIES.md` (GR-003).
* **The baseline audit `~/ArtCraft-Audit.md` was about the AUR desktop packages and
  missed the web builds entirely.** It is not wrong about the desktop apps; it is
  silent about the web ones. That silence would have changed the whole project plan.

---

## 1. Headline result

> **All 13 ArtCraft apps already have a browser build.** The web build runs the
> *same* egui application as the desktop app, through eframe's web runner
> (wgpu: WebGPU where available, WebGL2 otherwise), built with Trunk.
>
> **The only missing piece is the host bridge.** The web builds open documents
> through the browser file picker and save through the browser download /
> File System Access API. There is no "open from host" and no "save to host".
>
> **And the seam where the bridge must go already exists**, in every app's
> `ui-egui` crate, as the `Services` struct.

This changes the project from *"build a Craft web editor"* to
*"wire the existing Craft web editors to a host protocol"*, which is a much
smaller, much more upstreamable piece of work.

## 2. Every app has a web build

`GET repos/storytold/<app>/contents/apps`:

| App | `apps/` contents |
| --- | --- |
| wordcraft | `wordcraft`, `wordcraft-cli`, **`wordcraft-web`** |
| gridcraft | `gridcraft`, `gridcraft-cli`, **`gridcraft-web`** |
| deckcraft | `deckcraft`, `deckcraft-cli`, **`deckcraft-web`** |
| pdfcraft | `pdfcraft`, `pdfcraft-cli`, **`pdfcraft-web`** |
| vectorcraft | `vectorcraft`, `vectorcraft-cli`, **`vectorcraft-web`** |
| photocraft | `photocraft`, `photocraft-cli`, **`photocraft-web`**, `photocraft-web-boot` |
| figcraft | `figcraft`, `figcraft-cli`, **`figcraft-web`**, `figcraft-server` |
| designcraft | `designcraft`, `designcraft-cli`, **`designcraft-web`** |
| cadcraft | `cadcraft`, `cadcraft-cli`, **`cadcraft-web`** |
| filmcraft | `filmcraft`, `filmcraft-cli`, **`filmcraft-web`** |
| lightcraft | `lightcraft`, `lightcraft-cli`, **`lightcraft-web`** |
| effectcraft | `effectcraft`, `effectcraft-cli`, **`effectcraft-web`** |
| soundcraft | `soundcraft`, `soundcraft-cli`, **`soundcraft-web`** |

Two extra members are worth noting:

* `photocraft-web-boot` — a separate bootstrap front end.
* `figcraft-server` — FigCraft already has a **server** component, which is a
  precedent for a hosted deployment.

## 3. How a web build is produced

`apps/wordcraft-web/`:

```text
Cargo.toml     crate-type bin, deps: <app>-engine, <app>-ui-egui, egui,
               serde_json, <app>-doc, <app>-fonts
               [target.'cfg(target_arch = "wasm32")'.dependencies]
               eframe (features: default_fonts, wgpu, accesskit), rfd,
               wasm-bindgen, wasm-bindgen-futures, js-sys, web-sys
Trunk.toml     [build] target = "index.html", dist = "../../dist/web",
               public_url = "./", filehash = true
               [serve] 127.0.0.1:8771
index.html     <link data-trunk rel="rust" data-bin="wordcraft-web"
               data-wasm-opt="z" data-weak-refs />
               <canvas id="wordcraft_canvas">
src/main.rs    #![deny(clippy::unwrap_used, clippy::expect_used, clippy::panic, ...)]
               #[cfg(target_arch = "wasm32")] mod web; mod prefs; mod save_fallback;
               fn main() { web::start(); }
src/web.rs     623 lines - the web platform layer
```

Build command (from `src/main.rs`): `trunk build --release` in `apps/<app>-web`,
output in `dist/web`.

The `web-sys` feature list in `apps/wordcraft-web/Cargo.toml` already includes
`Blob`, `Url`, `HtmlIFrameElement`, `File`, `FileList`, `DataTransfer`,
`Storage`, `IdbFactory` / `IdbObjectStore` — i.e. the browser APIs a host
bridge needs are already compiled in.

## 4. The current web behaviour (WordCraft, read from `apps/wordcraft-web/src/`)

`src/main.rs` doc comment, verbatim:

> Runs the same [`wordcraft_ui_egui::WordApp`] as the desktop app through eframe's
> web runner (wgpu: WebGPU where available, WebGL2 otherwise).
>
> Differences from the desktop app: **no TCP control channel; Open and Insert >
> Pictures use the browser file picker (bytes arrive through `Services::inbox`);
> Save and Export download.** Preferences (theme, interface size, editing options…)
> are kept in `localStorage` (`prefs`). URL flags: `?webgl` forces WebGL2;
> `?sample` opens the sample document.

Two facts follow immediately:

* the desktop app's TCP control channel is the closest thing to an existing
  host protocol, and it is **absent in the web build**;
* the web build already has a **URL-flag convention** (`?webgl`, `?sample`),
  which is a natural place for a `?host=…` mode.

## 5. The seam: `Services` in `crates/ui-egui/src/lib.rs`

`wordcraft-ui-egui` (i.e. `crates/ui-egui/src/lib.rs`) defines:

```rust
/// Platform services injected by the host (file dialogs, file I/O).
#[derive(Default)]
pub struct Services {
    /// Pick a file to open; the argument says what for (`document`, `picture`).
    pub pick_open: Option<Box<dyn Fn(&str) -> Option<String>>>,
    /// Pick a path to save to, given a suggested name.
    pub pick_save: Option<Box<dyn Fn(&str) -> Option<String>>>,
    /// Web: open a file picker; the file arrives later through `inbox`.
    pub open_async: Option<Box<dyn Fn(&str)>>,
    /// Web: files (name, bytes) delivered asynchronously (picker, drag and drop).
    pub inbox: Option<Inbox>,
    /// Web: hand bytes to the browser as a download. An error means no download started
    /// (the browser can't tell the page whether the user then kept the file).
    pub download: Option<Box<dyn Fn(&str, &[u8]) -> Result<(), String>>>,
    /// Web: saves that `download` started and that finish later (the browser's save picker).
    /// The hook starts a ticket for such a save and reports how it ended; until then the
    /// document's save isn't confirmed, and a New/Open held back by the Save Changes prompt waits.
    pub async_saves: Option<async_saves::AsyncSaves>,
    /// Web: told whether the document has unsaved changes after each pass, for the browser's
    /// leave-page guard (`beforeunload` runs between frames and can't ask the app).
    pub on_dirty: Option<Box<dyn Fn(bool)>>,
    /// Web: pictures pasted from the browser's clipboard (the bytes; the name is ignored).
    pub pasted: Option<Inbox>,
    /* ... printing, clipboard, fonts, templates ... */
}
```

`Services` is a **plain struct of boxed closures** — not a trait, no async
signatures, no platform types. It is the app's dependency-injection seam, and
the doc comment says so: *"Platform services injected by the host"*.

### 5.1 The five fields a host bridge needs

| `Services` field | What the browser build does today | What a host bridge does |
| --- | --- | --- |
| `open_async` | opens the browser file picker | asks the **host** to supply a document |
| `inbox` | receives `(name, bytes)` from the picker / drag-and-drop | receives `(name, bytes)` from the **host** |
| `download` | triggers a browser download / save picker | hands the bytes to the **host** |
| `async_saves` | tracks a browser save that finishes later | tracks a **host save that finishes later** — identical semantics |
| `on_dirty` | drives the `beforeunload` guard | reports the dirty state to the **host** |

`async_saves` is the important one. Its documented contract is already exactly
what a host save needs:

> *The hook starts a ticket for such a save and reports how it ended; until then
> the document's save isn't confirmed.*

So "the document is not marked clean until the host acknowledges the write" is
**already implemented** in the Craft apps, for the browser's save picker. A host
bridge reuses `AsyncSaves` unchanged. That is a very large part of the save
protocol (GR-007) for free, and it is upstream-consistent.

### 5.2 The `Services` struct is not identical in every app

Counting the fields in each app's `crates/ui-egui/src/lib.rs`:

| App | `pub struct Services` | `open_async` | `inbox` | `download` |
| --- | --- | --- | --- | --- |
| wordcraft | yes | yes | yes | yes |
| gridcraft | yes | yes | yes | yes |
| deckcraft | yes | yes | yes | yes |
| vectorcraft | yes | yes | yes | yes |
| designcraft | yes | yes | yes | yes |
| photocraft | yes | – | yes | – |
| cadcraft | yes | – | – | – |
| lightcraft | yes | – | – | – |
| soundcraft | yes | – | – | – |
| pdfcraft | not in `lib.rs` | – | yes | – |
| figcraft | not in `lib.rs` | – | – | – |
| filmcraft | not in `lib.rs` | – | – | – |
| effectcraft | not in `lib.rs` | – | – | – |

**The 13 apps are therefore NOT equivalent.** WordCraft, GridCraft, DeckCraft,
VectorCraft and DesignCraft already carry the full set of web hooks. The others
have a reduced `Services` (or none found in `lib.rs` — they may define it in a
submodule or use a different name; that is **NOT VERIFIED** and is exactly what
the architect's full matrix must settle).

**Consequence for GR-003/GR-004: the "common host contract" cannot be a
one-shot uniform change across 13 apps.** The office-format apps (Word, Grid,
Deck) are ready; the rest need work. That is a strong argument for making the
**WordCraft MVP first** and treating the others as follow-ups — which is what
the mission already demands.

## 6. `storytold/craft-libs` — is there a shared place for the contract?

`storytold/craft-libs` (`MIT OR Apache-2.0`), crates:

```text
ai-core  atomic  cms  docpath  i18n  media  pdf  print  quit  settings  ui  window
```

* `crates/ui` — buttons, docking, icons, layout, printing, tabs, theme: a
  **shared widget** crate, not a services crate.
* `crates/window` — "decide who draws the window frame" (desktop window
  decoration policy). Desktop-only concern.
* `crates/quit` — `close.rs`, `menu.rs`, `macos.rs`: the app-quit / close
  handling.
* `crates/docpath` — document path handling.
* `crates/print` — printing.

**There is no host / embedding / bridge crate.** Nothing equivalent to a host
contract exists today, so creating one is justified (mission §24).

The natural home would be a **new crate in `craft-libs`**, e.g.
`crates/web-host` or `crates/host`, consumed by all 13 `apps/<app>-web`
crates. `craft-libs` is exactly the place the suite puts code that must be
identical across apps, and it is dual MIT/Apache-2.0, so it is licence-clean
for this repository.

Caveat to verify: `craft-libs` declares `unsafe_code = "forbid"` and a
`[workspace.lints]` policy, and the apps require
`#![deny(clippy::unwrap_used, clippy::expect_used, clippy::panic, ...)]`.
A host crate must satisfy the same bar.

## 7. Licences (updated finding for `docs/LICENSING.md`)

| Repository | Licence | Source |
| --- | --- | --- |
| `storytold/wordcraft` | **Apache-2.0** | `GET repos/storytold/wordcraft/license` -> `LICENSE-APACHE` |
| `storytold/gridcraft` | **Apache-2.0** | idem |
| `storytold/deckcraft` | **Apache-2.0** | idem |
| `storytold/pdfcraft` | **Apache-2.0** | idem |
| `storytold/vectorcraft` | **Apache-2.0** | idem |
| `storytold/craft-libs` | **MIT OR Apache-2.0** | `LICENSE-MIT` + `LICENSE-APACHE` in the repo root |

All compatible with this repository's dual MIT / Apache-2.0 licence.
The remaining 8 app licences are **NOT VERIFIED** in this document and must be
confirmed before any of their code is vendored or derived from.

## 8. What this means for the plan

| Before this finding | After this finding |
| --- | --- |
| "Do Craft web editors exist at all?" — unknown | **Yes, all 13.** |
| "We may have to build a web editor" | "We must add a host bridge to web apps that exist" |
| "The common contract may have to be invented from scratch" | The contract must be expressed in terms of the **existing `Services` seam** |
| "Which app first?" — open | **WordCraft** (richest `Services`, and the mandatory MVP) |
| "Upstream patch shape unknown" | "A new `craft-libs` crate + a thin per-app wiring" |

### 8.1 The likely upstream patch shape (GR-014 candidate)

```text
storytold/craft-libs
  crates/host/            <-- NEW: the host protocol, platform-agnostic types
      src/lib.rs          message types, no wasm dependencies
      src/wasm.rs         the postMessage transport (wasm32 only)

storytold/<app>
  apps/<app>-web/src/host.rs   <-- NEW: wire Services to the host transport
  apps/<app>-web/src/web.rs    <-- MODIFIED: choose browser mode or host mode
```

The `Services` wiring per app is small:

```rust
// browser mode (today)
open_async: Some(pick_file), inbox: Some(inbox), download: Some(download_bytes)

// host mode (new)
open_async: Some(|what| host.request_open(what)),
inbox:     Some(inbox),                 // the host's bytes land here
download:  Some(|path, bytes| host.send_document(path, bytes)),
async_saves: Some(saves),                // reused unchanged
on_dirty:  Some(|dirty| host.set_dirty(dirty)),
```

The **only** thing that changes is where the bytes come from and where they go.
The document model, the editor, the save-confirmation machinery and the dirty
tracking are untouched. That is a genuinely small, upstream-friendly change —
and it is the honest answer to "what belongs upstream in ArtCraft" (mission §44).

## 9. Open questions for the architect's full matrix

| # | Question |
| --- | --- |
| Q-1 | For the 8 apps whose `Services` is reduced or absent, where exactly is the equivalent seam? |
| Q-2 | Do all 13 web apps build with `trunk`, or do some use a different bundler? |
| Q-3 | Which apps expose a `--cli` command surface that could serve as an alternative, non-browser host protocol? |
| Q-4 | What is `figcraft-server`? A hosted-server precedent? |
| Q-5 | What is `photocraft-web-boot`? |
| Q-6 | Do any web apps already use `postMessage` or an `HtmlIFrameElement`? (`web-sys` requests `HtmlIFrameElement`, which is suspicious.) |
| Q-7 | Are the web builds deployed anywhere public (Cloudflare Pages is mentioned in a profile comment)? If so, their origin matters for the embedding security model. |
