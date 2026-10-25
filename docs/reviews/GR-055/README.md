# GR-055 evidence — reproducible WordCraft candidate

Implementation worktree: `/home/roddy/.t3/worktrees/artcraft-storage-lab/t3-c60d0371`
at base `0d16be1ea37ace6ddd282c514a05df6b4906cbc0`.

## Inputs and build record

| Check | Evidence |
|---|---|
| Exact source | Clone `https://github.com/storytold/wordcraft.git`, detached at `00bc6a4b028013b2dfb0e85e8b326aeed3ecff6d`; scratch path `/home/roddy/.cache/artcraft-storage-lab/gr055-source/wordcraft` |
| Stored patch digest | `sha256sum docs/reviews/GR-016/patches/wordcraft-shared-transport.patch` → `1c0bba26de821d1d54c161c5954bc8a5b0f5d7df71be7c4488c473b753842afc` (GR-054 value matches) |
| Patch application | `git -C /home/roddy/.cache/artcraft-storage-lab/gr055-source/wordcraft apply --check /home/roddy/.t3/worktrees/artcraft-storage-lab/t3-c60d0371/docs/reviews/GR-016/patches/wordcraft-shared-transport.patch` → exit 0, then the same command without `--check` applied it |
| Transport | `Cargo.toml` and `Cargo.lock` both name `90c261de22ef75c4c7c5c5cd1c712d483be0bbc8` |
| Build-only overlay | Scratch `apps/wordcraft-web/index.html`, only `data-wasm-opt="z"` → `data-wasm-opt="0"`; SHA-256 after edit `343233454c38b06b2737bbd6be4a393f69a4f7e9b0c19ea42d65f0a5edbde280`; stored patch not changed |
| Toolchain/build | Rust/Cargo 1.95.0, Trunk 0.22.0; `RUSTUP_TOOLCHAIN=1.95.0 trunk build --release --locked --dist /home/roddy/.cache/artcraft-storage-lab/gr055-wordcraft-static/wordcraft` from `apps/wordcraft-web` → exit 0 |
| Persistent build directories | Cargo target `/home/roddy/.cache/cargo-target`; Cargo temp `/home/roddy/.cache/cargo-tmp`; no Rust target or `TMPDIR` under `/tmp` |
| Candidate location | `/home/roddy/.cache/artcraft-storage-lab/gr055-wordcraft-static/wordcraft`; not in or promoted to dispatch |

Prerequisites are Rust/Cargo 1.95.0 with `wasm32-unknown-unknown` and Trunk
0.22.0. These were already installed for this run. For a clean machine, the
provisioning commands are:

```sh
rustup toolchain install 1.95.0 --profile minimal
rustup target add wasm32-unknown-unknown --toolchain 1.95.0
cargo install trunk --version 0.22.0 --locked
```

Build overlay command from the detached source checkout root (before the build
command in the table):

```sh
sed -i 's/data-wasm-opt="z"/data-wasm-opt="0"/' apps/wordcraft-web/index.html
sha256sum apps/wordcraft-web/index.html
```

Expected overlay digest: `343233454c38b06b2737bbd6be4a393f69a4f7e9b0c19ea42d65f0a5edbde280`.
The overlay is build-only; it does not alter the stored patch.

## Commands/results

See [`checks/hash-inventory.json`](checks/hash-inventory.json) for per-file
path/size/hash and [`checks/browser-smoke.txt`](checks/browser-smoke.txt) for
the run result. Recheck all candidate bundle hashes and exact file membership:

```sh
python3 docs/reviews/GR-055/verify_candidate.py
```

Browser command:

```sh
uv run --with playwright --python 3.14 -- python -u tests/test_wordcraft_host_roundtrip.py \
  --static-root /home/roddy/.cache/artcraft-storage-lab/gr055-wordcraft-static
```

Browser assertions passed against actual built WordCraft WASM and synthetic
in-memory storage: edit/serialize, one synthetic new version, host save
acknowledgement, fresh editor reopen. During teardown the HTTP server logged a
connection-reset traceback after browser closure; the browser test exited 0
after all assertions. This is not evidence of persistent Seafile behavior.

## Independent review R1

**Result: PROVISIONAL PASS**, with one small reproducibility finding. The
reviewer independently checked the pinned source, stored patch and transport,
four staged bundle hashes, the synthetic browser assertions, and that output
remains outside dispatch and outside `/tmp` for Cargo. No concrete reason was
found to block the separately authorized synthetic-library Seafile test.

Finding: the build report described the `data-wasm-opt=0` overlay but omitted
the command that applied it and did not make the Rust/Trunk prerequisites
explicit. Added the exact overlay/digest and the required toolchain/target/Trunk
versions plus clean-machine provisioning commands above. GR-055 still does
not establish Seafile persistence; that test remains the next milestone.

## Independent review R2

**Result: PROVISIONAL PASS**, no findings. The reviewer confirmed the R1 recipe
fix records the exact overlay command, expected digest, Rust/Cargo and Trunk
versions, WASM target, and clean-machine provisioning commands. The candidate
hash verifier passed again; all four staged asset hashes, the source commit,
patch digest, and transport pin matched the report. R2 did not rebuild or rerun
the browser smoke. Seafile persistence remains **NOT RUN**.

## Scope and review status

No Seafile or production service, credential, personal file, ONLYOFFICE setting,
upstream source write, issue, PR or RFC was used. Exact bundle optimized
`wasm-opt` behavior and persistent Seafile history/readback/reopen remain
**NOT VERIFIED**. Independent R1–R2 reviews are **PROVISIONAL PASS**; the work
item is **GPT REVIEW PENDING**. Project verdict remains **INCOMPLETE** and
upstream publication remains locked.
