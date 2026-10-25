# GR-056 evidence — reproducible GridCraft candidate

Implementation worktree: `/home/roddy/.t3/worktrees/artcraft-storage-lab/t3-4d53dbd5`,
branch `t3/gr056-gridcraft-candidate`, base
`247ae75753d4d22c7567b53271b3bf0c0d119f99`.

## Inputs and build record

| Check | Evidence |
|---|---|
| Exact source | `https://github.com/storytold/gridcraft.git`, commit `06920de8da609c19de7446945cfc62b844691efd`; source checkout `/home/roddy/.cache/artcraft-storage-lab/gr056-source/gridcraft` |
| Stored patch | `docs/reviews/GR-016/patches/gridcraft-shared-transport.patch`; SHA-256 `20b219e7f53d7fd0e2fa1c84033cef3d72b22e6f69fe4c4cbcab5ffff077945f` |
| Apply | `git apply --check` passed, then normal `git apply` completed; no fuzz option. The changed-file summary is in `checks.txt`. |
| Transport | App manifest rev `90c261de22ef75c4c7c5c5cd1c712d483be0bbc8`; lock source ends `#90c261de22ef75c4c7c5c5cd1c712d483be0bbc8` |
| Overlay | `apps/gridcraft-web/index.html`: `data-wasm-opt="z"` → `data-wasm-opt="0"`; post-overlay SHA-256 `b86f07792b2c600a4d5f3ff275e4dffc4adbb70fc6b23edd713cf4e7fd919fd1` |
| Toolchain/build | Rust/Cargo 1.95.0; Trunk 0.22.0; `RUSTUP_TOOLCHAIN=1.95.0 trunk build --release --locked --dist /home/roddy/.cache/artcraft-storage-lab/gr056-gridcraft-static/gridcraft` from `apps/gridcraft-web`; exit 0 |
| Persistent output | Candidate at `/home/roddy/.cache/artcraft-storage-lab/gr056-gridcraft-static/gridcraft`; `TMPDIR=/home/roddy/.cache/cargo-tmp`; configured Cargo target `/home/roddy/.cache/cargo-target`; no `/tmp` target/temp override |

Exact commands are in [`commands.sh`](commands.sh); collected outputs are in
[`checks.txt`](checks.txt). The Trunk `.trunk-lock` is a transient zero-byte
lock file and is not a served asset or part of the inventory.

## Candidate bundle inventory

[`hash-inventory.json`](hash-inventory.json) records the exact four served
files. Recheck the candidate and its source/patch/transport/overlay provenance:

```sh
python3 docs/reviews/GR-056/verify_candidate.py
```

The verifier accepts `--static-root` and `--source-root` overrides. It checks
exact file membership, sizes, SHA-256, index references, source commit, stored
patch SHA, both transport pins and the overlay digest.

## Actual-WASM Chromium smoke

The browser opened the exact staged release WASM through the supplied
`docs/reviews/GR-016/runtime/gridcraft-host.html` page. The host page and
`tests/fixtures/synthetic.xlsx` were copied into a disposable cache directory;
candidate assets were symlinked there, not copied into or promoted to dispatch.
The page ran at `http://127.0.0.1:8976/gridcraft-host.html` through a local
Python static server.

Recorded browser result:

- Initial synthetic fixture opened at 2,154 bytes.
- Chromium selected B2, entered `1337`, and the visible formula bar for B3
  showed `=SUM(B2:B2)` while the visible calculated result changed to `1337`.
- Ctrl+S emitted `gridcraft:save` ticket `gridcraft:1`. The parent sent
  `gridcraft:saveResult` with the same ticket and `ok:true`; the instrumented
  parent recorded a following `gridcraft:dirty` event with `dirty:false`.
- The serialized in-memory workbook is
  [`runtime/gridcraft-memory-saved.xlsx`](runtime/gridcraft-memory-saved.xlsx),
  4,149 bytes, SHA-256
  `cf240bb1f1f67b7ddefd38939aebe6f7d6c13167063a5983d02aba91ce97ea2c`. Its
  worksheet XML contains B2 value `1337`, B3 formula `SUM(B2:B2)` and cached
  B3 value `1337`.
- The host closed the first iframe, loaded a fresh GridCraft iframe from the
  stored bytes, and the screenshot shows B2 and B3 both at `1337` with
  `dirty=false`: [`runtime/gridcraft-fresh-reopen.png`](runtime/gridcraft-fresh-reopen.png)
  (63,436 bytes; SHA-256
  `54f4dab2c6bc5a7db1581bffd859d5d3b948dfd49cb553a8b89b2c9d69f6542c`).

This proves an actual-WASM browser roundtrip through a memory-only parent. It
does not prove durable version creation, Seafile API readback, Seafile browser
open, or the project's required Seafile MVP. Browser run summary and key
message sequence are recorded in [`browser-smoke.txt`](browser-smoke.txt).

## Scope and review status

Only the read-only Seafile preflight below was performed; no Seafile write or
persistence test, production-file access, credential use, ONLYOFFICE action,
upstream write, issue, PR or RFC occurred. Candidate remains outside dispatch.
Independent R1–R5 reviews are bounded PROVISIONAL PASS with no remaining
findings. This work is uncommitted and unpushed. Work item status is
**GPT REVIEW PENDING**; project verdict stays **INCOMPLETE** and upstream
publication stays locked.
## Real Seafile preflight

The authorized instance contains a dedicated synthetic library. A read-only
GET to the gateway's conditional-save route returned 404. No write or service
change was made; exact-candidate version/readback/reopen remains NOT RUN. The
redacted transcript is [`seafile-preflight.txt`](seafile-preflight.txt).

## Independent review follow-up

R1 identified a P3 verifier gap: reverse patch applicability alone did not reject
additional source changes. The verifier now rejects staged and untracked source
additions and hashes the complete tracked source diff, excluding only the declared
`index.html` build overlay, against the pinned patch SHA-256. R2 independently
confirmed the code fix. R2 found and R3 confirmed a documentation inconsistency:
the summaries now agree that a synthetic target exists but its conditional-save
route returns 404, and this README now distinguishes the read-only preflight
from writes/persistence tests. The wording cites the redacted transcript above.
R4 also noted that the candidate report's “No service access” contradicted the
preflight and the matrix did not name the review round. The report now explicitly
permits only the read-only preflight, and the matrix records R1–R5. R5 returned
PROVISIONAL PASS with no remaining findings; see
[`INDEPENDENT-REVIEW-R5.md`](INDEPENDENT-REVIEW-R5.md).
`python3 docs/reviews/GR-056/verify_candidate.py`, Python syntax compilation,
and `git diff --check` pass; Seafile persistence remains NOT RUN.
