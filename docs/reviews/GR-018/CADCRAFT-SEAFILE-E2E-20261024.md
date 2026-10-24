# GR-018 — CADCraft synthetic Seafile E2E

Date: 2026-10-24
Repository state before evidence update: `6632a575a0d0cead69167492906de20df06a1c0a`
CADCraft source base: `7bf5905ac97316a7896de8cbc12d243f57b09bd8`
Environment: isolated synthetic Seafile/Seahub/fileserver container; loopback only

## Result

**Reproduced for CADCraft in the isolated synthetic stack:** Seahub file-list
click → CADCraft Web/WASM → circle edit → Ctrl+S → durable Seafile history
entry → fresh Seahub click → fresh CADCraft instance shows the circle.

This is a bounded runtime result for CADCraft. It does not change the project
GPT-6.1 Sol FAIL on `0edbe524b4fa321b0f73f8601afef390e7f785e6`, establish
public-deployment readiness, or authorize upstream publication.

## Reproduction record

1. Built-in Seahub frontend assets were built and collected into the isolated
   test instance so its real file list could be used.
2. Uploaded the synthetic 131-byte DXF fixture
   `artcraft-cadcraft-seafile-synthetic.dxf` through the Seahub library UI.
   Fixture SHA-256: `4d7c3026f3b5b4c9c38bd306187d30c9fea5a21dda2d6d12852be3cf3449f7c5`.
3. Clicked that row in the `ArtCraft Synthetic` library. Seahub routed the file
   to the locally hosted CADCraft Web build at the gateway; the editor reported
   the DXF opened.
4. Entered `CIRCLE` in CADCraft's command line, created a circle, and pressed
   Ctrl+S. The gateway's `/session/<id>/save` request returned HTTP 200, and
   CADCraft displayed **Saved — new version** with commit
   `94a4521fae3bf94ded073714a43c020831fd05cb`.
5. Queried Seafile history and downloaded the saved file back through the
   Seafile API. History contained two commits. The earlier entry had file ID
   `0797b58fd2e214315a678bd2eb379a105186bbee` and size 131 bytes; the new entry
   had file ID `3646d5c4ca8b432339d8b03a6fbe0d85d789d770` and size 17,501 bytes.
   The readback SHA-256 was
   `fbc8b34170665efb248447c3850ebec22cc5567034b8d8d853ffd91a53093bf0`.
   The bytes contain a DXF `CIRCLE` entity and terminate with `EOF`.
6. Returned to the Seahub library and clicked the same file again. This opened
   a fresh CADCraft instance from Seafile; the circle was visible in the
   reopened drawing.

No manual download/upload was used for the save. The only UI upload was the
initial synthetic fixture. No production Seafile or ONLYOFFICE setting was
changed.

## Screenshots

- [Synthetic library and uploaded DXF](runtime/seafile-cadcraft-library-20261024.png)
- [CADCraft durable-save confirmation](runtime/seafile-cadcraft-save-confirm-20261024.png)
- [Fresh CADCraft reopen showing the circle](runtime/seafile-cadcraft-reopen-20261024.png)

## Limits

- The Seafile stack was local and synthetic, not the user's production instance.
- This run did not separately hash the exact bytes inside the browser's
  `cadcraft:save` message. The recorded SHA-256 is of bytes downloaded back
  from Seafile.
- The CADCraft build used the local GR-018 patch and GR-016 shared transport
  scratch checkout; its absolute `/tmp` dependency remains a reproducibility
  and publication gate. This was not a clean standalone build.
- The build had `wasm-opt=0`; optimized bundle size/performance is not verified.
- This run does not exercise timeout, save failure, permission revocation,
  external-writer races, cross-origin production topology, or the other Craft
  applications.
- The test account is synthetic. Its password was rotated locally and is kept
  only in the runtime test configuration with mode 0600; no credential is in
  this repository.

## Reproduction boundary

The browser observations above were made against the running isolated container
and were not a mock-host test. API readback independently confirmed the Seafile
history entry and saved bytes. The saved-byte hash proves the readback content;
it does not establish exact byte identity across the editor-to-gateway boundary.
