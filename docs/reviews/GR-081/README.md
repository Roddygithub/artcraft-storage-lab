# GR-081 evidence — DeckCraft native edit on synthetic Seafile

This bundle records the exact parent-run browser replay. The test generated a
native DeckCraft file as setup, uploaded it before editing, then used the
Seafile file list and actual editor UI for both save cycles.

## Recorded artifacts

- [`browser-results.json`](browser-results.json) — sanitized 26/26 assertion
  summary, outcome checks, screenshot hashes, and hashes of the private raw
  result and console log. Repository IDs, URLs, account fields, version IDs,
  and raw per-check details are omitted.
- [`source-manifest.json`](source-manifest.json) — candidate base, exact tested
  patch digest, runtime bundle/compose hashes, and seven source hashes.
- [`runtime/`](runtime/) — seven PNG captures of the editor before and after
  each save, the reopened session, and the baseline render.

The private raw JSON and console log remain under the local cache at
`~/.cache/artcraft-storage-lab/deckcraft-real-edit-20261103/runtime-64b0213/`;
they are not included in Git. Their digests are recorded in the sanitized
summary for local integrity checking.

## Workflow proven

1. DeckCraft itself created a native `.deckcraft` fixture; the setup upload
   occurred before the edit workflow.
2. A real Seafile file-list click opened the file in the bridge and DeckCraft.
3. Trusted keyboard input changed the slide title. The harness verified a
   localized rendered change, a native save payload containing the marker, and
   the host's positive save status.
4. Seafile history moved from one version to two, attributed to the logged-in
   synthetic user. Seafile readback contained the marker and different native
   bytes. No browser download occurred.
5. The original browser page was closed. A new browser context logged in,
   reopened from the Seafile file list, and received bytes identical to
   Seafile readback. The title edit remained visible.
6. A second trusted edit was saved in that reopened session. History moved from
   two versions to three; Seafile readback retained both markers and changed
   bytes. No download occurred.

## Validation and limits

- Actual browser run: **26 passed, 0 failed**.
- Local render-gate regression: **26/26**; native DeckCraft parser: **7/7**;
  Python syntax and whitespace checks passed.
- PNGs were checked for text/EXIF metadata; OCR found no email, URL, UUID, or
  credential terms. The captures show a missing-font warning for Arial/Inter;
  visual font fidelity is **NOT VERIFIED**.
- This covers one synthetic native `.deckcraft` document in headless Chromium.
  Foreign `.pptx`, other browsers, desktop HTTPS, production, and complete
  DeckCraft fidelity remain **NOT VERIFIED**.
- The prior HTTP slice result (48/48) was not repeated in this browser-only
  work item. Bridge source was unchanged.
- This was direct parent work, not Aptarchy task completion. Project GPT
  remains **INCOMPLETE** and upstream publication remains **LOCKED**.
- Evidence review R1 returned bounded PROVISIONAL PASS with one P3 about the
  review-queue banner. R2 confirmed that fix and found one stale sentence in
  the R1 record; it now says the remediation check is pending R2. R3 confirmed
  the correction and found no further issue.

`SHA256SUMS` covers this README, the sanitized result, source manifest, review
records, and retained PNGs.
