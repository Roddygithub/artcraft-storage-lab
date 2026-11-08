# GR-085 — WordCraft edit/save on the corrected layout corpus

On 2026-11-08, a fresh isolated rootless Podman lab passed the HTTP slice
**48/48**, followed by focused Chromium **28/28**. Released, unpatched
WordCraft Web v0.13.2 edited `fidelity-layout.docx` from the corrected GR-083
corpus on synthetic Seafile CE 13.0.28. Code candidate:
`8a6f07bbe1ddecfd44852ea8adc85777901e1788`.

## Result

The browser clicked the document in the Seafile file list, waited for visible
document content, typed a marker with keyboard input and saved with Ctrl+S.
The host confirmed the save; Seafile history gained a version attributed to
the test user. Readback contained the marker and the original main-document
text. The old editor page was closed. A new authenticated browser context
clicked the same file-list entry and fetched bytes identical to the first
Seafile readback. It rendered the document, accepted a second typed marker,
and saved a second user-attributed version. Both markers and the original
main-document text remained present. No browser download was observed.

The fixture upload was setup, before either interactive edit. The reopened
editor's own second save contained both markers, providing semantic evidence
beyond merely receiving the saved bytes. This run does not assert exact
relay-save/readback byte equality: its byte equality check covers first
readback versus fresh-session open.

## Why the earlier attempts failed

The two private attempts on 2026-11-04 displayed an empty document. Inspection
on resumption found four served WordCraft files that differed from the official
release, despite the copied provenance text claiming that release. Attempt 1
was interrupted; attempt 2 passed HTTP 48/48 but failed the visible-content
gate before editing (browser 5/6). Neither is counted as successful evidence.

For the successful fresh attempt, the retained official ZIP was checked against
SHA-256 `b6c9c8d3a730495189ba0c213fe64313f317be8fc0611ac1ff8cdd6a4b20880c`,
then imported through `scripts/craft_web_zip.py`. Exact membership and hashes
of all **26** served files matched GR-083. All ten recorded executable-source
and configuration files matched the candidate. The local ignored WordCraft
directory was also populated from that verified archive for future lab use.

## Scope and review

The new option is `BROWSER_WORDCRAFT_FIXTURE=fidelity-layout.docx`, used with
`BROWSER_ONLY_EDITOR=wordcraft`. Default scenarios remain available. The
visible-content gate uses a dark-pixel threshold in a fixed viewport; it is a
heuristic for rejecting the observed blank page, not proof of document identity.
Marker and original body-text assertions provide separate semantic checks.

Independent GPT Sol 6.1 low source review passed candidate `8a6f07b` with no
P1–P3 findings. Its record and the sanitized runtime evidence are in the
[evidence bundle](../lab/real-seafile/results/2026-11-08-wordcraft-fidelity-edit/README.md).
Independent evidence review R2 returned a bounded PASS on `c0690a9` with no
P1–P3 findings; its record is retained in that bundle.
Runtime chronology, rootless isolation and cleanup are parent observations;
they have not been independently replayed. Screenshots corroborate the visible
states. Raw logs/results remain private; public records contain their hashes.

This validates one corrected layout fixture's main-text edit/save/reopen flow.
Header/footer preservation, formatting fidelity, other corpus documents,
other browsers, human HTTPS behavior, production and post-change ONLYOFFICE
edit/save remain **NOT VERIFIED**. The HTTP slice exercised the lab's existing
ONLYOFFICE API/conversion checks. Project GPT remains **INCOMPLETE** and upstream
publication **LOCKED**. This is direct parent work, not Aptarchy completion.
