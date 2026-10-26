# GR-062 — PdfCraft real synthetic Seafile roundtrip

Date: 2026-10-26

Status: **GPT REVIEW PENDING**

Scope: one synthetic AcroForm PDF in the existing synthetic Seafile library.
The exact GR-057 PdfCraft candidate was staged on the existing GR-059 gateway
and dispatched only for PDF in that already allowlisted library. Existing
DOCX → WordCraft and XLSX → GridCraft routes were preserved. No production
documents were opened or changed.

## Result

The actual PdfCraft Web/WASM candidate completed this flow through the owner's
authenticated Seafile session:

1. Uploaded the source `form.pdf` from the pinned PdfCraft repository through
   Seafile's file-upload UI. The 1,744-byte AcroForm fixture upload was setup
   only; it was not used to persist the edit. A separate 655-byte synthetic
   PDF was also opened as a routing check and was not edited.
2. Clicked `form.pdf` in the Seafile file list. Seafile handed it to the
   gateway; the exact staged PdfCraft HTML, JavaScript and WASM loaded, and the
   gateway document request returned HTTP 200. PdfCraft reported five
   interactive form fields.
3. Entered `GR062 PDF host save roundtrip` in a form field. The editor showed
   unsaved changes.
4. Pressed Ctrl+S. The gateway save POST returned HTTP 200, PdfCraft displayed
   “Saved — new version …”, and a subsequent dirty-state update returned HTTP
   200.
5. Seafile's authenticated library-history UI showed `Modified "form.pdf"`
   after `Added "form.pdf"`.
6. Clicked `form.pdf` again in the Seafile file list. A different gateway
   session and a fresh PdfCraft editor instance fetched the stored document;
   the edited AcroForm value was visible after reopen.

This demonstrates one real Seafile versioned save and a fresh Seafile-backed
reopen for the synthetic PDF. The fixture upload is setup only. No manual
upload of the edited bytes occurred. The browser harness did not independently
hash the editor save-message bytes against Seafile readback, and no direct
content API readback was obtained; byte-for-byte provenance is **NOT VERIFIED**.

## Scoped deployment

- The deployed PdfCraft assets passed the GR-057 candidate verifier against the
  live static root before and after staging. The inventory covers three served
  files; the index references the recorded JS and WASM files.
- The active gateway dispatcher now maps PDF to PdfCraft while retaining DOCX
  to WordCraft and XLSX to GridCraft.
- Seahub's ArtCraft extension allowlist now contains DOCX, XLSX and PDF and
  remains restricted to the same single synthetic library.
- `ENABLE_ONLYOFFICE=True` was verified after the Seahub restart. No
  ONLYOFFICE settings or routes were changed. An ONLYOFFICE edit/save/version
  regression was not run in GR-062.
- Before deployment, a private rollback archive of the current Seahub settings,
  dispatcher and existing WordCraft/GridCraft static trees was retained outside
  Git. The dedicated GR-060 LXC remains stopped; this used the existing GR-059
  gateway.

## Evidence

- [Save confirmation](reviews/GR-062/runtime/pdfcraft-save-confirmed.png)
- [Fresh Seafile reopen](reviews/GR-062/runtime/pdfcraft-seafile-reopen.png)
- [Sanitized browser observations](reviews/GR-062/runtime/browser-observations.txt)
- [Artifact checksums](reviews/GR-062/SHA256SUMS)
- [Evidence README](reviews/GR-062/README.md)

The screenshots show only the synthetic PDF editor and its form content. No
private hostname, library identifier, account name, or session capability is
retained.

## Limits

- One synthetic PDF, one library, one browser session flow, and one candidate
  build were exercised.
- Byte-level editor-message to storage provenance, API readback, permission
  revocation, external writers, capability expiry/replay, response loss,
  concurrency, proxy/TLS security, optimized `wasm-opt` output, and a
  post-change ONLYOFFICE edit/save regression remain **NOT VERIFIED**.
- The candidate's build used `data-wasm-opt=0`; this is functional runtime
  evidence, not an optimized production bundle.
- Independent R1–R2 reviews returned bounded PROVISIONAL PASS with no blocker
  or major; R1's documentation MINOR was corrected and closed in R2. No
  project-level GPT PASS is claimed. Project status remains **INCOMPLETE**;
  upstream publication remains **LOCKED**.
