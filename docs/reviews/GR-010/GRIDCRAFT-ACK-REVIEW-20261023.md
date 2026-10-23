# Independent review — GridCraft durable save acknowledgement

Date: 2026-10-23  
Scope: `gridcraft-0.10.0-durable-save-ack.patch` against pinned GridCraft
`06920de8da609c19de7446945cfc62b844691efd`  
Reviewer: `artcraft-reviewer` (Nemotron 3 Ultra 550B A55B)  
Verdict: **PASS for this narrow patch**, with minor follow-ups. This is a
provisional free-model review, not a GPT verdict or GR-010 E2E pass.

## Findings

### Blocker

None.

### Major

None.

### Minor

1. `apps/gridcraft-web/src/host.rs`: pending saves have no timeout or cleanup if
   the host disappears before responding; long-lived sessions could retain
   pending entries.
2. The bridge has no protocol-version negotiation. An older host that does not
   send `gridcraft:saveResult` leaves the workbook dirty. This fails closed, but
   the compatibility behavior is not negotiated.
3. A concurrent Save As and Save can apply titles in acknowledgement order. The
   reviewer assessed this as low risk; snapshot-based dirty tracking remains
   intact.

These findings are recorded, not silently treated as fixed. The first two are
follow-ups for a bounded host integration; the third is a low-risk edge case.

## Evidence independently checked by reviewer

- Patch applies to the pinned source checkout.
- Engine and UI library tests passed; affected `file_menu` and
  `text_box_editing` integration targets passed individually.
- WASM check and optimized Trunk build passed according to the recorded run.
- Chromium smoke observed a real GridCraft edit, a failed acknowledgement
  retaining dirty state, and a successful retry clearing it.
- Reviewer inspected all eight changed source files.

The full `gridcraft-ui-egui` integration suite did not complete because the
temporary filesystem quota was exhausted while compiling unrelated targets.
No Seafile persistence/version or GridCraft semantic reopen was tested. Those
remain **NOT VERIFIED**; see `README.md` and `docs/TEST-MATRIX.md`.
