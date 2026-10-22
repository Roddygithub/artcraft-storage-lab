# Seafile ↔ ArtCraft Web — shared integration and app coverage

## User workflow

The target is a browser workflow comparable to Seafile ↔ ONLYOFFICE:

```text
Seafile Web click → matching ArtCraft Web editor → edit → save
→ Seafile commits a new version → close → reopen → edit remains
```

This is one Seafile connector and one editor dispatcher, not a desktop workflow,
filesystem mount, manual upload, or MCP production protocol.

## Shared path

```text
Seafile Web
  └─ per-library allow-list + file extension
       └─ same-origin `/open/` POST with a short-lived Seafile token
            └─ ArtCraft gateway
                 ├─ identifies the user, repo and path from the token
                 ├─ selects one Craft app from its extension table
                 ├─ embeds that app and passes document bytes
                 └─ waits for a user-authorized conditional Seafile commit
```

The common host contract carries only filename, bytes, dirty state and save
result. It contains no Seafile API, library id or account credential. Seahub
must provide a user-bound save endpoint, and the fileserver must compare the
opened file id and library head atomically before commit. The exact 12.0.14
drafts are in [`reviews/GR-015/`](reviews/GR-015/README.md); they are not built
or deployed.

Repository-scoped routing is mandatory. The former global `.xlsx` route was
removed from the live config and backed up because Seahub's extension hook runs
before ONLYOFFICE's file view. Only the synthetic `OnlyOffice` library may be
allow-listed for the first browser test. Other libraries must continue to route
to their existing Office configuration.

## App coverage

“Available” means a browser build exists; it does not mean the app can safely
open and save arbitrary Seafile bytes through the common host contract.

| App | Current browser integration evidence | Required work before Seafile dispatch |
| --- | --- | --- |
| WordCraft | Build in `integration/static/`; host bridge patch prepared in GR-014 | Apply bridge to a pinned build; prove DOCX click/edit/save/version/reopen |
| GridCraft | Build and `?host=parent` bridge in `integration/static/` | Make save acknowledgement wait for durable success; XLSX semantic and ONLYOFFICE tests |
| PdfCraft | Build and `?host=parent` bridge in `integration/static/` | Verify PDF save, reject export/Save As, prove reopen semantics |
| VectorCraft | Build in `integration/static/`; deterministic page API used for GR-012 | Replace broad automation API with a narrow host bridge or keep explicitly separate; verify SVG geometry/reopen |
| CADCraft | Existing upstream bridge was inspected; no build in the current static bundle | Fetch/build pinned version and test its serializer through the common contract |
| DeckCraft | Browser build exists; host bridge is absent | Implement open/save/dirty/error bridge, then test PPTX semantics |
| PhotoCraft | Browser build exists; bridge and download seam incomplete | Add browser open/save seam and test project format |
| FigCraft | Browser build exists; services are a placeholder | Implement browser document services before host bridge |
| DesignCraft | Browser build exists; save acknowledgement seam incomplete | Add async save result and test native format |
| FilmCraft | Browser build exists; current seam is filesystem-shaped | Add a browser byte-based document seam and test project format |
| LightCraft | Browser build exists; open/download seam incomplete | Add browser byte-based document seam and test project format |
| EffectCraft | Browser build exists; current seam is filesystem-shaped | Add a browser byte-based document seam and test project format |
| SoundCraft | Browser build exists; open/download seam incomplete | Add browser byte-based document seam and test project format |

The gateway currently dispatches only `docx`, `xlsx`, `pdf` and `svg`. The four
builds currently present in the local static bundle are WordCraft, GridCraft,
PdfCraft and VectorCraft. The other apps remain unsupported until their actual
browser APIs and serializers are wired and verified.

## Acceptance gate per app

An app may be enabled for a file type only after a synthetic document proves:

1. Seafile Web dispatches the file to the expected Craft app.
2. The app receives and opens the actual Seafile bytes.
3. A real edit changes the app's serialized document.
4. Save waits for an authorized Seafile commit or reports a visible error.
5. Seafile history gains a version, and downloaded bytes match the editor output.
6. Closing and reopening in the editor preserves the semantic edit.
7. Read-only, permission revocation, stale edit, save failure and concurrent edit
   cases do not report a false success or overwrite the newer file.

Only after app-by-app gates pass should its extension be enabled outside the
synthetic test library. Public Internet deployment also requires CSP, rate
limiting and the remaining security work in `docs/SECURITY.md`.
