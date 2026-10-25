# GR-046 evidence — EffectCraft browser host-save smoke

Scope: actual locally patched EffectCraft Web/WASM in Chromium, with a
same-origin in-memory synthetic parent. No mocked editor, Seafile service,
production data, or ONLYOFFICE configuration was used.

## Provenance and build

| Item | Value |
|---|---|
| Source | `https://github.com/storytold/effectcraft` at `049070d65c66a73f322b496b22521816e0018f14` |
| Transport | `craft-platform` locked revision `56c5e16d79b77751106173c13111ef4fe0a2c0ec` |
| Patch | `docs/reviews/GR-022/effectcraft-host-save.patch`; SHA-256 `4e0a1799e36209e1234a1b3ff504ab5ed647cf3bd066af6dec90dacd46ab7407` |
| Cache checkout | `/home/roddy/.cache/artcraft-effectcraft-gr046` |
| Rust / Trunk | Rust `1.95.0`; Trunk `0.22.0` (the release build used the project's `cargo xtask web`) |
| `effectcraft_web_bg.wasm` | SHA-256 `f7b608a8ce3f768f9f81c75df3431eb9fefd23cd38cd3447d029f7ec9cca1e39`; 56,691,300 bytes |
| `effectcraft_web.js` | SHA-256 `a069d10555da55ddbd7e108a7580c76a65a85f36a5928101b8bd69a3c4c1b4c3` |
| `index.html` | SHA-256 `3fb03ccd8d46c5839fb2a09b950004b187840867caae49816221ec76559dc0f3` |

Reproduction commands (run from the repository root, with `LAB` set to this
repository's absolute path):

```sh
LAB=/path/to/artcraft-storage-lab
SRC=/home/roddy/.cache/artcraft-effectcraft-gr046-repro
git clone --no-checkout https://github.com/storytold/effectcraft.git "$SRC"
git -C "$SRC" checkout --detach 049070d65c66a73f322b496b22521816e0018f14
git -C "$SRC" apply --unidiff-zero "$LAB/docs/reviews/GR-022/effectcraft-host-save.patch"
cd "$SRC"
grep -A4 'name = "craft-platform"' Cargo.lock
cargo +1.95.0 build -p effectcraft-web --release --target wasm32-unknown-unknown --locked
```

The direct `trunk build --release` attempt was not applicable: this repository
has no root `apps/effectcraft-web/index.html`. `cargo +1.95.0 xtask web` is the
documented build pipeline. Its first run stopped because `wasm-bindgen` was not
on PATH; using the already-installed exact `0.2.129` binary succeeded:

```sh
ln -s /home/roddy/.cache/cargo-target/wasm32-unknown-unknown "$SRC/target/wasm32-unknown-unknown"
PATH="/home/roddy/.cache/trunk/wasm-bindgen-0.2.129:$PATH" cargo +1.95.0 xtask web
```

Cargo's normal global config put build/temp artifacts under
`/home/roddy/.cache/cargo-target` and `/home/roddy/.cache/cargo-tmp`; neither
`CARGO_TARGET_DIR` nor `TMPDIR` was overridden. The symlink in the cache
checkout only lets `xtask` find the Cargo-configured WebAssembly output. The
release build completed with one existing `effectcraft-ui-egui` unused-field
warning. The first CLI invocation built the synthetic fixture with:

```sh
FIXTURE="$LAB/docs/reviews/GR-046/runtime/synthetic.ecproj"
cargo +1.95.0 run -p effectcraft-cli -- run --empty --save-as "$FIXTURE" \
  comp.new '{"name":"GR-046 synthetic","width":800,"height":450,"frameRate":24,"duration":2}' \
  layer.newText '{"name":"Smoke text","text":"GR-046 original","size":72,"fill":"#ffffff"}' --save
```

The CLI returned composition ID `1` and layer ID `2`. The resulting native
fixture SHA-256 is `cb7852f97d55e8048d8d5cb9f1649085b5cf06ff301104d7fcb608188c0a4ec0`.

## Browser run and artifacts

The included [`runtime/host.html`](runtime/host.html) opens
`synthetic.ecproj` in `index.html?host=parent&empty&noworkers&nogpuworkers&nosw`
and checks origin and iframe source. It retains the exact save bytes in memory,
hashes them, sends a positive ACK with the returned ticket, and reopens those
bytes in a newly-created iframe. The static bundle was served only on loopback:

```sh
python3 -m http.server 18746 --bind 127.0.0.1 \
  -d "$SRC/target/web/dist"
```

The Chromium tab loaded `http://127.0.0.1:18746/host.html`. Network entries
showed HTTP 200 for the parent page, EffectCraft page, generated JS, WASM, glue
snippet, and synthetic fixture. After Open, the loaded EffectCraft API
identified version `0.16.0`, WebGL backend `Gl`, active composition `1`, and
`restored=false`. The in-app `layer.newText` call returned layer `41`; the
parent observed dirty state. Ctrl+S emitted 62,136 bytes with SHA-256
`0828d978e619e0b3afdfd9a8bfba3578b3844aebb9e18f24f412d3eadba2b3d6`. The
parent echoed ticket `effectcraft:1` with `ok:true`; dirty became false. After
the parent replaced the iframe, the fresh instance opened the exact retained
byte array and reported clean. The screenshot shows `GR-046 runtime edit
passed` visible in the reopened composition.

| Artifact | SHA-256 | Meaning |
|---|---|---|
| [`runtime/synthetic.ecproj`](runtime/synthetic.ecproj) | `cb7852f97d55e8048d8d5cb9f1649085b5cf06ff301104d7fcb608188c0a4ec0` | 32,280-byte CLI-generated native test project |
| [`runtime/host.html`](runtime/host.html) | `64dd5e098b89a04414caf83eb7bfd818fbbf48739fb83d377cb22e9aea3b2b6d` | In-memory synthetic parent and fresh-iframe reopen harness |
| [`runtime/effectcraft-host-reopen.png`](runtime/effectcraft-host-reopen.png) | `ed2e5ff023fc4e171dd0d19530e05ca63c72e4d0bd396cb1b06b638f0d748a1e` | Chromium screenshot after ACK and fresh iframe reopen |

## Limits

The parent ACK is synthetic and in-memory; it does not demonstrate a durable
write. The exact saved bytes are identified by size and SHA-256 but are not
stored as a binary evidence file. Seafile version creation/readback, dispatcher
routing, public deployment, production authorization, and ONLYOFFICE were not
exercised and remain **NOT VERIFIED**. No upstream repository or production
service was accessed.

## Independent verification and reviews

The parent independently checked source `HEAD`, the stored GR-022 patch hash,
Cargo.lock transport pin, and WASM/JS/index hashes. It applied the patch with
`--unidiff-zero` to a fresh worktree at the pinned base; all nine changed-file
hashes matched the locally patched build checkout. No rebuild or browser replay
was performed during that check.

- [R1](INDEPENDENT-REVIEW-R1.md): **PROVISIONAL PASS**, no blocker/major; one
  MINOR reproduction-path issue.
- [R2](INDEPENDENT-REVIEW-R2.md): **PROVISIONAL PASS**, no blocker/major; the
  reproduction path was fixed. Both reviews agree that Seafile persistence and
  deployment behavior remain **NOT VERIFIED**.
