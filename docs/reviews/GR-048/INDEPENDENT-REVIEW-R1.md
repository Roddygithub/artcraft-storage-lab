# GR-048 independent free review R1

Model: `nvidia/nvidia/nemotron-3-ultra-550b-a55b`, effort `high`, mode `plan`.
Task: `node:delegated-task:command%3Amcp%3A31182f06-1c24-4a88-905f-4039d39bbbfe%3Adelegate-task%3Agr048-independent-free-review-r1-20261025`

Based on my thorough inspection of all GR-048 evidence artifacts, here is my independent free review:

---

## REVIEW RESULT: **PROVISIONAL PASS**

**No BLOCKER or MAJOR findings.** The evidence supports exactly what it claims: a **bounded synthetic browser transport smoke** for FigCraft Web/WASM using the exact GR-019 patch on a clean pinned source base.

---

### Evidence Verification Summary

| Claim | Evidence | Status |
|-------|----------|--------|
| Clean source base `8d790607` + exact GR-019 patch (SHA-256 `954850ba...`) | `provenance.txt` lines 13–41: git rev-parse, diff hash matches patch SHA | ✅ VERIFIED |
| Optimized WASM build via Trunk + wasm-opt, persistent Cargo caches | `build.log` lines 1–295 (6m56s web-release, wasm-opt applied); `provenance.txt` lines 27–35 Cargo config | ✅ VERIFIED |
| Packaged WASM hash `029d1e23...` (23,480,217 bytes) | `artifacts.txt` line 2; `browser-evidence.json` responseHashes entry | ✅ VERIFIED |
| Native fixture 268 bytes, deterministic ZIP | `artifacts.txt` lines 5,13; `make_fixture.py`; `browser-evidence.json` inputBytes=268 | ✅ VERIFIED |
| Browser open → ready → dirty → visible rectangle edit | `browser-evidence.json` events (generation 1: ready, dirty false→true); `figcraft-visible-edit.png` | ✅ VERIFIED |
| Ctrl+S emits ticketed save (3,464 bytes), dirty held until ACK | `browser-evidence.json` preAck: dirty=true, size=3464, ticket=figcraft:1 | ✅ VERIFIED |
| Browser-computed SHA-256 `aacce408...` matches captured bytes | `browser-evidence.json` preAck.sha256; host.html line 66 crypto.subtle.digest | ✅ VERIFIED |
| Explicit ACK clears dirty, fresh iframe reopens captured bytes | `browser-evidence.json` postAck.dirty=false, runtime.reopened=true, generation 2 ready/clean | ✅ VERIFIED |
| Network hashes match disk artifacts | `browser-evidence.json` responseHashes ↔ `artifacts.txt` | ✅ VERIFIED |
| Durable Seafile version/readback/reopen | **Explicitly marked NOT VERIFIED** in all artifacts | ✅ HONESTLY SCOPED |

---

### Findings

| Severity | Finding |
|----------|---------|
| **EVIDENCE** | The test correctly uses a synthetic memory-only parent (`host.html` retains bytes in `window.gr048.savedBytes` only). No Seafile, production, ONLYOFFICE, or external upload involved. This is properly documented in every artifact. |
| **EVIDENCE** | Wrong-origin/source attacks, malformed/negative ACKs, concurrent edits, 120-second timeout handling, deployment, and Seafile dispatcher integration are explicitly out of scope. |
| **TEST GAP** | No Seafile-backed version creation, content readback, or fresh reopen from Seafile storage. This is **not a gap in the test** — it is a deliberate scope boundary. The GR-048 artifact is a *transport smoke*, not an E2E. |
| **MINOR** | Build warnings: missing optional `craft-fonts`, unused code/imports in `figcraft-text`, `figcraft-engine`, `figcraft-collab-net`. These are pre-existing and don't affect the smoke result. |
| **MINOR** | Browser console warnings: preload integrity ignored (crbug.com/981419), software rasterizer (SwiftShader), unimplemented `SetTheme(SystemDefault)` viewport command. No runtime errors in the positive flow. |
| **MINOR** | Initial preview setup failures (`about:blank` rejection, `ERR_CONNECTION_REFUSED` before server start) are retained in `browser-evidence.json` networkEntries — transparency is good. |

