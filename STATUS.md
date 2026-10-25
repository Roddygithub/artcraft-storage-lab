# STATUS

```text
PHASE:      GPT-6.1 Sol INCOMPLETE on 95d8983; remediation continues on local main
BRANCH:     main
LAST REVIEWED SHA: 95d89835b2b1d06fd098c586469ed03b8fd0549e
CURRENT CANDIDATE: remediation after reviewed 95d8983; later changes include GR-038/039 and are not project-level GPT-reviewed
WORKTREE:   main-only workflow; GR-048 FigCraft browser smoke completed from isolated worktree based on main `32069b9`; DesignCraft, DeckCraft and FilmCraft patches are repinned/reviewed; GR-024 malformed-ACK transport fix is pushed at 56c5e16; EffectCraft exact patch is pinned, built and independently reviewed; SoundCraft GR-025 replacement guard is source-reviewed; GR-027/028/029 compatibility slices passed bounded reviews; GR-030 browser smoke passed with an in-memory parent; GR-031 reproduced SoundCraft Seafile save/version/readback/fresh reopen on an isolated synthetic stack; GR-033/035 reproduced PhotoCraft browser host flow; GR-036 reproduced PhotoCraft Seafile version/readback/fresh reopen on the isolated synthetic stack; GR-038 safely stages hash-pinned Web assets; GR-039 CSP enforcement has GR-042 browser coverage; GR-041 bounds staged Craft Web ZIP download/extraction; GR-043 covers expired-session save refusal; GR-044 through GR-048 cover DeckCraft, DesignCraft, EffectCraft, FilmCraft and FigCraft host-save browser runtime; no upstream changes
LUNA AUDIT: docs/reviews/GPT-LUNA-AUDIT.md (implementation/docs through 71a7d82)

OWNER:      artcraft-owner            (nvidia/z-ai/glm-5.3-flash#thinking)
            -- MiniMax free was RETIRED during GR-012; see docs/AI-ROUTING.md --
ARCHITECT:  artcraft-architect        (nvidia/z-ai/glm-5.3#thinking)
IMPLEMENTER:artcraft-worker           (nvidia/z-ai/glm-5.3-flash#thinking)
REVIEWER:   artcraft-reviewer         (nvidia/nvidia/nemotron-3-ultra-550b-a55b#high)

FREE REVIEW: PASS (2 rounds, both remediated) — see docs/reviews/REVIEW-0*.md
GPT REVIEW:  INCOMPLETE (GPT-6.1 Sol on 95d8983; earlier frozen candidates FAIL:
             c76a7594cc43ba2a6cf56de2232836f008a97863,
             d9ef476e6fbcb04c9a9e23cfe235812167d1f27c, and
             afec19e63a6a4faec8a94f93651363dbe007e526, and
             0edbe524b4fa321b0f73f8601afef390e7f785e6)
FIRST-PASS:   docs/reviews/GPT-FIRST-PASS-95D8983.md

CURRENT GR: GR-051 — loopback Chromium post-commit response-loss/retry proof
based on 5a1ceb66; synthetic editor (not actual WASM), FakeSeafile (not
real). First fetch fails/ticket-1 negative/dirty; user retry ticket-2 returns
receipt HTTP 200 with one fake write; editor and host confirm clean. GR-049/050
and gateway checks pass. Independent R1 bounded review: PROVISIONAL PASS, no
blocker/major; two P3 wording corrections closed. GPT REVIEW PENDING.
Upstream response loss before gateway receipt and real Seafile MVP NOT VERIFIED.
No production code changes or project-level GPT PASS.
See `docs/GR-051-BROWSER-SAVE-RETRY.md` and `docs/reviews/GR-051/`.

PREVIOUS GR: GR-050 — loopback HTTP post-commit response-loss proof;
independent R1 bounded review PROVISIONAL PASS. See `docs/reviews/GR-050/`.

PREVIOUS GR: GR-049 — gateway last-successful-save receipt implemented;
6 focused retry tests and existing gateway checks pass. Independent R1 bounded
review is PROVISIONAL PASS, no findings. Actual network-loss/browser/Seafile
runtime NOT VERIFIED. GPT REVIEW PENDING; no project GPT PASS.
See `docs/GR-049-IDEMPOTENT-SAVE-RETRY.md` and `docs/reviews/GR-049/`.

PREVIOUS GR: GR-048 — exact GR-019 patched FigCraft built as optimized actual
Web/WASM and passed a bounded synthetic browser open/edit/save/ACK/clean/fresh
iframe reopen smoke. Captured 3,464 bytes under `figcraft:1`; the rectangle
remained visible after reopen. Parent bytes were memory-only. Durable Seafile
version/readback, dispatch and deployment remain **NOT VERIFIED**. GPT REVIEW
PENDING; independent free R1 PROVISIONAL PASS, no blocker/major. No project
GPT PASS. The task worktree was left uncommitted for parent review as requested;
the lab integration is recorded in project history and review queue.
See `docs/GR-048-FIGCRAFT-WASM-SMOKE.md` and `docs/reviews/GR-048/`.

GR-043 — Chromium verifies an expired in-memory gateway session is
refused during save: actual 404 with reopen guidance, dirty preserved,
`saveResult ok:false`, and no fake Seafile write. Real token expiry and Seafile
behavior remain **NOT VERIFIED**. See `docs/GR-043-SESSION-EXPIRY.md`.

GR-042 — Chromium enforces the CSP on the real dynamic `POST /open/`
response using synthetic loopback services: the configured Seafile ancestor is
allowed, a nested foreign ancestor is blocked, nonce script/style execute, and
no CSP violation fires in the allowed host page. Craft bundle, production,
proxy behavior and other browsers remain **NOT VERIFIED**. See
`docs/GR-042-BROWSER-CSP.md` and `docs/reviews/GR-042/`.

GR-041 — Candidate ZIP downloads are capped at 256 MiB with a
30-second socket timeout and 15-minute total deadline; extraction is capped at
1 GiB and 10,000 entries. Eight standard-library tests cover byte/count limits,
ZIP64/multi-disk, duplicate and unsafe paths, symlinks, malformed ZIPs and
timeout behavior. Active static app trees are not touched; host protocol
compatibility remains **NOT VERIFIED**. Independent exact round 3 returned
bounded PROVISIONAL PASS, no blocker/major. See
`docs/GR-038-CRAFT-ASSET-INGESTION.md`.

GR-040 — A real browser regression on the isolated synthetic stack
confirms ONLYOFFICE still edits, saves two Seafile versions, and reopens both
edits from the library file list. Production/deployed ONLYOFFICE and security
remain **NOT VERIFIED**. Independent evidence review: bounded PROVISIONAL
ACCEPT, no blocker/major, three minor limitations; see
`docs/reviews/GR-040/INDEPENDENT-REVIEW-R1.md`. Evidence:
`docs/reviews/GR-040/`.
GR-039 — The `/open/` capability host page sends a fresh nonce-based CSP and
fails closed to `frame-ancestors 'none'` when the configured Seahub origin is
invalid. Gateway unit tests pass; independent exact-patch round 3 returned a
bounded PROVISIONAL PASS. GR-042 adds synthetic Chromium enforcement coverage
on the real route. Static Craft editor HTML, proxy behavior, other browsers and
deployment security remain **NOT VERIFIED**. See `docs/GR-039-HOSTPAGE-CSP.md`,
`docs/GR-042-BROWSER-CSP.md` and their review evidence.

GR-038 — The Web asset fetcher requires an exact release tag and SHA-256,
validates archive paths, and stages under `integration/static/candidates/`
without modifying active builds. A real release artifact passed the staging
check; Luna High bounded re-review returned PROVISIONAL ACCEPT with no material
finding. Host protocol compatibility is **NOT VERIFIED**; staged artifacts are
not approved for promotion. See `docs/GR-038-CRAFT-ASSET-INGESTION.md`.

LATEST E2E: GR-040 confirms synthetic ONLYOFFICE preservation; see
`docs/reviews/GR-040/`. GR-037 PhotoCraft’s editor message, gateway request body, and
Seafile readback matched byte-for-byte (8,555 bytes; SHA-256
`ea0121c1e465c753947005e1ff4452cc031f734baed3345400bcd3a96218c4ca`). History
grew 2→3; a fresh Seahub route opened a new clean editor session. PhotoCraft
remains excluded from dispatch. Cargo build/temp paths use the persistent home
filesystem. Production security, deployed ONLYOFFICE compatibility, optimized output and
project-level GPT PASS remain NOT VERIFIED; details are in `docs/reviews/GR-037/`.

FREE REVIEW: PASS (3 rounds: 01 FAIL->remediated, 02 FAIL->remediated, 03 PASS)
INDEPENDENT REVIEW: Nemotron FAIL on `a4ecc8e` candidate readiness; follow-up
                    two-editor save race reproduced afterward; Nemotron also
                    returned FAIL on `36c0bc0`; see review reports

VERIFIED IN LOCAL REMEDIATION:
- GR-015's synthetic DOCX file-list click → WordCraft edit → durable version →
  close/reopen is REPRODUCED against isolated patched Seahub and C fileserver;
  evidence: `docs/reviews/GR-015/ISOLATED-RUNTIME-E2E-20261023.md`
- a real simultaneous conditional-save request race returned one 200 and one
  409; a fresh WordCraft open rendered the winning writer
- two actual WordCraft sessions also sent Ctrl+S concurrently after different
  edits; one committed, one stayed dirty on 409, and a fresh Seahub click/reopen
  rendered only the committed edit
- a follow-up used separate synthetic loopback origins for Seahub (`:18000`)
  and gateway/Craft (`:18777`); WordCraft saved `OriginCheck`, and a fresh
  route load/readback preserved it. A subsequent fresh gateway session reported
  `Saved — new version`, `dirty=false`, `confirmedSave=true`; a later Seafile
  content readback contained `AckConfirmed`. Synthetic Seahub config was restored.
- GR-010 now has a real GridCraft Web/WASM → isolated Seafile save → new
  committed head acknowledgement → Seahub click/reopen reproduction for a
  synthetic XLSX; the reopened editor showed the saved cell value. Exact hashes,
  screenshot and limitations: `docs/reviews/GR-010/GRIDCRAFT-SEAFILE-E2E-20261023.md`.

OPEN GAPS:
- GR-040 closes ONLYOFFICE regression on the local synthetic patched stack:
  two browser edits, two HTTP-200 callbacks, history 3→5 and a fresh library
  click/reopen showing both edits. Production configuration, deployment
  topology, other Document Server versions and other file types remain
  NOT VERIFIED.
- GridCraft's ticketed acknowledgement patch received an independent narrow
  review PASS with three minor follow-ups. Its Seafile runtime path is now
  reproduced in the isolated synthetic stack; formula recalculation, GridCraft
  conflict behavior, and deployment security remain NOT VERIFIED.
- GR-017 adds a ticketed durable-result adapter to PdfCraft.
  Seven focused native acknowledgement tests, Rust 1.95 WASM check, formatting
  and diff checks pass on the current callback-cap remediation. Sol low rounds
  Sol low round 4 returned bounded PROTOTYPE PASS (no blocker/major; lifecycle
  test coverage remains a minor). A subsequent isolated synthetic Seafile run
  used actual PdfCraft WASM to annotate a PDF, save a new Seafile history
  revision, read back and parse the PDF, and reopen it in a fresh PdfCraft
  instance with the annotation visible. It opened through the direct Seahub file
  route; file-list click and exact outbound payload hash remain NOT VERIFIED.
  Evidence is in `docs/reviews/GR-017/`.
- GR-018 adds ticketed host save acknowledgements to CADCraft in a pinned
  scratch clone. GPT-6.1 Sol low round 4 returned a bounded prototype PASS after
  four rounds of remediation; Rust 1.95 WASM check and 344 engine tests pass.
  A local Chromium synthetic-host smoke now reproduces a real circle edit,
  ticketed 17,504-byte save, SHA-256 of the received message bytes, successful
  ACK, dirty=false, and fresh editor reopen with the circle visible. A second
  run rejected the first save, observed dirty remain true, and accepted a retry.
  A separate isolated synthetic Seafile run used a real Seahub library click,
  saved a circle edit as a new history entry/file ID, and reopened it in a fresh
  CADCraft instance. The Seafile readback hash is recorded; exact
  editor-to-gateway bytes were not captured. The bundle used `wasm-opt=0`, and
  timeout/security paths remain unverified, so this is not publication-ready.
  The stored app patch pins the packaged transport revision and now passes a
  clean Rust 1.95 locked WASM check.
  Evidence is in `docs/reviews/GR-018/`.
- GR-019 adds a local FigCraft Web adapter over the pinned shared transport.
  Three engine snapshot tests and one synthetic-host UI lifecycle test pass;
  Rust 1.95 WASM check and clean-base patch application pass. It is restricted
  to one `.figcraft` file per iframe and refuses host Save As. The patch is not
  in Seafile dispatch. GR-048 now verifies actual-WASM browser transport with
  a synthetic memory-only parent; durable Seafile remains NOT VERIFIED. Sol low
  rounds 1 and 2 found one-document scope bypasses (including duplicate and
  live-session commands) plus a startup-reporting issue. The latest patch
  blocks those dispatches; focused tests/WASM checks pass and Sol low round 3
  returned bounded PASS with one minor dirty-report retry limitation. Seafile
  browser/runtime E2E remains NOT VERIFIED. Details:
  `docs/reviews/GR-019/README.md`.
- GR-020 adds a local DeckCraft Web host-save adapter over the shared transport
  pinned to `56c5e16`. Two engine tests and four UI lifecycle tests pass, as do the Rust
  1.95 app WASM check, `xtask wasm`, `assets`, and `layers`; two independent Luna
  high rounds returned bounded PASS on the current exact patch. Host mode is
  restricted to one document and waits for a ticket-matched durable ACK. GR-044
  verifies actual WASM host messaging in Chromium with an in-memory parent;
  Seafile dispatch/version/reopen remains NOT VERIFIED. The
  full workspace test suite did not complete; `xtask ci` stops at existing
  Clippy findings outside the changed files. See `docs/reviews/GR-020/README.md`.
- GR-021 provides a one-document DesignCraft Web host-save adapter over the
  shared transport at `56c5e16`. Five focused Rust 1.95 tests, the locked WASM
  check, formatting and diff checks pass. Luna high R3 and the independent
  transport re-pin review found no code-level blocker or major on the exact
  patch. A P3 resource limit remains: the 64 MiB outbound guard runs after
  serialization allocation, so it does not bound peak memory for larger
  documents. GR-045 verifies actual-WASM browser open/edit/save/ACK/reopen with
  an in-memory parent; Seafile version/reopen remains NOT VERIFIED. See
  `docs/reviews/GR-021/` and `docs/reviews/GR-045/`.
- GR-024 changes the shared transport parser to ignore malformed save ACKs,
  preserving pending/unknown outcome semantics. The bounded review and package
  checks pass; browser execution was not run. The immutable transport commit is
  `56c5e16d79b77751106173c13111ef4fe0a2c0ec`; active app patches must pin it
  before their final exact-patch review. Evidence:
  `docs/reviews/GR-024/`.
- GR-023 adds a one-document FilmCraft host-save adapter over the pinned
  transport. Engine tests 4/4, UI tests 3/3, locked Rust 1.95 WASM check,
  formatting and diff checks pass after the final host-only `file.closeProject`
  guard. Independent round 2 exact review found no blocker/major. GR-047
  verifies actual patched-WASM browser open/edit/save/ACK/fresh iframe reopen;
  durable Seafile version/reopen remains NOT VERIFIED. See
  `docs/reviews/GR-023/` and `docs/reviews/GR-047/`.
- GR-025 SoundCraft has a ticketed host-save source prototype, and the local
  picker/drop replacement bypass was fixed and independently source-reviewed.
  The Symphonia audio crate now builds/tests on native and WASM (GR-027 exact
  provisional PASS); CPAL playback also checks on native/WASM and has 36 tests
  passing in GR-028, whose independent review found no CPAL API semantic issue
  but could not verify exact applicability or reproduce reported commands.
  GR-029 local egui 0.37 overlays now let the full Web WASM build pass; exact
  review R3 is bounded PROVISIONAL PASS and GPT REVIEW PENDING. The focused
  host-bound UI regression passes. GR-030 now verifies browser messaging and
  memory-backed fresh-iframe reopen; Seafile version/reopen remain NOT VERIFIED.
  Do not add SoundCraft to dispatch. See
  `docs/reviews/GR-025/`, `GR-027/`, `GR-028/`, `GR-029/`.
- GR-030 now exercises that adapter in Chromium: host Open, a real UI track edit,
  Ctrl+S, matching success ACK, clean-state report, and fresh iframe reopen all
  passed against a same-origin in-memory parent. It is not Seafile evidence. The
  66,203,163-byte save is below SoundCraft’s 64 MiB cap but above the gateway’s
  50 MiB default; configure and verify the limit or use a smaller fixture before
  the isolated Seafile run. See `docs/reviews/GR-030/`.
- GR-031 then used a 4,041-byte synthetic `.scraftz` fixture and the existing
  50 MiB gateway ceiling in an isolated rootless Podman Seafile stack. A real
  Seahub file-list click opened SoundCraft Web/WASM; adding `Audio 2` and Ctrl+S
  created a new file ID/head, received host confirmation, and read back 6,877
  bytes. A fresh Seahub click reopened all three tracks with a clean editor.
  Exact editor-to-gateway bytes, optimized WASM, deployment security and
  ONLYOFFICE regression remain NOT VERIFIED. Luna High returned a bounded
  PROVISIONAL PASS with minor evidence gaps; SoundCraft stays out of dispatch.
  Evidence: `docs/reviews/GR-031/`.
- GR-026 now has a bounded core patch for pathless open and revision ACK, with
  per-open incarnation identity to reject ACKs after close/reopen with a reused
  document ID. Independent R2 review is provisional PASS; engine 4/4 pass, UI
  and post-change WASM checks pass. It is not a host adapter: browser
  behavior and Seafile version/reopen remain NOT VERIFIED. See
  `docs/reviews/GR-026/`.
- GR-032 adds a local Rust-only PhotoCraft `?host=parent` adapter on top of that
  core: one pathless `.pcraft`, ticketed File Save, snapshot-specific positive
  ACK, negative/unknown outcome preservation, and host-mode route guards. Final
  locked WASM/UI checks pass. R1’s unbounded ACK inbox and swallowed listener
  failure findings are remediated; R2/R3 independent bounded reviews are
  PROVISIONAL PASS; browser and Seafile version/reopen are NOT VERIFIED. R2 also recorded the 50 MiB gateway
  default versus post-serialization rejection as an unverified size/memory limit.
  See `docs/reviews/GR-032/`.
- GR-033 reproduces PhotoCraft Web/WASM Open → UI layer edit → exact save
  bytes/ticket → matching in-memory ACK → dirty=false → fresh iframe reopen
  path in a same-origin browser. The new layer is visible after reopen. This is
  browser protocol evidence only: the parent holds bytes in page memory, so
  Seafile version/readback, optimized WASM, deployment security and ONLYOFFICE
  regression remain NOT VERIFIED. PhotoCraft remains excluded from dispatch;
  see `docs/GR-033-PHOTOCRAFT-BROWSER-SMOKE.md` and `docs/reviews/GR-033/`.
- GR-034 adds gateway-only `.pcraft` save validation using central-directory
  metadata for exactly one nonempty root `manifest.json`, without decompression.
  Focused gateway unit checks pass, including duplicate/empty manifest cases
  and invalid-save rejection before a fake Seafile call. Nemotron 3 Ultra R2
  returned bounded PROVISIONAL PASS. Seafile runtime was unavailable and not
  accessed; the PhotoCraft dispatch table remains unchanged. See
  `docs/GR-034-PHOTOCRAFT-GATEWAY-VALIDATION.md`.
- GR-035 builds GR-032 with optimized release WASM and reproduces open, edit,
  ticketed save, in-memory ACK, and fresh iframe reopen in Chromium. The saved
  bytes never left the parent page; Seafile persistence/version/reopen remains
  NOT VERIFIED. Nemotron returned bounded PROVISIONAL ACCEPT; screenshot-to-
  WASM-hash binding remains NOT VERIFIED. See
  `docs/GR-035-PHOTOCRAFT-OPTIMIZED-BROWSER-SMOKE.md`.
- The isolated synthetic Seafile runtime flows currently documented are for
  WordCraft, GridCraft, VectorCraft, PdfCraft and CADCraft. VectorCraft uses its
  page API, not the common `?host=parent` contract. DeckCraft now has a local
  host-save adapter but no browser or Seafile runtime reproduction.
- GR-016 WordCraft and GridCraft now both have reproduced shared-transport Seafile save/version/reopen flows on the isolated synthetic stack. GridCraft also recalculated `SUM(B2:B2)` after B2 changed to 1337, persisted a new Seafile version, and reopened showing 1337. GR-018 CADCraft now has a separate synthetic Seafile history/reopen run. Exact outbound-payload hashing and optimized-bundle performance remain open. These synthetic runs do not establish public deployment readiness or all-app support.
- Sol low's interim review found a possible 32-bit fingerprint collision in VectorCraft polling. The host now compares exact serialized bytes; the focused synthetic Chromium collision test passes, and the isolated Seafile-backed VectorCraft flow was rerun successfully after the fix (695 B saved/read back byte-identically and reopened with the new path). See the GR-012 post-fix runtime report.
- Nemotron independently returned a bounded PASS for that exact-byte fix. A later synthetic Chromium test now verifies failed-write retry; VectorCraft still lacks a full dirty signal, concurrent-save coverage and CSP/sandbox controls. This does not establish common-contract support or an overall project PASS.
- the first E2E browser run used a same-origin proxy; a separate-origin loopback
  follow-up now verifies the handoff and durable save, but production TLS,
  reverse-proxy behavior, CSP, CSRF, rate limits and adversarial-frame isolation
  remain NOT VERIFIED
- public deployment is NOT READY; upstream remains LOCKED

NEXT:
- FigCraft and CADCraft are repinned to `56c5e16`; exact bounded repin reviews
  are recorded
- address GR-031's remaining exact-payload provenance, optimized-bundle,
  security and ONLYOFFICE regression gaps before considering SoundCraft for
  dispatch. PhotoCraft now has browser protocol smoke evidence; the next slice
  is isolated Seafile version/readback/fresh reopen, respecting the gateway's
  50 MiB request ceiling and PhotoCraft's post-serialization size check. Neither
  app enters dispatch without browser and Seafile version/reopen evidence
- add any app to Seafile dispatch only after synthetic browser and Seafile
  version/reopen evidence exists
- continue app-by-app adapters from the GR-016 seam inventory; WordCraft,
  GridCraft, PdfCraft and CADCraft now use the immutable packaged transport
  revision and compile from clean pinned-source checkouts with Rust 1.95
- continue from GR-021 to remaining apps; FigCraft and DeckCraft patches are
  local prototypes only until browser and Seafile runtime evidence exists
- retain the limits: WordCraft, GridCraft, PdfCraft and CADCraft have recorded
  clean-checkout build evidence; DeckCraft has a passing local pinned-source
  WASM build, but its full workspace suite did not complete. Other app
  integrations, runtime coverage and deployment controls remain incomplete
- continue remaining Craft Web adapters from the GR-016 per-app seam inventory;
  CADCraft synthetic Seafile save/version/reopen evidence is already recorded
- rerun the Playwright protocol suite when its dependency is available; the
  current T3 Chromium preview verifies Open-request guidance and dirty-state
  preservation only
- continue app-by-app seam implementation and evidence; do not infer all-app support from the WordCraft/GridCraft synthetic Seafile runs
- the standalone GR-016 transport artifact and four exact Git-pinned app patch
  manifests are present; clean-checkout WASM build evidence is recorded; no
  upstream dependency or patch has been published
- keep later app adapters scoped to their observed per-app open/serialize/save
  seams; a common transport does not create an editor serializer or durable ack
- keep Seafile/provider persistence in the connector and editor lifecycle in
  Rust/WASM; do not publish upstream before GPT PASS
- preserve the existing file-type dispatch behavior for out-of-scope libraries;
  that is a compatibility guard, while the product work remains the ArtCraft
  editor integration
- a Django runtime save-route test rejects read-only and revoked cached edit
  capabilities before update-token minting/fileserver access; its Seafile RPC
  permission result is synthetic, so live revocation propagation is not verified
- unsupported stock/Go fileserver rejection and broader authorization tests
  remain open; do not install the patch on the live LXC
- once prototype-critical tests and exact diffs are recorded, freeze a new SHA
  for one cost-bounded independent final review; no Sol call is being made now
- keep upstream publication locked; GPT REVIEW remains FAIL
```

