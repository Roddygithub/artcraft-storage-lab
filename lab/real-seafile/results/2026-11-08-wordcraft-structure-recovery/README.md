# WordCraft layout-fixture edit and structural preservation

Parent-operated fresh synthetic rootless lab, captured application source
matching `c909252`. Released WordCraft v0.13.2, standard layout corpus fixture.

| Stage | Result |
| --- | --- |
| HTTP | 44 passed, 2 failed: ODT/PPTX mixed-suite ONLYOFFICE errors |
| Focused WordCraft Chromium | 28 passed, 0 failed |
| Launcher exit | 1, intentionally preserving the HTTP failure after browser diagnostics and cleanup |

The browser typed and saved a marker, closed the old page, opened a fresh
Seafile session, typed a second marker and saved again. Both saves gained
user-attributed versions; both markers and original main text were retained.
No browser download was observed. These are harness assertions, not an
independent runtime replay. No final reopen after the second save is claimed.

The four retained synthetic DOCX files enable checks beyond the prior body-text
assertions. The first relay payload equals its Seafile readback byte-for-byte.
Both readbacks preserve the original's **referenced** header/footer text,
normalized PAGE field instructions, table-cell texts, explicit page-break count,
page dimensions/margins and paragraph style references. The simple PAGE field
is rewritten as a complex field; the semantic instruction is retained.
This does not prove every style definition, visual pagination, font, header/footer
placement or arbitrary-document feature. No full DOCX-fidelity PASS is claimed.

The three browser screenshots were visually inspected by the parent. They show
initial header/content, a saved marker and the reopened document with both
markers and its table. The final capture also shows a page-number footer on
the preceding page. They do not show every page in full. PNGs have no text/EXIF
metadata. Document package contents were scanned against the disposable lab's
credential values before retention; no matches were found.

Raw private results, URLs, accounts, tokens and version identities are omitted.
Provenance contains raw JSON hashes, source hashes and the static-manifest hash;
it does not independently authenticate actual asset serving, chronology or
cleanup. Parent observed no running lab containers after exit. Production and
its ONLYOFFICE integration were unchanged.

```sh
python3 lab/real-seafile/results/2026-11-08-wordcraft-structure-recovery/verify.py
```

Review outcomes are recorded separately in
`docs/reviews/PROJECT-CLOSURE-20261108/RECOVERY-REVIEWS.md`.
Project INCOMPLETE; upstream LOCKED. ONLYOFFICE
retirement remains conditional on WordCraft readiness and a rollback plan.
