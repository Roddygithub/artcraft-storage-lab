# GR-084 evidence bundle

This bundle records the 2026-11-04 isolated PdfCraft browser run. The synthetic PDF, screenshots, test summaries, source and release provenance, runtime configuration snapshot, and cleanup observation are retained. Raw browser/HTTP results, logs, Seafile identifiers, URLs, cookies, account details, and the generated environment file remain in the local private cache; only SHA-256 digests for the raw records are committed.

## Result

- HTTP slice: **48/48** checks passed against synthetic Seafile CE **13.0.28**.
- Focused Chromium browser slice: **18/18** checks passed using actual PdfCraft Web **v0.16.1**.
- A browser-typed AcroForm value was present in the editor save payload, Seafile readback, and a fresh-session `/relay/file` response.
- The relay save payload and Seafile readback were byte-identical (2,386 bytes; SHA-256 `d1bb31792966cf0b5551029e56224074629e2590c9a6865be92ce70d6599dad2`). The retained PDF matches these bytes. A new user-attributed Seafile version was observed, the fresh session reopened the edit, and no editor download occurred.
- `pdftotext` extracted the saved field value but emitted three `Bad form bounding box` warnings; full external PDF validity is not claimed.
- The fixture upload was setup only. The fresh PDF editor was opened through the direct Seafile `?edit_pdf=true` route because the ordinary PDF list link opens Seafile preview.

## Contents

- `runtime/http-summary.json` and `runtime/browser-summary.json` — sanitized assertion names and outcomes only.
- `runtime/observations.json` — bounded narrative and explicit limits.
- `runtime/environment.json`, `runtime/image-digests.json`, `runtime/compose.yml`, `runtime/runner.py` — sanitized environment metadata and the exact compose/runner snapshots used. The snapshots require the omitted private `.env`, runtime source/assets, and cache data; they are not a standalone launch bundle.
- `runtime/candidate-provenance.json` — source-file hashes, exact runtime copy match, synthetic fixture digest, and PdfCraft release asset hashes.
- `runtime/cleanup.json` — project-scoped cleanup and post-run socket/port observations.
- `runtime/private-artifact-hashes.json` — hashes of private raw JSON/log files; raw data is not included.
- `runtime/checks.txt` — runtime counts and local focused commands.
- `runtime/pdfcraft-*.png` — four unaltered Chromium captures before edit, after typing, after save, and after fresh-session reopen. They were visually inspected; PNG metadata contains no account, origin, or library details.
- `runtime/pdfcraft-saved.pdf` — synthetic saved PDF returned by Seafile. The relay payload copy remains private; its equal digest is recorded above.
- `../..` `lab/real-seafile/fixtures/form.pdf` — original synthetic fixture, copied from the reviewed GR-057 synthetic PDF.
- `INDEPENDENT-REVIEW-R1.md` — bounded independent source audit, separate from the exact-candidate GPT review.
- `INDEPENDENT-GPT-REVIEW-R1.md` through `INDEPENDENT-GPT-REVIEW-R6.md` — exact-candidate GPT findings and remediations; R6 returned a bounded PASS with no P1–P3 findings.

The R1-corrected candidate code was copied into the private runtime before the run; its runtime-copy digest is retained in `candidate-provenance.json`. The later R2 EOF guard is a test-helper-only change, regression-tested offline after the run; the valid run-7 PDF result was not rerun for it. The R3 stale history byte count was corrected. The saved-output assertion reads active objects through the classic xref chain, with regression coverage that rejects a value from a superseded revision. The release bundle provenance is recorded as `storytold/pdfcraft` v0.16.1, archive SHA-256 `00f3e85e29bb9dfa3d43a655cc4197cdc679f4ec7e8ef1bb5e623dc3603c0edf`, unpatched.

This evidence does not verify other PDF files, full PDF fidelity, a Seafile file-list click into PdfCraft, production, the human HTTPS checklist, or project completion. It is direct parent work, not Aptarchy completion. Project GPT remains **INCOMPLETE** and upstream remains **LOCKED**.
