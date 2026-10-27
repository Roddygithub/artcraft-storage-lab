# Independent PdfCraft v0.14.0 release evidence review R1

**Verdict: PROVISIONAL PASS for the bounded release smoke, with two LOW
findings.** This was a read-only review of the exact-base port, release build,
bundle manifest, browser smoke logs, runtime JSON/screenshots, and cross-file
claims. No edits, tests, builds, browser sessions, or services were used.

1. **LOW — the browser harness did not assert the reopened marker.** The test
   hardcoded `visible_edit` and inferred reopen from the ready count. The
   retained screenshots did show the marker in the fresh editor, so the current
   bounded claim was supported by manual inspection, but a future automated
   PASS could miss a rendering/readback regression. Remediation: assert the
   marker from the captured fresh-editor image.
2. **LOW — changed-file count was inaccurate.** The report said six source
   files changed; the port changes seven non-vendored source/manifest paths
   plus the packaged shared transport snapshot. Remediation: correct the count.

The reviewed evidence matched the release source, patch, test source, served
bundle, fixture, and screenshots. The build log records exit 0 and `wasm-opt`
131 `-Oz`; R3 records the correct before/after hashes. Seafile persistence,
identity binding, and replacement/Save As refusal remain **NOT VERIFIED**.

See [`RESPONSE-PDFCRAFT-RELEASE-REVIEW-R1.md`](RESPONSE-PDFCRAFT-RELEASE-REVIEW-R1.md).
