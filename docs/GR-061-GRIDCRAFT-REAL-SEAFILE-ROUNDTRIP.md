# GR-061 — GridCraft real synthetic Seafile roundtrip

Date: 2026-10-26  
Status: **GPT REVIEW PENDING**  
Scope: one synthetic `.xlsx` in the existing synthetic Seafile library. The
exact GR-056 GridCraft candidate was staged on the existing GR-059 gateway and
dispatched only for `.xlsx` in that already allowlisted library. WordCraft's
DOCX route remains enabled. No production documents were opened or changed.

## Result

The actual GridCraft Web/WASM candidate completed this browser flow through the
owner's authenticated Seafile session:

1. Added the generated `synthetic.xlsx` fixture through Seafile's own file
   upload UI. This was test-fixture setup only; it is not save evidence.
2. Clicked `synthetic.xlsx` in the Seafile file list. Seafile handed it to the
   gateway, which opened the staged GridCraft candidate and delivered the
   workbook.
3. Changed B2 from `42` to `1337` in the GridCraft UI. The visible B3 formula
   remained `=SUM(B2:B2)` and recalculated to `1337`.
4. Pressed Ctrl+S. The editor displayed `Saved — new version …`; the browser
   recorded the gateway save POST as HTTP 200 and the editor returned to a
   clean state. Seafile's library history subsequently showed a
   `Modified "synthetic.xlsx"` event, separate from the fixture's earlier
   `Added` event.
5. Returned to the Seafile file list and clicked `synthetic.xlsx` again. This
   created a fresh editor iframe/session. GridCraft loaded the stored workbook
   and displayed B2=1337, the B3 formula, and B3=1337.

The edited bytes were persisted by the editor-to-gateway-to-Seafile save path.
The fixture upload was only the initial test setup; no manual upload was used
to persist the edit. The result demonstrates one successful Seafile version
and a fresh Seafile-backed reopen for GridCraft. It does not establish general
formula compatibility or production readiness.

## Scoped deployment

- The deployed GridCraft assets were checked against the four-file GR-056
  candidate inventory before installation. The runtime verifier also passes
  against the deployed static root.
- The gateway dispatcher now maps DOCX to WordCraft and XLSX to GridCraft.
- Seahub's ArtCraft extension allowlist now contains DOCX and XLSX, while
  retaining the same single synthetic library restriction. No other library
  was added to that allowlist.
- `ENABLE_ONLYOFFICE=True` remained set. The prior GR-059 open-only check still
  records ONLYOFFICE loading from a non-allowlisted synthetic library; this
  GR-061 change did not touch that integration. A new ONLYOFFICE save/version
  regression was not run.
- Before the change, the live gateway dispatch/static tree and Seahub settings
  were backed up outside Git. The private rollback copy is retained locally.
- The dedicated GR-060 LXC remains stopped with auto-start disabled; this test
  used the existing GR-059 gateway.

## Evidence

- [Save confirmation screenshot](reviews/GR-061/runtime/gridcraft-save-confirmed.png)
- [Fresh Seafile reopen screenshot](reviews/GR-061/runtime/gridcraft-seafile-reopen.png)
- [Sanitized browser observations](reviews/GR-061/runtime/browser-observations.txt)
- [Artifact checksums](reviews/GR-061/SHA256SUMS)
- [Evidence README](reviews/GR-061/README.md)
- [Independent R1–R3 reviews](reviews/GR-061/INDEPENDENT-REVIEWS.md)

The screenshots show only the synthetic workbook in the editor. Private
hostnames, library identifiers, session capabilities, account details, and
user names are intentionally excluded.

## Limits

- One file, one synthetic library, one browser session, and one candidate build
  were exercised.
- Permission revocation, external writers, capability expiry/replay, response
  loss, cross-origin proxy/TLS deployment, optimized `wasm-opt` output, and a
  post-change ONLYOFFICE edit/save regression remain **NOT VERIFIED**.
- Independent R1–R3 bounded reviews were PROVISIONAL PASS with no blocker or
  major; two documentation minors were corrected. R3 did not verify exact
  historical comparison against the unavailable R1/R2 snapshots.
- No project-level GPT PASS is claimed. Project status remains **INCOMPLETE**;
  upstream publication remains **LOCKED**.
