# GR-040 — ONLYOFFICE regression evidence

**Claim:** On 2026-10-25, an actual ONLYOFFICE browser editor opened a synthetic
Seafile DOCX, saved two UI edits through the existing callback, caused two new
Seafile versions, and reopened the final content from a fresh Seahub file-list
click.

**Scope:** isolated synthetic Seahub/C-fileserver and ONLYOFFICE Document
Server only. No production or upstream service was accessed. This closes the
synthetic preservation regression, not production compatibility or the overall
project GPT review.

## Seafile records

| State | Content ID | File size | History count | Latest commit | Readback SHA-256 |
|---|---|---:|---:|---|---|
| Before ONLYOFFICE edits | `4013284e8809fc29b350714340e05ba4dd24ee0d` | 5,305 B | 3 | `f7c006db6b699f8aae3f9a76e785d0bbead01da4` | Not captured before the test |
| After first edit (`gr039seafilecommit`) | `fbacbb91d1ea637db256039225c848f3695d7a96` | 24,950 B | 4 | `d306b22d3cfbde43d3f0965e5fe89417ce08fb87` | `3352c6b8daca84b279d6250ec7658a15d590b116b2f85708d905d49a6553fcac` |
| Final edit (`gr040onlyofficeack`) | `c9989d09d742f02ca70b9f7e2d3d2a18c34ee67c` | 24,960 B | 5 | `699e43932253a0abf9b58e498490aff62d382ca5` | `861c00c56e1b9ae42d1d99f5ae9feed6e2d0a038178fbc6b41343e2559c9c2fa` |

Both post-save readbacks were HTTP 200 and valid DOCX ZIPs. Final
`word/document.xml` contains both markers. After that API readback, a fresh
Seahub route loaded the document, and a click on the file row opened a second
fresh editor page; both displayed the final markers. Seahub access logs show
the corresponding ONLYOFFICE callback POSTs returning HTTP 200. The sanitized
runtime transcript keeps only non-secret facts.

## Retained artifacts

- [`onlyoffice-editor-saved-status.png`](runtime/onlyoffice-editor-saved-status.png)
  — browser editor after the second edit, showing the marker and
  `All changes saved`.
- [`onlyoffice-storage-reopen.png`](runtime/onlyoffice-storage-reopen.png) —
  new Seahub route after final API readback.
- [`onlyoffice-file-list-reopen.png`](runtime/onlyoffice-file-list-reopen.png)
  — editor opened by clicking the file in the library list.
- [`seafile-readback.json`](runtime/seafile-readback.json) — version metadata,
  byte count/hash, and ZIP/content assertions; no token or file bytes.
- [`sanitized-runtime-transcript.txt`](runtime/sanitized-runtime-transcript.txt)
  — browser steps, callback statuses, and environment/rollback notes.
- [`SHA256SUMS`](runtime/SHA256SUMS) — checksums for retained evidence files.

## Independent review and remaining scope

Independent exact-evidence review: **PROVISIONAL ACCEPT**, no blocker or major;
three minor limitations are recorded in
[`INDEPENDENT-REVIEW-R1.md`](INDEPENDENT-REVIEW-R1.md). The reviewer verified
the retained checksums and cross-document consistency but did not replay the
historical browser run. The remaining limitations are the still-running
synthetic Document Server container, no hash for the browser-to-callback body,
and the test-specific loopback mapping/relay.

NOT VERIFIED: production ONLYOFFICE preservation; TLS, reverse proxy, CSP,
CSRF, and adversarial-frame security; other file types and Document Server
versions; cross-version compatibility; callback payload byte identity; and
project-wide GPT REVIEW PASS. These results do not unlock upstream publication.
