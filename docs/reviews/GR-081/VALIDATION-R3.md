# GR-081 validation R3

**Scope:** compile and run existing Rust UI unit suites for the identity-bound
WordCraft and GridCraft source patches. This validates that the patched app
checkouts compile and that their existing UI tests pass; it does not prove the
new identity refusal or save protocol end to end.

## Results

| Check | Result |
|---|---|
| WordCraft web WASM compile | PASS — `cargo check -p wordcraft-web --target wasm32-unknown-unknown --locked` |
| GridCraft web WASM compile | PASS — `cargo check -p gridcraft-web --target wasm32-unknown-unknown --locked` |
| WordCraft UI unit suite | PASS — `cargo test -p wordcraft-ui-egui --lib --locked --quiet`; 824 passed, 0 failed, 2 ignored |
| GridCraft UI unit suite | PASS — `cargo test -p gridcraft-ui-egui --lib --locked --quiet`; 151 passed, 0 failed, 0 ignored |
| Gateway browser protocol test | NOT RUN — Python Playwright is not installed (`ModuleNotFoundError`) |

Both Rust builds/tests used Rust 1.95.0 and the exact app source copies and
transport dependency pins recorded in
[`patches/identity-binding-r1-manifest.json`](patches/identity-binding-r1-manifest.json).
Cargo was invoked with `--locked`. Because transport commit
`d572f2d550278a7f4aad91a1bac650105c19812b` is local and not published, Git URL
resolution was temporarily redirected in the command environment to this local
repository; no global Git/Cargo configuration was changed. Fresh resolution
from the public remote remains **NOT VERIFIED**.

## Limits

The existing UI suites do not establish that same-name replacement, Save As,
or other refused actions cause zero serialization and zero upload. They also do
not establish save acknowledgement ordering in a browser, actual WASM
host-message behavior, Seafile version creation or fresh reopen. The save
identity MAJOR therefore remains open. ONLYOFFICE preservation remains
**INCONCLUSIVE / NOT VERIFIED** and was not accessed or changed.

The project review of candidate
`70fa192ed5d414daf28087315f0f77f8312e98b5` remains **FAIL**. This validation
does not constitute a new project GPT review or unlock upstream publication.
