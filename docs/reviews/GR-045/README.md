# GR-045 evidence — DesignCraft browser host-save smoke

Scope: synthetic Chromium run of the actual locally patched DesignCraft Web
WASM. The adapter opened a native `.designcraft`, accepted an in-editor text
change, emitted bytes on Ctrl+S, received a matching positive ACK, reported
clean, and reopened the captured bytes in a fresh iframe with the edit intact.

## Provenance and build

| Item | Value |
| --- | --- |
| Upstream source | `storytold/designcraft` `80d13911b2d20fbb5cd9398696627bb3a715417b` |
| Transport source | `craft-platform` exact Cargo.lock revision `56c5e16d79b77751106173c13111ef4fe0a2c0ec` |
| Stored GR-021 patch SHA-256 | `519c03180b17f035ef8fbfcd08a85bda312f6f0721bfbdf9dc1d9d5992fdf972` |
| Built DesignCraft Web WASM SHA-256 | `e06f61ce6f004653ed2d9adfb1d3db1b363b2c6bab0c1b025b760b57aeec446c` (49,467,912 bytes) |
| Generated JS SHA-256 | `bc068abd27138afc2bdbb8e1a3c42b0cc45e1446ab251ad93fe5006e67b288df` |
| Generated `index.html` SHA-256 | `c360de13da0982a51876f318c3c8b82b1c358f122d46c3b1d95c32b6c015c14d` |
| Trunk | `0.22.0` |
| Rust | `1.95.0` |

Reproduction commands, from a clean checkout of the source pin:

```sh
LAB_ROOT=/path/to/artcraft-storage-lab
SRC=/home/roddy/.cache/artcraft-designcraft-gr045
git clone --no-checkout https://github.com/storytold/designcraft.git "$SRC"
git -C "$SRC" checkout --detach 80d13911b2d20fbb5cd9398696627bb3a715417b
git -C "$SRC" apply --unidiff-zero "$LAB_ROOT/docs/reviews/GR-021/designcraft-host-save-ack.patch"
cd "$SRC"
cargo +1.95.0 build -p designcraft-web --release --target wasm32-unknown-unknown --locked
cd apps/designcraft-web
RUSTUP_TOOLCHAIN=1.95.0 trunk build --release
```

The build used the machine's normal persistent Cargo cache/target configuration;
no target or temp override was set. It completed successfully. Fixture creation
used the app's own CLI serializer (commands run from the patched checkout):

```sh
FIXTURE="$LAB_ROOT/docs/reviews/GR-045/runtime/synthetic.designcraft"
cargo +1.95.0 run --release -p designcraft-cli -- run \
  --cmd 'file.new={}' \
  --cmd "file.save={\"path\":\"$FIXTURE\"}"
cargo +1.95.0 run --release -p designcraft-cli -- run \
  --in "$FIXTURE" \
  --cmd 'frame.create={"rect":[36,36,300,100],"content":"text","text":"GR-045 synthetic text"}' \
  --cmd "file.save={\"path\":\"$FIXTURE\"}"
```

To serve the harness and build on one origin, place the files as `host.html`,
`synthetic.designcraft`, and `designcraft/` where `designcraft/` is the contents
of `apps/designcraft-web/dist/web`; run `python3 -m http.server 8768 --bind
127.0.0.1` there and open `/host.html` in Chromium. In the visible text frame,
replace the text, press Ctrl+S, and choose **Reopen captured bytes**.

## Runtime result and artifacts

| Artifact | SHA-256 | Notes |
| --- | --- | --- |
| [`runtime/host.html`](runtime/host.html) | `e86e586cf109fbeff406ca719877ff0d32951f74a8a3e63b36eed49942caa7a0` | Same-origin parent; retains exact save bytes in memory, ACKs the matching ticket, and reopens in a fresh iframe |
| [`runtime/synthetic.designcraft`](runtime/synthetic.designcraft) | `eff10a921f0d5c279075d6785b3f24e9af15b5a926efe6f278d620c20f04ffc2` | 6,585-byte native fixture produced by the pinned CLI |
| [`runtime/saved.designcraft`](runtime/saved.designcraft) | `77e282dbc6c3cc5a29f541193a356e6029b785199c38d859eb074983b01f7cce` | Exact 3,184-byte `designcraft:save` payload; archive contains edited text |
| [`runtime/designcraft-host-reopen.png`](runtime/designcraft-host-reopen.png) | `ad79ad83d8143c4d93849607218c886282f57ef6b1591a1c60f305b48ab65994` | Chromium screenshot showing fresh iframe, clean state, same ticket/hash, and edit |

Browser observations: app assets and fixture returned HTTP 200; browser console
identified the DesignCraft renderer as WebGL backend `Gl` on Chromium SwiftShader.
The input was opened as `GR-045-synthetic.designcraft`; after editing, parent
captured 3,184 bytes, computed the listed SHA-256, and sent a positive ACK for
`designcraft:1:1`. The app reported `dirty=false`. A fresh iframe then opened
those in-memory captured bytes and rendered `GR045 runtime edit passed` while
remaining clean.

## Independent provenance check

The parent independently verified that the cached source checkout is at
`80d13911b2d20fbb5cd9398696627bb3a715417b`, the stored GR-021 patch hash is
`519c03180b17f035ef8fbfcd08a85bda312f6f0721bfbdf9dc1d9d5992fdf972`, and
`Cargo.lock` pins `craft-platform` to
`56c5e16d79b77751106173c13111ef4fe0a2c0ec`. The patch applied to a fresh
worktree of the pinned base with `git apply --unidiff-zero`; all nine changed
file hashes matched the patched build checkout. The cached WASM hash matches
the value above. The parent did not rebuild it.

Independent reviews R1 and R2 returned bounded **PROVISIONAL PASS** with no
remaining findings; see `INDEPENDENT-REVIEW-R1.md` and
`INDEPENDENT-REVIEW-R2.md`.

## Limits and disposition

The parent ACK is synthetic and in-memory; it is not a durable storage write.
Seafile versions/readback, dispatcher routing, production behavior, and
ONLYOFFICE were not exercised and remain **NOT VERIFIED**. No production system
or upstream repository was accessed or changed. Review state: **GPT REVIEW
PENDING**.
