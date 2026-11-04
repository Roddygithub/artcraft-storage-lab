# GR-084 exact-candidate GPT review — R2

**Reviewed candidate:** `a83c784228e3cb1ed84593baf088d8567c8c2e40`.

**Verdict:** changes required. One P2 and one P3; no P1.

## Findings

1. **P2 — retained PDF did not match the recorded runtime identity.** The report
   and README claimed a 2,385-byte readback with SHA-256
   `69c2f8989bf0345a4620483fffaf5c72c27e4e2486b6099032ccb0d3b25af35b`, but the
   retained PDF blob was 2,386 bytes with SHA-256
   `d1bb31792966cf0b5551029e56224074629e2590c9a6865be92ce70d6599dad2`.
   Both private run-7 relay-save and Seafile-readback files are 2,386 bytes and
   match the latter digest. Documentation and the observation record now match
   the retained file.

2. **P3 — malformed xref at EOF could loop indefinitely.** The blank-line loop
   in `_current_pdf_object_bodies()` could reread EOF without advancing. The
   reader now returns a failure sentinel at EOF and the caller checks progress.
   A regression exercises truncated-xref input without a timeout.

R1's P2 is closed: current xref entries take precedence and the regression
rejects a superseded matching value. The README, report, matrix, status, history,
and queue now describe the corrected archive identity and helper behavior.
The successful runtime itself was not rerun for the malformed-input-only
helper change; full PDF parser support remains out of scope.

Exact-commit GPT R3 review is pending. No project-level PASS or upstream
authorization is implied.
