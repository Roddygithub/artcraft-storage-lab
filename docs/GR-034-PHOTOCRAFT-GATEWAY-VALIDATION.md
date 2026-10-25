# GR-034 — PhotoCraft gateway payload validation

**Status:** gateway-only validation; bounded independent R2 review PROVISIONAL PASS after adding duplicate/empty-manifest cases. PhotoCraft remains excluded from dispatch. Seafile runtime was unavailable and was not accessed.

## Scope and change

`integration/gateway/server.py::payload_matches_name` now accepts `.pcraft` only when Python's ZIP central directory contains exactly one nonempty entry whose name is exactly `manifest.json` at the archive root. The validator reads `ZipInfo` metadata only; it does not open or decompress the manifest or any other member. Common malformed-ZIP parsing errors return `False`. `Gateway.save` already calls `payload_matches_name` before `thirdparty_file_save`; the new fake-Seafile test asserts an invalid nested-manifest `.pcraft` returns gateway status 400 with zero save calls and no writes.

The validation follows the native PhotoCraft format detector at `storytold/photocraft` commit `a02f2ee41059d3312e7ff24a5af5edcac7b6435a`, `crates/format/src/lib.rs:133-147`, which identifies `.pcraft` by a ZIP `manifest.json` entry. The synthetic fixture in `docs/reviews/GR-033/runtime/photocraft-smoke.pcraft` was generated with PhotoCraft's CLI and has a root `manifest.json` plus image/tile members (4,000 bytes; SHA-256 `c5fe5c8fb2bd9b38b4a0de1ad4ebc9c6e97006100e2b25e147265e2666b5a3c2`).

## Focused evidence

Command:

```sh
python3 tests/test_gateway_unit.py
```

Result: **PASS**, `ALL CHECKS PASSED`, including these GR-034 checks:

- the generated native fixture passes;
- a malformed ZIP, a ZIP with no root manifest, a ZIP with only a nested manifest, duplicate exact-root manifests, and an empty exact-root manifest are rejected;
- saving a nested-manifest `.pcraft` returns 400 before the fake Seafile save method is called (`save_calls == 0`, no writes).

`git diff --check` is run after the documentation and matrix updates.

## Boundaries

- This is structural type validation, not `.pcraft` semantic or integrity validation. Because the gateway does not decompress members, it does not validate manifest JSON, member CRCs, local member data, or whether tile/image data is usable; PhotoCraft's parser remains responsible for those checks.
- The `.pcraft` extension is not added to `integration/config/dispatch.json`. No Seahub patch/configuration, app bundle, service, or Seafile instance was changed or accessed.
- No Seafile runtime was available. This test proves rejection before a fake save call, not durable storage/version behavior.
- Unrelated `.docx`, `.xlsx`, `.pptx`, `.scraftz`, PDF, and SVG validation paths were not changed.

Independent Nemotron 3 Ultra R2 review returned a bounded PROVISIONAL PASS; it confirmed the duplicate and empty-manifest tests close the initial MINOR coverage gap. The reviewer did not rerun the suite or access services. This artifact is not a project GPT PASS or publication approval.
