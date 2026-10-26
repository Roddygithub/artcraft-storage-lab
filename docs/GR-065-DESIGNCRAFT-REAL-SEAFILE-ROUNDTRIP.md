# GR-065 — DesignCraft on the synthetic Seafile library

Date: 2026-10-26

Status: **GPT REVIEW PENDING**

## Result

The staged DesignCraft Web WASM completed a real file-list open, edit, save,
Seafile history update, and fresh-session reopen for `synthetic.designcraft`:

1. Uploaded the 6,585-byte GR-045 synthetic DesignCraft fixture through the
   Seafile UI for setup.
2. Opened it from the synthetic library file list. The pinned DesignCraft
   JavaScript/WASM loaded and the gateway returned the document.
3. Replaced the visible text with `GR-065 DesignCraft save verified`; the
   editor showed `Unsaved changes`.
4. Ctrl+S returned `Saved — new version …`; the DesignCraft status changed to
   `Saved to file host`. The gateway save POST returned HTTP 200.
5. A browser-back keyboard attempt left the same visible text while the editor
   showed `Unsaved changes`; Ctrl+S was used again before leaving. This created
   two `Modified` history events. The history UI also showed the initial
   `Added` fixture event.
6. Navigated away from the first editor to Seafile home, returned to the
   synthetic library, and opened the file from its list again. The new open
   handoff and document GET returned HTTP 200; the fresh editor displayed the
   saved text.

No edited output was downloaded or manually uploaded. The fixture upload was
setup only. The first editor was exited by navigating away; an explicit
in-editor close action was not recorded.

## Candidate and scoped deployment

- Source: `storytold/designcraft` commit
  `80d13911b2d20fbb5cd9398696627bb3a715417b`.
- Host-save patch: GR-021, SHA-256
  `519c03180b17f035ef8fbfcd08a85bda312f6f0721bfbdf9dc1d9d5992fdf972`.
- Shared transport: `craft-platform` revision
  `56c5e16d79b77751106173c13111ef4fe0a2c0ec`.
- Reused the GR-045 actual-WASM candidate; this work item did not rebuild it.
  [`hash-inventory.json`](reviews/GR-065/hash-inventory.json) records all three
  served assets. The candidate verifier passes both the staged candidate and
  the active static root, including each index-to-file SRI association.
- The 49,630,474-byte bundle is below the gateway's 50 MiB default request
  ceiling (52,428,800 bytes).
- Added DesignCraft routing and `.designcraft` to the existing one-library
  synthetic allowlist for this test. Prior app mappings were retained. The
  change is in the local test deployment, not committed repository dispatch.
  A private rollback copy is retained outside Git.
- This GR did not edit ONLYOFFICE settings or routes. A post-change
  ONLYOFFICE edit/save regression was not run.

## Limits

- The T3 preview did not expose Seafile's popup as a controllable tab. A
  page-local `window.open` shim, restricted to `synthetic.designcraft`, sent
  that popup to the same tab. The actual Seafile file-list click and gateway
  open/save flow ran; the native popup lifecycle was not tested.
- The history screen showed `Added` and two `Modified` entries. Its screenshot
  was not retained because it exposed the account display name. The sanitized
  observation transcript records only the event types and file name.
- No editor-message payload hash was captured and compared with Seafile
  readback. The HTTP success, host confirmation, history entries, and visible
  fresh-session edit support persistence, but do not prove byte-for-byte
  identity across the editor/gateway/storage boundary.
- This is one synthetic DesignCraft document on one private Seafile instance.
  It does not establish broad format compatibility, deployment security, or
  post-change ONLYOFFICE edit/save behavior.
- Project GPT remains **INCOMPLETE** and upstream publication remains
  **LOCKED**.

See [`docs/reviews/GR-065/`](reviews/GR-065/README.md) for the candidate
verifier, sanitized observations, hashes, and screenshots.
