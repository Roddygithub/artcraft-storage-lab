# GR-063 — VectorCraft real synthetic Seafile roundtrip

Date: 2026-10-26
Status: **GPT REVIEW PENDING**

## Result

The exact GR-058 source-built VectorCraft candidate completed an SVG edit,
versioned save, and fresh Seafile-backed reopen in the existing private test
deployment. The test used only `synthetic.svg` in the dedicated synthetic
library.

1. Uploaded the 270-byte `tests/fixtures/synthetic.svg` through Seafile as
   fixture setup. It was not the edited output.
2. Opened `synthetic.svg` from the Seafile file list. The gateway `/open/`
   handoff, candidate index, JS, WASM, and session document request returned
   HTTP 200. The SVG rendered in the actual VectorCraft candidate.
3. Added a 20 × 20 px rectangle through VectorCraft's Rectangle tool.
4. Ctrl+S opened VectorCraft's Save As dialog for this imported SVG; it was
   cancelled. Then File → Export → Export As SVG was used. The gateway's
   in-page VectorCraft adapter captured the export in memory and submitted it
   automatically; no browser download or manual upload occurred.
5. The gateway save POST returned HTTP 200. VectorCraft's host page displayed
   “Saved — new version …”. Seafile library history showed
   `Modified "synthetic.svg"` after `Added "synthetic.svg"`.
6. Opened `synthetic.svg` again from the Seafile file list. This created a
   distinct gateway/editor session; its document GET returned HTTP 200, and
   the new VectorCraft instance displayed the rectangle. The first editor was
   not explicitly closed before this second open.

The observed operation therefore demonstrates Seafile version creation and
fresh storage-backed reopen for this synthetic SVG. It is specifically the
VectorCraft page-API/export adapter, not the shared `?host=parent` save/ACK
protocol. The export completed at the host and the fresh session retained the
edit. In the save screenshot VectorCraft's tab title still has an asterisk:
SVG export does not clear the editor's native dirty marker. The host's version
confirmation is visible; the native marker behavior remains a UX limitation.

The browser harness did not hash the editor-produced export bytes against a
Seafile content readback. Exact byte provenance and direct API readback are
**NOT VERIFIED**. The evidence establishes the saved edit through the history
event and fresh editor rendering, not byte identity.

## Candidate and deployment scope

- The deployed VectorCraft bundle is the exact GR-058 candidate. Its verifier
  passed against the active static root: nine files, all sizes/SHA-256 values,
  index references, and SHA-384 integrity values matched.
- The active dispatcher adds SVG → VectorCraft while retaining DOCX →
  WordCraft, XLSX → GridCraft, and PDF → PdfCraft.
- Seahub's extension allowlist contains SVG alongside DOCX, XLSX and PDF, and
  remains limited to the same synthetic library. `ENABLE_ONLYOFFICE=True`
  remained set. No ONLYOFFICE settings or routes were changed. A post-change
  ONLYOFFICE edit/save regression was not run.
- A private rollback archive was retained outside Git. The GR-060 dedicated
  LXC remains stopped; this test used the existing gateway deployment.

## Evidence

- [Save confirmation](reviews/GR-063/runtime/vectorcraft-save-confirmed.png)
- [Fresh Seafile-backed reopen](reviews/GR-063/runtime/vectorcraft-fresh-reopen.png)
- [Sanitized browser observations](reviews/GR-063/runtime/browser-observations.txt)
- [Artifact checksums](reviews/GR-063/SHA256SUMS)
- [Evidence README](reviews/GR-063/README.md)

Screenshots contain only the synthetic SVG editor. Private origin, library ID,
account identity, and gateway session capabilities are omitted from retained
evidence.

## Limits

- One SVG fixture, one synthetic library, one save, and one second file-list
  open in a distinct session were exercised. The first editor was not
  explicitly closed before the second open.
- The app's Ctrl+S path opened Save As; the tested host persistence path was
  Export As SVG captured by the in-page adapter. This UX difference is
  explicit and is not represented as native-save cleanliness.
- Editor-export-to-Seafile byte identity, direct content API readback,
  permission revocation, external writers, capability expiry/replay, response
  loss, concurrency, proxy/TLS security, optimized deployment hardening, and
  post-change ONLYOFFICE edit/save remain **NOT VERIFIED**.
- The GR-058 candidate was source-built with optimized `wasm-opt -Oz`, but this
  work item did not independently rebuild it. Release-binary reproducibility
  remains **NOT VERIFIED** as documented by GR-058.
- Independent R1–R2 returned bounded PROVISIONAL PASS with no remaining
  findings; R1's wording MINOR was corrected. R2 did not replay the browser or
  independently verify live service observations. Project GPT remains
  **INCOMPLETE** and upstream publication remains **LOCKED**.
