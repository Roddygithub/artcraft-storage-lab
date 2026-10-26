# GR-054 — Current candidate manifest and evidence reconciliation

Date: 2026-10-25. Status: **bounded independent R1–R2 reviews PROVISIONAL PASS**.
Project GPT verdict: **INCOMPLETE**; no new GPT review or PASS.

## Decision before real-Seafile tests

Prepare and review this inventory first. The exact tracked source snapshot is
`1c7914bf1e166ac4731a1c9b11dce649210eed70` (clean local main at task start).
It is the current source candidate for review, **not a deployable or
candidate-ready editor bundle**. The historical GPT first pass reviewed
`95d89835b2b1d06fd098c586469ed03b8fd0549e`; it did not review this snapshot.
GR-054 adds documentation/evidence and a stdlib verifier only; no service, credential, Seafile,
ONLYOFFICE, upstream, build or promotion operation was performed.

## Follow-up on 2026-10-26

The inventory below is a dated observation, not a mutable current-state claim.
At capture time the four local default bundles had no matched source/build
provenance. GR-055–058 subsequently produced pinned per-app candidates; GR-059
and GR-061–063 used those candidates for individual synthetic Seafile runs.
GR-071 checked their 20 files together against the separate GR-059 test static
root and the checked-in four-route dispatch. This closes the per-app candidate
identity gap for that local test root. It does not alter the original
`integration/static` inventory below, promote files into it, or prove what a
running service serves. See [GR-071](GR-071-DISPATCHED-CANDIDATE-PROVENANCE.md).

Two inventories must remain distinct:

| Inventory | Observation | Meaning |
| --- | --- | --- |
| This clean child worktree at the source base | `integration/static/` absent; no tracked static files | JS/WASM/index SHA-256 for every dispatched app: **absent / NOT VERIFIED**, neither tracked nor untracked files present here |
| Parent checkout `/home/roddy/Projects/artcraft-storage-lab/integration/static/` | 82 local files, all untracked and ignored; parent HEAD equals source base | Read-only operational byte inventory, not part of the tracked source snapshot; no deployment/reproducibility claim |
| `docs/reviews/GR-054/inventory.json` | 55 tracked source/patch pins, every local file's size/SHA-256/status, seven index reference maps | Exact machine-readable evidence, excludes itself and this document from hashing |

Evidence: `git rev-parse HEAD`, `git status --short`, `git worktree list
--porcelain`, `git ls-files integration`, and filesystem/Git inspection recorded
in [the evidence bundle](reviews/GR-054/README.md). No assets were copied.
The parent checkout's tracked status was clean at inspection. No running
server configuration was inspected: whether this tree is actually served is
**NOT VERIFIED**. “Active” below means the default static app path, not proof of
an active service. The gateway defaults to `integration/static`, maps
`/artcraft/` into that tree and serves each directory's `index.html`
([server.py](../integration/gateway/server.py):34–35, 353–354, 515–535).

## Dispatch at the source base

Source: [dispatch.json](../integration/config/dispatch.json), entire file
(SHA-256 pinned in the inventory). Gateway aliases alone do not add routes.
Seahub's separate per-library allowlist is not inspected or implied by this table.

| Extension | App | Configured URL | Default local parent index linkage | Exact current bundle provenance / E2E |
| --- | --- | --- | --- | --- |
| `.pdf` | PdfCraft | `/artcraft/pdfcraft/?host=parent` | JS and WASM targets present | **NOT VERIFIED** |
| `.svg` | VectorCraft | `/artcraft/vectorcraft/` | JS and WASM targets present | **NOT VERIFIED**; page API, not common parent protocol |
| `.xlsx` | GridCraft | `/artcraft/gridcraft/?host=parent` | JS and WASM targets present | **NOT VERIFIED**; differs from GR-016 runtime hashes |
| `.docx` | WordCraft | `/artcraft/wordcraft/?host=parent` | JS and WASM targets present | **NOT VERIFIED** |

No other extension/app is dispatched. PhotoCraft and SoundCraft are local
non-dispatch trees. `candidates/` is staging, not the dispatch destination
([fetcher](../scripts/fetch-craft-web.sh):73–96). No dispatch change is proposed.

