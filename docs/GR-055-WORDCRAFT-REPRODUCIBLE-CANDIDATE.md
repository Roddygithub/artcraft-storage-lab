# GR-055 — WordCraft reproducible host candidate

Date: 2026-10-25. Implementation result: **candidate built; synthetic browser
roundtrip PASS**. Bounded independent R1–R2 reviews: **PROVISIONAL PASS**, no
remaining findings. Work item status: **GPT REVIEW PENDING**. Project GPT review:
**PENDING**. Project verdict:
**INCOMPLETE**. Upstream publication remains locked.

## Result

GR-055 creates an exact, reproducible WordCraft Web/WASM candidate from the
requested upstream source and already-tracked host transport patch. The bundle
is staged outside the dispatch tree at
`/home/roddy/.cache/artcraft-storage-lab/gr055-wordcraft-static/wordcraft`.
Nothing was copied to or promoted into `integration/static/` or another dispatch
location. No Seafile service, production data, ONLYOFFICE configuration,
credential, issue, PR or upstream source repository write was used.

The browser roundtrip used the actual generated WordCraft app assets. It edited
the synthetic DOCX, serialized the edit, received one new version from the
test's synthetic in-memory storage, observed WordCraft's save confirmation, and
reopened the document in a fresh session with the edit intact. This is a
**synthetic memory-parent browser result**. It does not establish Seafile
persistence or the MVP against Seafile.

## Exact inputs and build

| Input | Exact identity / result |
|---|---|
| Base | Local `main` commit `0d16be1ea37ace6ddd282c514a05df6b4906cbc0`; isolated implementation worktree `t3/gr055-wordcraft-candidate` |
| WordCraft repository | `https://github.com/storytold/wordcraft.git` |
| WordCraft source | `00bc6a4b028013b2dfb0e85e8b326aeed3ecff6d` |
| Patch | `docs/reviews/GR-016/patches/wordcraft-shared-transport.patch`, SHA-256 `1c0bba26de821d1d54c161c5954bc8a5b0f5d7df71be7c4488c473b753842afc` (matches GR-054) |
| Apply | Normal `git apply --check` passed at the exact source checkout; normal `git apply` then applied the patch |
| Shared transport | `craft-platform` immutable revision `90c261de22ef75c4c7c5c5cd1c712d483be0bbc8`; `Cargo.toml` and `Cargo.lock` both record that revision |
| Toolchain | `rustc 1.95.0 (59807616e 2026-04-14)`, Cargo 1.95.0, Trunk 0.22.0 |
| Build | `RUSTUP_TOOLCHAIN=1.95.0 trunk build --release --locked --dist /home/roddy/.cache/artcraft-storage-lab/gr055-wordcraft-static/wordcraft` from `apps/wordcraft-web`; exit 0, release profile completed |

The checked-out source and build work in
`/home/roddy/.cache/artcraft-storage-lab/gr055-source/wordcraft`. Cargo's
configured target directory is `/home/roddy/.cache/cargo-target` and configured
temporary directory is `/home/roddy/.cache/cargo-tmp`; neither Cargo target nor
`TMPDIR` was placed under `/tmp`.

The source checkout and patch application were performed with:

```sh
git clone https://github.com/storytold/wordcraft.git \
  /home/roddy/.cache/artcraft-storage-lab/gr055-source/wordcraft
git -C /home/roddy/.cache/artcraft-storage-lab/gr055-source/wordcraft \
  checkout --detach 00bc6a4b028013b2dfb0e85e8b326aeed3ecff6d
git -C /home/roddy/.cache/artcraft-storage-lab/gr055-source/wordcraft \
  apply --check /home/roddy/.t3/worktrees/artcraft-storage-lab/t3-c60d0371/docs/reviews/GR-016/patches/wordcraft-shared-transport.patch
git -C /home/roddy/.cache/artcraft-storage-lab/gr055-source/wordcraft \
  apply /home/roddy/.t3/worktrees/artcraft-storage-lab/t3-c60d0371/docs/reviews/GR-016/patches/wordcraft-shared-transport.patch
```

### Build-local optimizer overlay

The source index defaults to `data-wasm-opt="z"`. For this build only, the
scratch checkout's `apps/wordcraft-web/index.html` changed that single
attribute to `data-wasm-opt="0"`, following the documented functional-build
setting. The scratch index SHA-256 after that overlay was
`343233454c38b06b2737bbd6be4a393f69a4f7e9b0c19ea42d65f0a5edbde280`. The
tracked stored patch was not edited; its SHA-256 remains the value above. The
generated bundle is a release-profile functional build with the optional
`wasm-opt` pass skipped; optimized size/performance are not established.

Exact Linux command, from the source checkout root, to recreate the build-only
overlay before `trunk build`:

```sh
sed -i 's/data-wasm-opt="z"/data-wasm-opt="0"/' apps/wordcraft-web/index.html
sha256sum apps/wordcraft-web/index.html
```

Expected index digest: `343233454c38b06b2737bbd6be4a393f69a4f7e9b0c19ea42d65f0a5edbde280`.
This is an overlay on the disposable detached source checkout, not a change to
the stored GR-016 patch.

## Candidate inventory

All served candidate files, byte sizes and SHA-256 values are recorded in
[`checks/hash-inventory.json`](reviews/GR-055/checks/hash-inventory.json).
Run the integrity check from the repository root:

```sh
python3 docs/reviews/GR-055/verify_candidate.py
```

The check verifies the exact candidate file set, sizes, SHA-256 values and
`index.html` references. `.trunk-lock` is Trunk's zero-byte transient build lock,
not a served bundle asset, and is excluded from the candidate manifest.

## Browser smoke and limits

Command:

```sh
uv run --with playwright --python 3.14 -- python -u tests/test_wordcraft_host_roundtrip.py \
  --static-root /home/roddy/.cache/artcraft-storage-lab/gr055-wordcraft-static
```

Result: **PASS** — real built WordCraft Web edited and serialized the DOCX;
synthetic storage acknowledged one new version; the host observed the
post-save `dirty=false` acknowledgement; and a fresh WordCraft session reopened
the saved edit. During browser teardown the loopback HTTP server printed an
expected connection-reset traceback after the browser closed a request; the
test process exited successfully after all assertions. Evidence output is in
[`checks/browser-smoke.txt`](reviews/GR-055/checks/browser-smoke.txt).

| Boundary | Status |
|---|---|
| Actual patched WordCraft release WASM and host browser roundtrip | **PASS** |
| Synthetic memory parent version acknowledgement and fresh reopen | **PASS** |
| Persistent Seafile save/history/readback/reopen using this exact bundle | **NOT RUN** |
| Production Seafile, production files, credentials or ONLYOFFICE changes | **NOT USED** |
| Optimized `wasm-opt` bundle | **NOT VERIFIED** |
| Independent review and project GPT verdict | **PENDING**; project remains **INCOMPLETE** |

See [evidence README](reviews/GR-055/README.md) for commands and machine-checkable
hashes. This artifact does not establish deployment readiness or authorize
promotion into dispatch or upstream publication. The user-authorized
synthetic-library Seafile test remains a separate, not-yet-run step.
