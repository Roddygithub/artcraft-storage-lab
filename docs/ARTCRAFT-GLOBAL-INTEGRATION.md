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
| `.docx` | WordCraft | GR-059 primary roundtrip; GR-076 allow-list recheck; GR-078 combined replay retained `gr078docx` after reopen | GR-076 post-change ONLYOFFICE check is inconclusive; byte identity and broader compatibility are not established |
| `.xlsx` | GridCraft | GR-061 individual roundtrip; GR-078 combined replay retained B2/B3 = 1338 after reopen | Exact save/readback byte identity and production behavior remain unverified |
| `.pdf` | PdfCraft | GR-068 individual roundtrip; GR-078 combined replay retained `GR078savededit` after reopen | Exact save/readback byte identity and broader PDF semantics remain unverified |
| `.svg` | VectorCraft | GR-063 individual export roundtrip; GR-078 combined replay retained the added rectangle after reopen | Exact save/readback byte identity remains unverified |
| `.pcraft` | PhotoCraft | GR-076 per-file roundtrip/readback; GR-078 combined replay retained the added layer after reopen | Low-optimization build only; production, optimized bundle and serialization peak memory remain unverified |

GR-037 separately recorded PhotoCraft editor-message, gateway-body and Seafile
readback hashes matching at 8,555 bytes. GR-076's PhotoCraft readback instead
matched the latest Seafile history entry; it did not compare that payload with
the editor message. GR-035 also recorded an optimized PhotoCraft browser smoke,
but GR-076's Seafile run used its low-optimization bundle.

The repository's ignored `integration/static/` directory currently contains the
GR-076 PhotoCraft bundle; the other four app bundles remain absent from that
checkout root. GR-071 used a separate test static root. GR-078 subsequently
verified active serving and a combined five-route replay in the synthetic lab
deployment, without promoting those four bundles into this checkout. This
distinction does not establish production readiness or exact save/readback byte
identity. See [GR-071](TEST-MATRIX.md#gr-071--shared-test-root-candidate-provenance-recheck),
[GR-076](TEST-MATRIX.md#gr-076--bounded-photocraft-browser-host-adapter) and
[GR-078](TEST-MATRIX.md#gr-078--combined-five-route-synthetic-seafile-browser-replay).
GR-079 later confirmed current Seafile History rows for the five GR-078 files;
it did not compare editor output bytes with Seafile readback.

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