## Local operational JS/WASM/index SHA-256

Paths are relative to the **parent** static root above. Every row is
**untracked + ignored**, verified with `git ls-files` and `git check-ignore` in
that checkout. Complete supporting files (icons, fonts, licenses, hosting
notes, fixtures, locks and staged release files) are included in
[inventory.json](reviews/GR-054/inventory.json), not omitted from the byte inventory.
Checksums establish byte identity only; filenames are never source provenance.

| Local relative path | SHA-256 | Bytes |
| --- | --- | ---: |
| `gridcraft/gridcraft-web-a862b19ca88ea5df.js` | `d95343e37a003a436512ebf05a8c1ec77e3123ac7af27c8a3d61d3013a410a8b` | 160353 |
| `gridcraft/gridcraft-web-a862b19ca88ea5df_bg.wasm` | `823bdc868268261b93180d539210069ed8027e3c58487d3fa9a5a4e839db3554` | 18932615 |
| `gridcraft/index.html` | `cc4258d5b6f5418f2c4f8794819e7d25b6fece61bf4356e2e64d568ba413a042` | 1604 |
| `pdfcraft/index.html` | `1574042de6fcc5a7ba494664fecfcaeb93903b99db0539f0865dfa24fa53fb46` | 1210 |
| `pdfcraft/pdfcraft-web-2faa2bc762f98c12.js` | `aa607caaac01fb75433a4f4f2322e8b6c1332a00239bbe10d3c51ead99b04515` | 165222 |
| `pdfcraft/pdfcraft-web-2faa2bc762f98c12_bg.wasm` | `63caadb98c3decbdd61f1f7cbda5f6d3a6131bc34c1fb329437abd55607c2835` | 39154172 |
| `photocraft/index.html` | `e49904620d4e17e49b2f1b39dba4c45db9c16a72bd25f827118346e3257a4a4d` | 2320 |
| `photocraft/photocraft-web-5251a55206c25672.js` | `9269838cd5fbbf3c9df7c1fd01dd73e0b1edc959e20c7897a911de20090cacf6` | 177649 |
| `photocraft/photocraft-web-cbd436f9a105b44d_bg.wasm` | `f67193223bc7367bade2bca00e105ee856eafc892eda538a2112a86df13f155b` | 26342447 |
| `soundcraft/index.html` | `d3555a07841abeb83472a79105299e5ebd5f1ee8183af185d73d66bfdb284432` | 2700 |
| `soundcraft/soundcraft-web-4155a64cbebbeb93_bg.wasm` | `c45d655fbb85ab115b03db7ff03a6f0d42c8c56eccce882b30dfabd1284cf264` | 22358112 |
| `soundcraft/soundcraft-web-c3f262f265311041.js` | `39163c52ec78914bfe87dce8da481d0245be59d9114ffb18719531a09eef5fe5` | 173800 |
| `vectorcraft/index.html` | `55f3e447e46af2d38be31efb4d9fe6a53944d11b3a90db82efbeae55faf7800f` | 2513 |
| `vectorcraft/vectorcraft-web-d0094b3b031c2f0c.js` | `6fefae1599ba61e318df66e0e63defa829fe176995bde7aa796d50b5edd5f01b` | 176550 |
| `vectorcraft/vectorcraft-web-d0094b3b031c2f0c_bg.wasm` | `6ff3616ff6cf11723d5b453ec2a64f5410cdd3830503017d761a775c3b24254d` | 73742886 |
| `wordcraft/index.html` | `c607aa5e707ac1ccb680c3ec9d5d2f951166a23dff4f8099571d2095120b3598` | 1604 |
| `wordcraft/wordcraft-web-2afd9dce3f994b7f.js` | `fe62980e5df0989bb9766fd40f130076c3db979bf8ae780a95f01c6a3e7fa6b0` | 172457 |
| `wordcraft/wordcraft-web-fb90ec805f7fe330_bg.wasm` | `c559957bb12e87cd535f7844d449d2b8abd5a3a8d91f933bd42f11051fa590f1` | 61654782 |
### Index linkage and staging