## Verification legend

| Label | Meaning |
| --- | --- |
| `PROVISIONAL — FREE REVIEW PASS` | A free, independent model reviewed it and found no blocker. Not final. |
| `PROVISIONAL — FREE REVIEW FAIL` | A free, independent model found a blocker. Must be remediated. |
| `INDEPENDENT FREE REVIEW PENDING` | No independent reviewer has looked at it yet. |
| `GPT REVIEW PENDING` | Queued for the future GPT review pass. |
| `GPT REVIEW PASS` | Independently verified by GPT. **Only this unlocks upstream publication.** |
| `GPT REVIEW FAIL` | GPT rejected it. Back to remediation. |

## GR tracker

| GR | Title | Artifact | Free review | GPT review |
| --- | --- | --- | --- | --- |
| GR-001 | Seafile online-editor integration contract | `docs/reviews/GR-001/DEPLOYED-INSTANCE-CONTRACT.md` | PASS (remediated, REVIEW-01) | PENDING |
| GR-002 | Seafile integration point | `docs/SEAFILE-INTEGRATION-POINTS.md` | PASS (remediated, REVIEW-01) | PENDING |
| GR-003 | ArtCraft Web capability matrix | `docs/ARTCRAFT-WEB-CAPABILITIES.md` | PASS (remediated, REVIEW-01) | PENDING |
| GR-004 | Common Craft Web Host Contract | `docs/HOST-CONTRACT.md` | PASS (remediated, REVIEW-01) | PENDING |
| GR-005 | First technical proof | `docs/reviews/GR-005/` | PASS (remediated, REVIEW-02) | PENDING |
| GR-006 | WordCraft Seafile MVP | `docs/reviews/GR-006/` | remediation required | FAIL (Sol) |
| GR-007 | Save protocol | `docs/SAVE-PROTOCOL.md` | PASS (REVIEW-03) | PENDING |
| GR-008 | Data integrity and conflicts | `docs/CONFLICTS.md` + `docs/reviews/GR-008/` | remediation required | FAIL (Sol) |
| GR-009 | Web integration security | `docs/SECURITY.md` | remediation required | FAIL (Sol) |
| GR-010 | GridCraft Seafile integration | `docs/reviews/GR-010/README.md` | synthetic Seafile edit/save/version-ack/reopen reproduced; formula recalculation and conflict cases open | FAIL on 0edbe52 |
| GR-011 | DeckCraft Seafile integration | — (needs the upstream bridge) | not started | PENDING |
| GR-012 | Non-office Craft integration | `docs/reviews/GR-012/` | PASS (remediated, REVIEW-04) | PENDING |
| GR-013 | ArtCraft upstream RFC | `docs/RFC-DRAFT.md` | PASS (REVIEW-03) | PENDING |
| GR-014 | First ArtCraft upstream patch | `docs/reviews/GR-014/` | PASS (REVIEW-03) | PENDING |
| GR-015 | Per-library routing and conditional Seafile save | `docs/reviews/GR-015/` | runtime DOCX path and conditional conflict reproduced locally; remaining security/compatibility gaps | FAIL (0edbe52 candidate) |

