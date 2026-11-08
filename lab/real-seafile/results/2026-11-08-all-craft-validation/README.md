# Six-editor validation, Craft-only

Exact source `8369e8f`; fresh rootless synthetic Seafile, internal HTTP.
HTTP **40/40**, Chromium **119/119**, offline command groups **18/18**;
launcher exit **0** and project containers absent after cleanup. No ONLYOFFICE
service was configured or started. No production change or upstream publication.

The browser covered WordCraft DOCX, GridCraft XLSX, PdfCraft AcroForm,
CADCraft DXF, VectorCraft SVG and FigCraft with real semantic edits,
Seafile-attributed versions and fresh editor reopen assertions. This is the
six-editor subset, not all office formats or broad document fidelity.
GridCraft XLSX and CADCraft DXF payloads were not retained by the harness;
their semantic assertions are recorded in browser.json. Retained payloads
for the other four editors are synthetic and scanned against the generated
lab credential values before retention. No visual screenshot review is claimed.

The source snapshot and verified static-manifest identity are in provenance.json.
The same assets as the prior structure-recovery run were reused, with their
existing ingestion provenance. No new bundle was introduced. JSON omits raw
URLs, tokens, user identities and version IDs; hashes identify private originals.
The first offline attempt had 17/18 groups because system Python lacked
Playwright; the isolated uv environment completed all 18 groups.

Run `python3 lab/real-seafile/results/2026-11-08-all-craft-validation/verify.py`.
For new runs and remaining gaps, read `docs/VALIDATION-STATE.md` and use
`scripts/validate-candidate.py`; inspect only failing private logs.
HTTPS desktop acceptance, remaining office formats and independent forensic/GPT
review remain NOT VERIFIED. Project INCOMPLETE; upstream LOCKED.
