# GR-048 — FigCraft host-save browser runtime smoke

**Result: bounded synthetic browser PASS — GPT REVIEW PENDING.** The parent is synthetic and memory-only. Durable Seafile save,
version creation/readback and fresh reopen from Seafile remain **NOT VERIFIED**.
No Seafile, production, ONLYOFFICE, external upload or upstream issue/PR was used.

## Exact inputs and build

| Input | Value |
| --- | --- |
| Lab worktree starting commit (current local main) | `32069b9d42e3b36b34402d6faa1de1d6dfb5a4d4` |
| Clean detached FigCraft base | `8d790607ff1ad40e32343ca2116d8fdcf3244c8d` |
| Shared transport lock pin | `56c5e16d79b77751106173c13111ef4fe0a2c0ec` |
| Accepted patch | `docs/reviews/GR-019/figcraft-shared-host-save.patch` |
| Patch SHA-256 | `954850ba5aff7362e776b2331a5a5ff54bf9d71374d7b29bc856c2b7a47c4798` |
| Source checkout | `/home/roddy/.cache/artcraft-figcraft-gr048` |
| Build | `RUSTUP_TOOLCHAIN=1.95.0 trunk build --release` in `apps/figcraft-web` |
| Browser | T3 collaborative preview only, loopback `http://localhost:18748/host.html` |

The exact patch applied to the clean pinned source worktree without modifying
its hunks or upstream sources. The regenerated source diff hash matches the
accepted patch. Cargo used the global persistent target directory
`/home/roddy/.cache/cargo-target` and temporary directory
`/home/roddy/.cache/cargo-tmp`. No environment override or cache move was used.
See [provenance](reviews/GR-048/provenance.txt),
[build log](reviews/GR-048/build.log), and
[reproduction commands](reviews/GR-048/commands.sh).

## Runtime

| Step | Observation / evidence |
| --- | --- |
| Actual optimized build | PASS, Rust web-release 6m56s followed by configured `wasm-opt -Oz`; Trunk success in `build.log` |
| Packaged WASM | 23,480,217 bytes; SHA-256 `029d1e23bb231c307c4d51e3ffafc7cd92052edf35833e3e38bb95b9b0ebc757` |
| Pre-packaging WASM | 28,210,786 bytes; SHA-256 `2cebbe07c1e46cd0ef52b9532c3408f147143da457f51228a0c8ae6e03f8ca10` |
| Native fixture | 268-byte ZIP; SHA-256 `899204d7ab596e9efd9d86df7935474ef15df0bc2cbb80a8798ad8ce102b3d8a`; empty synthetic page |
| Open | `figcraft:ready` version `0.10.0`; host sent `figcraft:open`; FigCraft rendered `GR-048 synthetic`, page `GR-048 page`, clean |
| Visible engine edit | R tool and UI pointer events created a 280×180 rectangle; app rendered it and emitted `dirty=true` |
| Save before ACK | Ctrl+S emitted `figcraft:save`, ticket `figcraft:1`, name `synthetic.figcraft`, `saveAs:false`, 3,464 bytes; dirty remained true |
| Captured save hash | SHA-256 `aacce408951c464cc453b33be53280069cca7dfcf52b65c0e961bb2e93ac8ca0`, computed in browser |
| Matching synthetic ACK | `gr048.ack()` sent `figcraft:saveResult {ticket:'figcraft:1',ok:true}`; editor then emitted `dirty=false` |
| Fresh iframe | `gr048.reopen()` removed generation 1 and created generation 2; received ready/clean messages and visibly rendered the rectangle from captured in-memory bytes |
| HTTP / browser | Host, fixture, index, JS and WASM returned 200; fresh iframe loaded a new index (200) and reused JS/WASM after HTTP 304 revalidation (browser snapshot exposes effective 200). Browser-fetch response-body hashes match disk artifacts. WebGL2/SwiftShader used. |

Evidence: [browser transcript](reviews/GR-048/runtime/browser-evidence.json),
[visible edit](reviews/GR-048/runtime/figcraft-visible-edit.png),
[fresh reopen](reviews/GR-048/runtime/figcraft-reopen.png),
[HTTP log](reviews/GR-048/network.log),
[artifact hashes](reviews/GR-048/artifacts.txt).
Build warnings concern missing optional `craft-fonts`, unused code/imports;
browser warnings concern preload integrity, software rasterizer and unimplemented
system-theme viewport command. No runtime error occurred in the positive flow.

### Browser reproduction

Run [commands.sh](reviews/GR-048/commands.sh), then use T3 `preview_status` and
`preview_open` if needed, followed by navigation to the loopback host URL. The
recorded viewport was 1440×1050 CSS pixels. Click the canvas (parent coordinates
650,620), press R, and evaluate [draw.js](reviews/GR-048/runtime/draw.js) through
T3 `preview_evaluate`. These dispatched UI pointer/mouse events enter eframe's
normal input path; they do not edit saved bytes or inject an engine substitute.
Press Ctrl+S. Inspect `gr048.dirty === true` and the captured ticket/size/hash.
Evaluate `gr048.ack()`, wait for `dirty=false`, then evaluate `gr048.reopen()`.
After generation 2 is ready/clean, inspect the visible rectangle and run
`gr048.verify()` (throws unless the recorded transport lifecycle is complete).
The visual screenshot check is separate from that transport assertion.
Retained-record check: `python3 docs/reviews/GR-048/check_evidence.py` passes;
source and lab `git diff --check` pass.

Initial preview setup attempted `about:blank`, which this tool rejected as an
invalid URL, then contacted the loopback port before its server started and
received `net::ERR_CONNECTION_REFUSED`. These setup failures preceded the
successful run and are not omitted from the retained browser network history.

## Scope and limits

The host [harness](reviews/GR-048/runtime/host.html) checks same-origin and the
current iframe source, supplies a deterministic native ZIP
[fixture](reviews/GR-048/runtime/synthetic.figcraft), retains outbound serialized
save bytes only in page memory, holds ACK for observation, and sends the exact
matching ticket only when explicitly invoked. Reopen destroys the old iframe
and supplies those captured bytes to a new FigCraft instance. An ACK here
means receipt by a synthetic page, with no durable-storage claim.

Wrong-origin/source attacks, malformed or negative ACKs, concurrent edits,
120-second missing-ACK handling, deployment and Seafile dispatcher integration
are outside this bounded positive smoke. No manual download/upload counts as
a save. The stored accepted GR-019 patch remains unchanged. This task left its
lab documentation uncommitted for parent review, as requested; integration
into the lab's main branch is recorded in project history and review queue.

## Independent free review

Nemotron Ultra high returned **PROVISIONAL PASS**, no BLOCKER/MAJOR. Its MINOR
observations concern the disclosed build/browser warnings and initial setup
failures; no app or accepted-patch change was requested. The review record
includes clarifications for the final matrix row 11.9, setup-error retention,
and the unverified pre-existing status of warnings. See
[review R1](reviews/GR-048/INDEPENDENT-REVIEW-R1.md). This is not a GPT REVIEW
PASS; GR-048 stays **GPT REVIEW PENDING**.
