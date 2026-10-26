# GR-063 evidence — VectorCraft on synthetic Seafile

This bundle records the actual candidate's Seafile file-list open, SVG edit,
gateway save, history event, and fresh file-list reopen described in
[`docs/GR-063-VECTORCRAFT-REAL-SEAFILE-ROUNDTRIP.md`](../../GR-063-VECTORCRAFT-REAL-SEAFILE-ROUNDTRIP.md).

## Artifacts

- `runtime/vectorcraft-save-confirmed.png` — added rectangle and host-page
  “Saved — new version …” confirmation.
- `runtime/vectorcraft-fresh-reopen.png` — a second VectorCraft session opened
  from Seafile, showing the rectangle after loading the stored file. The first
  editor was not explicitly closed before this open.
- `runtime/browser-observations.txt` — sanitized route outcomes and UI
  observations; private origins and session identifiers are omitted.
- `checks.txt` — exact local candidate, dispatcher, screenshot-download-list,
  checksum, and whitespace-check results. These are implementer-run checks;
  the independent reviewer did not access the live service.
- `SHA256SUMS` — checksums for the retained PNGs and transcript.

## Candidate and scope checks

The active static assets are the GR-058 candidate. Recheck membership, hashes,
index references, and integrity values with:

```sh
python3 docs/reviews/GR-058/verify_candidate.py \
  --static-root /home/roddy/.cache/artcraft-storage-lab/gr059-deployment/integration/static
```

The test used VectorCraft's existing page-API adapter in
`integration/gateway/hostpage.py`; the SVG route does not use the common
`?host=parent` protocol. The active dispatcher retains DOCX/WordCraft,
XLSX/GridCraft, and PDF/PdfCraft while adding SVG/VectorCraft. The extension
allowlist remains scoped to the same synthetic library. `ENABLE_ONLYOFFICE=True`
was preserved and no ONLYOFFICE settings/routes were changed; no post-change
ONLYOFFICE edit/save test was run.

## Evidence boundary

The editor's SVG export was captured by the gateway page in memory and submitted
to the session save route; no browser download or manual upload was used. The
successful host confirmation, Seafile history `Modified` event, and fresh
Seafile-list reopen with the rectangle are observed. The browser did not retain
or hash the exported bytes against a content API readback, so byte provenance
is **NOT VERIFIED**. VectorCraft's native dirty asterisk also remained visible
after export, despite the host confirmation; this UX limitation is documented
in the report.

The private rollback archive remains outside Git. The dedicated GR-060 LXC is
stopped. Production, permission-revocation, concurrency, response-loss,
deployment-security, optimized-hardening, and post-change ONLYOFFICE checks
remain unverified. Independent R1–R2 returned bounded PROVISIONAL PASS with no
remaining findings; R1's wording MINOR was corrected. R2 did not replay the
browser or verify live service state. This is not a project GPT PASS,
production-readiness claim, or upstream authorization.
