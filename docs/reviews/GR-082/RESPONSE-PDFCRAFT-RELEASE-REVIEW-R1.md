# Response to PdfCraft release evidence review R1

Both LOW findings are closed:

1. `tests/test_pdfcraft_host_roundtrip.py` now runs Tesseract 5.5.3 on the
   fresh-editor screenshot and requires the edited marker in OCR output before
   reporting success. R4 reran the browser smoke; its log binds that assertion
   to the test source and all actual served assets with matching before/after
   hashes.
2. `ports/pdfcraft-v0.14.0.md` now states that seven non-vendored
   source/manifest paths changed, plus the packaged shared transport snapshot.

The updated manifest, runtime evidence and status summaries point to R4. The
Seafile workflow, identity binding, and replacement/Save As refusal remain
**NOT VERIFIED**.
