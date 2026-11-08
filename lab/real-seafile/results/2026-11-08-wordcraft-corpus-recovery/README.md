# WordCraft prose and list/table recovery runs

Two parent-operated fresh synthetic rootless labs, with all 33 captured
application files matching `9a71dff`. Released WordCraft v0.13.2 edited the
existing deterministic `fidelity-prose.docx` and `fidelity-structure.docx` fixtures.

| Case | HTTP | Chromium | Launcher exit |
| --- | --- | --- | --- |
| Prose / bold / italic / color | 44 pass, 2 fail | 28 pass, 0 fail | 1 |
| Lists / headings / table | 44 pass, 2 fail | 28 pass, 0 fail | 1 |

Both runs retain the known ODT/PPTX ONLYOFFICE routing failures. Diagnostic
browser continuation does not erase them. The parent observed cleanup after
each run; no production or existing ONLYOFFICE settings were changed.

The browser typed a marker, saved a new attributed version, closed the old page,
opened the saved file through a fresh authenticated session, typed another
marker and saved a second attributed version. Original main text and both
markers survive; no browser downloads were observed. These are retained
harness assertions, not independent runtime replay. No final reopen after the
second save is claimed.

The first relay bytes equal first Seafile readback. Both readbacks preserve:
referenced header/footer texts and PAGE instructions; table-cell text; page
geometry and explicit page breaks; paragraph style references; direct formatted
run text/properties; and each list paragraph's text, resolved numbering format
and level text. This checks the synthetic bold, italic, accent color, bullets
and decimal list cases. Added unused numbering levels are not treated as loss.
The verifier reuses the prior layout bundle's structural reader.

Four parent-inspected screenshots corroborate rendered original formatting and
the reopened documents after both typed markers. They are not a full-page,
pixel-exact independent export comparison. Full style inheritance, arbitrary
DOCX compatibility, fonts, other browsers, HTTPS desktop acceptance and general
ONLYOFFICE-replacement readiness remain NOT VERIFIED.

Synthetic DOCX packages were scanned against disposable credential values;
no matches were found. PNG CRCs passed and no text/EXIF metadata was present.
Public JSON keeps only check names/booleans/totals. Source/asset and private raw
JSON hashes establish byte consistency, not independent chronology or serving.

```sh
python3 lab/real-seafile/results/2026-11-08-wordcraft-corpus-recovery/verify.py
```

Independent review outcomes are recorded separately in
`docs/reviews/PROJECT-CLOSURE-20261108/RECOVERY-REVIEWS.md`.
Project INCOMPLETE; upstream LOCKED. No ONLYOFFICE removal is authorized here.
