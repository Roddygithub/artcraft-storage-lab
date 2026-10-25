# GR-034 — PhotoCraft gateway payload validation evidence

## Base and changed files

- Repository base: `39b69444a2596b4a73f65be1b1124395335b91c8` (`39b6944`).
- Changed files in this uncommitted slice:
  - `integration/gateway/server.py` — metadata-only `.pcraft` root-manifest shape validation.
  - `tests/test_gateway_unit.py` — malformed ZIP, missing/nested manifest, native fixture, and save-before-Seafile-call checks.
  - `docs/GR-034-PHOTOCRAFT-GATEWAY-VALIDATION.md` — assessment and scope/limits.
  - `docs/TEST-MATRIX.md`, `STATUS.md`, `HISTORY.md`, `docs/GPT-REVIEW-QUEUE.md` — milestone tracking.
  - `docs/reviews/GR-034/README.md` — this evidence index.

## Source and fixture

The validator follows the native detector in `storytold/photocraft` at
`a02f2ee41059d3312e7ff24a5af5edcac7b6435a`,
`crates/format/src/lib.rs:133-147`: `.pcraft` is a ZIP containing a root
`manifest.json` entry. The test uses the project-generated fixture
`docs/reviews/GR-033/runtime/photocraft-smoke.pcraft` (4,000 bytes; SHA-256
`c5fe5c8fb2bd9b38b4a0de1ad4ebc9c6e97006100e2b25e147265e2666b5a3c2`). The GR-033
evidence records that PhotoCraft CLI generated and reopened the fixture.

## Checks

```text
python3 tests/test_gateway_unit.py
PASS — ALL CHECKS PASSED
  - native PhotoCraft fixture accepted
  - malformed ZIP rejected
  - missing root manifest rejected
  - nested-only manifest rejected
  - duplicate exact-root manifests rejected
  - empty exact-root manifest rejected
  - invalid `.pcraft` save rejected with gateway status 400 before the fake Seafile
    save method (save_calls=0; no writes)

rtk git diff --check
PASS
```

No broader suite was run for this slice.

## Independent review

Nemotron 3 Ultra R2 returned a bounded **PROVISIONAL PASS**. The first review's
MINOR test-coverage gap for duplicate and empty root manifests was closed by the
two explicit regression cases above. The reviewer verified source and test
coverage but did not rerun tests or access services.

## Boundaries

- Validation reads ZIP central-directory metadata only; it does not decompress
  members, parse manifest JSON, verify CRCs/local data, or establish semantic
  PhotoCraft validity. Those checks remain with PhotoCraft's parser.
- `.pcraft` was not added to `integration/config/dispatch.json`. No dispatcher,
  Seahub patch/configuration, app bundle, service, or Seafile instance was
  changed or accessed.
- Seafile runtime/version/readback behavior is **NOT VERIFIED**. This is not a
  project GPT PASS or upstream publication approval.
