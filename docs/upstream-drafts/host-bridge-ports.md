# Porting the `?host=parent` bridge to the remaining apps — notes, DRAFT, unpublished

Reference implementation: `apps/wordcraft-web/src/host.rs` (upstream, merged). Same vocabulary in
GridCraft, PdfCraft, CADCraft. Our DeckCraft port in `deckcraft-host-bridge/` is a fourth copy of the
same ~150 lines; the right end state is one crate in `craft-libs` (capabilities audit §3).

| App | Web seam (upstream, 2026-10-31) | Open | Save | Dirty | Notes |
| --- | --- | --- | --- | --- | --- |
| DeckCraft 0.13.1 | `Services{open_async, write, download, inbox}` + `SlideApp::begin_external_file` | queue bytes, shell drains them into the inbox with a fresh id | hook `write`/`download` | no `on_dirty` in `Services` | port written; see `deckcraft-host-bridge/` |
| VectorCraft 0.19.0 | `window.vectorcraft` page API (`api.rs`) | `openFile` | `captureDownloads` + `files`/`readFile` polling; `file.save {path}` | `document.inspect` (no flag found yet) | **works today through the lab shim** (`lab/real-seafile/static/host-shim.js`); a native `host.rs` would replace the polling |
| FigCraft 0.13.1 | `window.figcraft` page API, same shape | same | same | same | shim wired; fixture made by the app itself in the browser slice |
| PhotoCraft 0.18.0 | `Services{write, write_unconfirmed, file_dialog, inbox}` + `has_unsaved_work()` | push into the open inbox | hook `write`, `write_unconfirmed = false` | yes (`has_unsaved_work`) | port written; see `photocraft-host-bridge/`; no engine change needed (GR-076 superseded) |
| DesignCraft 0.15.2 | `Services{open_async(ImportRequest), write, download, inbox}` + `DesignApp::import_request` | drain host files into the inbox with a fresh import request | hook `write`/`download` | no | port written; see `designcraft-host-bridge/` (GR-021 superseded) |
| SoundCraft 0.15.0 | `io::set_deliver(fn)` global hook + `Inbox` by `Purpose::of(ext)` | push `(Purpose::of(name), name, bytes)` | thread-local bridge behind `host::deliver` | no | port written; see `soundcraft-host-bridge/`; sessions are `.scraft`/`.scraftz` |
| FilmCraft 0.15.0 | `lib.rs` + `fs.rs`/`opfs.rs` (OPFS-backed project) | project is a folder, not one file | export only | — | not a single-document app; the capabilities audit flagged "no browser-shaped seam". Export-only integration (`saveAs: true`) is the realistic scope |
| EffectCraft 0.19.0 | `lib.rs` + `store.rs`/`diskcache.rs` | same as FilmCraft | export only | — | same |
| LightCraft 0.16.0 | `lib.rs` + `store.rs`/`backend.rs` (72 MB bundle) | catalog + raw files | export only | — | same; bundle size alone makes it a poor iframe citizen |

Order of value for a Seafile user: VectorCraft (done via shim) → DeckCraft (pptx) → PhotoCraft →
DesignCraft → SoundCraft; the three media apps last, as export-only.
