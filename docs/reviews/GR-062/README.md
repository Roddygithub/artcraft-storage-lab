# GR-062 evidence — PdfCraft on synthetic Seafile

This bundle records the actual-WASM Seafile file-list open, AcroForm edit,
acknowledged save, history event, and fresh file-list reopen described in
[`docs/GR-062-PDFCRAFT-REAL-SEAFILE-ROUNDTRIP.md`](../../GR-062-PDFCRAFT-REAL-SEAFILE-ROUNDTRIP.md).

## Artifacts

- `runtime/pdfcraft-save-confirmed.png` — edited field and PdfCraft's
  successful new-version confirmation.
- `runtime/pdfcraft-seafile-reopen.png` — a fresh Seafile-triggered PdfCraft
  session with the edited field intact.
- `runtime/browser-observations.txt` — sanitized routes, HTTP results, and
  history observation. Private origins and session IDs are omitted.
- `SHA256SUMS` — digests for retained screenshots and transcript.

## Candidate and deployment checks

PdfCraft is the exact GR-057 candidate. Its source pin, patch, transport,
build settings and asset inventory are recorded in
[`docs/reviews/GR-057/README.md`](../GR-057/README.md). The candidate verifier
passed against the live static root:

```sh
python3 docs/reviews/GR-057/verify_candidate.py \
  --static-root /home/roddy/.cache/artcraft-storage-lab/gr059-deployment/integration/static
```

That command checks exact file membership, sizes, SHA-256 hashes, and index
references; it does not contact Seafile. The separate source/build provenance
record is in the GR-057 report. GR-062 added only the PDF route and PDF
extension to the same synthetic-library allowlist. DOCX/WordCraft and
XLSX/GridCraft remain routed.

## Safety boundary

Only the existing synthetic library was in the ArtCraft repository allowlist.
The uploaded AcroForm was a generated test fixture; its upload was setup only.
The edited value was persisted by the editor-to-gateway-to-Seafile save path.
`ENABLE_ONLYOFFICE=True` remained set, and no ONLYOFFICE settings or routes
were changed. The private rollback archive is outside Git. The GR-060 LXC
remains stopped.

## Review state

Independent R1–R2 reviews returned bounded PROVISIONAL PASS with no blocker or
major; R1's documentation MINOR was corrected and closed in R2. Work-item
status is **GPT REVIEW PENDING**; project status remains **INCOMPLETE** and
upstream publication remains **LOCKED**. This is not a project-level GPT
verdict or production readiness claim. See `INDEPENDENT-REVIEW-R1.md` and
`INDEPENDENT-REVIEW-R2.md`.
