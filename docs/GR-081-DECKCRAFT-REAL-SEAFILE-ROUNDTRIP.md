# GR-081 — DeckCraft native edit roundtrip on synthetic Seafile

## Result

The native DeckCraft `.deckcraft` browser path passed **26/26 assertions** on a
fresh synthetic Seafile repository. Chromium opened the file from the Seafile
file list, rendered its initial slide, accepted a real keyboard edit, saved
through the WOPI bridge, created a user-attributed Seafile version, and read
back the edited native document. The old editor page was closed; a new browser
context logged in and reopened the file from the Seafile list. The reopened
bytes matched Seafile readback, and a second visible edit produced another
version retaining both edit markers.

The generated native fixture was saved by DeckCraft and uploaded once before
editing as test setup. No edited output was downloaded or manually uploaded.
The browser recorded zero downloads for both editor saves. This was a direct
parent-run ArtCraft test, **not an Aptarchy-generated or Aptarchy-integrated
result**.

## Candidate and runtime

- Candidate base: `fce28f23682f00844418bdde97523d0cf25fb935`.
- Tested browser/test-harness patch SHA-256:
  `6484634af87678bda8bcb17957402813d6d9f76414283917386deb14b1a69fac`.
- Exact changed-source and runtime bundle hashes are recorded in
  [`source-manifest.json`](reviews/GR-081/source-manifest.json).
- Isolated, rootless Podman project; Seafile and test documents were synthetic.
  The browser created a fresh repository for this run.
- The HTTP slice was **not rerun** for this browser-only change. Its retained
  48/48 result uses the unchanged bridge source; GR-081 specifically records
  the native DeckCraft browser workflow.

## Evidence

The sanitized result record lists all 26 passing checks and omits repository
identifiers, URLs, account fields, version IDs, and per-check raw details. The
original browser JSON and console log remain in the local private cache; their
SHA-256 values are recorded without copying their contents into Git. Seven
retained PNGs show the initial editor, edit, host confirmation, fresh-session
reopen, and second edit/save. OCR and PNG metadata checks found no email, URL,
UUID, credential term, or text/EXIF chunk in the images.

The screenshot also shows DeckCraft's warning that Arial and Inter are not
installed in the browser container and a substitute font is used. This test
verifies save/readback and visible edits in that environment; it does not
establish layout fidelity for those fonts.

## Limits

- One synthetic native `.deckcraft` fixture and Chromium run only. Foreign
  `.pptx` editing, broader DeckCraft fidelity, other browsers, desktop HTTPS,
  and production deployment remain **NOT VERIFIED**.
- The old browser page was closed; this is not a claim that DeckCraft's own
  in-app close control was exercised.
- The test confirms semantic marker persistence and visible title-region
  change; it does not compare full document rendering or all slide content.
- No production Seafile, production ONLYOFFICE setting, or external upstream
  service was accessed or changed. No upstream publication is authorized.

## Review state

The exact render-gate patch received bounded GPT 6.1 Sol low reviews. R5 and R6
found defects; R7 closed the stale-render findings, and R8 confirmed the
missing-prerequisite guard. Evidence review R1 returned PROVISIONAL PASS with
one P3 about the queue banner; R2 confirmed that fix and found one stale sentence
in the R1 record. That sentence now says its remediation check is pending R2;
R3 confirmed the correction with no findings. The evidence reviews R1–R3 are
bounded PROVISIONAL PASS; project-level GPT review remains pending. Project
status remains INCOMPLETE and upstream remains LOCKED.

See [`reviews/GR-081/README.md`](reviews/GR-081/README.md) for the retained
evidence and checksums.
