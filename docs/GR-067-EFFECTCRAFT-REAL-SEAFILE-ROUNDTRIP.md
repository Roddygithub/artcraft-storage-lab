# GR-067 — EffectCraft on the synthetic Seafile library

Date: 2026-10-26

Status: **GPT REVIEW PENDING**

## Result

The existing GR-046 EffectCraft Web/WASM candidate completed a synthetic
Seafile file-list open, visible text edit, host save, history check, and fresh
file-list reopen for `GR-067-synthetic.ecproj`.

1. Uploaded the 32,280-byte native `.ecproj` fixture through the Seafile UI
   for setup only. SHA-256:
   `cb7852f97d55e8048d8d5cb9f1649085b5cf06ff301104d7fcb608188c0a4ec0`.
2. Added `.ecproj` to the existing synthetic-library extension allowlist and
   mapped it to EffectCraft in the local test-gateway dispatch. Existing
   mappings were retained.
3. The Seafile file-list click reached the patched `/open/` route. The dynamic
   parent page and EffectCraft index, JS, WASM, and runtime snippet returned
   HTTP 200. One initial attempt got HTTP 404 for the omitted `snippets/.../host.js`
   asset and stayed on the loading screen. The exact snippet from the existing
   GR-046 build was copied into staged and active roots; its SHA-256 matched,
   and the subsequent request returned HTTP 200.
4. In EffectCraft's canvas, replaced the visible text with
   `EffectCraft GR-067 saved`. The editor showed `Unsaved changes`.
5. The sanitized operator observation records Ctrl+S displaying `Saved to
   host`, one gateway save POST returning HTTP 200, and Seafile displaying
   `Saved — new version …`. The retained
   `reviews/GR-067/runtime/save-confirmation.png` shows the canvas edit and
   Seafile's new-version confirmation; it does not show the editor's `Saved to
   host` message.
6. Navigated the original editor tab away to the Seafile library list, then
   opened the file from that list in a new tab/session. The new open and
   document GET returned HTTP 200; the composition displayed the saved text.
   The fresh-session screen is retained in
   `reviews/GR-067/runtime/fresh-reopen.png`.
7. Seafile's file History → Versions page showed the current version at
   `2026-10-26 05:21:54` and the preceding version at `2026-10-26 05:13:31`.
   The page exposed an account display name, so no history screenshot or name
   is retained.

No edited output was downloaded or manually uploaded. The initial fixture
upload was setup only. The old editor view was exited by navigating back to the
library list; an explicit in-app close action was not recorded.

## Candidate and scoped deployment

- Source: `storytold/effectcraft` commit
  `049070d65c66a73f322b496b22521816e0018f14`.
- Host-save patch: GR-022, SHA-256
  `4e0a1799e36209e1234a1b3ff504ab5ed647cf3bd066af6dec90dacd46ab7407`.
- Shared transport: `craft-platform` revision
  `56c5e16d79b77751106173c13111ef4fe0a2c0ec`.
- Reused the GR-046 actual-WASM candidate; no build was run. The manifest
  records 11 served files totalling 57,470,921 bytes. The staged candidate,
  active static-root copy, and build cache match file-for-file and by SHA-256.
- `.ecproj` was added only to the existing synthetic-library allowlist and the
  local test-gateway dispatch. DOCX, XLSX, PDF, SVG, PPTX, DesignCraft and
  FilmCraft routes remained present. After the run, the local dispatch was
  restored to its pre-test copy, the Seahub settings file was restored byte for
  byte from its private rollback copy, and `seahub.service` was verified active.
  `ENABLE_ONLYOFFICE=True` remained in the restored configuration. The temporary
  gateway process was stopped. No ONLYOFFICE edit/save regression was run.
- The static EffectCraft files remain staged locally but the `.ecproj` route is
  no longer enabled.

## Limits

- The editor save-message bytes and Seafile readback bytes were not separately
  captured and hashed. HTTP 200, the editor/host confirmations, a second
  Seafile version, and the fresh editor session support persistence but do not
  prove byte-for-byte identity across the message/gateway/storage boundary.
- The recorded Seafile history observations are manual browser observations;
  the account-bearing history screenshot was intentionally omitted.
- One initial static asset request returned 404 before the omitted runtime
  snippet was restored. The successful retry loaded all required assets.
- This is one synthetic project on one private Seafile instance. It does not
  establish broad project compatibility, deployment security, or a post-change
  ONLYOFFICE edit/save regression. Production behavior remains **NOT VERIFIED**.
- Project GPT remains **INCOMPLETE** and upstream publication remains
  **LOCKED**.

See [`docs/reviews/GR-067/`](reviews/GR-067/README.md) for provenance, hashes,
sanitized observations, and the candidate verifier.

R1's bounded **PROVISIONAL PASS** was followed by two MINOR evidence-presentation
findings, both corrected. R2 returned a bounded **PROVISIONAL PASS** with one
tracking MINOR, also corrected. R3 returned a bounded **PROVISIONAL PASS** with
two P3 documentation findings: the R1 follow-up's R2-pending statement is now
qualified as historical, and the evidence README checksum has been refreshed.
R4 returned a bounded **PROVISIONAL PASS** with no new findings. Runtime chronology, fresh-session creation,
history timestamps, cleanup, and service state remain implementer-reported.
Exact save/readback identity, explicit in-app close, and post-change ONLYOFFICE
edit/save remain **NOT VERIFIED**. This is not project GPT PASS or upstream
authorization.
