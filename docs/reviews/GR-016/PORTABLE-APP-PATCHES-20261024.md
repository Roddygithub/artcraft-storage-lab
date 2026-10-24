# Pinned shared transport in four Craft app patches

Date: 2026-10-24  
Status: implementation and reproducible build evidence; bounded GPT-6.1 Sol
review PASS after remediation. This is not a project-level GPT verdict.

## Immutable transport source

The four app patches depend on the packaged `craft-platform` crate at root
repository commit `90c261de22ef75c4c7c5c5cd1c712d483be0bbc8`:

```toml
craft-platform = { git = "https://github.com/Roddygithub/artcraft-storage-lab.git", rev = "90c261de22ef75c4c7c5c5cd1c712d483be0bbc8", package = "craft-platform" }
```

Browser-enabled apps also request `features = ["browser"]`. No branch name,
local path, or guessed revision is used. The package's source provenance,
license notices and standalone checks remain documented in
[`README.md`](README.md) and
[`REVIEW-PORTABLE-CRAFT-PLATFORM-20261024.md`](REVIEW-PORTABLE-CRAFT-PLATFORM-20261024.md).
The app-patch follow-up review is recorded in
[`REVIEW-PORTABLE-APP-PATCHES-SOL-LOW-20261024.md`](REVIEW-PORTABLE-APP-PATCHES-SOL-LOW-20261024.md).

## Clean-checkout WASM checks

Each patch was applied to the pinned upstream source revision listed below.
Cargo used Rust 1.95.0 and a shared build target directory outside `/tmp`.
Every command exited 0 with `--locked`; warnings were existing dead-code or
unused-code warnings in the upstream app crates.

| App | Source SHA | Command | Result |
|---|---|---|---|
| WordCraft | `00bc6a4b028013b2dfb0e85e8b326aeed3ecff6d` | `cargo +1.95.0 check -p wordcraft-web --target wasm32-unknown-unknown --locked` | PASS |
| GridCraft | `06920de8da609c19de7446945cfc62b844691efd` | `cargo +1.95.0 check -p gridcraft-web --target wasm32-unknown-unknown --locked` | PASS |
| PdfCraft | `57e531ccca0047597809748b5cb4276336d6051a` | `cargo +1.95.0 check -p pdfcraft-web --target wasm32-unknown-unknown --locked` | PASS |
| CADCraft | `7bf5905ac97316a7896de8cbc12d243f57b09bd8` | `cargo +1.95.0 check -p cadcraft-web --target wasm32-unknown-unknown --locked` | PASS |

The WordCraft and GridCraft patches intentionally do not change their
`data-wasm-opt` settings. Earlier functional browser bundles used
`wasm-opt=0`; optimized bundle size and performance remain NOT VERIFIED. These checks establish dependency
resolution and WASM compilation, not browser runtime behavior for PdfCraft or
CADCraft and not Seafile persistence.

## Stored patch identities

Each stored patch was compared byte-for-byte with the generated source diff at
its base SHA. For WordCraft, the tracked diff was combined with an explicit
new-file diff for `apps/wordcraft-web/src/host.rs` because Git omits untracked
files from ordinary `git diff`. All four hashes match. GridCraft's temporary
`data-wasm-opt=0` experiment was removed from the stored patch; that setting
was used locally for the functional release bundle but is not part of this
patch.

| Patch | SHA-256 |
|---|---|
| `patches/wordcraft-shared-transport.patch` | `1c0bba26de821d1d54c161c5954bc8a5b0f5d7df71be7c4488c473b753842afc` |
| `patches/gridcraft-shared-transport.patch` | `20b219e7f53d7fd0e2fa1c84033cef3d72b22e6f69fe4c4cbcab5ffff077945f` |
| `../GR-017/patches/pdfcraft-durable-host-ack.patch` | `6d50eb1f45e81f2037948cd6160878feb2d87eb0881d167f0fc1d290e4450562` |
| `../GR-018/cadcraft-host-save.patch` | `cb85f2ed0493333d4e3dfa6df959cbc85e460ca208c4f07d9e59f740525a516e` |

## Boundaries

This closes the `/tmp` dependency and clean-build reproducibility gap for these
four stored app patches. It does not add or validate host adapters for the
remaining Craft apps, establish optimized release bundles, prove app runtime
behavior beyond the previously recorded evidence, or resolve security,
deployment, licensing, and overall GPT review findings. No upstream Craft
repository, Seafile production service, issue, PR, or RFC was changed.
