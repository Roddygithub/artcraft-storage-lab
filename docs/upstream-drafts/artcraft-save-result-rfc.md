# RFC: `<app>:saveResult` — telling a Craft web app how a host save ended — DRAFT, unpublished

Target: the four apps with a `?host=parent` bridge (WordCraft, GridCraft, PdfCraft, CADCraft) and
any future shared bridge crate in `craft-libs`.

## Problem

`<app>:save` hands bytes to the parent page. GridCraft's and WordCraft's `Services::download` has no
`Result`, so after posting the message the app marks the document saved. When the parent's storage
write fails (network, conflict, permission), the user sees "saved" and closes the tab; the edit is
lost. PdfCraft returns a synchronous `Result` from `host_save`, which only covers the `postMessage`
call itself, not the storage write that happens later.

## Proposal (backwards compatible)

1. `<app>:save` gains an optional `ticket` (a string the app chooses, unique per save).
2. The parent may answer `<app>:saveResult { ticket, ok, version?, error? }` on the app's own origin.
3. An app that sent a `ticket` keeps the document **dirty until** it receives `ok: true` for that
   ticket; on `ok: false` it shows `error` and stays dirty. An app that did not send a ticket keeps
   today's optimistic behaviour. A parent that does not answer changes nothing.
4. `version` is an opaque string the host may use to label the document (not interpreted by the app).

## Reference implementation on the host side

`bridge/static/host.js` already answers `saveResult` when a `ticket` is present (`handleSave`), and
keeps the host-page dirty state consistent with the editor's. The lab's older per-app patches
(`docs/reviews/GR-010`, `GR-017`, `GR-018`) implemented the app side for GridCraft 0.10, PdfCraft and
CADCraft of October 2026; they need rebasing on the upstream `host.rs` files that have since landed.

## Why upstream

Thirteen apps are converging on the same bridge; a shared crate in `craft-libs` with this
acknowledgement built in removes the "saved but lost" class of bug for every host (Nextcloud,
Seafile, a personal file server), not only ours.
