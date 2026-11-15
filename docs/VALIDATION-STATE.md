# Validation checkpoint — tested source `be51c3b` (2026-11-15)

This short checkpoint is the continuation entry point. Do not re-read the
historical GR corpus to resume routine validation.

| Scope | State | Evidence |
| --- | --- | --- |
| Active offline checks | 20/20 command groups PASS at exact source `be51c3b577fda9834de4364a35d0784d28f62492` | `../lab/real-seafile/results/2026-11-15-offline-validation/` |
| Core Seafile DOCX edit/save/reopen | HTTP slice 56/56; browser 58/58; two typed saves create versions and fresh-session reopen preserves edits | `../lab/real-seafile/results/2026-11-15-seafile-render-readonly/` |
| Legacy read-only Seafile routes | 34/34 route assertions; exact fixture bytes, OCR marker/value, no download, no version write, host reports `read-only` | `../lab/real-seafile/results/2026-11-15-seafile-render-readonly/` |
| Legacy format status | `VIEW_SUPPORTED`: ODT, ODS, CSV, PPSX. `UNSUPPORTED`: DOC, XLS, FODS, FODT, FODP, PPT, ODP, PPS | `ONLYOFFICE-REPLACEMENT-MATRIX.md` |
| Bundle render diagnosis | DOC/XLS/ODT/ODS/CSV/PPSX markers verified in standalone bundles; FODS shows flat XML. DOC/XLS host failure was observed in exploratory runs, not retained as an exact-source screenshot | `../lab/real-seafile/results/2026-11-15-legacy-render-probe/` |
| Default ArtCraft edit/save workflows | DOCX, XLSX, PPTX evidence remains the prior synthetic baseline; broad document/workbook/deck fidelity NOT VERIFIED | `../lab/real-seafile/results/2026-11-08-wordcraft-corpus-recovery/`, `../lab/real-seafile/results/2026-11-08-seven-craft-validation/` |
| HTTPS automated WordCraft replay | HTTP 40/40, browser 28/28 at source `7961db5`; does not cover physical-device acceptance | `../lab/real-seafile/results/2026-11-08-wordcraft-https-current/` |
| Direct read-only WOPI PutFile | Seafile CE 13.0.28 accepts direct `PutFile` with read-only token; bridge relay refuses it, but token is browser-visible | `../bridge/README.md`, `../lab/real-seafile/results/2026-11-15-seafile-render-readonly/` |
| Hardware WebGPU/clipboard/fonts/unload acceptance | NOT VERIFIED | `../lab/real-seafile/README.md` checklist |
| Independent and final review | GPT-6 Sol at `d263583`: PROVISIONAL PASS for isolated sequential subset only; production-boundary MAJOR remains disclosed. No project-wide PASS | `../reviews/PROJECT-CLOSURE-20261115/SOL-REVIEW-D263583.md` |
| Mechanical evidence self-audit | PASS at evidence HEAD `9def0bb`: 20 result directories/checksums, 17 available verifiers run, 16 provenance files checked, 2 loose JSON files scanned. Pattern-based secret scan; not independent | `../scripts/forensic-audit.py`, `../reviews/PROJECT-CLOSURE-20261115/MECHANICAL-AUDIT-9DEF0BB.json` |
| Owner's live Seafile server | Read-only HTTPS/TLS and ping PASS; release is older than tested CE 13.0.28, ArtCraft bridge is absent, and synthetic library is unshared. Supplied account is not registered in Seafile; no test library created. Authenticated edit/save NOT VERIFIED | private infrastructure discovery; no production writes |

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
   synthetic document. Read-only Seafile lookup did not find the supplied
   account, so the owner-authorized test-library creation is paused until a
   valid account is identified. The existing synthetic library must be shared
   to that account. No existing user files were changed. The inspected live
   release is older than CE 13.0.28 and has no ArtCraft bridge; an upgrade or
   deployment is a separate owner decision and is not authorized here.
2. Run the human checklist for WebGPU, clipboard, exact fonts, popups, dirty
   close, refused saves and network recovery.
3. GPT-6 Sol at `ad638d1` returned PROVISIONAL PASS for the isolated subset
   only and found one closure-ledger MINOR, now corrected. Obtain an adversarial
   review of the current follow-up SHA; no project-wide gate has passed.
4. Replacement completeness remains PARTIAL: eight legacy viewing formats are
   unrouted, arbitrary-file fidelity is unknown, and no legacy save is claimed.
   No converter or LibreOffice product path is planned.

The default six-editor candidate remains unchanged. `--pptx` is opt-in and the
four legacy routes are also opt-in and read-only.
