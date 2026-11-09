# Validation checkpoint — 2026-11-08

This short checkpoint is the continuation entry point. Do not re-read the
historical GR corpus to resume routine validation.

| Scope | State | Evidence |
| --- | --- | --- |
| Active offline checks | 20/20 command groups PASS (legacy fixtures added) | local rerun; `tests/test_legacy_fixtures.py` |
| Craft-only WordCraft layout cycle | HTTP 40/40, browser 28/28, exit 0 | `lab/real-seafile/results/2026-11-08-craft-only-wordcraft/` |
| All six default Craft editors, source `8369e8f` | HTTP 40/40, browser 119/119, exit 0 | `../lab/real-seafile/results/2026-11-08-all-craft-validation/` |
| Official DeckCraft PPTX opt-in | focused 15/15; combined HTTP 40/40, browser 132/132, exit 0 | `../lab/real-seafile/results/2026-11-08-seven-craft-validation/` |
| Remaining office viewing formats and broad fidelity | Fixtures + routing ready; runtime import NOT VERIFIED | `ONLYOFFICE-REPLACEMENT-MATRIX.md`, `fixtures/legacy/` |
| Automated WordCraft HTTPS edit/save/reopen | HTTP 40/40, browser 28/28, exit 0; TLS routes restored | `../lab/real-seafile/results/2026-11-08-wordcraft-https-current/` |
| Hardware WebGPU/clipboard/fonts/unload acceptance | NOT VERIFIED | `../lab/real-seafile/README.md` checklist |
| Independent forensic review and final project GPT gate | NOT PERFORMED | `PROJECT-CLOSURE.md` |

ONLYOFFICE is retired; do not restart compatibility campaigns. Production is
outside this validation run. Upstream remains LOCKED. An automated subset PASS
must never be presented as full format coverage or project approval.

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

1. Required legacy/OpenDocument viewing formats: deterministic fixtures, an
   opt-in routing candidate and a real-Seafile routing replay now exist for all
   twelve; DOC/ODT (WordCraft) and XLS/ODS/CSV (GridCraft) have a documented
   upstream import and a proven route. Browser **import** of a legacy fixture is
   still NOT VERIFIED, and seven formats have no documented import at all.
2. Hardware WebGPU, clipboard, exact fonts and unload-guard acceptance.
3. Independent forensic review and a fresh project GPT gate, in a context that
   did not implement this candidate. No global PASS has been granted.

The default six-editor candidate remains unchanged. Add `--pptx` and the
verified official DeckCraft assets for the validated seven-editor option.
