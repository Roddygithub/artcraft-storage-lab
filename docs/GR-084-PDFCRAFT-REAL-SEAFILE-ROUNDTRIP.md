# GR-084 — PdfCraft real edit on synthetic Seafile

**Bounded runtime result: pass for one synthetic AcroForm PDF in the isolated lab.** The focused Chromium run passed 18/18 assertions; the HTTP slice passed 48/48. This is not project GPT approval, production validation, or upstream authorization. Project GPT remains **INCOMPLETE** and upstream publication remains **LOCKED**.

The exact-candidate GPT R1 review found a P2 in the saved-field assertion: it
could accept a value from a superseded incremental PDF revision. The assertion
now resolves active objects through the classic xref chain, and a regression
rejects stale values. GPT R2 also found that the retained PDF's documented hash
and size were stale, plus an EOF no-progress case in the narrow xref helper.
The archived PDF metadata now matches the actual run-7 relay/readback bytes;
the helper now fails closed on EOF and has a regression. GPT R3 found one stale
2,385-byte count in `HISTORY.md`; it is corrected to 2,386. R4 found and closed
a stale closing-review sentence; R5 found and closed a stale opening-review
sentence. Exact-commit GPT R6 review is pending. The EOF guard was added after
the run; it affects only
malformed helper input, not the valid saved PDF used by the recorded run.

## Run result

On 2026-11-04, the parent ran the browser slice in a fresh, rootless Podman project with synthetic Seafile CE 13.0.28 data. It served the unpatched PdfCraft Web v0.16.1 release bundle. The HTTP slice completed before a focused `BROWSER_ONLY_EDITOR=pdfcraft` Chromium run. The runner exited successfully and executed its project-scoped `down --remove-orphans` cleanup.

The browser opened the synthetic `form.pdf`, typed a unique value into its existing `name` AcroForm field, and observed unsaved state before Ctrl+S. The editor's `/relay/save` request contained that field value. The host reported `saved to Seafile`; the synthetic Seafile history check observed a new version attributed to the test user. The Seafile readback had the expected PDF signature and contained the typed field value; the fresh PdfCraft session opened it and rendered the field.

The captured relay save payload and Seafile readback were **byte-identical**: both were 2,386 bytes with SHA-256 `d1bb31792966cf0b5551029e56224074629e2590c9a6865be92ce70d6599dad2`. The retained PDF matches that readback. A new browser context then authenticated separately and reopened the same file through the explicit Seafile `?edit_pdf=true` route. Its `/relay/file` bytes matched the Seafile readback exactly, and the field value remained present. No editor download was observed. `pdftotext` extracted the saved field value but emitted three `Bad form bounding box` warnings; full external PDF validation is therefore not claimed.

The original synthetic fixture was uploaded before the edit as setup. That upload is not counted as the editor save. The final run exercised the active-xref assertion against the saved PDF. The offline regression rejects values present only in a superseded object revision. The later EOF guard has its own offline regression; the successful runtime was not repeated for that malformed-input-only test-helper change. Raw results remain only in the private cache.

## Scope and limits

This proves one visible edit/save/version/readback/reopen sequence for a one-page synthetic AcroForm PDF in the isolated lab. The ordinary Seafile PDF file-list link opens its preview, so the fresh editor reopen used the direct file route with `?edit_pdf=true`; this run does **not** claim a file-list click into PdfCraft.

The following remain **NOT VERIFIED**: other PDF forms or documents, broad PDF fidelity, complete external PDF validity or parser correctness, a human HTTPS browser pass, other browsers, production behavior, a post-change ONLYOFFICE edit/save regression, and the remaining project-level roadmap gates. The browser flow uses the actual released PdfCraft bundle, but this evidence does not certify the wider project or every dispatched editor.

This was direct parent work, not Aptarchy task completion. No production Seafile or ONLYOFFICE configuration was accessed or changed, and no upstream repository was contacted. Evidence and reproducibility notes are in [`docs/reviews/GR-084/`](reviews/GR-084/README.md). GPT findings and remediations are recorded in the R1–R5 review files under `docs/reviews/GR-084/`; R4's stale closing status and R5's stale opening status have both been corrected. Exact-commit R6 is pending.
