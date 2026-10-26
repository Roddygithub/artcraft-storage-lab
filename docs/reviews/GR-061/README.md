# GR-061 evidence — GridCraft on synthetic Seafile

This bundle records the actual-WASM Seafile file-list open, edit, acknowledged
save, history event, and fresh file-list reopen described in
[`docs/GR-061-GRIDCRAFT-REAL-SEAFILE-ROUNDTRIP.md`](../../GR-061-GRIDCRAFT-REAL-SEAFILE-ROUNDTRIP.md).

## Files

- `runtime/gridcraft-save-confirmed.png` — B2 and B3 show 1337; GridCraft
  displays its successful new-version confirmation.
- `runtime/gridcraft-seafile-reopen.png` — a fresh Seafile-triggered editor
  session shows B2=1337 and B3=1337 with the formula visible.
- `runtime/browser-observations.txt` — sanitized routes, statuses and history
  observation. Session IDs and private host details are omitted.
- `SHA256SUMS` — digests for the retained screenshots and transcript.

The editor candidate is GR-056's exact staged bundle. Its source pin, patch,
transport, asset hashes, and synthetic browser smoke are recorded in
[`docs/reviews/GR-056/README.md`](../GR-056/README.md). The deployed bundle was
independently rechecked with:

```sh
python3 docs/reviews/GR-056/verify_candidate.py \
  --static-root /home/roddy/.cache/artcraft-storage-lab/gr059-deployment/integration/static
```

That command verifies the candidate bytes and provenance; it does not contact
Seafile. The retained browser evidence is specific to the owner's private
instance and is not a standalone replay fixture.

## Safety boundary

Only the named synthetic library was in the ArtCraft repository allowlist.
The only new extension was XLSX, added alongside the existing DOCX route. The
XLSX fixture was uploaded as setup; the edited workbook was stored through the
editor save protocol. ONLYOFFICE remained enabled. No production files,
unrelated libraries, upstream repositories, or private services outside this
test were accessed.

## Review state

Independent R1–R3 reviews are bounded PROVISIONAL PASS with no blocker or major;
the two documentation minors were corrected. Exact historical comparison with
the unavailable R1/R2 snapshots was not verified. The detailed review record is
[`INDEPENDENT-REVIEWS.md`](INDEPENDENT-REVIEWS.md). This is not a project-level
GPT verdict, production-readiness claim, or authorization for upstream
publication.