Each of the four dispatched `index.html` files explicitly imports its JS and
passes its listed WASM path to initialization. The JS contains generic
`<app>-web_bg.wasm` fallback names; the explicit index parameter is the observed
linkage, not a requirement for a generic-named file. All referenced dispatched
JS/WASM and icon targets exist. This is static inspection, **not browser execution**.
Full relative references and existence booleans are in `index_links` in the JSON.
All 14 integrity attributes for present default-index assets also match their
local SHA-384 values; the fifteenth names the missing PhotoCraft WASM target
([checks](reviews/GR-054/checks.txt)). This confirms static byte/link consistency,
not source provenance or browser execution.

| Non-dispatch tree | Linkage / provenance result |
| --- | --- |
| PhotoCraft | Index imports `photocraft-web-5251a55206c25672.js` but names **missing** `photocraft-web-840a87a8cfbe4217_bg.wasm`. Present WASM is `photocraft-web-cbd436f9a105b44d_bg.wasm`; its SHA matches [GR-035](GR-035-PHOTOCRAFT-OPTIMIZED-BROWSER-SMOKE.md), but that does not repair or verify this index/bundle combination. **NOT VERIFIED / broken local linkage**. |
| SoundCraft | Index links to the present JS and `soundcraft-web-4155a64cbebbeb93_bg.wasm`. WASM SHA matches [GR-030](GR-030-SOUNDCRAFT-BROWSER-SMOKE.md); current JS/index exact source linkage remains **NOT VERIFIED**. GR-031 separately records isolated Seafile evidence, not a complete hash match for this current tree. |
| `candidates/wordcraft/v0.10.0-46e32c024cac86d644874e7120ee9e42a6c0ccc76bd020ba9c741706b5b77b05/` | Contains its own index/JS/WASM and `ARTIFACT-PROVENANCE.txt`; JSON pins all files. Provenance note records release `v0.10.0`, ZIP SHA `46e32c024cac86d644874e7120ee9e42a6c0ccc76bd020ba9c741706b5b77b05`, repository `storytold/wordcraft`, release asset URL and “staged candidate; not installed”. Its JS/WASM differ from active WordCraft. ZIP absent here, so original archive checksum/source commit and host compatibility are **NOT VERIFIED** by GR-054. No promotion. |

The staged note's recorded URL is
`https://github.com/storytold/wordcraft/releases/download/v0.10.0/wordcraft-web-0.10.0.zip`;
it was read locally, not fetched. None of the six default app directories has
an `ARTIFACT-PROVENANCE.txt`. Bundled README/license/hosting files do not establish
which source revision, patch or transport produced a binary.

## Available source pins versus exact operational provenance

The table that follows records evidence available at the original GR-054
capture. The per-app candidate provenance and later Seafile runs are updated in
the 2026-10-26 follow-up above and in GR-071; don't read this historical table
as a statement that the newer source-pinned candidates lack provenance.

These are **available historical source/build records**, not proof that the
current default local assets were built from them. Source and runtime transport
pins differ in the records and must not be silently conflated.

