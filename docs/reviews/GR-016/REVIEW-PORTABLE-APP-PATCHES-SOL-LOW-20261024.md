# Independent Sol review — portable Craft app patches

Date: 2026-10-24  
Reviewer: GPT-6.1 Sol, low bounded review  
Scope: exact pin and patch reproducibility for GR-016 WordCraft/GridCraft,
GR-017 PdfCraft, and GR-018 CADCraft. This is not a project-level verdict.

## Final bounded result

**PASS. No blocker or major finding.** Two minor findings from round 1 were
corrected and independently rechecked in round 3.

## Evidence

- The packaged `craft-platform` commit is
  `90c261de22ef75c4c7c5c5cd1c712d483be0bbc8`; public `main`, each app
  manifest, and each generated lockfile resolve that exact immutable revision.
- All four stored patch hashes match the generated diffs. WordCraft's new
  untracked `host.rs` is included in its patch.
- Clean-base forward application checks and patched-tree reverse checks pass.
- Rust 1.95 locked WASM checks pass for WordCraft, GridCraft, PdfCraft, and
  CADCraft. The standalone transport check passes six native tests and its
  browser-feature WASM build; all 19 source/notice checksum entries pass.

Full commands, pins, and patch hashes are in
[`PORTABLE-APP-PATCHES-20261024.md`](PORTABLE-APP-PATCHES-20261024.md).

## Review rounds

### Round 1 — PASS with two MINOR findings

1. `TEST-MATRIX.md` and `STATUS.md` still described app pins/builds and the
   CADCraft synthetic Seafile flow as pending.
2. The GridCraft patch included a temporary `data-wasm-opt=0` HTML change,
   unrelated to dependency pinning.

### Round 2 — remediation

- Updated the stale matrix and status entries to reflect the recorded pin,
  clean-checkout builds, and existing CADCraft Seafile evidence.
- Removed the GridCraft optimizer change from the stored patch, regenerated its
  hash, reran its Rust 1.95 `--locked` WASM check, and checked reverse/forward
  patch application. The functional browser run's `wasm-opt=0` setting remains
  disclosed as a bundle-performance limitation.

### Round 3 — PASS

Sol independently confirmed both findings resolved, verified the updated
GridCraft hash and all four patch hashes, found no new in-scope contradiction,
and ran `git diff --check`. Builds were not rerun in round 3; owner reran the
GridCraft WASM check after the optimizer hunk removal.

## Limits

This review establishes reproducible dependency resolution and compilation for
these four stored app patches only. It does not establish runtime behavior for
all four, all-app support, optimized bundle performance, public deployment
readiness, project-level GPT PASS, or authorization to publish upstream.
