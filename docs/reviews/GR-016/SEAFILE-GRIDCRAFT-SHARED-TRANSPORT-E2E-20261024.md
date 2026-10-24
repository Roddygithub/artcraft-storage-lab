# GR-016 — GridCraft shared transport against isolated Seafile

Date: 2026-10-24
Lab repository base: `38b2631e1a01ec5a843295fca318254d1a5f6a97`
Result: **RUNTIME REPRODUCED in synthetic Seafile; bounded to GridCraft**

## Scope and environment

This run exercises the GridCraft GR-016 Rust/WASM adapter through the same
synthetic Seafile and gateway stack used for WordCraft. It is not a project
GPT verdict and does not establish public deployment readiness.

| Component | Exact setup |
|---|---|
| GridCraft | `storytold/gridcraft` base `06920de8da609c19de7446945cfc62b844691efd`, with GR-016 adapter patch in `/tmp/artcraft-gr016-gridcraft` |
| Shared transport | craft-libs GR-016 worktree based on `f180fc0d35d521c5d18e118c881d3efde1ec1eee`; Rust 1.95 |
| Seafile / Seahub | same isolated patched versions and loopback-only stack recorded in [WordCraft evidence](SEAFILE-WORDCRAFT-SHARED-TRANSPORT-E2E-20261024.md) |
| Synthetic file | `tests/fixtures/synthetic.xlsx`, uploaded only as test setup to `ArtCraft Synthetic` |
| Browser | Collaborative Chromium; real Seahub file route, GridCraft Web/WASM, gateway and Seafile API |

The Seahub extension allowlist was temporarily expanded to include `xlsx` in
the synthetic stack. The production Seafile service and ONLYOFFICE were not
touched. After testing, the synthetic allowlist was restored to DOCX only and
the repository's original GridCraft static bundle was restored. The test-fixture
upload initialized the synthetic library; it is not counted as an editor save.

## Build and run

- `RUSTUP_TOOLCHAIN=1.95.0 trunk build --release`, run from
  `/tmp/artcraft-gr016-gridcraft/apps/gridcraft-web`: exit 0, optimized Rust
  release profile. As with WordCraft, the scratch `index.html` used
  `data-wasm-opt="0"` to skip the optional lengthy wasm-opt pass; this is not a
  production-optimized bundle.
- Built GridCraft JS and WASM were served from the gateway's local static path
  and returned HTTP 200 in Chromium.
- Opened the Seahub file route for `synthetic.xlsx`. Seahub posted the scoped
  capability to gateway `/open/`; the gateway loaded
  `/artcraft/gridcraft/?host=parent`, then fetched the document from the
  synthetic Seafile session.
- In the actual GridCraft sheet, replaced cell A1 with `GridSeafileAck`. The
  editor showed `Unsaved changes`. Ctrl+S sent serialized workbook bytes
  through the shared host transport. The host waited for the Seafile write,
  returned the matching durable result and showed `Saved — new version` with
  head `f3ca3e70086535f345ac18b51f279ffc0e69ae0c`.
- Reloaded the Seafile file route into a fresh GridCraft Web/WASM instance.
  The reopened sheet displayed `GridSeafileAck` in A1.

Screenshot: [`runtime/gridcraft-seafile-reopen-20261024.png`](runtime/gridcraft-seafile-reopen-20261024.png).
The visible editor tab in the screenshot came from a fresh Seahub route load;
Seafile API readback below independently verifies its stored bytes and version.

## Seafile and workbook evidence

| | Before GridCraft save | After GridCraft host save |
|---|---:|---:|
| Repository head | `7ef83136912299a0b7bac9d61c2e55fd04554994` | `f3ca3e70086535f345ac18b51f279ffc0e69ae0c` |
| File ID | `037c053ea15cdf1e7dcd2855c17ae9f4736333aa` | `b22503cfa050ac7b7be2878a588d15af22c26bc1` |
| Length | 2,154 bytes | 4,144 bytes |
| SHA-256 from fixture / Seafile API download | `7fd3c578c6411fc8c97e798c1f8b0de43337aaa15ca4ca07d4ffd6cd511815d7` | `cff9f03d5ed7ea8319670f1b166045ee7bb9292195b73ce6c9a54a296d808abe` |
| XLSX history entries | 1 | 2 |
| Semantic/integrity check | baseline synthetic workbook | valid ZIP; shared string for A1 is `GridSeafileAck`; formula `<f>SUM(B2:B2)</f>` and cached `<v>42</v>` remain |

The API response's current file ID matched the newest history `rev_file_id`, and
the downloaded length matched Seafile file detail. The editor's exact outbound
`gridcraft:save` bytes were not separately captured and hashed; only the
Seafile readback is hashed.

### Formula recalculation save and fresh reopen

The first editor session was restarted with the synthetic Seahub service. Its
old capability then correctly failed with HTTP 403; that attempt created no
version. I reopened the document through a fresh Seahub session and repeated
the edit rather than treating the failed request as a save.

In the fresh GridCraft Web/WASM session, cell B2 changed from 42 to 1337. The
editor displayed the formula `=SUM(B2:B2)` in B3 and recalculated B3 to 1337.
Ctrl+S displayed `Saved — new version` with Seafile head
`fbdcec44f48ef805d89d142203a405b0108bcbc7`. Seafile API readback returned a
new file ID and history entry; the downloaded XLSX was 4,145 bytes with SHA-256
`ec33a69193d3acf2efea9d2e61f8722cd96ef275be55941d0046f49582d2ac72`. The
package remained a valid ZIP; its worksheet contained B2=1337, B3 formula
`SUM(B2:B2)`, and cached B3 value 1337. A fresh Seahub route load created a new
GridCraft instance displaying B2=1337 and B3=1337. Screenshot:
[`runtime/gridcraft-seafile-reopen-20261024.png`](runtime/gridcraft-seafile-reopen-20261024.png).

This verifies recalculation for the tested workbook and edit path. It does not
establish broad formula compatibility or an independent byte hash at the
editor-to-gateway boundary.

## Reproducible artifacts

- Built WASM SHA-256: `9ac87a80d82aa7265587e3a220b7c2c166f5b225ba2a440c4a96a6e77bd6511b`
- Built JS SHA-256: `05a38b0e13cc4edca61d454d48c905723e42dcd739e2bb7f33175c3ab4760dc4`
- Workbook SHA-256 after Seafile API readback: `cff9f03d5ed7ea8319670f1b166045ee7bb9292195b73ce6c9a54a296d808abe`
- Workbook SHA-256 after B2 formula-recalculation save and Seafile API readback: `ec33a69193d3acf2efea9d2e61f8722cd96ef275be55941d0046f49582d2ac72`

## Limits

- This is an isolated synthetic Seafile runtime, not production. Authorization
  revocation, external writer races, interrupted acknowledgements, proxy/TLS,
  CSP/CSRF, and public deployment remain unverified.
- Formula recalculation was verified for one `SUM(B2:B2)` formula after B2
  changed from 42 to 1337. Broader workbook semantics and formula compatibility
  remain NOT VERIFIED.
- Exact serialized bytes emitted by GridCraft were not separately captured and
  hashed before the gateway; the recorded SHA-256 is from Seafile API readback.
- The app route was opened directly from the Seahub file URL in this run; the
  WordCraft evidence separately includes an actual Seahub file-list open.
- This proves the GridCraft adapter's save round-trip only; it does not prove
  all ArtCraft apps implement the shared contract.
