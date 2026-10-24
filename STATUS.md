# STATUS

```text
PHASE:      GPT-6.1 Sol FAIL on 0edbe52; GR-016 all-app seam audit and Rust transport prototype in progress
BRANCH:     main
LAST REVIEWED SHA: 0edbe524b4fa321b0f73f8601afef390e7f785e6
CURRENT CANDIDATE: local remediation after 0edbe52; current tip is not frozen or reviewed
WORKTREE:   GR-016 docs are modified locally; Rust prototype lives only in scratch clones
LUNA AUDIT: docs/reviews/GPT-LUNA-AUDIT.md (implementation/docs through 71a7d82)

OWNER:      artcraft-owner            (nvidia/z-ai/glm-5.3-flash#thinking)
            -- MiniMax free was RETIRED during GR-012; see docs/AI-ROUTING.md --
ARCHITECT:  artcraft-architect        (nvidia/z-ai/glm-5.3#thinking)
IMPLEMENTER:artcraft-worker           (nvidia/z-ai/glm-5.3-flash#thinking)
REVIEWER:   artcraft-reviewer         (nvidia/nvidia/nemotron-3-ultra-550b-a55b#high)

FREE REVIEW: PASS (2 rounds, both remediated) — see docs/reviews/REVIEW-0*.md
GPT REVIEW:  FAIL (GPT-6.1 Sol; original c76a7594cc43ba2a6cf56de2232836f008a97863,
             d9ef476e6fbcb04c9a9e23cfe235812167d1f27c, and
             afec19e63a6a4faec8a94f93651363dbe007e526, and
             0edbe524b4fa321b0f73f8601afef390e7f785e6)

CURRENT GR: GR-016 — all 13 app seams inventoried; WordCraft/GridCraft synthetic-host round trips and GridCraft host-driven in-app Open pass; two GridCraft issues remediated and independently passed by Sol low with minor notes; project GPT status remains FAIL

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
- ONLYOFFICE edit/save/version/reopen regression remains NOT VERIFIED; this is
  a non-regression check, not a change to the ArtCraft target
- GridCraft's ticketed acknowledgement patch received an independent narrow
  review PASS with three minor follow-ups. Its Seafile runtime path is now
  reproduced in the isolated synthetic stack; formula recalculation, GridCraft
  conflict behavior, and deployment security remain NOT VERIFIED.
- GR-012 VectorCraft SVG has a reproduced synthetic Seafile click/edit/save/version/history/reopen flow; it uses VectorCraft's page API, not the common `?host=parent` contract. The 13-app source seam inventory is now recorded in GR-016, but runtime coverage remains limited to the documented WordCraft, GridCraft and VectorCraft flows.
- Sol low's interim review found a possible 32-bit fingerprint collision in VectorCraft polling. The host now compares exact serialized bytes; the focused synthetic Chromium collision test passes, and the isolated Seafile-backed VectorCraft flow was rerun successfully after the fix (695 B saved/read back byte-identically and reopened with the new path). See the GR-012 post-fix runtime report.
- Nemotron independently returned a bounded PASS for that exact-byte fix. A later synthetic Chromium test now verifies failed-write retry; VectorCraft still lacks a full dirty signal, concurrent-save coverage and CSP/sandbox controls. This does not establish common-contract support or an overall project PASS.
- the first E2E browser run used a same-origin proxy; a separate-origin loopback
  follow-up now verifies the handoff and durable save, but production TLS,
  reverse-proxy behavior, CSP, CSRF, rate limits and adversarial-frame isolation
  remain NOT VERIFIED
- public deployment is NOT READY; upstream remains LOCKED

NEXT:
- commit and push the independently reviewed GR-016 evidence to main; keep the
  bounded review's minor notes and Seafile/remaining-app gaps visible
- the Chromium tests use synthetic `sessionStorage`, not Seafile, and the app
  dependency is still a temporary local path
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
| Craft web builds | fetched with `scripts/fetch-craft-web.sh` into `integration/static/` (gitignored) |
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
