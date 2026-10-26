# GR-078 runtime observations

## Environment and method

Sequential browser workflow through Seafile Web in the synthetic
`ArtCraft GPT Review Synthetic` library, dated 2026-10-26. Each file was opened
from the library, edited in the routed web editor, saved with its host-bound
save control, closed by closing the editor tab, then reopened from the library.
No download or manual upload was used. The active lab deployment loaded each
mapped editor's JS/WASM and the document API successfully. This is synthetic
lab evidence, not production verification.

## Observations

| File / app | Save observation | Reopen observation | Screenshots |
|---|---|---|---|
| `photocraft-fixture/photocraft-smoke.pcraft` / PhotoCraft | Added a layer; host save returned HTTP 200; editor returned to clean state | Added layer visible after reopen | `photocraft-save.png`, `photocraft-reopen.png` |
| `synthetic.docx` / WordCraft | Added `gr078docx`; retained screenshot shows marker and saved state. New-version confirmation was observed during the run but is not captured in the screenshot | Marker visible after fresh Seafile open | `wordcraft-save.png`, `wordcraft-reopen.png` |
| `synthetic.xlsx` / GridCraft | B2 changed to 1338; B3 `=SUM(B2:B2)` recalculated to 1338; new version `5724ff96254801716d84bb07b8e8705060d410f9` | B2 and B3 remained 1338 | `gridcraft-save.png`, `gridcraft-reopen.png` |
| `form.pdf` / PdfCraft | First form field changed to `GR078savededit`; new version `9e9a8b9a7e2fa90df924cab8d6da9798676e7630` | Field value remained visible | `pdfcraft-save.png`, `pdfcraft-reopen.png` |
| `synthetic.svg` / VectorCraft | Added 20 × 20 px rectangle; Export As SVG invoked host save; new version `55962c8fedfe0e0a25a547a8a9b1992f8daf9b32` | Added rectangle visible | `vectorcraft-save.png`, `vectorcraft-reopen.png` |

The WordCraft save confirmation was observed during the run, but the retained
save screenshot only shows the document saved state and the marker. The exact
WordCraft version ID and screenshot-backed new-version confirmation are
therefore **NOT VERIFIED**. The reopen screenshot was captured in a separate
fresh open after closing the first editor tab.

PhotoCraft's in-app File → Close command reports unavailable for a host-bound
document. The tab was closed normally and the document reopened from Seafile.
Other apps were also exited by closing their browser tabs. No Seafile history
page was captured in this run, and no editor-output/readback byte comparison was
made for all five files. The “new version” observations are the editor's save
confirmation, not a claim of uniform history-page verification.

## Screenshot SHA-256

```text
gridcraft-reopen.png  79fbbd11b5a4b2f44e3118e22c473615c51208b3a9c201bb1225674aa7a05f32
gridcraft-save.png    2efd336f0d47ebda577a8d281d473527d5f85043ceafd0c895b301672bde354c
pdfcraft-reopen.png   61c224c36dc22c9d1c7feaf866735788f1c6b18d5248cf9a6d2d2a4e198cb277
pdfcraft-save.png     3c2e5943fffe7114619060cb3685515335ccc5b7c5323c41e7801db1be93b477
photocraft-reopen.png b60193ba19e61fdc935e75977cf004d58f386a122e41b36a280fda49e9c7ad0e
photocraft-save.png   b125c49e403c1a31a9cdb3bfb9ca4145a26e2014fe10086a1de97b8148873287
vectorcraft-reopen.png f1791206e8e43f23f880da2358aef094c8fd3198f05cf7c3c86a119fa35044ae
vectorcraft-save.png   e70a39d27b624cd9919b14f6f5053a263b8a78d321c599287fe81f79a9254b88
wordcraft-reopen.png   f2d8a531702bb37d3418df6452a096f5a4a1c64729ed18783a15289f77e0a7b2
wordcraft-save.png     480b11ffee42b226b2a3a5091c523786efc952b18c424ba82151f06c5bbfc83e
```

The record omits server addresses, cookies, credentials, usernames and session
capability identifiers. Screenshots contain only synthetic document content
and editor UI. ONLYOFFICE was not used or changed.
