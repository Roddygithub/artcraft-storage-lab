# GR-077 — Seafile integration coverage reconciliation

## Result

The global integration summary was stale after the GR-064–GR-076 Seafile
roundtrips and the GR-076 tracked PhotoCraft route. It now distinguishes the
five routes in the tracked dispatcher, their per-app synthetic runtime evidence,
and what remains unverified. This is a documentation change; no browser,
Seafile, gateway or ONLYOFFICE runtime test was performed for GR-077.

## Evidence checked

| Claim | Evidence |
|---|---|
| Tracked dispatch has five routes | `integration/config/dispatch.json`; GR-076 route review in `docs/reviews/GR-076/runtime/review-r1-and-response.md` |
| WordCraft synthetic workflow and post-allow-list regression | `docs/GR-059-REAL-SEAFILE-WORDCRAFT-DEPLOYMENT.md` and `docs/reviews/GR-076/runtime/README.md` |
| GridCraft, VectorCraft, PdfCraft, PhotoCraft individual synthetic workflows | `docs/GR-061-GRIDCRAFT-REAL-SEAFILE-ROUNDTRIP.md`, `docs/GR-063-VECTORCRAFT-REAL-SEAFILE-ROUNDTRIP.md`, `docs/GR-068-PDFCRAFT-REAL-SEAFILE-ROUNDTRIP.md`, `docs/GR-076-PHOTOCRAFT-BOUNDED-HOST-ADAPTER.md` and their evidence bundles |
| Other synthetic app runs are not currently tracked routes | `docs/GR-064-DECKCRAFT-REAL-SEAFILE-ROUNDTRIP.md` through `docs/GR-069-FIGCRAFT-REAL-SEAFILE-ROUNDTRIP.md`; `integration/config/dispatch.json` |
| Only PhotoCraft is present in this checkout's `integration/static/` | Read-only inventory recorded in `docs/reviews/GR-077/README.md` |
| One combined route replay and production behavior remain unverified | `docs/TEST-MATRIX.md` GR-071/GR-077 rows; existing per-app evidence scope |

## Boundaries

- The per-app workflows were performed against a synthetic Seafile library; they
  do not prove production readiness.
- The current checkout's ignored static root contains the verified PhotoCraft
  files only. Tracked dispatch entries alone do not prove their apps are served.
- The five routes have not been replayed together in one Seafile session.
- Save/readback byte identity is not established uniformly across apps.
- ONLYOFFICE settings and service were not changed. GR-076's post-change UI
  attempt remains inconclusive; the existing GR-072 synthetic regression smoke
  is separately recorded.
- Project status remains **INCOMPLETE**, GPT review **PENDING**, and upstream
  publication **LOCKED**.

## Checks performed

Read-only comparison of the tracked dispatcher with the status and evidence
documents, and inventory of `integration/static/`. Markdown whitespace checks
were run. No application tests, builds, remote service changes, or upstream
publication were performed.

Independent R1 returned **PROVISIONAL PASS** with ten MINOR wording/reference
findings and no BLOCKER or MAJOR. R2 verified all ten remediations and found no
new findings. Both results remain PROVISIONAL, not GPT review approval. The
finding-by-finding response is in
`docs/reviews/GR-077/INDEPENDENT-REVIEW-R1-RESPONSE.md`; final-state review is
in `docs/reviews/GR-077/INDEPENDENT-REVIEW-R2.md`.