## What is already true

| Claim | Evidence |
| --- | --- |
| Seafile ships a **generic, configuration-only** hook for third-party online editors | `docs/SEAFILE-INTEGRATION-POINTS.md` §2, `haiwen/seahub` `seahub/thirdparty_editor/` |
| the contract Seafile expects from an external web editor | `docs/reviews/GR-001/DEPLOYED-INSTANCE-CONTRACT.md` |
| Deployed Seafile has no user-bound conditional file-save endpoint; its core does have a transactional branch compare-and-update primitive | `docs/reviews/GR-015/README.md`; exact source SHAs in the bundle |
| **all 13** ArtCraft apps have a browser build; **3** already have a `?host=parent` bridge | `docs/ARTCRAFT-WEB-CAPABILITIES.md` |
| the Craft web apps' host seam is the `Services` struct, and WordCraft's is the richest | `docs/ARTCRAFT-WEB-CAPABILITIES.md` §1 |
| the old GR-005 bundle recorded a browser/gateway save; Sol did not accept it as the Seafile Web DOCX MVP because it bypassed the Seafile file-list click and did not reopen in WordCraft | `docs/reviews/GPT-SOL-FINAL-REVIEW.md` |
| a stale save is **refused**, and the file is left alone | `tests/test_integration.py` §3 |
| the WordCraft host bridge (the GR-014 patch) **compiles** | `docs/reviews/GR-014/` |

