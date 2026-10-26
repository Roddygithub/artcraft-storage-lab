# GR-078 — combined five-route synthetic Seafile browser replay

## Result

On 2026-10-26, all five routes in the tracked dispatcher were exercised from
Seafile Web in the existing synthetic library. Each file opened in its mapped
ArtCraft editor, accepted an edit, and showed the edit after the editor tab was
closed and the file reopened from Seafile. GridCraft, PdfCraft and VectorCraft
screenshots show a new-version ID. The WordCraft retained screenshots show the
edit and saved state; a new-version confirmation was observed during the run
but was not captured. PhotoCraft's host save returned HTTP 200 and its editor
returned to a clean state. No manual download or upload was used. Per-route
screenshots and a sanitized observation record are in
[`reviews/GR-078/runtime/`](reviews/GR-078/runtime/).

This closes the combined synthetic browser replay gap identified in GR-077 for
the running lab deployment used in this session. It does not mean the four
non-PhotoCraft bundles were promoted into this checkout's ignored
`integration/static/`; that directory still contains only the PhotoCraft
bundle. It also does not establish production readiness, byte-for-byte
editor-payload/readback identity for all apps, permissions, conflicts, proxy or
CSP behavior, or ONLYOFFICE post-change UI behavior.

## Route results

| Seafile file | Dispatcher route | Edit and save evidence | Reopen result |
|---|---|---|---|
| `synthetic.docx` | `.docx` → WordCraft | Added `gr078docx`; retained screenshot shows marker and saved state. New-version confirmation was observed during the run but not captured | Marker remained visible after close/reopen |
| `synthetic.xlsx` | `.xlsx` → GridCraft | Changed B2 from 1337 to 1338; formula cell B3 recalculated to 1338; save displayed version `5724ff96254801716d84bb07b8e8705060d410f9` | B2 and formula result remained 1338 |
| `form.pdf` | `.pdf` → PdfCraft | Changed the first interactive field to `GR078savededit`; save displayed version `9e9a8b9a7e2fa90df924cab8d6da9798676e7630` | Field value remained visible |
| `synthetic.svg` | `.svg` → VectorCraft | Added a 20 × 20 px rectangle and used Export As SVG; host save displayed version `55962c8fedfe0e0a25a547a8a9b1992f8daf9b32` | New rectangle remained visible |
| `photocraft-fixture/photocraft-smoke.pcraft` | `.pcraft` → PhotoCraft | Added a layer; Ctrl+S returned HTTP 200 and the editor showed its clean/saved state | Added layer remained after tab close and reopen |

For PhotoCraft, the in-app File → Close command is unavailable for a host-bound
document. The editor tab was closed and reopened from Seafile; this is the
browser close/reopen boundary used here. The other editors were also closed by
closing their browser tabs. This replay confirms the app save UI and host save
path for these synthetic files; it does not independently query Seafile's
history page or compare every editor payload byte-for-byte with a readback.

## Scope and preservation

- The existing `ArtCraft GPT Review Synthetic` library and synthetic documents
  were used; no production library or user document was accessed.
- No Seafile configuration, dispatcher, extension allow-list, ONLYOFFICE
  configuration, or service was changed during this replay.
- The run was sequential in one browser profile and one synthetic library; it
  exercised each of the five tracked routes against the active lab deployment.
- The ONLYOFFICE UI regression remains inconclusive as recorded in GR-076. This
  work does not change or replace the separate GR-072 ONLYOFFICE smoke.
- Screenshots retain only the synthetic editor content. Network paths and
  session capability identifiers are omitted from the evidence record.

R1 returned **MAJOR — remediation required**; all findings were addressed.
R2 verified the fixes and returned **PROVISIONAL PASS**, with no new findings.
Reviews and responses are recorded in `docs/reviews/GR-078/`. Free-model
verdicts remain PROVISIONAL; project GPT review is still PENDING and upstream
publication remains LOCKED.
