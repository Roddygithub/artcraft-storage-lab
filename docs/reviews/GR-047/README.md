# GR-047 evidence — FilmCraft browser host-save smoke

Scope: actual FilmCraft Web/WASM built from the pinned GR-023 source changes;
synthetic same-origin parent in Chromium; synthetic native project only.

| Artifact | SHA-256 / result |
|---|---|
| Source base | `fa550ce2d07bdfee6b1d7b6835e8abc8c6913d00` |
| Transport pin | `56c5e16d79b77751106173c13111ef4fe0a2c0ec` |
| Stored patch | `16158f500b2ec12f93c8fcb14867e0b452030dbb338b2d4d7fa8612850a694d4` |
| Generated local source diff | same SHA-256 as stored patch |
| Build WASM | 40,913,852 bytes; `c1ccf010da400943fbe29c79287a5fa72194b3f8426befa5f608c6e646549d87` |
| Packaged WASM | 37,637,092 bytes; `342d877787bb684a834fc6a6bac38eb63717c0551a1f75fbc15eb2134d56718b` |
| Browser JS / HTML | `filmcraft_web.js`: `1211b1a44d994158c133493e820385853b62a90f8511897e6d1cb97a2fec90e6`; `index.html`: `87feed442b67fadd423ce5118b3b6c52225f714068383836401386e041f768c1` |
| Input `.fcproj` | 3,301 bytes; `7b9747511b3a2382bfe09667aa29d4a55dabc39b74ca25962c4c033d0296813a` |
| Save payload | 6,468 bytes; `891cc9648eab2496acbac908a3694f878dada101da3575673697e0faeb764e84` |
| Browser screenshot | `runtime/filmcraft-reopen.png`; `8079c694a52a73115f71d6d98753fbaf829175c297363e632c65067e7b06b9a5` |
| Host harness | `runtime/host.html`; `50ab2dfa879ee0c21c4b1498a4f81c3f86a759731afb81e30778609053e3ea16` |
| Supplemental replay | `runtime/replay-20261025.txt` records browser network entries, response-body hashes, edit, ACK and fresh reopen; `runtime/filmcraft-review-replay.png` shows that replay |
| Pre-packaging WASM | `filmcraft_web.wasm` in the persistent Cargo cache: 40,913,852 bytes; `c1ccf010da400943fbe29c79287a5fa72194b3f8426befa5f608c6e646549d87`, verified with `stat` and `sha256sum` on 2026-10-25; not committed due to size |
| Supplemental record hashes | `replay-20261025.txt`: `9237fd079ef588ee9253bd7e1e887d183fd0eb846ba588f732fb841cde4ad644`; `filmcraft-review-replay.png`: `f50fcb65de32e53d68081686cd262f933d7485d962daa818b879b42c24b0e2a9` |

The Chromium network snapshot showed HTTP 200 for the FilmCraft index, JS,
packaged WASM and synthetic fixture. The host received `filmcraft:ready` for
version `0.12.0`, captured the Ctrl+S `filmcraft:save` payload, acknowledged
matching ticket `filmcraft:1`, observed clean state, then opened the saved bytes
in a new iframe. The screenshot shows `GR-047 visible edit passed` rendered
again in the fresh instance.

The parent is an in-memory test harness. No bytes were durably stored and no
Seafile version/history/readback was queried. Authorization, dispatch,
production deployment and ONLYOFFICE are outside this evidence. This test task
did not perform an independent review. The supplemental replay is a separate
owner-run confirmation; its payload differs from the original smoke and also
remained in browser memory only.

The independent R1 review found no blocker or major issue and one minor
evidence-retention gap. The owner added browser response-body hashes and a
replay log. R2 accepted the served-asset evidence and found one remaining minor
about the separate pre-packaging WASM hash. That artifact was hashed from the
Cargo cache and distinguished from the packaged browser WASM. R3 returned
bounded PROVISIONAL PASS with no findings. See
[`INDEPENDENT-REVIEW-R1.md`](INDEPENDENT-REVIEW-R1.md),
[`INDEPENDENT-REVIEW-R2.md`](INDEPENDENT-REVIEW-R2.md), and
[`INDEPENDENT-REVIEW-R3.md`](INDEPENDENT-REVIEW-R3.md). These bounded reviews
do not change the project-level GPT verdict.

Full pins, exact build and fixture commands, browser steps and limits:
[`docs/GR-047-FILMCRAFT-WASM-SMOKE.md`](../../GR-047-FILMCRAFT-WASM-SMOKE.md).
