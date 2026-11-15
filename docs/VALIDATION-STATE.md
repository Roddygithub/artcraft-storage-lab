# Validation checkpoint — candidate `123d2a0` (2026-11-15)

**Technical candidate SHA:** `123d2a0ca8435e93e37b6d2f31fb73ac016fc5fb`.
This candidate adds a reproducible Seafile CE12 runner and retains a corrected
66/66 browser replay. The offline runner passed 21/21 command groups at this
exact SHA. An independent free-model review of `123d2a0` returned PROVISIONAL
PASS for the claimed lab scope; its one limitation and four documentation
minors are resolved. See
`reviews/PROJECT-CLOSURE-20261115/INDEPENDENT-REVIEW-2DD571F.md`.
The prior GPT-6 Sol PROVISIONAL PASS at `98c6bba` covered
an earlier evidence-only delta, not this candidate. **No GPT gate has run on
`123d2a0`**, so the global gate remains open.

This short checkpoint is the continuation entry point. Do not re-read the
historical GR corpus to resume routine validation.

| Scope | State | Evidence |
| --- | --- | --- |
| Active offline checks | 21/21 command groups PASS at exact candidate `123d2a0ca8435e93e37b6d2f31fb73ac016fc5fb`; all logs are retained and manifest-verified | `../lab/real-seafile/results/2026-11-15-offline-validation-123d2a0/` |
| Core Seafile DOCX edit/save/reopen | HTTP slice 56/56; browser 58/58; two typed saves create versions and fresh-session reopen preserves edits | `../lab/real-seafile/results/2026-11-15-seafile-render-readonly/` |
| Legacy read-only Seafile routes | 34/34 route assertions; exact fixture bytes, OCR marker/value, no download, no version write, host reports `read-only` | `../lab/real-seafile/results/2026-11-15-seafile-render-readonly/` |
| Legacy format status | `VIEW_SUPPORTED`: ODT, ODS, CSV, PPSX. `UNSUPPORTED`: DOC, XLS, FODS, FODT, FODP, PPT, ODP, PPS | `ONLYOFFICE-REPLACEMENT-MATRIX.md` |
| Seafile 12.0.14 isolated browser workflows | Reproduced through the checked-in CE12 launcher: WordCraft DOCX 24/24, GridCraft XLSX 27/27, DeckCraft PPTX 15/15; each saved a new version and reopened edits in a fresh session. Synthetic data only. Initial bridge-start ordering defect was fixed before this passing replay | `../lab/real-seafile/results/2026-11-15-seafile12-replay/` |
| Bundle render diagnosis | DOC/XLS/ODT/ODS/CSV/PPSX markers verified in standalone bundles; FODS shows flat XML. DOC/XLS host failure was observed in exploratory runs, not retained as an exact-source screenshot | `../lab/real-seafile/results/2026-11-15-legacy-render-probe/` |
| Default ArtCraft edit/save workflows | DOCX, XLSX, PPTX have isolated CE 12.0.14 save/version/fresh-reopen checks (24/24, 27/27, 15/15). Broad document/workbook/deck fidelity NOT VERIFIED | `../lab/real-seafile/results/2026-11-15-seafile12-replay/`; prior multi-app runs: `../lab/real-seafile/results/2026-11-08-seven-craft-validation/` |
| HTTPS automated WordCraft replay | HTTP 40/40, browser 28/28 at source `7961db5`; does not cover physical-device acceptance | `../lab/real-seafile/results/2026-11-08-wordcraft-https-current/` |
| Direct read-only WOPI PutFile | Seafile CE 13.0.28 accepts direct `PutFile` with read-only token; bridge relay refuses it, but token is browser-visible | `../bridge/README.md`, `../lab/real-seafile/results/2026-11-15-seafile-render-readonly/` |
| Hardware WebGPU/clipboard/fonts/unload acceptance | NOT VERIFIED | `reviews/PROJECT-CLOSURE-20261115/HARDWARE-ACCEPTANCE-CHECKLIST.md` |
| Independent and final review | Free-model independent review of `123d2a0` at docs `2dd571f`: PROVISIONAL PASS for the claimed lab scope; 1 limitation and 4 documentation minors, all resolved. GPT-6 Sol at `98c6bba` covered only the earlier evidence delta. **No GPT gate has run on this candidate.** | `reviews/PROJECT-CLOSURE-20261115/INDEPENDENT-REVIEW-2DD571F.md` |
| Mechanical evidence self-audit | PASS at exact candidate `123d2a0`: 24 result directories, 21 available verifiers run, 19 provenance commits checked, 307 files hashed and 87 JSON files scanned; two loose root JSON files scanned; pattern-based secret scan | `../scripts/forensic-audit.py`, `reviews/PROJECT-CLOSURE-20261115/MECHANICAL-AUDIT-123D2A0.json` |
| Owner's live Seafile server | HTTPS/TLS and ping PASS; synthetic library shared read-write. Seafile 12.0.14; current WOPI disabled. Patched Seahub route allowlists the synthetic library; a separate gateway service is active, but its relationship to the configured action URL is unverified. Supplied credentials were rejected at login; authenticated current-bridge edit/save NOT VERIFIED. No config/content changed | [`OWNER-SERVER-ACCESS-20261115.md`](reviews/PROJECT-CLOSURE-20261115/OWNER-SERVER-ACCESS-20261115.md), `GR-059-REAL-SEAFILE-WORDCRAFT-DEPLOYMENT.md` |

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
   synthetic document. Test-library access is now prepared, but the supplied
   credentials were rejected at login and the live
   Seafile is 12.0.14 and the current WOPI bridge is disabled. A legacy patched
   route allowlists the synthetic library, and a separate gateway service is
   active; their connection is unverified. Stock WOPI routing is extension-wide,
   so the current bridge cannot be limited to one
   library with the existing configuration. Use an isolated Seafile test
   instance or obtain separate approval for broader routing changes. These
   post-review server findings need an independent documentation review.
2. Run the human checklist for WebGPU, clipboard, exact fonts, popups, dirty
   close, refused saves and network recovery.
3. An independent free-model review of `123d2a0` at docs `2dd571f` returned
   PROVISIONAL PASS for the claimed lab scope. No GPT gate has run on this
   candidate. The next step is the GPT-6 Sol review once the provider quota
   resets (previously blocked until 2026-11-20), then the human hardware
   checklist. Neither is a code change.
4. Replacement completeness remains PARTIAL: eight legacy viewing formats are
   unrouted, arbitrary-file fidelity is unknown, and no legacy save is claimed.
   No converter or LibreOffice product path is planned.

The default six-editor candidate remains unchanged. `--pptx` is opt-in and the
four legacy routes are also opt-in and read-only.
