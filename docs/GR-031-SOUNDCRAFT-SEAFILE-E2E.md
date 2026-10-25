# GR-031 — SoundCraft Seafile file-list save and reopen

**Status:** reproduced on the isolated synthetic stack; independent bounded
Luna High review returned PROVISIONAL PASS with minor evidence qualifications.
This is not a project GPT PASS or publication approval.

## Result

The actual Seahub file-list route opened the patched SoundCraft Web/WASM app.
After adding an `Audio 2` track in the editor and pressing Ctrl+S, the host
reported **“Saved — new version”**. Seafile returned a different file ID and
repository head. A fresh click from the Seahub file list reopened the saved
project with three tracks (`Starter`, `Audio 1`, `Audio 2`) and no unsaved
changes.

```text
Seahub synthetic file-list click
  → SoundCraft Web/WASM opens the stored .scraftz
  → user adds Audio 2
  → Ctrl+S → gateway → Seafile commits a new head
  → host ACK → editor shows Saved — new version
  → fresh Seahub file-list click → three tracks restored
```

This run used an isolated rootless Podman Seafile test stack and the synthetic
`ArtCraft Synthetic` library. Production Seafile and ONLYOFFICE were not
accessed or changed.

## Runtime evidence

| | Before final save | After final save and fresh readback |
|---|---|---|
| File ID | `dd4e8d6dbae23fc2c2a46461b93797b49b692d7e` | `9dcd6e06ab96d7e6f1ffc46b3a073ceeb7645c46` |
| Seafile head | `fd213fbb6ca633a5bea840c8d7e9d6ab5b5c67ee` | `d2ffd245b443e291d0dd956e3448f7e9612dfc7b` |
| Stored bytes | 5,449 | 6,877 |
| SHA-256 of Seafile content readback | previous head | `895bce8fa565730ded872bbf1dd1746ddddc0345e72d9485279e3d987a5a3aff` |

The readback used the patched user-bound `thirdparty-editor/file-info` and
`thirdparty-editor/file-content` endpoints. Both returned HTTP 200 for the
final file. The fresh editor route then rendered the added track. The exact
`soundcraft:save` MessageEvent bytes were not separately captured and hashed;
the hash above is for bytes read back from Seafile.

Screenshots are in [`runtime/`](reviews/GR-031/runtime/): one shows the
editor’s version confirmation and three-track state; the other shows the fresh
Seahub reopen with all three tracks and a clean editor state.

## Host binding fix

The first Seafile attempt exposed a filename mismatch: SoundCraft serializes its
internal project title (`ArtCraft SoundCraft Smoke.scraftz`), while the
Seafile object was `host-fixture-small.scraftz`. Sending the editor title as
`X-ArtCraft-Filename` made the gateway reject the write. The host page now:

- pins the write filename to the originally selected Seafile filename;
- refuses explicit `saveAs` and a different output extension, returns a failed
  ticket result, and leaves the session dirty;
- checks that the `.scraftz` ZIP directory contains exactly one nonempty root
  `.scraft` entry before storage. This checks archive shape, not the session
  entry's CRC or semantic validity.

This keeps the one-file session bound to its original target. It does not add a
Save As workflow.

## Reproduction details and checks

| Item | Value |
|---|---|
| SoundCraft source | `storytold/soundcraft` `d47abe484d4f9ef0cc9f8e872e0b3880a61a4588` |
| Local compatibility sequence | GR-025 → GR-027 → GR-028 → GR-029, documented in those review bundles |
| Shared transport | `craft-platform` `56c5e16d79b77751106173c13111ef4fe0a2c0ec` |
| Seafile | isolated synthetic Seahub and C fileserver from GR-015 runtime |
| Browser | Chromium through T3 preview; Seahub `127.0.0.1:18000`, gateway `127.0.0.1:8777` |
| File | `host-fixture-small.scraftz`, synthetic, 4,041 bytes before upload; SHA-256 `2aa2bc5777df6e9e6002b523d423bb59e2065e8b1ab90e7878a42d52453a064b` |
| Temporary test config | allowlisted `.scraftz`, action URL `http://127.0.0.1:8777/open/`, one synthetic repository |
| Gateway ceiling | `ARTCRAFT_MAX_BYTES=52,428,800` (the existing 50 MiB default); final save 6,877 bytes |
| SoundCraft bundle | release profile, `wasm-opt=0`; not optimized production evidence |

Checks run:

- `rtk python3 tests/test_gateway_unit.py` — **PASS**, including SoundCraft ZIP
  validation, authorization, stale-write, size-limit, and concurrent-save cases.
- `rtk python3 tests/test_hostpage_protocol.py` — **NOT RUN**; this Python
  environment has no `playwright` module. The actual Seafile browser run above
  exercised a successful editor save, host ACK, and fresh storage-backed reopen;
  Save As/export rejection was not separately exercised in the browser.
- `git diff --check` — PASS before final documentation updates.

## Limits

- The run is synthetic and loopback-only; it does not establish production
  deployment security, TLS/proxy/CSP/CSRF hardening, external-writer races, or
  ONLYOFFICE non-regression.
- The SoundCraft bundle used `wasm-opt=0`; optimized bundle size/performance is
  NOT VERIFIED.
- Outbound browser-message bytes were not hashed independently from Seafile
  readback bytes.
- SoundCraft remains excluded from the committed dispatcher. No upstream
  changes were made.
