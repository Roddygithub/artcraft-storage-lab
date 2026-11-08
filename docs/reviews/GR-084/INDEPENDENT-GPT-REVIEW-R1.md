# GR-084 exact-candidate GPT review — R1

**Reviewed candidate:** `c09933c7f45b49e6b2d518c1589fc1a52863619e`.

**Verdict:** one P2 finding; no other P1–P3 findings identified in scope.

## Finding

`pdf_text_field_has_value()` scanned every textual object body in a PDF,
including superseded object revisions. An older matching AcroForm `/V` could
therefore satisfy the saved-value assertion even if a later incremental update
replaced that field value. This weakened the semantic save/readback check.

## Remediation and follow-up

The assertion now follows the active classic-xref revision chain, taking the
newest entry for each object and failing closed for unsupported or malformed
xref framing. The regression appends two revisions for the same field and
checks that the earlier value fails while the current value passes. The
focused test passed, and the corrected source was included in a fresh isolated
Seafile/PdfCraft replay (HTTP 48/48; browser 18/18). The exact resulting commit
was pending independent GPT R2 review when this record was written. R2 returned
two further findings; their outcomes are recorded in
`INDEPENDENT-GPT-REVIEW-R2.md`.

## Limits

This helper is a narrow assertion for the retained PdfCraft fixture/output,
not a complete PDF parser. Xref streams and object streams are explicitly
unsupported. One synthetic AcroForm document was exercised. Full PDF validity,
other documents, production, human HTTPS, and project-level completion remain
**NOT VERIFIED**. The run was direct parent work, not Aptarchy completion.