## Environment notes

| Item | Value |
| --- | --- |
| OpenCode | v2.1.0, V2 agent format (Markdown + frontmatter, `~/.config/opencode/agents/`) |
| Agent definitions | `config/opencode/agents/` -> installed with `scripts/install-agents.sh` |
| Seafile reference host | `svc-seafile-host.tailb64fb1.ts.net` (LXC 108, Pro 12.0.14) |
| Reverse proxy | Nginx Proxy Manager, LXC 103 |
| ONLYOFFICE | LXC 112, Document Server 24.04, **untouched** |
| Test library | `c82cc792-389d-43e6-b963-0dab1a47a9a8` ("OnlyOffice"), folder `/artcraft-lab/` |
| Gateway | `integration/gateway/`; running in the development workspace only, not installed on LXC 108 |
| Craft web builds | pinned releases are staged under `integration/static/candidates/`; protocol-check before manual promotion |
| Rust toolchain | 1.97.0 + `wasm32-unknown-unknown`; `trunk` 0.22.0 in `~/.local/bin` |
| Browser test | Playwright chromium in `~/.cache/ms-playwright`; a Python venv with `playwright` |
| Live Seafile config | global third-party `.xlsx` route removed; ONLYOFFICE settings untouched; backup at `/root/seahub_settings.py.artcraft-rollback-20261022` on LXC 108 |

## The two decisive early findings

1. **The Craft web apps exist.** The baseline audit was about the desktop packages
   and was silent about the browser builds. The project is therefore *"wire the
   existing editors to a host protocol"*, not *"build editors"*.
2. **A host bridge already exists in three of the thirteen apps**, with a consistent
   vocabulary and a correct security model. The project is therefore *"generalise
   and upstream what is there"*, not *"invent a host API"*.
