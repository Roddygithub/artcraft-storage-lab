# GR-031 Independent Review — SoundCraft Seafile E2E

**Result: PROVISIONAL PASS**, bounded to the changed gateway code and supplied
synthetic-run evidence. This is not a project GPT PASS or production-readiness
verdict.

## Findings

| Severity | Finding | Disposition |
|---|---|---|
| MINOR | Save As and cross-extension refusal assertions are present, but the Playwright protocol suite was not run and the browser E2E exercised only a successful save. | Retained as a test gap; no successful negative-path runtime claim is made. |
| MINOR | `.scraftz` validation checks ZIP directory shape and a nonempty root `.scraft` member; it does not verify member CRC or SoundCraft session semantics. | Documentation and matrix now explicitly scope the check to archive shape. |
| MINOR | SoundCraft’s row in the Host Contract had three cells under a four-column table header. | Fixed by separating bridge status, current hook, and remaining work into the correct columns. |

## Evidence reviewed

- Selected-file binding and rejection of `saveAs` / differing extensions are
  visible in `integration/gateway/hostpage.py`; the write header uses the
  originally selected `FILE_NAME`.
- The `.scraftz` validator requires a ZIP directory with exactly one nonempty
  root `.scraft` entry. The positive unit fixture is `{}`; this is only a
  structural check.
- Both screenshot SHA-256 values match the GR-031 README. The screenshots show
  save confirmation and the fresh clean editor with three tracks.
- File IDs, heads, readback length and hash are internally consistent across
  the GR-031 report, review README, test matrix and review queue. The readback
  bytes and API response capture are not bundled, so the reviewer could not
  independently verify the Seafile identifiers or recompute that hash.
- SoundCraft is absent from the committed dispatch configuration, and the
  reviewed diff does not change dispatch or ONLYOFFICE configuration.
- GR-030 terminology now identifies the two static artifacts (parent harness
  and one screenshot) and explicitly states there is no video or recording.

## Verification limits

The reviewer did not run tests, access Seafile, or reproduce the browser run.
The reported `tests/test_gateway_unit.py` pass and the actual synthetic E2E are
implementer-reported. `tests/test_hostpage_protocol.py` was not run because the
Python Playwright module is unavailable. The exact outgoing `soundcraft:save`
bytes were not independently hashed; optimized WASM, deployment security,
ONLYOFFICE regression and production behavior remain **NOT VERIFIED**.

SoundCraft remains excluded from the committed dispatcher. No project GPT
verdict or upstream authorization is granted.
