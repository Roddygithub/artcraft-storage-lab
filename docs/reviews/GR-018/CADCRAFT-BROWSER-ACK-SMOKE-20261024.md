# GR-018 CADCraft browser host-ACK smoke

**Result: PASS for the local synthetic host flow only.** This is not a Seafile
save/version test, not a project-level GPT verdict, and not deployment evidence.

## Environment

- Scratch source: `/home/roddy/.cache/artcraft-gr018-cadcraft-work`, based on
  CADCraft `7bf5905ac97316a7896de8cbc12d243f57b09bd8` plus the GR-018 patch
  reviewed by GPT-6.1 Sol low round 4.
- Rust/WASM release build used the local `craft-platform` scratch dependency.
  `data-wasm-opt="z"` was temporarily changed to `"0"` for this functional
  build, then restored in the scratch source; the optimized bundle is not
  verified.
- Served locally at `http://localhost:8771`; Chromium loaded the built
  `cadcraft-web` WASM and the temporary `cadcraft-host-test.html` harness.
- No Seafile, network storage, production instance, or upstream repository was
  used.

## Observed flow

1. The synthetic parent received `cadcraft:ready` and opened a minimal synthetic
   `synthetic.dxf` in the editor.
2. Used CADCraft's Circle tool to create a circle on the drawing canvas. The
   host status changed from `Editor dirty=false` to `Editor dirty=true`.
3. Pressed Ctrl+S. The parent received `cadcraft:save` with ticket
   `cadcraft:1`, name `synthetic.dxf`, and 17,504 serialized bytes. The harness
   calculated SHA-256
   `994686eaa79b2d7345c6ba2c934cde107a02ee7977bba8fe19eaa5ec9ac3ae06` over
   the exact `ArrayBuffer` received in that message, retained those bytes in
   page memory, then returned `cadcraft:saveResult {ok:true}` for that ticket.
4. The editor reported `dirty=false` after the acknowledgement.
5. Clicked **Reopen saved bytes**. The harness created a fresh iframe/editor
   instance, supplied the retained serialized bytes on its new `cadcraft:ready`,
   and the reopened canvas displayed the circle. The parent recorded a second
   `cadcraft:ready` and `reopened=true`.

Screenshot: [`runtime/cadcraft-host-ack-reopen.png`](runtime/cadcraft-host-ack-reopen.png).

## Limits

This verifies a real CADCraft Web/WASM edit, host message delivery, content
hashing at the browser-message boundary, successful ACK handling, dirty-state
transition, and a fresh-editor reopen from the same in-memory bytes. The
synthetic host did not persist bytes to Seafile or create a version. Save
failure, stale/late ACK, origin rejection, timeout scheduling, and standalone
download/native regressions were not exercised in this browser run. The absolute
scratch dependency still prevents a standalone build from this repository.
