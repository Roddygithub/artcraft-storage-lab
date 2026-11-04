# GR-084 — PdfCraft real edit on synthetic Seafile

**Bounded runtime result: pass for one synthetic AcroForm PDF in the isolated lab.** The focused Chromium run passed 18/18 assertions; the HTTP slice passed 48/48. This is not project GPT approval, production validation, or upstream authorization. Project GPT remains **INCOMPLETE** and upstream publication remains **LOCKED**.

## Run result

On 2026-11-04, the parent ran the browser slice in a fresh, rootless Podman project with synthetic Seafile CE 13.0.28 data. It served the unpatched PdfCraft Web v0.16.1 release bundle. The HTTP slice completed before a focused `BROWSER_ONLY_EDITOR=pdfcraft` Chromium run. The runner exited successfully and executed its project-scoped `down --remove-orphans` cleanup.

The browser opened the synthetic `form.pdf`, typed a unique value into its existing `name` AcroForm field, and observed unsaved state before Ctrl+S. The editor's `/relay/save` request contained that field value. The host reported `saved to Seafile`; the synthetic Seafile history check observed a new version attributed to the test user. The Seafile readback had the expected PDF signature and contained the typed field value; the fresh PdfCraft session opened it and rendered the field.

The captured relay save payload and Seafile readback were **byte-identical**: both were 2,385 bytes with SHA-256 `69c2f8989bf0345a4620483fffaf5c72c27e4e2486b6099032ccb0d3b25af35b`. A new browser context then authenticated separately and reopened the same file through the explicit Seafile `?edit_pdf=true` route. Its `/relay/file` bytes matched the Seafile readback exactly, and the field value remained present. No editor download was observed. `pdftotext` extracted the saved field value but emitted three `Bad form bounding box` warnings; full external PDF validation is therefore not claimed.

The original synthetic fixture was uploaded before the edit as setup. That upload is not counted as the editor save. The first run of the harness is retained only in the private cache; the recorded result is the final clean run described above.

## Scope and limits

This proves one visible edit/save/version/readback/reopen sequence for a one-page synthetic AcroForm PDF in the isolated lab. The ordinary Seafile PDF file-list link opens its preview, so the fresh editor reopen used the direct file route with `?edit_pdf=true`; this run does **not** claim a file-list click into PdfCraft.

The following remain **NOT VERIFIED**: other PDF forms or documents, broad PDF fidelity, complete external PDF validity or parser correctness, a human HTTPS browser pass, other browsers, production behavior, a post-change ONLYOFFICE edit/save regression, and the remaining project-level roadmap gates. The browser flow uses the actual released PdfCraft bundle, but this evidence does not certify the wider project or every dispatched editor.

This was direct parent work, not Aptarchy task completion. No production Seafile or ONLYOFFICE configuration was accessed or changed, and no upstream repository was contacted. Evidence and reproducibility notes are in [`docs/reviews/GR-084/`](reviews/GR-084/README.md).
