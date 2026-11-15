# Validation checkpoint — candidate source `4a5ab57` (2026-11-15)

This short checkpoint is the continuation entry point. Do not re-read the
historical GR corpus to resume routine validation.

| Scope | State | Evidence |
| --- | --- | --- |
| Active offline checks | 20/20 command groups PASS at exact source `4a5ab576da0e0a0f227e672d8ea6258ea90c9acc` | `../lab/real-seafile/results/2026-11-15-offline-validation/` |
| Core Seafile DOCX edit/save/reopen | HTTP slice 56/56; browser 58/58; two typed saves create versions and fresh-session reopen preserves edits | `../lab/real-seafile/results/2026-11-15-seafile-render-readonly/` |
| Legacy read-only Seafile routes | 34/34 route assertions; exact fixture bytes, OCR marker/value, no download, no version write, host reports `read-only` | `../lab/real-seafile/results/2026-11-15-seafile-render-readonly/` |
| Legacy format status | `VIEW_SUPPORTED`: ODT, ODS, CSV, PPSX. `UNSUPPORTED`: DOC, XLS, FODS, FODT, FODP, PPT, ODP, PPS | `ONLYOFFICE-REPLACEMENT-MATRIX.md` |
| Bundle render diagnosis | DOC/XLS/ODT/ODS/CSV/PPSX markers verified in standalone bundles; FODS shows flat XML. DOC/XLS host failure was observed in exploratory runs, not retained as an exact-source screenshot | `../lab/real-seafile/results/2026-11-15-legacy-render-probe/` |
| Default ArtCraft edit/save workflows | DOCX, XLSX, PPTX evidence remains the prior synthetic baseline; broad document/workbook/deck fidelity NOT VERIFIED | `../lab/real-seafile/results/2026-11-08-wordcraft-corpus-recovery/`, `../lab/real-seafile/results/2026-11-08-seven-craft-validation/` |
| HTTPS automated WordCraft replay | HTTP 40/40, browser 28/28 at source `7961db5`; does not cover physical-device acceptance | `../lab/real-seafile/results/2026-11-08-wordcraft-https-current/` |
| Direct read-only WOPI PutFile | Seafile CE 13.0.28 accepts direct `PutFile` with read-only token; bridge relay refuses it, but token is browser-visible | `../bridge/README.md`, `../lab/real-seafile/results/2026-11-15-seafile-render-readonly/` |
| Hardware WebGPU/clipboard/fonts/unload acceptance | NOT VERIFIED | `../lab/real-seafile/README.md` checklist |
| Independent and final review | Prior audit at `cd4c8ba` was PROVISIONAL PASS with six minors; implementation/doc delta awaits new independent review and GPT-6 Sol gate | `../reviews/PROJECT-CLOSURE-20261108/`, current candidate dossier |
| Mechanical evidence self-audit | PASS: 20 evidence directories, hashes/verifiers/provenance, 2 loose JSON files and secret scan at source `4a5ab57`; not independent | `../scripts/forensic-audit.py`; private run summary |
| Owner's live Seafile server | Read-only HTTPS/TLS and ping PASS; inspected release is older than tested CE 13.0.28, ArtCraft bridge is absent, and synthetic library is not shared. Authenticated browser/edit/save NOT VERIFIED | private infrastructure discovery; no production writes |

ArtCraft is the intended suite. ONLYOFFICE retirement is authorized, but
production is outside these tests and remains untouched. Upstream remains
LOCKED. An automated subset PASS is not full format coverage or project approval.

The prior independent audit and follow-up fixes are recorded in repository
history. Its verdict remains PROVISIONAL; owner-server and hardware acceptance
and the GPT gate remain open.

## Repeat checks with compact output

```sh
# With Playwright, Pillow and its Chromium already installed in the Python environment:
python3 scripts/validate-candidate.py --output /absolute/new/private-check-dir
# Or use an isolated dependency environment (Chromium still required):
uv run --with playwright --with pillow python scripts/validate-candidate.py \
  --output /absolute/new/private-check-dir
# Real Seafile/browser run: no editor filter means all six default editors.
python3 lab/real-seafile/local.py --run-dir /absolute/new/private-lab-dir \
  --static /absolute/verified-static --manifest /absolute/verified-manifest.json
```

The compact runner uses four workers, captures full per-command private logs,
prints only totals and failing command names, returns nonzero on any failure,
and records command exits/source SHA in `summary.json`. It does not run legacy
integration tests, mutate production or confer independent review approval.

To save tokens: read this file and `git status --short`; run the compact runner;
inspect only failed logs; retain sanitized runtime totals and exact provenance.
Do not repeatedly dump successful logs, historical reports or bundle contents.

The HTTPS reopened-saved screenshot was inspected: both typed markers are
visible with the table and the saved-to-Seafile host status. This does not
prove full pagination or font fidelity.

## Next unresolved work

1. Reproduce the authenticated HTTPS workflow on the owner's Seafile with a
   synthetic document. The credentials supplied in chat have not been used.
   The existing synthetic library must be shared to the supplied account, or
   the owner must authorize creation of a dedicated test library. No existing
   user files will be changed. The inspected live release is older than the
   CE 13.0.28 candidate and has no ArtCraft bridge; an upgrade or deployment is
   a separate owner decision and is not authorized by this validation task.
2. Run the human checklist for WebGPU, clipboard, exact fonts, popups, dirty
   close, refused saves and network recovery.
3. Perform a mechanical evidence audit, then independent forensic review and
   GPT-6 Sol adversarial review of the frozen exact candidate SHA. Existing free
   reviews remain PROVISIONAL and do not satisfy this gate.
4. Replacement completeness remains PARTIAL: eight legacy viewing formats are
   unrouted, arbitrary-file fidelity is unknown, and no legacy save is claimed.
   No converter or LibreOffice product path is planned.

The default six-editor candidate remains unchanged. `--pptx` is opt-in and the
four legacy routes are also opt-in and read-only.
