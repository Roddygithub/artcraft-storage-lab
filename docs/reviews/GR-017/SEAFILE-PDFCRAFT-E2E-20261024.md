# GR-017 — PdfCraft synthetic Seafile save and reopen

**Date:** 2026-10-24

**Lab repository base:** `99d72e4c3436d87e5c8e7100748f42a0ab0f231d`

**PdfCraft source:** `57e531ccca0047597809748b5cb4276336d6051a`

**craft-libs transport:** `f180fc0d35d521c5d18e118c881d3efde1ec1eee`

**Environment:** isolated synthetic Seafile/Seahub and Chromium preview; no production data or services

## Result

**PASS for this bounded synthetic runtime flow.** A real PdfCraft Web/WASM editor
opened a synthetic PDF through the Seahub file route, created a text annotation,
and saved through the ticketed host bridge. The synthetic Seafile library gained
a new file head and history entry. A fresh route load created another PdfCraft
instance, which rendered the persisted annotation.

The browser automation did **not** observe a click on the Seahub file-list row:
click and double-click did not navigate in the collaborative preview. The test
opened the same Seahub file URL directly. This verifies the route/dispatch and
editor/save path, but the file-list click interaction remains unverified for
PdfCraft.

## Reproduction

1. Started only the isolated `artcraft-seafile-gr016-runtime` stack and the local
   gateway. Seahub and the gateway were configured on separate loopback origins.
   The synthetic library was temporarily configured to dispatch `.pdf` to
   PdfCraft; production Seahub and ONLYOFFICE were not changed.
2. Opened the synthetic `synthetic.pdf` through its Seahub file route. The
   original Seafile file was 655 bytes, with file ID
   `a304fe5d2f9912f75258c2827359d12736715224`.
3. The actual PdfCraft WASM rendered the fixture text. Using PdfCraft's “Add
   comments” → “Text box” tool, added the text annotation
   `PdfCraftSeafileRoundTrip`. PdfCraft showed `Unsaved changes`.
4. Pressed Ctrl+S. PdfCraft displayed `Saved — new version
   356627e30e928352b97fe5ce29decf6bd46c264f` after the host received the
   Seafile commit result.
5. Queried the synthetic Seafile API: the new file ID was
   `7c5c4566cf0c87c18e0c60632c32954b53c0795c`, size 2,034 bytes. History grew
   from one to two commits. The new commit
   `356627e30e928352b97fe5ce29decf6bd46c264f` has parent
   `dcce7f0558d1190fdb8b15b61c0baf1a36d1bd3a`; its revision file ID matches the
   current file. The earlier commit contains the original 655-byte fixture.
6. Read the file back from Seafile. The 2,034 returned bytes had SHA-256
   `99aaa1772bc8b0b114b71c229fe0d8f9374d669f0ccd3b6c48a80fd413023e53`.
   `pdfinfo` parsed it as an unencrypted, one-page PDF. `pdftotext` returned the
   original fixture text and `PdfCraftSeafileRoundTrip`.
7. Navigated to the same Seahub route with a fresh query marker, creating a new
   editor instance. The reopened PdfCraft page displayed the original text and
   the saved annotation in both the page and its Comments inspector.

## Evidence files

| Artifact | SHA-256 | What it shows |
|---|---|---|
| [`seafile-pdfcraft-saved-20261024.png`](runtime/seafile-pdfcraft-saved-20261024.png) | `758020f3a14f5f71991b29545bc15eb045c0af2615b9bdbfe24a9cb5999a0479` | PdfCraft after host confirmed the new Seafile version |
| [`seafile-pdfcraft-reopen-20261024.png`](runtime/seafile-pdfcraft-reopen-20261024.png) | `ebf6bf61437d26ca1aa4159e2d1d911f524f0da8f1e39c8908f169f037a2766b` | Fresh PdfCraft instance renders the saved annotation |

The saved screenshot includes the `Saved — new version` status; the reopen
screenshot shows the annotation text in the PDF and Comments inspector.

## Scope and limits

- **REAL:** isolated synthetic Seafile, Seahub route, Chromium preview, PdfCraft
  WASM, user edit via PdfCraft UI, host save acknowledgement, Seafile API
  persistence/history, fresh editor instance and semantic PDF readback.
- The exact outgoing `pdfcraft:save` message bytes were not separately captured
  and hashed against the Seafile readback; the readback hash and parsed content
  are recorded, but byte identity across that boundary is not claimed.
- This was a direct file-route navigation, not an observed file-list click.
- Only a text annotation on one synthetic PDF was exercised; this is not broad
  PDF feature-compatibility evidence.
- This does not test production Seafile, TLS/reverse-proxy deployment,
  authorization revocation, timeout/response-loss, cross-user access, rate
  limits, CSP, or all ArtCraft apps.
- The PdfCraft bridge patch and its `craft-libs` path dependency remain in
  scratch checkouts. No upstream repository was modified or published.
- Overall GPT review remains **FAIL** on `0edbe524b4fa321b0f73f8601afef390e7f785e6`;
  public deployment is not ready and upstream publication remains locked.
