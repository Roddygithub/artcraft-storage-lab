# GR-016 — ArtCraft Web host seam audit

Status: **PROVISIONAL, source audit only.** No upstream source was edited and no
Seafile production service was accessed. This inventory identifies integration
surfaces; it does not claim that every app can already complete a durable host
save.

## Findings by app

| App | Upstream revision inspected | Existing web seam | Main gap before durable host save |
|---|---|---|---|
| WordCraft | `00bc6a4b028013b2dfb0e85e8b326aeed3ecff6d` | `Services` has inbox, async open, serializer/download, dirty hook and late `AsyncSaves`; no upstream parent bridge. | Bridge host open/save-result to existing async lifecycle. Local GR-014 patch supplies the app adapter. |
| GridCraft | `06920de8da609c19de7446945cfc62b844691efd` | Existing same-origin `?host=parent` bridge with open/save/dirty. | Upstream baseline clears dirty after posting; local GR-010 patch adds save tickets and durable result handling. |
| PdfCraft | `57e531ccca0047597809748b5cb4276336d6051a` | Existing same-origin parent bridge and app-owned PDF serialization. | `mark_saved` follows synchronous message delivery; no durable host acknowledgement or file revision identity. |
| DeckCraft | `0f4fffcf6c71ffa16029d07ac23752fedd783547` | Web picker/inbox and in-memory `saveBytes`; no host JS export. | WASM path writes are disabled and save falls back to browser download. Add host open/save callback and completion transition. |
| FigCraft | `8d790607ff1ad40e32343ca2116d8fdcf3244c8d` | Real `Services` trait, byte-based open and serializer. | Web writer is download-only; WASM engine path write is an explicit error. Earlier docs saying `NoServices` are stale. |
| VectorCraft | `125df6d8ecfae01d01ce369ac02e4aa03e0deed5` | Private same-origin `window.vectorcraft` request/control API, open and capture-download methods. | No upstream common `postMessage` bridge or pushed dirty/save acknowledgement; current Seafile proof is app-specific polling. |
| SoundCraft | `d47abe484d4f9ef0cc9f8e872e0b3880a61a4588` | Self-contained `.scraftz` serialization/open and a web `DeliverHook`. | Web delivery downloads; hook is a synchronous function pointer and cannot await remote persistence. |
| CADCraft | `7bf5905ac97316a7896de8cbc12d243f57b09bd8` | Existing iframe open/dirty/save-byte bridge. | `postMessage` success is treated as save completion; editor marks clean before durable host acknowledgement. |
| DesignCraft | `80d13911b2d20fbb5cd9398696627bb3a715417b` | Picker/inbox open, internal dirty state and `.designcraft` serializer. | No host open bridge; browser download is treated as save and clears dirty state. |
| FilmCraft | `fa550ce2d07bdfee6b1d7b6835e8abc8c6913d00` | `window.filmcraft.openProject`, serializable `.fcproj`, pollable dirty/revision. | Web write path triggers download and returns success; no durable host response. |
| EffectCraft | `049070d65c66a73f322b496b22521816e0018f14` | `addFile` and project summary/query expose open and dirty primitives. | Web writes use browser storage/download; flush does not acknowledge a host save. |
| PhotoCraft | `a02f2ee41059d3312e7ff24a5af5edcac7b6435a` | Picker-based byte import and export serializer. | No host-driven open or durable save bridge; web writer is unconfirmed/download-oriented. |
| LightCraft | `98702b5c446ce2791b0aab92dab65cf9da7220b7` | Browser-local photo library, picker/drop and download export. | `web.stats.dirty` concerns local library state; no document host open/save acknowledgement. Product fit as a file editor needs separate scoping. |

The SHA values above are the revisions recorded by the respective source audits.
WordCraft and GridCraft were cloned again at their listed SHAs in this run for
the Rust adapter prototype. The other source reads are not runtime verification.

## Source anchors

These are source locations at the exact revision shown above:

- **WordCraft:** `crates/ui-egui/src/lib.rs:100–180` (`Services`, serialize/handoff);
  `apps/wordcraft-web/src/web.rs:117–133,209–245,393–412` (web open and download).
