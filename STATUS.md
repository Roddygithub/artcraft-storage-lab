# STATUS

```text
PHASE:      Phase 0 — OpenCode routing & bootstrap
BRANCH:     main
SHA:        (see git log)

OWNER:      artcraft-owner            (openrouter/minimax/minimax-m3.1-flash:free#max)
ARCHITECT:  artcraft-architect        (nvidia/z-ai/glm-5.3#thinking)
IMPLEMENTER:artcraft-worker           (nvidia/z-ai/glm-5.3-flash#thinking)
REVIEWER:   artcraft-reviewer         (nvidia/nvidia/nemotron-3-ultra-550b-a55b#high)

FREE REVIEW: PENDING
GPT REVIEW:  PENDING

CURRENT GR: GR-001 (research in progress)

BLOCKERS:
- none yet

NEXT:
- GR-001  research the real Seafile <-> ONLYOFFICE online-editor contract
- GR-002  determine the correct Seafile integration point
- GR-003  audit Web/WASM/host capabilities of the 13 Craft apps
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

| GR | Title | Free review | GPT review |
| --- | --- | --- | --- |
| GR-001 | Seafile online-editor integration contract | PENDING | PENDING |
| GR-002 | Seafile integration point | PENDING | PENDING |
| GR-003 | ArtCraft Web capability matrix | PENDING | PENDING |
| GR-004 | Common Craft Web Host Contract | PENDING | PENDING |
| GR-005 | First host-integration technical proof | PENDING | PENDING |
| GR-006 | WordCraft Seafile MVP | PENDING | PENDING |
| GR-007 | Save protocol | PENDING | PENDING |
| GR-008 | Data integrity and conflicts | PENDING | PENDING |
| GR-009 | Web integration security | PENDING | PENDING |
| GR-010 | GridCraft Seafile integration | PENDING | PENDING |
| GR-011 | DeckCraft Seafile integration | PENDING | PENDING |
| GR-012 | Non-office Craft integration | PENDING | PENDING |
| GR-013 | ArtCraft upstream RFC | PENDING | PENDING |
| GR-014 | First ArtCraft upstream patch | PENDING | PENDING |

## Environment notes

| Item | Value |
| --- | --- |
| OpenCode | v2.1.0 |
| Agent definitions | `config/opencode/agents/` → installed to `~/.config/opencode/agents/` |
| Seafile test host | `svc-seafile-host.tailb64fb1.ts.net` (read-only inspection so far) |
| Seafile local install | none on this workstation — Seafile is remote |
| ArtCraft apps on this machine | 13 `*-bin` AUR packages installed (native Rust/egui, **no webview**) |
| Production ONLYOFFICE | **untouched** |

## Key early findings

1. **ArtCraft is native, not web.** The baseline audit (`~/ArtCraft-Audit.md`) states
   the 13 apps are **Rust only, egui/eframe + wgpu, explicitly not Tauri/Electron/webview**.
   The CI gate mentions `wasm`, so some crates may already target WASM.
   => Whether usable "Craft Web" editors exist **today** is the pivotal open
   question of GR-003, and it may change the project plan.
2. **Seafile reference is remote.** No local Seafile/Docker runtime on this
   workstation; the integration test bed is the remote server.
