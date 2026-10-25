# GR-047 — FilmCraft host-save browser runtime smoke

**Result:** the exact GR-023 patched FilmCraft Web/WASM passed a bounded
synthetic Chromium open → visible edit → save bytes → matching ACK → clean →
fresh iframe reopen flow. The same-origin parent kept save bytes in memory.
This is not a Seafile write or version test. Authorization, Seafile version
creation/readback, dispatcher routing, production deployment, and ONLYOFFICE
behavior remain **NOT VERIFIED**. The work item is **GPT REVIEW PENDING**;
this task did not self-review.

| Check | Observation |
|---|---|
| Source | `storytold/filmcraft` base `fa550ce2d07bdfee6b1d7b6835e8abc8c6913d00` |
| Shared transport | `craft-platform` `56c5e16d79b77751106173c13111ef4fe0a2c0ec` (Cargo.lock) |
| Stored GR-023 patch | SHA-256 `16158f500b2ec12f93c8fcb14867e0b452030dbb338b2d4d7fa8612850a694d4`; local source diff regenerated with `git diff --no-ext-diff --src-prefix=c/ --dst-prefix=w/` had the same SHA-256 |
| Rust | `rustc 1.95.0 (59807616e 2026-04-14)`; `cargo 1.95.0` |
| Build WebAssembly | `filmcraft_web.wasm`, 40,913,852 bytes; SHA-256 `c1ccf010da400943fbe29c79287a5fa72194b3f8426befa5f608c6e646549d87`; verified from persistent Cargo cache with `stat` and `sha256sum` on 2026-10-25 (not committed due to size) |
| Packaged WebAssembly | `filmcraft_web_bg.wasm`, 37,637,092 bytes; SHA-256 `342d877787bb684a834fc6a6bac38eb63717c0551a1f75fbc15eb2134d56718b` |
| Browser JS / HTML | `filmcraft_web.js` SHA-256 `1211b1a44d994158c133493e820385853b62a90f8511897e6d1cb97a2fec90e6`; `index.html` SHA-256 `87feed442b67fadd423ce5118b3b6c52225f714068383836401386e041f768c1` |
| Synthetic input | Native `.fcproj`, 3,301 bytes; SHA-256 `7b9747511b3a2382bfe09667aa29d4a55dabc39b74ca25962c4c033d0296813a` |
| Visible edit | FilmCraft API command `graphics.newText` added `GR-047 visible edit passed`; the program monitor showed it and the parent observed `dirty=true` |
| Save | Ctrl+S emitted 6,468 bytes; SHA-256 `891cc9648eab2496acbac908a3694f878dada101da3575673697e0faeb764e84`; filename `GR-047-synthetic.fcproj` |
| ACK | Synthetic same-origin parent sent `filmcraft:saveResult` with the matching ticket `filmcraft:1` and `ok:true`; editor reported `dirty=false` |
| Reopen | Parent created a new iframe and supplied the captured in-memory bytes; fresh FilmCraft reported clean and rendered the edit, shown in [`filmcraft-reopen.png`](reviews/GR-047/runtime/filmcraft-reopen.png) |
| Browser | T3 collaborative Chromium preview; WebGL2 with SwiftShader software rasterizer; loopback HTTP bound to `127.0.0.1:18747` |
| Supplemental replay | A second loopback Chromium run fetched the same asset URLs, hashed their response bodies in-page, edited, saved 6,466 bytes, ACKed `filmcraft:1`, and reopened clean in a new iframe. Log and screenshot: [`replay-20261025.txt`](reviews/GR-047/runtime/replay-20261025.txt), [`filmcraft-review-replay.png`](reviews/GR-047/runtime/filmcraft-review-replay.png) |

## Reproduction record

All Cargo output used the machine's global `/home/roddy/.cargo/config.toml`,
which directs targets to `/home/roddy/.cache/cargo-target` and temporary files
to `/home/roddy/.cache/cargo-tmp`. Neither `CARGO_TARGET_DIR` nor `TMPDIR` was
overridden. The FilmCraft checkout and `xtask` staging tree were also under
`/home/roddy/.cache`.

