# GR-068 — PdfCraft on the synthetic Seafile library

Date: 2026-10-26

Status: **GPT REVIEW PENDING**

## Result

The GR-057 PdfCraft Web candidate opened the existing synthetic `form.pdf` from
Seafile, saved a visible AcroForm text edit through the host route, and reopened
the file from the Seafile list in a new editor session.

1. The existing synthetic PDF showed five interactive form fields. No fixture
   upload was needed; the file was already in the synthetic library.
2. Seafile's file-list click opened the PdfCraft route. The gateway `/open/`,
   PdfCraft index, JS, WASM, and document GET returned HTTP 200.
3. Replaced the top form field with `GR-068 saved edit`. The editor displayed
   `Unsaved changes`.
4. Ctrl+S displayed `Saved — new version …`; the gateway save POST returned
   HTTP 200. The final save screen is retained in
   `reviews/GR-068/runtime/save-confirmation.png`.
5. Navigated the original editor tab back to the Seafile library, then opened
   `form.pdf` from the list in a new tab/session. The new document GET returned
   HTTP 200 and the field displayed `GR-068 saved edit`. See
   `reviews/GR-068/runtime/fresh-reopen.png`.
6. Seafile's History → Versions page listed three entries: current 3.0 KB at
   `2026-10-26 05:29:46`, preceding 2.4 KB at `01:30:57`, and older 1.7 KB at
   `01:30:16`. The page exposed an account display name, so no history
   screenshot or name is retained.

There was an initial editing attempt that was canceled with Escape; the field
returned to its previous text. A later edit was committed by moving focus out
of the field before saving. The final saved value is confirmed in the fresh
session. The initial attempt showed a host version message, but the retained
history does not establish whether that no-op attempt created a separate
revision; we do not claim its version count.

No edited output was downloaded or manually uploaded. The existing synthetic
PDF was used throughout; no service configuration or dispatch change was
needed.

## Candidate and scope

- Source: `storytold/pdfcraft` commit
  `57e531ccca0047597809748b5cb4276336d6051a`.
- Host-save patch: GR-017, SHA-256
  `6d50eb1f45e81f2037948cd6160878feb2d87eb0881d167f0fc1d290e4450562`.
- Shared transport: `craft-platform` revision
  `90c261de22ef75c4c7c5c5cd1c712d483be0bbc8`.
- Reused the GR-057 actual-WASM candidate; no build was run. Its three served
  files match the active local static root by size and SHA-256. The candidate
  is the functional `wasm-opt=0` build recorded in GR-057.
- Existing `.pdf` route and allowlist were reused; neither gateway dispatch nor
  Seahub settings were changed. `ENABLE_ONLYOFFICE=True` remained enabled. No
  ONLYOFFICE edit/save regression was run.
- The temporary gateway process was stopped after the test. No other service
  was modified or restarted.

## Limits

- Save-message bytes and Seafile readback bytes were not separately captured
  and hashed. The host confirmation, successful save POST, Versions entries,
  and fresh editor session support persistence but do not prove byte identity
  across the browser/gateway/storage boundary.
- The history observation is a manual browser observation; the account-bearing
  screenshot was intentionally omitted.
- This is one synthetic PDF on one private Seafile instance. It does not
  establish broad PDF compatibility, deployment security, optimized production
  performance, or post-change ONLYOFFICE edit/save behavior. Production
  readiness remains **NOT VERIFIED**.
- Project GPT remains **INCOMPLETE** and upstream publication remains
  **LOCKED**.

See [`docs/reviews/GR-068/`](reviews/GR-068/README.md) for asset hashes,
sanitized observations, and the candidate verifier.

Independent R1 returned a bounded **PROVISIONAL PASS** with no findings. HTTP
results, file-list/fresh-session chronology, history entries, configuration
changes, ONLYOFFICE state, and gateway cleanup remain implementer-reported.
Exact save/readback identity, explicit in-app close, post-change ONLYOFFICE
edit/save, and production readiness remain **NOT VERIFIED**. This is not
project GPT PASS or upstream authorization.