- **GridCraft:** `apps/gridcraft-web/src/host.rs:32–52,84–110,112–132` (bridge and
  optimistic saved snapshot); `crates/ui-egui/src/lib.rs:196` (download hook).
- **PdfCraft:** `apps/pdfcraft-web/src/main.rs:140–257` (bridge); `crates/ui-egui/src/editing.rs:659–704`
  (WASM save path); `crates/engine/src/lib.rs:4355–4374` (`mark_saved`).
- **DeckCraft:** `apps/deckcraft-web/src/web.rs:112–177` (picker/download);
  `crates/ui-egui/src/lib.rs:1281–1304` (save-as); `crates/engine/src/io.rs:53–56`
  (WASM path-write error).
- **FigCraft:** `crates/ui-egui/src/lib.rs:244–312` (`Services`); `apps/figcraft-web/src/web.rs:90–111,234–258`
  (open/download); `crates/engine/src/cmd/file.rs:473–475` (WASM write error).
- **VectorCraft:** `apps/vectorcraft-web/src/api.rs:121–184` (private page API);
  `crates/ui-egui/src/control.rs:155` (pollable dirty state);
  `crates/engine/src/cmd/fileio/save.rs:705` (write callback pipeline).
- **SoundCraft:** `crates/engine/src/io.rs:1220–1241` (`DeliverHook`), `1246–1277`
  (bundle serialization), `1280–1294` (save bundle); `apps/soundcraft-web/src/web.rs:17`
  (download hook installation).
- **CADCraft:** `apps/cadcraft-web/src/host.rs:68–90` (open), `98–125` (dirty/save);
  `crates/engine/src/cmd/file.rs:431–448` (save completion transition).
- **DesignCraft:** `apps/designcraft-web/src/web.rs:390–450` (web services);
  `crates/ui-egui/src/menus.rs:1984–1992` (download then saved);
  `crates/engine/src/cmd/file.rs:81–87` (serializer command).
- **FilmCraft:** `apps/filmcraft-web/src/api.rs:201–211` (`openProject`);
  `crates/engine/src/commands.rs:1493–1496,4351–4371` (serialize/write/clean);
  `apps/filmcraft-web/src/fs.rs:338–352` (web writer).
- **EffectCraft:** `apps/effectcraft-web/web/index.html:49–69` (`addFile`);
  `crates/engine/src/commands/query.rs:59–68` (dirty query);
  `apps/effectcraft-web/src/files.rs:110–131` and `src/persist.rs:168–179` (web write/flush).
- **PhotoCraft:** `apps/photocraft-web/src/web.rs:392–439` (import/export writer);
  `crates/ui-egui/src/discard_ui.rs:113–118` (local unsaved state);
  `crates/ui-egui/src/lib.rs:474–478,586–589` (unconfirmed writes stay dirty).
- **LightCraft:** `apps/lightcraft-web/src/web.rs:120–139` (picker/drop), `620–648`
  (`web.stats`); `crates/catalog/src/journal.rs:217–222` (local catalog journal);
  `apps/lightcraft-web/src/backend.rs:188–235` (browser storage flush).

## Cross-app conclusion

The applications do **not** share one interchangeable save hook. A common Rust
transport can standardize same-origin message validation, opaque string tickets,
byte transfer, and listener lifecycle. Each application still owns its document
identity, serializer, dirty/revision tracking, and the point at which a durable
host acknowledgement is allowed to mark the document clean.

The first practical shared-transport trial is WordCraft plus GridCraft because
both already have identifiable byte serialization and host seams (or, for
WordCraft, the required `Services` hooks). PdfCraft/CADCraft have optimistic
bridges that need lifecycle changes. DeckCraft, FigCraft, DesignCraft,
PhotoCraft, SoundCraft, FilmCraft, EffectCraft and LightCraft need app-specific
save/open work before the shared transport is useful. VectorCraft remains an
app-specific adapter until upstream exposes a durable host seam.

## Not established by this audit

- Durable save, Seafile new version, or reopen for any revision listed above.
- Security behavior beyond the source-level message origin/source checks noted
  for the existing bridges.
- A stable API or shared contract already adopted by upstream ArtCraft.
- Whether LightCraft's local photo-library workflow is in scope for a document
  storage connector.

See the GR-016 prototype and test record before treating any shared Rust code as
reusable or ready for upstream review.
