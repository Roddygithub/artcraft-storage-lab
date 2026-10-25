# GR-056 — GridCraft reproducible host candidate

Date: 2026-10-25. Result: **Rust 1.95 release build PASS; synthetic actual-WASM
browser roundtrip PASS**. Independent R1–R5 reviews: **PROVISIONAL PASS**, no
remaining findings. Work-item status:
**GPT REVIEW PENDING**. Project verdict remains **INCOMPLETE**; upstream writes
remain locked.

## Result

Built the exact requested GridCraft source plus the stored GR-016 shared
transport patch. The candidate is staged at
`/home/roddy/.cache/artcraft-storage-lab/gr056-gridcraft-static/gridcraft`,
outside integration/static and the dispatch tree. Nothing was promoted or
replaced. The four served candidate files, sizes and SHA-256 digests are in
[`hash-inventory.json`](reviews/GR-056/hash-inventory.json); run
[`verify_candidate.py`](reviews/GR-056/verify_candidate.py) to check the bundle
and provenance pins.

The built WASM opened `tests/fixtures/synthetic.xlsx` in the provided
[`gridcraft-host.html`](reviews/GR-016/runtime/gridcraft-host.html) memory
parent. Chromium changed B2 from 42 to 1337; B3 recalculated from
`SUM(B2:B2)` to 1337. The parent captured a save request with ticket
`gridcraft:1`, returned `ok:true` for that same ticket, and the editor reported
`dirty=false`. A fresh iframe reopened the memory-stored bytes and showed B2
and B3 as 1337. The serialized XLSX and fresh-reopen screenshot are preserved
in [`runtime/`](reviews/GR-056/runtime/); browser details are in the
[evidence README](reviews/GR-056/README.md).

This is a synthetic in-memory parent test. It does not create a durable file
version or establish the Seafile MVP. A dedicated synthetic library has been identified on the authorized Seafile
instance, but a read-only GET to the required `thirdparty-editor/file-save/`
route returns 404. No write was attempted. The sanitized preflight record is
[`seafile-preflight.txt`](reviews/GR-056/seafile-preflight.txt).

The R1 P3 verifier finding is remediated: the verifier now rejects staged and
untracked source additions and requires the complete tracked source diff, except
for the declared build overlay, to hash exactly to the pinned GR-016 patch. A
negative check confirmed an extra tracked edit is rejected, and verification
passes after restoring the source. See the follow-up in the evidence README.

## Exact inputs and build

| Input | Exact identity / result |
|---|---|
| Implementation base | Isolated worktree branch `t3/gr056-gridcraft-candidate`, base local main `247ae75753d4d22c7567b53271b3bf0c0d119f99`; initially clean |
| GridCraft repository | `https://github.com/storytold/gridcraft.git` |
| GridCraft source | `06920de8da609c19de7446945cfc62b844691efd` |
| Stored patch | `docs/reviews/GR-016/patches/gridcraft-shared-transport.patch`, SHA-256 `20b219e7f53d7fd0e2fa1c84033cef3d72b22e6f69fe4c4cbcab5ffff077945f` |
| Patch application | Normal `git apply --check` passed; normal `git apply` then applied all 11 changed files with zero fuzz |
| Shared transport | Both `Cargo.toml` and `Cargo.lock` pin `craft-platform` to `90c261de22ef75c4c7c5c5cd1c712d483be0bbc8` |
| Toolchain | `rustc 1.95.0 (59807616e 2026-04-14)`, Cargo 1.95.0, Trunk 0.22.0 |
| Build | `RUSTUP_TOOLCHAIN=1.95.0 trunk build --release --locked --dist /home/roddy/.cache/artcraft-storage-lab/gr056-gridcraft-static/gridcraft` from `apps/gridcraft-web`; exit 0 |
| Persistent build paths | `TMPDIR=/home/roddy/.cache/cargo-tmp`; Cargo target directory is Cargo-configured under `/home/roddy/.cache/cargo-target`; `CARGO_TARGET_DIR` was unset; no build output was directed under `/tmp` |

The source working copy is
`/home/roddy/.cache/artcraft-storage-lab/gr056-source/gridcraft`, detached at
the requested source commit. The source checkout was copied with
`git clone --no-hardlinks` from the existing clean local checkout whose
`origin` is `https://github.com/storytold/gridcraft.git`. The stored patch was
applied to that disposable checkout. The source index overlay and build
commands are recorded in the evidence README and `commands.sh`.

### Build-only optimizer overlay

Only the disposable checkout's `apps/gridcraft-web/index.html` changed from
`data-wasm-opt="z"` to `data-wasm-opt="0"`. Its post-overlay SHA-256 is
`b86f07792b2c600a4d5f3ff275e4dffc4adbb70fc6b23edd713cf4e7fd919fd1`. The
stored patch was not changed. This functional release build skips the optional
wasm-opt pass; optimized output size and performance are **NOT VERIFIED**.

Exact overlay command from the disposable source root:

```sh
sed -i 's/data-wasm-opt="z"/data-wasm-opt="0"/' apps/gridcraft-web/index.html
sha256sum apps/gridcraft-web/index.html
```

Expected digest: `b86f07792b2c600a4d5f3ff275e4dffc4adbb70fc6b23edd713cf4e7fd919fd1`.

## Evidence and boundaries

| Check | Result | Boundary |
|---|---|---|
| Source, patch and transport pins | **PASS** | Exact source/patch and Cargo manifest/lock pins checked |
| Normal zero-fuzz patch application | **PASS** | `git apply --check`, then `git apply`; no fuzz options used |
| Rust 1.95 Trunk release build | **PASS** | Functional release build with the exact overlay above; optimized bundle not verified |
| Candidate inventory | **PASS** | Four served files, paths, byte sizes and SHA-256 checked by runnable verifier |
| Actual-WASM browser open/edit/save/ACK/clean/reopen | **PASS** | Chromium; synthetic sessionStorage parent only; B2=1337 and formula B3=1337 |
| Seafile new version/history/readback/reopen using this exact bundle | **NOT RUN** | Synthetic library identified; required conditional-save route returns 404; no write attempted ([preflight](reviews/GR-056/seafile-preflight.txt)) |
| Production Seafile/data, credentials, ONLYOFFICE, upstream writes | **NOT USED** | Only the read-only synthetic-target preflight ran; no Seafile write/persistence test or upstream mutation |
| Independent review / project GPT verdict | R1–R5 bounded **PROVISIONAL PASS**; project GPT remains **INCOMPLETE** | Candidate remains outside dispatch; upstream publication remains locked |

See [`docs/reviews/GR-056/README.md`](reviews/GR-056/README.md) for exact
commands, sizes, hashes, browser evidence and the verifier invocation.
