# Validation checkpoint — tested source `be51c3b` (2026-11-15)

**Reviewed candidate SHA:** `546ce0dd711eade0d9cb253a0fc4389c28ee2617`.
GPT-6 Sol returned PROVISIONAL PASS for this documentation follow-up only;
runtime source remains `be51c3b`. No project-wide gate has passed.

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
| Hardware WebGPU/clipboard/fonts/unload acceptance | NOT VERIFIED | `reviews/PROJECT-CLOSURE-20261115/HARDWARE-ACCEPTANCE-CHECKLIST.md` |
| Independent and final review | GPT-6 Sol at `546ce0d`: PROVISIONAL PASS for documentation follow-up; no new MINOR. A later live-route discovery is not included in that review. No global GPT PASS | `reviews/PROJECT-CLOSURE-20261115/SOL-REVIEW-546CE0D.md` |
| Mechanical evidence self-audit | PASS at evidence HEAD `9def0bb`: 20 result directories/checksums, 17 available verifiers run, 16 provenance files checked, 2 loose JSON files scanned. Pattern-based secret scan; not independent | `../scripts/forensic-audit.py`, `reviews/PROJECT-CLOSURE-20261115/MECHANICAL-AUDIT-9DEF0BB.json` |
| Owner's live Seafile server | HTTPS/TLS and ping PASS; synthetic library shared read-write. Seafile 12.0.14; current WOPI bridge disabled. A pre-existing patched, repo-scoped third-party route and gateway are active. Historical GR-059 records a real legacy-route save/version/reopen, not current WOPI. No config/content changed during this task. Authenticated current-bridge edit/save NOT VERIFIED | [`OWNER-SERVER-ACCESS-20261115.md`](reviews/PROJECT-CLOSURE-20261115/OWNER-SERVER-ACCESS-20261115.md), `GR-059-REAL-SEAFILE-WORDCRAFT-DEPLOYMENT.md` |

ArtCraft is the intended suite. ONLYOFFICE retirement is authorized. Production
deployment remains outside these tests. Only the authorized synthetic-library
permission changed; server configuration and file contents were not changed.
Upstream remains LOCKED. An automated subset PASS is not full format coverage
or project approval.

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
   synthetic document. Test-library access is now prepared, but the live
   Seafile is 12.0.14 and the current WOPI bridge is disabled. A legacy patched
   route and gateway remain active for the synthetic library. Stock WOPI
   routing is extension-wide, so the current bridge cannot be limited to one
   library with the existing configuration. Use an isolated Seafile test
   instance or obtain separate approval for broader routing changes. These
   post-review server findings need an independent documentation review.
2. Run the human checklist for WebGPU, clipboard, exact fonts, popups, dirty
   close, refused saves and network recovery.
3. GPT-6 Sol at `546ce0d` returned PROVISIONAL PASS for the documentation
   follow-up. This closes the exact-HEAD documentation review only; no
   project-wide gate has passed.
4. Replacement completeness remains PARTIAL: eight legacy viewing formats are
   unrouted, arbitrary-file fidelity is unknown, and no legacy save is claimed.
   No converter or LibreOffice product path is planned.

The default six-editor candidate remains unchanged. `--pptx` is opt-in and the
four legacy routes are also opt-in and read-only.
