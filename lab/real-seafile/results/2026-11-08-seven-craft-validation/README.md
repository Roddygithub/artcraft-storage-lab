# Combined seven-editor candidate

Application source `4f4b2dc`, opt-in `--pptx`, official unpatched DeckCraft
v0.16.0 added to the previously verified six-editor asset snapshot. No editor
or Seafile patch. Generated editor configuration and exact source/static-manifest
hashes are recorded in provenance.json. The default six-editor configuration
has not been changed or silently promoted.

Fresh rootless synthetic Seafile: HTTP **40/40**, browser **132/132**, launcher
exit **0**. Offline **19/19 command groups**. Project containers were absent after
cleanup; focused PPTX and HTTPS project containers were also absent.

WordCraft DOCX, GridCraft XLSX, PdfCraft AcroForm, CADCraft DXF, VectorCraft SVG,
FigCraft and DeckCraft PPTX each exercised actual edits, host-confirmed saves,
attributed Seafile versions and fresh reopen assertions. No downloads counted
as saves. The PPTX retains original title and typed marker in the same format.
This is bounded synthetic coverage, not full document or format fidelity.

Sanitized checks and raw-result hashes are retained. Available synthetic payloads
were scanned against generated lab credentials. The harness does not retain
GridCraft XLSX/CADCraft DXF payloads; those have assertion evidence only. No
visual screenshot review is claimed for this combined run. Focused PPTX and
HTTPS screenshots were inspected separately in their retained evidence folders.
The PPTX source has an observed Arial fallback-font warning.

Run `python3 lab/real-seafile/results/2026-11-08-seven-craft-validation/verify.py`.
Remaining viewing formats, hardware/clipboard/font/unload acceptance and independent
forensic/GPT review remain open. Production Seafile was untouched; upstream LOCKED.
