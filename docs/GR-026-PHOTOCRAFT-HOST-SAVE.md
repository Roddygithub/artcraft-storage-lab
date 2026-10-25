# GR-026 — PhotoCraft host integration assessment

**Status:** pathless-open/snapshot-ACK core implemented as a local patch and
independently reviewed PROVISIONAL PASS after fixing stale ACK identity and
patch application format. The full host adapter is not implemented. This is not
a project verdict or upstream authorization.

| Field | Value |
|---|---|
| Audited source | `storytold/photocraft` `a02f2ee41059d3312e7ff24a5af5edcac7b6435a` |
| Required shared transport | `craft-platform` `56c5e16d79b77751106173c13111ef4fe0a2c0ec` |
| Code patch | [`photocraft-core-slice-r2.patch`](reviews/GR-026/photocraft-core-slice-r2.patch), SHA-256 `4ca7ea1e88bf215f80e6edc137417b8b21d0302e82b9a7a496ffd4e60b0cd3e4` |
| Evidence | [`README.md`](reviews/GR-026/README.md), [independent R2](reviews/GR-026/REVIEW-INDEPENDENT-R2.md) |

## Decision

Do not attach host saves to PhotoCraft's current browser `write` callback. It
only triggers a download, and the UI explicitly sets `write_unconfirmed: true`
so a download cannot mark the document saved. Setting it false or treating
`post_save` delivery as success would create false clean state. The current
public `PhotocraftApp::open_file(path, bytes)` also binds `path` as a native
save path; passing a host filename there would silently misrepresent host data
as a local file. The app supports multiple document tabs and a large set of
document creation/open/replace routes, so an adapter that only guards File ›
Save/Save As would not establish a one-document binding.

The smallest safe next implementation is a pathless, one-document host mode:

1. Add a public Rust-only pathless open method that imports bounded supplied
   bytes using the host name only as the display name; it must not set
   `DocState.path` or Open Recent.
2. Add an engine/UI host-save hook which captures `(document id, revision,
   name, bytes)` from one supported lossless format (`.pcraft`) and sends it
   with one bounded `SaveTicket` through the existing `craft-platform` browser
   transport. Keep at most one pending save and reject additional/unknown
   tickets. Only a valid matching positive `saveResult` advances the saved
   baseline to the captured revision; edits after capture remain dirty.
3. Preserve dirty state on a negative ACK. On timeout, retain the unresolved
   ticket as unknown, keep dirty state and tell the user to reconcile before
   retry. Do not auto-retry an unknown write.
4. In host mode, refuse second host Opens, native file pick/drop Open,
   document replacement, new/duplicate-document flows, Save As, Save a Copy,
   and any close/discard route that can lose an unresolved or dirty snapshot.
   Exports that do not replace the bound file can remain explicit exports.
   Standalone browser download and native filesystem behavior must remain on
   their existing path.
5. Add focused engine/UI tests for pathless open, matching ACK, edit-after-save,
   negative/unknown ACK, duplicate/unknown ACK, pending bound, standalone
   download/native behavior, and each replacement/Save As bypass. Then perform
   Rust 1.95 locked WASM check, format and diff checks on a patch generated
   against the exact audited SHA.

This remains a design only. Seafile authorization, browser protocol execution,
version creation and fresh-editor reopen are **NOT VERIFIED**.

The core patch is a necessary primitive only. It does not implement browser
transport, the async UI save lifecycle, or Seafile integration. Browser protocol,
authorization, version creation and fresh-editor reopen remain **NOT VERIFIED**.
