# GR-066 — FilmCraft on the synthetic Seafile library

Date: 2026-10-26

Status: **GPT REVIEW PENDING**

## Result

The exact GR-047 FilmCraft Web candidate completed a real Seafile file-list
open, edit, host save, history update, and fresh-session reopen for
`GR-047-synthetic.fcproj`:

1. Uploaded the 3,301-byte GR-047 native project through the Seafile UI for
   setup. The fixture SHA-256 is
   `7b9747511b3a2382bfe09667aa29d4a55dabc39b74ca25962c4c033d0296813a`.
2. Opened it from the existing synthetic library. The gateway `/open/` and
   document GET returned HTTP 200; FilmCraft index, JS, packaged WASM, and
   favicon also returned HTTP 200.
3. Used **Graphics and Titles → New Layer → Text**, replacing `New Text` with
   `GR-066 Film`. The Program monitor displayed the edit and the editor showed
   `Unsaved changes`.
4. Ctrl+S returned `Saved — new version …`; FilmCraft showed `Saved to host`.
   The gateway save POST returned HTTP 200.
5. Navigated away from the editor, returned to the Seafile file list, and
   opened the project again. The new open/document requests returned HTTP 200
   and the fresh FilmCraft session displayed `GR-066 Film` in the Program
   monitor.
6. Seafile's library History UI showed `Added "GR-047-synthetic.fcproj"`
   followed by `Modified "GR-047-synthetic.fcproj"`.

No edited output was downloaded or manually uploaded. The fixture upload was
setup only. The editor was exited by page navigation; an explicit in-app close
action was not recorded.

## Candidate and scoped deployment

- Source: `storytold/filmcraft` commit
  `fa550ce2d07bdfee6b1d7b6835e8abc8c6913d00`.
- Host-save patch: GR-023, SHA-256
  `16158f500b2ec12f93c8fcb14867e0b452030dbb338b2d4d7fa8612850a694d4`.
- Shared transport: `craft-platform` revision
  `56c5e16d79b77751106173c13111ef4fe0a2c0ec`.
- Reused the exact GR-047 actual-WASM candidate; no build was run. The
  five-file inventory includes the HTML, JS, WASM, favicon, and dynamically
  referenced audio worklet. Candidate and active static-root verification
  passed.
- Total served bundle size is 37,842,580 bytes, below the gateway's 50 MiB
  default request ceiling (52,428,800 bytes).
- Added `.fcproj` to the existing single synthetic-library route allowlist and
  mapped it to FilmCraft in the local test-gateway dispatch. Existing mappings
  were retained. Private rollback copies of the prior dispatch and Seahub
  settings remain outside Git.
- The Seahub extension-list assignment was the only settings line changed;
  `ENABLE_ONLYOFFICE=True` remained set. No ONLYOFFICE route/setting was
  changed, and no post-change ONLYOFFICE edit/save regression was run.
- The T3 preview did not expose Seafile's popup as a controllable tab. A
  page-local `window.open` shim restricted to this fixture routed its popup to
  the same tab; the file-list click and gateway handoff still ran.

## Limits

- No editor-message payload hash was captured and compared with Seafile
  readback. The host confirmation, HTTP success, History entry, and visible
  fresh-session edit support persistence but do not prove byte-for-byte
  identity across the browser/gateway/storage boundary.
- The History panel showed the `Added` and `Modified` events, but its screenshot
  was not retained because it displayed the account name.
- A Seafile thumbnail-generation request returned HTTP 500 during browsing;
  the editor file-list handoff and save flow succeeded. The thumbnail failure
  was not investigated.
- This is one synthetic project on one private Seafile instance. It does not
  establish broad project compatibility, deployment security, native popup
  behavior, or a post-change ONLYOFFICE edit/save regression.
- Project GPT remains **INCOMPLETE** and upstream publication remains
  **LOCKED**.

See [`docs/reviews/GR-066/`](reviews/GR-066/README.md) for the verifier,
sanitized observations, hashes, and screenshots.
