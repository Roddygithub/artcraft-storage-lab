# GR-048 evidence — FigCraft browser smoke

**Bounded synthetic transport PASS; GPT REVIEW PENDING.** Durable Seafile is
**NOT VERIFIED**. No project GPT verdict is implied. The implementation task
left its changes uncommitted for parent review and publication; subsequent lab
integration is recorded in project status and history.

| Artifact | Evidence |
| --- | --- |
| `../../GR-048-FIGCRAFT-WASM-SMOKE.md` | Result, exact pins, commands, warnings, limitations |
| `provenance.txt` | Lab main/worktree start, exact source/patch hash, toolchain, global persistent Cargo config |
| `checks.txt` | Four successful focused checks, including reverse patch applicability and whitespace |
| `build.log` | Actual optimized Trunk/WASM build and wasm-opt success |
| `check_evidence.py` | Runnable retained-record, host/fixture response hash and accepted-patch check |
| `commands.sh` | Reproduction commands (source worktree creation/apply documented; no app patch mutation) |
| `artifacts.txt` | Disk asset sizes and SHA-256 values, including distinct pre-packaging WASM |
| `network.log` | Loopback HTTP server request/status log |
| `runtime/make_fixture.py`, `runtime/synthetic.figcraft` | Runnable deterministic native ZIP fixture generator and input |
| `runtime/host.html` | Same-origin/source checked, synthetic memory-only parent; ACK held explicitly |
| `runtime/draw.js` | Exact UI event sequence evaluated through T3 preview to create visible engine rectangle |
| `runtime/browser-evidence.json` | Pre-ACK dirty, post-ACK clean, fresh iframe transcript; T3 snapshot network/console; browser-fetched response hashes |
| `runtime/figcraft-visible-edit.png` | Rendered rectangle and dirty state |
| `runtime/figcraft-reopen.png` | Fresh iframe renders rectangle with clean state |

The 3,464 outbound bytes were retained in page memory only and are not a
filesystem-backed platform save. The harness's matching ACK confirms receipt
by that synthetic page. No Seafile, production, ONLYOFFICE, external uploads,
manual file save/upload, or upstream issue/PR occurred. Accepted GR-019 patch
and app sources were not altered beyond applying that exact patch to scratch.

Independent free review: **PROVISIONAL PASS**, no BLOCKER/MAJOR; warning and
setup MINOR observations remain disclosed. See
[`INDEPENDENT-REVIEW-R1.md`](INDEPENDENT-REVIEW-R1.md) and recorder clarifications. Parent publication remains outstanding by
explicit task instruction.
