# Seafile ↔ ArtCraft Web — shared integration and app coverage

## User workflow

The target browser workflow is:

```text
Seafile Web click → matching ArtCraft Web editor → edit → save
→ Seafile commits a new version → close → reopen → edit remains
```

This uses one Seafile connector and one extension dispatcher. It does not use a
desktop workflow, filesystem mount, manual upload, or production MCP protocol.

## Shared path and save boundary

```text
Seafile Web
  └─ per-library allow-list + file extension
       └─ same-origin `/open/` POST with a short-lived Seafile token
            └─ ArtCraft gateway
                 ├─ identifies user, repository and path from the token
                 ├─ selects one Craft app from the extension table
                 ├─ embeds the app and passes document bytes
                 └─ waits for a user-authorized conditional Seafile commit
```

The common host contract carries filename, bytes, dirty state and save result;
it contains no Seafile API, library id or account credential. The production
save path still depends on the user-bound conditional endpoint drafts in
[`reviews/GR-015/`](reviews/GR-015/README.md); those drafts are not built or
deployed. Synthetic runtime evidence below does not establish production
conflict or permission handling.

Repository-scoped routing remains mandatory. Only the synthetic test library is
allow-listed for ArtCraft. Other libraries must continue to use their existing
Office configuration; ONLYOFFICE remains enabled and its settings are not part
of the ArtCraft dispatcher.

## Current dispatcher and Seafile evidence (2026-10-26)

The tracked `integration/config/dispatch.json` contains five routes. The table
separates that tracked configuration from prior per-app runtime evidence; it
does not claim all bundles are present in this checkout's active static root.

| Extension | Tracked app | Synthetic Seafile runtime evidence | Remaining limit |
| --- | --- | --- | --- |
| `.docx` | WordCraft | GR-059 is the primary synthetic roundtrip; GR-076 re-verified edit/save/version/reopen after the `.pcraft` allow-list change | The GR-076 post-change ONLYOFFICE check is inconclusive; WordCraft byte identity and broader compatibility are not established |
| `.xlsx` | GridCraft | GR-061: synthetic Seafile save/version/reopen | Combined five-route replay and production behavior are not verified |
| `.pdf` | PdfCraft | GR-068: synthetic Seafile save/version/reopen | Exact save/readback byte identity and broader PDF semantics remain unverified |
| `.svg` | VectorCraft | GR-063: synthetic Seafile export/version/reopen using the app's page API | This is a separate app-specific export path; exact export/readback byte identity remains unverified |
| `.pcraft` | PhotoCraft | GR-076: synthetic Seafile open/edit/save/version/readback/close/reopen; current bytes match the latest of three history versions | Low-optimization build only; production, optimized bundle and serialization peak memory remain unverified |

GR-037 separately recorded PhotoCraft editor-message, gateway-body and Seafile
readback hashes matching at 8,555 bytes. GR-076's PhotoCraft readback instead
matched the latest Seafile history entry; it did not compare that payload with
the editor message. GR-035 also recorded an optimized PhotoCraft browser smoke,
but GR-076's Seafile run used its low-optimization bundle.

The repository's ignored `integration/static/` directory currently contains the
GR-076 PhotoCraft bundle. The other four app bundles are not present there in
this checkout. GR-071 used a separate test static root for the four candidate
bundles; that historical root does not establish current static serving or
asset promotion in this checkout. One combined five-route Seafile replay and
active serving of all five bundles remain **NOT VERIFIED**. See the matrix
rows for [GR-071](TEST-MATRIX.md#gr-071--shared-test-root-candidate-provenance-recheck)
and [GR-076](TEST-MATRIX.md#gr-076--bounded-photocraft-browser-host-adapter).

## Other app coverage

These apps have synthetic Seafile workflow evidence, but are not in the current
tracked dispatcher:

| App | Evidence | Current tracked route |
| --- | --- | --- |
| DeckCraft | GR-064 synthetic PPTX save/version/reopen | No |
| DesignCraft | GR-065 synthetic document save/version/reopen | No |
| FilmCraft | GR-066 synthetic document save/reopen | No |
| EffectCraft | GR-067 synthetic document save/reopen | No |
| FigCraft | GR-069 synthetic document save/version/reopen | No |

CADCraft, LightCraft and SoundCraft do not have an accepted Seafile dispatch
route in the tracked configuration. Their browser support and host integration
remain separate work; availability of an upstream browser build alone is not
evidence that the byte-based Seafile save contract is supported.

## Acceptance gate per app

Before adding an extension to the tracked dispatcher, a synthetic document must
show:

1. Seafile Web selects the expected Craft app.
2. The app opens the actual Seafile bytes.
3. A real edit changes the app's serialized document.
4. Save waits for an authorized Seafile commit or reports a visible error.
5. Seafile history gains a version, and readback is compared with the editor's
   saved bytes where the evidence can capture them.
6. Closing and reopening preserves the semantic edit.
7. Read-only access, permission revocation, stale edits, save failures and
   concurrent edits do not report false success or overwrite newer content.

Passing a synthetic single-app flow is bounded evidence; it does not establish
the combined dispatcher, production deployment or public-internet readiness.
The latter also requires CSP, rate limiting and the remaining work in
[`SECURITY.md`](SECURITY.md).