| Dispatched app | Available source / patch / transport evidence | Historical browser and real isolated Seafile scope | Exact local asset conclusion |
| --- | --- | --- | --- |
| WordCraft | Source `00bc6a4b028013b2dfb0e85e8b326aeed3ecff6d`; GR-016 combined GR-014/016 patch below; stored patch pins packaged transport `90c261de22ef75c4c7c5c5cd1c712d483be0bbc8`. [Portable patch record](reviews/GR-016/PORTABLE-APP-PATCHES-20261024.md). | [GR-015](reviews/GR-015/ISOLATED-RUNTIME-E2E-20261023.md): actual WASM, real isolated patched Seafile with synthetic documents, file-list click/edit/save/version/ACK/reopen and two-editor conflict. [GR-016](reviews/GR-016/SEAFILE-WORDCRAFT-SHARED-TRANSPORT-E2E-20261024.md): actual WASM shared transport, click/save/history 2→3/reopen; runtime used local craft-libs base `f180fc0d35d521c5d18e118c881d3efde1ec1eee`, scratch patches and `wasm-opt=0`. Exact outbound save bytes not separately hashed. | No current JS/WASM/index hash match found in stored evidence. Exact source/patch/transport **NOT VERIFIED**. Historical MVP is not revalidated on this source-plus-assets combination. |
| GridCraft | Source `06920de8da609c19de7446945cfc62b844691efd`; GR-016 patch below; packaged transport pin `90c261de22ef75c4c7c5c5cd1c712d483be0bbc8`. Same portable patch record. | [GR-016](reviews/GR-016/SEAFILE-GRIDCRAFT-SHARED-TRANSPORT-E2E-20261024.md): actual WASM, real isolated patched Seafile, direct route/save/version/reopen and one formula recalculation; runtime local craft-libs `f180fc0d35d521c5d18e118c881d3efde1ec1eee`, `wasm-opt=0`. Report says original static bundle restored afterward. | Recorded runtime JS `05a38b0e13cc4edca61d454d48c905723e42dcd739e2bb7f33175c3ab4760dc4` and WASM `9ac87a80d82aa7265587e3a220b7c2c166f5b225ba2a440c4a96a6e77bd6511b` **do not match** local files. Exact source/patch/transport **NOT VERIFIED**. |
| PdfCraft | Source `57e531ccca0047597809748b5cb4276336d6051a`; current stored GR-017 patch below pins packaged transport `90c261de22ef75c4c7c5c5cd1c712d483be0bbc8`. [GR-017 README](reviews/GR-017/README.md). | [R4 smoke](reviews/GR-017/RUNTIME-SMOKE-R4.md): actual optimized WASM with synthetic sessionStorage parent, **not Seafile**. [Isolated E2E](reviews/GR-017/SEAFILE-PDFCRAFT-E2E-20261024.md): actual WASM/direct Seahub route/annotation/save/history/readback/fresh reopen; local craft-libs base `f180fc0d35d521c5d18e118c881d3efde1ec1eee`; no file-list click or outbound payload hash. | R4 records patch `de30f47e823536c8b99d4d718a0731f8afdc1f56537deceec3d77f9ffda7fbf5` and WASM `2dda4ff36e8259a687f30827ca2fe7fe1fefc76b3958ec3beb9c4daccf97567c`, differing from current stored patch/local WASM. R4 cannot establish their identity. Exact source/patch/transport **NOT VERIFIED**. |
| VectorCraft | [GR-012 E2E](reviews/GR-012/VECTORCRAFT-SEAFILE-E2E-20261023.md) records release `v0.14.0` and release-checksum verification; no exact source revision or current extracted-file checksum binding located. Uses `window.vectorcraft`, not packaged host transport ([hostpage.py](../integration/gateway/hostpage.py):75–86). | Actual WASM, real isolated patched Seafile with synthetic SVG: file-list click, page API path edit, polling save, new version/history/readback and fresh reopen. Synthetic collision/retry tests are separate. No dirty/save event and no common host-contract claim. | Release label is historical evidence, not an inferred pin for current filenames. Exact source/release/patch and current E2E **NOT VERIFIED**; shared transport pin **not applicable**. |

Current patch SHA-256, computed from the tracked source base (also in JSON):

| Artifact | SHA-256 |
| --- | --- |
| `docs/reviews/GR-016/patches/wordcraft-shared-transport.patch` | `1c0bba26de821d1d54c161c5954bc8a5b0f5d7df71be7c4488c473b753842afc` |
| `docs/reviews/GR-016/patches/gridcraft-shared-transport.patch` | `20b219e7f53d7fd0e2fa1c84033cef3d72b22e6f69fe4c4cbcab5ffff077945f` |
| `docs/reviews/GR-017/patches/pdfcraft-durable-host-ack.patch` | `6d50eb1f45e81f2037948cd6160878feb2d87eb0881d167f0fc1d290e4450562` |
| `docs/reviews/GR-015/seahub-12.0.14.patch` | `3ace48b53d8ed8468384f75b50f47f49ae19d780ee912a97905258f08b6f8eab` |
| `docs/reviews/GR-015/seafile-server-12.0.14.patch` | `69abef7b322721ce9d5a2c9cdb55f7812ce44acd9dd3db199416997c1b729c9e` |
GR-015 source pins: Seahub 12.0.14 Pro
`1e9bde801b4360c14d784d9681d4261abc233a8b`; Seafile Server 12.0.14
`32ed9c69594c9faa5cea28024403fcde362589ec`
([GR-015 README](reviews/GR-015/README.md), exact-source table). They are
historical patched-stack targets, not evidence for stock/Go/production servers.
[Packaged transport provenance](../integration/rust/craft-platform/PROVENANCE.md)
identifies craft-libs base `f180fc0d35d521c5d18e118c881d3efde1ec1eee` plus local
changes; [GR-024](reviews/GR-024/README.md) records later hardening at
`56c5e16d79b77751106173c13111ef4fe0a2c0ec`. That later pin must **not** be
attributed to the dispatched app binaries or their `90c261de` stored patches.
The inventory hashes every tracked integration file and every stored `.patch`
file, including transport source, Cargo files, provenance/checksum files and
non-dispatched app patches. It does not prove upstream patch application or
reproduce a build.

