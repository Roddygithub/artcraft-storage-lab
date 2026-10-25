# GR-054 — Inventory evidence and review handoff

Date: 2026-10-25. **Independent R1–R2 bounded review: PROVISIONAL PASS**.
Uncommitted/unpushed by task instruction. No independent review is claimed;
this implementation self-check is not independent review. Project GPT remains
**INCOMPLETE**, no GPT PASS; upstream gate remains locked.

Artifact: [current candidate manifest](../../GR-054-CURRENT-CANDIDATE-MANIFEST.md).
Source base: `1c7914bf1e166ac4731a1c9b11dce649210eed70`.

## Retained evidence

| File | Content |
| --- | --- |
| [inventory.json](inventory.json) | Base SHA; SHA-256 for all 55 tracked integration/Cargo/fetcher/patch files in scope; absolute parent-local root and HEAD; 82 file sizes/hashes/tracked/ignored flags; seven index reference maps |
| [verify_manifest.py](verify_manifest.py) | Stdlib-only, read-only verifier; no build/network/service dependency |
| [checks.txt](checks.txt) | Local verifier, negative check, syntax/checksum/link and whitespace results |

Scope of `source_files`: every tracked `integration/` file, every tracked
`.patch` artifact in the repository, root Cargo manifest/lockfile, `.gitignore`,
asset fetch/extraction scripts. It is an explicit source subset at the exact
base, not a self-hash or a claim to hash every document in the repository.
`local_files` includes **every** file under the observed parent static root,
including staging and ancillary files; no binary bytes or fixture contents
were copied into evidence. New GR-054 files are intentionally excluded from
source hashing, avoiding recursive manifests.

## Read-only observations and method

| Command / inspection | Result |
| --- | --- |
| `git rev-parse HEAD` | Exact source base above |
| `git status --short` before edits | Empty; clean child worktree |
| `git worktree list --porcelain` | Parent main checkout `/home/roddy/Projects/artcraft-storage-lab` at same source base |
| `git ls-files integration` and local filesystem walk | No tracked static files; child's `integration/static` absent |
| `git -C /home/roddy/Projects/artcraft-storage-lab status --short --untracked-files=no` | Empty at inspection; tracked parent files clean |
| Recursive parent static walk + SHA-256 + byte sizes | 82 regular files, no symlinks observed; captured as `local_files` |
| Parent `git ls-files -- ABSOLUTE_FILE` and `git check-ignore -- ABSOLUTE_FILE`, every local file | All untracked and ignored; `.gitignore` lines 6 and 13 cover WASM/app trees |
| Read each local index and extract literal `./...js/wasm/ico/png` references | Seven maps; four dispatch app links present; PhotoCraft index WASM target absent; no HTML/JS execution |
| Check default-index `integrity` attributes against local SHA-384 | All 14 present referenced assets match; PhotoCraft WASM target missing (see checks) |
| Read default-app README/license/hosting files and staged `ARTIFACT-PROVENANCE.txt` | No exact default-app source binding; staged WordCraft archive/tag note is separate from active path |
| Compare local JS/WASM/index SHA-256 against existing `docs/` Markdown/text/JSON evidence | No match for four dispatched app bundles; PhotoCraft/SoundCraft WASM match GR-035/030 respectively, not complete bundle bindings |

Index inspection includes explicit initialization parameters; the generated JS
has generic fallback WASM names, which do not override the index's supplied
path. Existing provenance claims were inspected in GR-015/016/017/012,
transport PROVENANCE/SHA256SUMS, GR-024, GR-030/031/035/036/037/038/040,
STATUS and review queue. No provenance was inferred from a hash-looking filename,
release README, or source pin with no binary match.

## Reproduce and interpret

```sh
python3 docs/reviews/GR-054/verify_manifest.py
python3 docs/reviews/GR-054/verify_manifest.py --local-static-root /home/roddy/Projects/artcraft-storage-lab/integration/static
```

Default verification works from the tracked repository without the parent
assets. Optional verification requires that exact observed tree (or an identical
ignored tree in a Git checkout). No writes are made to it. An inventory PASS
preserves known defects; it does not bless PhotoCraft's missing target or prove
source provenance, successful browser save, reproducible deployment or readiness.

GR-040's retained checksum bundle is checked locally as corroboration of the
existing evidence; GR-054 does not replay its browser test. The isolated
synthetic ONLYOFFICE preservation result is proven in that scope; production,
other types/versions and security remain NOT VERIFIED.

## Independent review R1

**Result: PROVISIONAL PASS**, with one P3 wording finding. The reviewer
confirmed both verifier modes, the dispatch/linkage inventory, PhotoCraft's
missing index target, GR-040's bounded ONLYOFFICE evidence, and the historical
scope of the `95d898` GPT first pass. Current bundle provenance and current
source-plus-assets replay remain **NOT VERIFIED**.

Finding: the verifier checked per-file tracking/ignore status but not the
recorded parent HEAD or whole-checkout cleanliness, while its output said
“Git status … match observation.” Narrowed the message to state exactly what
the optional mode checks: per-file tracking/ignore status. The recorded clean
parent status remains a captured observation, not a verifier-enforced check.

The corrected command output is retained in [checks.txt](checks.txt).

## Independent review R2

**Result: PROVISIONAL PASS**, no new findings. Both verifier modes were rerun:
55 source pins match base and working files; optional mode also matches all 82
parent-local files, per-file tracking/ignore status and index links. R2 confirmed
that the revised output and README describe the checks accurately. Source/bundle
provenance, actual serving behavior, and a current source-plus-assets replay
remain **NOT VERIFIED**. No services, builds, Seafile, production, or upstream
were accessed.

## Review scope and remaining boundary

Review source/base separation, every dispatch row/hash/status, index linkage,
source-versus-runtime pin mismatches, bounded GR-040 reconciliation and the
verifier's meaning. No source code, app builds or promotion changed. GR-054 is
committed with project GPT review pending; no upstream publication is allowed
while the project verdict remains incomplete.
