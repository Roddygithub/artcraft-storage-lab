# GR-068 evidence — PdfCraft on synthetic Seafile

This bundle records the GR-057 PdfCraft Web candidate opening the existing
synthetic `form.pdf`, saving a visible AcroForm edit through the host protocol,
and reopening the stored file from the Seafile list in a fresh editor session.

## Evidence

- [`runtime/save-confirmation.png`](runtime/save-confirmation.png) — final form
  value and Seafile's new-version confirmation.
- [`runtime/fresh-reopen.png`](runtime/fresh-reopen.png) — the saved form value
  after a new file-list open.
- [`runtime/browser-observations.txt`](runtime/browser-observations.txt) —
  sanitized event sequence and HTTP statuses. Private origin, repository ID,
  session capability, and account identity are omitted.
- [`candidate-inventory.json`](candidate-inventory.json) and
  [`verify_candidate.py`](verify_candidate.py) — three served assets, sizes,
  and hashes for the staged candidate and active static root.
- [`SHA256SUMS`](SHA256SUMS) — screenshot and transcript digests.

The existing `pdf` route and allowlist were used without changes. No Seahub
settings, dispatch entries, services, or ONLYOFFICE configuration were
modified. The existing document had two earlier versions before this test;
the final history page showed the current 3.0 KB version and two older
versions. An early canceled edit attempt displayed a host version message, but
its separate revision is not claimed.

The full scope and limitations are in the
[GR-068 report](../../GR-068-PDFCRAFT-REAL-SEAFILE-ROUNDTRIP.md). This is not a
project-level GPT PASS or upstream authorization.

R1 returned a bounded PROVISIONAL PASS with no findings. The exact review
record is in [`INDEPENDENT-REVIEW-R1.md`](INDEPENDENT-REVIEW-R1.md).