## Reconciled evidence gates

| Gate | Current assessment | Evidence / remaining boundary |
| --- | --- | --- |
| Synthetic transport/gateway tests | Recorded, bounded **synthetic** evidence | GR-049/050 use fake upstream; GR-051 uses a synthetic editor and FakeSeafile, **not actual WASM or real Seafile**. GR-052/053 local regressions do not revalidate deployed editors. |
| Actual-WASM browser host tests | Recorded per app, sometimes memory/sessionStorage only | Must be distinguished from persistent Seafile version/reopen; source/bundle identity must be matched before reusing a result. |
| Real isolated Seafile MVP | Historical bounded reproduction with synthetic files | GR-015/016/017/012 above; **not** a current source-plus-assets replay, production proof or all-version/type coverage. |
| ONLYOFFICE preservation | **Proven on isolated synthetic stack** | [GR-040](reviews/GR-040/README.md): actual ONLYOFFICE 8.0.1-31 DOCX editor, two saves, HTTP-200 callbacks, history 3→5, fresh file-list reopen with both edits. Independent evidence review **PROVISIONAL ACCEPT**. The old unqualified “ONLYOFFICE regression unverified” blocker is historical and superseded for this scope. |
| Production/deployment and broader ONLYOFFICE compatibility | **NOT VERIFIED** | GR-040 does not cover production configuration/topology, other file types or Document Server versions, TLS/proxy/CSP/CSRF, callback byte identity or all security cases. No production access in GR-054. |
| Exact per-app candidate in the GR-059 test static root | **Verified, bounded to the local test root** | GR-071 rechecked all 20 WordCraft/GridCraft/PdfCraft/VectorCraft candidate files against their GR-055–058 manifests and confirmed tracked dispatch mapping. GR-059 and GR-061–063 record per-app Seafile runs. |
| Original repository `integration/static` bundle promotion and live service root | **NOT VERIFIED** | GR-054 records that separate ignored/untracked tree as observed on 2026-10-25; GR-071 neither replaced it nor checked a running service. |
| One full four-route dispatcher replay / production readiness | **NOT VERIFIED** | Per-app Seafile runs are recorded separately; production routing, security, authorization, and simultaneous ONLYOFFICE behavior remain open. |
| Project GPT review / upstream gate | **INCOMPLETE; LOCKED** | Historical [95d first pass](reviews/GPT-FIRST-PASS-95D8983.md); no new GPT verdict. GR-054's bounded reviews do not change project status; no upstream publication allowed. |

Before promoting these candidates or testing another deployment, verify the
exact static root and source/patch/transport combination there, then define
rollback and run the synthetic-library preservation checks against that
deployment. This document authorizes no deployment or production changes.

## Recheck

From the repository root, no dependencies, network or services:

```sh
python3 docs/reviews/GR-054/verify_manifest.py
python3 docs/reviews/GR-054/verify_manifest.py --local-static-root /home/roddy/Projects/artcraft-storage-lab/integration/static
```

Default mode verifies the 55 source pins against both base-commit blobs and
current working files; it does not require ignored assets. Optional mode also
checks every observed local file's SHA-256/size, exact file set, tracking/ignore
status and index links. A PASS means **inventory matches the observation**,
including the known missing PhotoCraft target. It never means provenance,
browser success, deployment reproducibility or candidate readiness. Additional
or changed local files require a new reviewed inventory, not automatic pin updates.
