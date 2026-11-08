# Parent evidence inventory — independent forensic review pending

The earlier version of this file incorrectly described a completed forensic
review and aggregate HTTP checks as per-editor coverage. Those claims are
withdrawn. This inventory is not a project gate or an independent review.

| Recorded private run | Passing browser assertions | Boundary |
| --- | --- | --- |
| WordCraft | 28 | First save freshly reopened; second save has storage readback |
| GridCraft | 27 | First save freshly reopened; second save has storage readback |
| PdfCraft | 18 | Synthetic AcroForm only |
| CADCraft | 20 | Synthetic circle only |
| VectorCraft | 20 | Released bundle plus declared JavaScript shim |
| FigCraft | 21 | Released bundle plus declared JavaScript shim |
| ONLYOFFICE | 11 | Two saves; final fresh reopen missing; semantic parser correction pending replay |

These counts were independently read from private summaries in the bounded
recovery audit of `2825f4c`. They are retained harness assertions, not an
independent replay. The six Craft runs identify the earlier shim at `4e7d637`,
not the subsequent rewrite at `fccee4d`. That rewrite failed the existing shim
regression and has been replaced with the earlier tested implementation.
New source review and final runtime evidence remain required.

The HTTP slice is one aggregate 46-check suite. It does not establish seven
independent CRUD/locking suites. Its direct read-only-token probe reproduces
Seahub accepting an unauthorized write; it is a disclosed host limitation,
not a successful host rejection. The bridge separately checks permissions.

The seven private closure runs have not been committed as a complete sanitized
evidence bundle. Not every run retains relay/readback payloads or history JSON.
Private hashes alone cannot authenticate chronology, cleanup, loaded assets or
isolation. Existing committed GR-085/GR-086 evidence has earlier source identities.

Before freeze: correct ONLYOFFICE predicates and final reopen; retain and verify
sanitized exact-source evidence; complete HTTPS acceptance; then obtain an
independent forensic review followed by a fresh independent GPT project gate.
`docs/PROJECT-CLOSURE.md` is the current ledger. Project INCOMPLETE; upstream LOCKED.
