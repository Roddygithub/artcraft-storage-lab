# Independent review — standalone `craft-platform` package

Date: 2026-10-24
Review model: GPT-6.1 Sol, low
Scope: local GR-016/GR-018 source packaging only; no project-level verdict

## Result

**PROVISIONAL PASS for the package snapshot; app-patch portability remains open.**

The reviewer independently confirmed that packaged `src/` and `tests/` files
match the scratch checkout at `f180fc0d35d521c5d18e118c881d3efde1ec1eee`, and
that its MIT/Apache license texts and NOTICE match the source. The package does
not contain unrelated/private data or credential-pattern matches. All 19
entries in `SHA256SUMS` verified. Root Cargo metadata resolves the nested
workspace package. This does **not** independently establish consumption via
an immutable Git dependency.

The reviewer ran `./scripts/check-craft-platform.sh`: six native tests passed,
and the browser-feature WASM check passed. It also ran shell syntax and
`git diff --check`. Browser integration test binaries ran zero tests, so no
browser transport runtime behavior is claimed here.

## Finding and remediation

**MINOR — Cargo metadata was not locked.** The first review found that the
metadata invocation could update the lockfile. The owner added `--locked` to
that command. After the change, the owner reran the check script, verified all
19 checksums from the artifact directory, ran `sh -n`, and ran
`git diff --check`; all passed. The reviewer did not rerun this one-line
follow-up.

## Still open

The WordCraft, GridCraft, and CADCraft patch files still reference the old
absolute `/tmp/artcraft-gr016-craft-libs` path. These patches are not yet
portable. The package must first be committed; then each app patch must pin the
exact immutable Git revision, its stored diff/hash must be refreshed, and clean
app checkouts must build against that dependency before the portability gate
can close.

No upstream app repository, upstream issue/PR, or production service was
changed. This review does not change the project GPT FAIL, public-deployment
readiness, or upstream lock.
