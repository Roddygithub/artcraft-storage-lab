# Seafile legacy viewing candidate — 2026-11-15

**Source:** `4a5ab576da0e0a0f227e672d8ea6258ea90c9acc`
**Host:** stock Seafile CE 13.0.28 in the private rootless lab
**Bundles:** exact static manifest SHA in `provenance.json`

## Result

| Check | Result |
| --- | ---: |
| HTTP slice | 56/56 PASS |
| Browser slice | 58/58 PASS |
| Legacy route checks | 34/34 PASS |
| Visible fixture marker and spreadsheet value | 4/4 PASS |
| Legacy WOPI UI read-only status | 4/4 PASS |
| Read-only bridge save | refused (403) |
| Seafile version on open | unchanged for all four routed fixtures |
| Core DOCX | typed edits, saves, new Seafile versions, and fresh-session reopen PASS |

The four opt-in routes are ODT→WordCraft, ODS/CSV→GridCraft, and
PPSX→DeckCraft. The retained screenshots are synthetic. OCR assertions check
the unique marker and, for spreadsheets, `42`; screenshots are also available
for direct visual inspection.

DOC, XLS, FODS, FODT, FODP, PPT, ODP and PPS are verified as unrouted in this
candidate. The retained probe confirms FODS displays raw XML in GridCraft.
Earlier exploratory runs reported a DOC host-render mismatch and an empty XLS
frame, but those results are not retained as exact-source evidence and are not
counted as verified. See `../2026-11-15-legacy-render-probe/`.

**Security limit:** the passing check `seahub_putfile_ignores_can_edit` records a
host gap: Seafile accepts a direct PutFile with a read-only WOPI token. The
bridge blocks a save sent through its own relay and displays `read-only`, but
the browser can extract the token and call Seahub directly. These routes are
lab-only and do not establish production authorization safety. No legacy save
or conversion workflow is supported.

## Reproduce

```sh
uv run --with playwright --with pillow python lab/real-seafile/local.py \
  --run-dir /absolute/new-private-dir \
  --static /absolute/pinned-static \
  --manifest /absolute/pinned-static-sha256.json \
  --viewing --editor wordcraft
python3 lab/real-seafile/results/2026-11-15-seafile-render-readonly/verify.py
```

The disposable Playwright container installs Tesseract for the OCR assertions.
The runner creates synthetic accounts and data; no user credentials or
production services are used.