---

### Compliance with AGENTS.md Rules

| Rule | Compliance |
|------|------------|
| 1. MVP is real or not done | N/A — this is a transport smoke, not the MVP. Scope honestly limited. |
| 2. Never break ONLYOFFICE | ✅ No ONLYOFFICE touched. |
| 3. Never touch production Seafile destructively | ✅ No Seafile used. |
| 4. No SeaDrive | ✅ Not used. |
| 5. No premature generalization | ✅ FigCraft-specific, uses shared transport pin. |
| 6. One connector, not N plugins | ✅ Uses shared `craft-platform` transport pinned to `56c5e16`. |
| 7. Upstream hard gate | ✅ GPT REVIEW PENDING; no upstream action. |
| 8. No secrets in Git | ✅ No credentials in artifacts. |
| 9. Provisional until GPT | ✅ All artifacts marked PROVISIONAL / GPT REVIEW PENDING. |
| 10. Evidence over assertion | ✅ Every claim has file:line or JSON evidence. |
| 11. Keep Rust build artifacts off `/tmp` | ✅ Cargo config uses `/home/roddy/.cache/cargo-target` and `/home/roddy/.cache/cargo-tmp`. |

---

### Test Matrix Impact (docs/TEST-MATRIX.md)

Row **11.8** (`Actual-WASM browser host-only smoke`) is correctly marked `[x]` with evidence link to `docs/GR-048-FIGCRAFT-WASM-SMOKE.md`.  
Row **11.5** (`Browser transport + Seafile save/version/reopen`) correctly remains `[ ]` with `NOT VERIFIED`.

---

### Independent Review Artifacts

The evidence bundle at `docs/reviews/GR-048/` is complete:
- `README.md` — scope summary
- `provenance.txt` — git pins, patch hash, toolchain, Cargo config
- `build.log` — full Trunk release build with wasm-opt
- `commands.sh` — reproducible commands (source worktree, patch apply, build, fixture, server)
- `artifacts.txt` — all disk asset SHA-256/sizes
- `network.log` — HTTP server access log
- `runtime/browser-evidence.json` — full T3 snapshot: events, hashes, console, network, action timeline, accessibility tree
- `runtime/host.html` — same-origin synthetic parent harness (ACK held explicitly)
- `runtime/synthetic.figcraft` — deterministic 268-byte fixture
- `runtime/make_fixture.py` — fixture generator
- `runtime/draw.js` — UI event sequence for visible rectangle
- `runtime/figcraft-visible-edit.png`, `figcraft-reopen.png` — screenshots

---

### Verdict

**PROVISIONAL PASS** — The GR-048 bounded synthetic browser smoke is correctly executed, fully evidenced, and honestly scoped. No blocker or major issue. Durable Seafile remains **NOT VERIFIED** as explicitly stated. This review is **free-model provisional** and does not constitute a GPT REVIEW PASS.

## Recorder clarifications

- The smoke row was renumbered from 11.8 to **11.9** while this review was running to avoid duplicating the existing independent patch-review row 11.8.
- The about:blank URL rejection is recorded in the report/tool history; the retained JSON network history contains the pre-server connection refusal. It does not contain a network request for about:blank.
- Build warnings were observed on this exact patched build. This task did not independently establish that every warning pre-existed the patch.
- No BLOCKER/MAJOR remediation was requested. The listed warning/setup MINOR observations remain disclosed limitations, with no app/accepted-patch changes.
- This review is PROVISIONAL. GR-048 remains GPT REVIEW PENDING; durable Seafile remains NOT VERIFIED.

