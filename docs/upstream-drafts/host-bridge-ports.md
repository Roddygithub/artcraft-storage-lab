# Porting the `?host=parent` bridge to the remaining apps — notes, DRAFT, unpublished

Reference implementation: `apps/wordcraft-web/src/host.rs` (upstream, merged). Same vocabulary in
GridCraft, PdfCraft, CADCraft. Our DeckCraft port in `deckcraft-host-bridge/` is a fourth copy of the
same ~150 lines; the right end state is one crate in `craft-libs` (capabilities audit §3).

| App | Web seam (upstream, 2026-10-31) | Open | Save | Dirty | Notes |
| --- | --- | --- | --- | --- | --- |
| DeckCraft 0.13.1 | `Services{open_async, write, download, inbox}` + `SlideApp::begin_external_file` | queue bytes, shell drains them into the inbox with a fresh id | hook `write`/`download` | no `on_dirty` in `Services` | port written; see `deckcraft-host-bridge/` |
| VectorCraft 0.19.0 | `window.vectorcraft` page API (`api.rs`) | `openFile` | `captureDownloads` + `files`/`readFile` polling; `file.save {path}` | `document.inspect` (no flag found yet) | **works today through the lab shim** (`lab/real-seafile/static/host-shim.js`); a native `host.rs` would replace the polling |
| FigCraft 0.13.1 | `window.figcraft` page API, same shape | same | same | same | shim wired; fixture made by the app itself in the browser slice |
| PhotoCraft 0.18.0 | `apps/photocraft-web/src/web.rs` (30 KB), `preset_bridge.rs` | engine open path | engine save hook | — | GR-076 patch (14 files, incl. `crates/engine`) is the starting point; needs rebasing |
| DesignCraft 0.15.2 | `web.rs` (21 KB), `browser_policy.rs` | — | — | — | GR-021 patch touches `crates/engine/src/cmd/file.rs`; rebase |
| SoundCraft 0.15.0 | `io::set_deliver(fn)` global hook + `Inbox` by `Purpose::of(ext)` | push `(Purpose::of(name), name, bytes)` | thread-local bridge behind `host::deliver` | no | port written; see `soundcraft-host-bridge/`; sessions are `.scraft`/`.scraftz` |
| FilmCraft 0.15.0 | `lib.rs` + `fs.rs`/`opfs.rs` (OPFS-backed project) | project is a folder, not one file | export only | — | not a single-document app; the capabilities audit flagged "no browser-shaped seam". Export-only integration (`saveAs: true`) is the realistic scope |
| EffectCraft 0.19.0 | `lib.rs` + `store.rs`/`diskcache.rs` | same as FilmCraft | export only | — | same |
| LightCraft 0.16.0 | `lib.rs` + `store.rs`/`backend.rs` (72 MB bundle) | catalog + raw files | export only | — | same; bundle size alone makes it a poor iframe citizen |

Order of value for a Seafile user: VectorCraft (done via shim) → DeckCraft (pptx) → PhotoCraft →
DesignCraft → SoundCraft; the three media apps last, as export-only.