```sh
SRC=/home/roddy/.cache/artcraft-filmcraft-gr047-repro
LAB=/home/roddy/Projects/artcraft-storage-lab
git clone https://github.com/storytold/filmcraft.git "$SRC"
git -C "$SRC" fetch --depth=1 origin fa550ce2d07bdfee6b1d7b6835e8abc8c6913d00
git -C "$SRC" checkout --detach fa550ce2d07bdfee6b1d7b6835e8abc8c6913d00
git -C "$SRC" apply "$LAB/docs/reviews/GR-023/filmcraft-host-save-ack.patch"
cd "$SRC"

git -C "$SRC" rev-parse HEAD
sha256sum "$LAB/docs/reviews/GR-023/filmcraft-host-save-ack.patch"
git -C "$SRC" diff --no-ext-diff --src-prefix=c/ --dst-prefix=w/ | sha256sum

# Cargo's global target-dir is outside SRC; xtask expects a checkout-relative path.
mkdir -p "$SRC/target"
test ! -e "$SRC/target/wasm32-unknown-unknown"
ln -s /home/roddy/.cache/cargo-target/wasm32-unknown-unknown "$SRC/target/wasm32-unknown-unknown"
PATH="/home/roddy/.cache/trunk/wasm-bindgen-0.2.129:$PATH" cargo +1.95.0 xtask web

cargo +1.95.0 build -p filmcraft-cli --locked
printf '%s\n' '{"id":"file.newProject","params":{"name":"GR-047 synthetic host smoke"}}' '{"id":"file.newSequence","params":{"name":"GR-047 synthetic sequence","width":1280,"height":720,"fps":24}}' | /home/roddy/.cache/cargo-target/debug/filmcraft-cli --save-as "$LAB/docs/reviews/GR-047/runtime/GR-047-synthetic.fcproj" run -

cp "$LAB/docs/reviews/GR-047/runtime/host.html" "$SRC/target/web/dist/host.html"
cp "$LAB/docs/reviews/GR-047/runtime/GR-047-synthetic.fcproj" "$SRC/target/web/dist/GR-047-synthetic.fcproj"
python3 -m http.server 18747 --bind 127.0.0.1 --directory "$SRC/target/web/dist"
```

In Chromium, open `http://localhost:18747/host.html?run=2`. After the host
reports the input open, the in-app edit command used was:

```js
document.querySelector('iframe').contentWindow.filmcraft.execute(
  'graphics.newText',
  {text:'GR-047 visible edit passed',position:[200,180],size:72,seconds:5}
)
```

Then press Control+S and invoke `window.gr047.reopen()` in the same-origin
parent. The host harness at [`runtime/host.html`](reviews/GR-047/runtime/host.html)
checks origin and iframe source, retains the byte array only in page memory,
hashes it, sends the ticket-matched positive ACK, and gives those exact bytes to
a newly-created iframe.

## Limits

The positive ACK means only that this synthetic page received the bytes; it
does not mean durable storage. No Seafile service, production system, or
ONLYOFFICE installation was accessed or changed. No manual download or upload
was used. No independent review was performed as part of this test task.

The independent R1 review found no blocker or major issue and one minor
evidence-retention gap; the supplemental replay records the browser response
hashes. R2 accepted the served-asset evidence but noted that the distinct
pre-packaging WASM hash needed verification; that file was then hashed from the
persistent Cargo cache and distinguished from the packaged runtime WASM. R3
returned bounded PROVISIONAL PASS with no findings; historical cache continuity
was not established. See
[`INDEPENDENT-REVIEW-R1.md`](reviews/GR-047/INDEPENDENT-REVIEW-R1.md),
[`INDEPENDENT-REVIEW-R2.md`](reviews/GR-047/INDEPENDENT-REVIEW-R2.md), and
[`INDEPENDENT-REVIEW-R3.md`](reviews/GR-047/INDEPENDENT-REVIEW-R3.md).
