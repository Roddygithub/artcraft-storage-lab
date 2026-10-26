# GR-081 — editor document identity binding design R1

## Result

**PROVISIONAL — the save-identity MAJOR remains open.** Filename validation
cannot distinguish the selected document from a same-name replacement. The
host receives serialized bytes after the editor has already chosen to serialize,
so a host-only check cannot enforce refusal before serialization.

This is a design record, not an implementation or verification result. Source
inspection used the pinned WordCraft revision
`00bc6a4b028013b2dfb0e85e8b326aeed3ecff6d` and GridCraft revision
`06920de8da609c19de7446945cfc62b844691efd`. The corresponding disposable
source checkouts are outside this repository. Existing GR-016 patches were
applied to those checkouts for inspection; no GR-081 changes were made there.
No tests, builds, browser workflows, or services were used.

## Relevant source facts

- WordCraft exposes [`Session::document_id()` and advances it when a new
  document is installed](https://github.com/storytold/wordcraft/blob/00bc6a4b028013b2dfb0e85e8b326aeed3ecff6d/crates/engine/src/session.rs#L798).
  Web Save and Save As converge before serialization in
  [`WordApp::execute()`](https://github.com/storytold/wordcraft/blob/00bc6a4b028013b2dfb0e85e8b326aeed3ecff6d/crates/ui-egui/src/lib.rs#L1006).
  The app command path and engine session command path both need enforcement;
  guarding only the toolbar would leave shortcut, dialog, macro, and direct
  command paths. Macros call
  [`Session::run()`](https://github.com/storytold/wordcraft/blob/00bc6a4b028013b2dfb0e85e8b326aeed3ecff6d/crates/engine/src/session.rs#L1384).
- GridCraft assigns each `DocState` a UID in
  [`Session::new_document()`](https://github.com/storytold/gridcraft/blob/06920de8da609c19de7446945cfc62b844691efd/crates/engine/src/lib.rs#L168).
  A pathless workbook's ordinary Save
  currently falls through to a Save As dialog and serializes in the web dialog
  handler. Blocking that dialog alone would also block ordinary browser Save.
  Backstage and export code include additional serializer paths.
- Both current GR-016 web adapters send `saveAs=false` from a callback that
  already has serialized bytes. The gateway cannot infer native document
  identity from that flag or from a filename.

## Proposed fail-closed protocol

This protocol is proposed and **not implemented**:

```text
ready       { saveIdentity: 1 }
open        { openId, mode: "update-only", name, bytes }
opened      { openId, documentId }
save        { openId, documentId, intent: "save", ticket, name, bytes }
saveResult  { openId, documentId, ticket, ok, error }
dirty       { openId, documentId, dirty }
```

`openId` identifies one host opening; `documentId` is the editor's native
identity serialized as a string. They are correlation values, not credentials.
The editor should bind only after the trusted host-supplied initial document
has parsed successfully. A normal picker/drop inbox must not be able to replace
that initial document before binding.

In update-only mode, reject New, Open/replacement, Save As, template replacement,
and destination-changing save parameters before prompts, side effects, or
serialization. Recheck the actual native identity immediately before
serialization. The adapter must send the identity captured for that
serialization; copying the host's binding onto every save would not prove which
document produced the bytes. Keep exports and save-copy operations outside the
host update path.

The gateway should enable writable mode only after feature negotiation and a
matching `opened` message. It should accept a save only when `openId`,
`documentId`, `intent`, and ticket match the active binding, in addition to the
existing filename/format constraints. Bind dirty state and acknowledgements to
the same context and clear the rejection latch only after durable storage
succeeds. Old hosts and old editors must fail closed rather than falling back
to filename-only writes.

## Implementation surfaces

- **WordCraft:** guard `WordApp::run()` before discard/save prompts;
  `WordApp::execute()` before web serialization; direct dialog entry points;
  replacement commands including mailings; and `Session::run()` because
  macros call it directly. Preserve ordinary Save and keep exports separate.
- **GridCraft:** intercept hosted `file.save` in `SheetApp::run_command()` and
  Backstage `save()` so pathless ordinary Save reaches the host; guard direct
  dialogs and engine command execution; protect Backstage export paths; retain
  the `(uid, Arc<Workbook>)` snapshot used for matching acknowledgements.
- **Transport/adapters/gateway:** extend the two app adapters and web-shell
  initial-open flow, shared [`craft-platform` messages](../../../integration/rust/craft-platform/src/browser/host.rs),
  and the [`gateway listener`](../../../integration/gateway/hostpage.py).
  Preserve source/origin checks, framing, size bounds, save tickets, timeouts,
  and dirty-state latching.
- **Pins and bundles:** WordCraft/GridCraft pin the existing transport
  revision `90c261de…`; updating only the repository transport source would not
  change the candidates. New adapter patches, exact dependency pins/locks,
  inventories and rebuilt bundles will be needed after implementation.

## Required future verification

Before closing the finding, verify through both editor command surfaces that
same-name replacement and Save As produce zero serializer calls and zero
uploads; exercise keyboard and GridCraft Backstage ordinary Save; cover initial
open/drop races, parse failure, duplicate open, stale identity, old-peer
negotiation, wrong acknowledgements, failed-save retry, and edits during an
outstanding save; then run actual-WASM roundtrips and synthetic Seafile
version/fresh-reopen evidence. Existing GR-055/056 evidence does not establish
these refusal properties. The current protocol test also retains an old
renamed-save expectation; it was not edited or run in this work item.

Until those changes and checks exist, editor-side pre-serialization refusal,
same-name replacement safety, and deployed behavior remain **NOT VERIFIED**.
