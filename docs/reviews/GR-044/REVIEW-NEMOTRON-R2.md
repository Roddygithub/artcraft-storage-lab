# GR-044 Independent Second Review — Nemotron 3 Ultra

**Date:** 2026-10-25
**Reviewer:** artcraft-reviewer (Nemotron 3 Ultra 550B A55B, high)
**Scope:** `docs/GR-044-DECKCRAFT-WASM-SMOKE.md`, `docs/reviews/GR-044/` (corrected artifacts post-R1 remediation)
**Verdict:** **PROVISIONAL PASS** (bounded browser runtime smoke only)

---

## Summary of Verified Evidence (Re-validated Post-Remediation)

| Artifact | Claimed SHA-256 (README) | Actual SHA-256 | Match |
|---|---|---|---|
| `runtime/host.html` | `a58f83d85e85cdab72b8340a0e04a0d5bb89a6a26dc7d529969dcf86e7337b6b` | `a58f83d85e85cdab72b8340a0e04a0d5bb89a6a26dc7d529969dcf86e7337b6b` | ✅ |
| `runtime/make_fixture.py` | `b10e5c99acfd45c7b610bee21735a94c8a71e60c35ea2858d3580c439c2baf69` | `b10e5c99acfd45c7b610bee21735a94c8a71e60c35ea2858d3580c439c2baf69` | ✅ |
| `runtime/synthetic.pptx` | `c06d0e05220a380b595a5ca1cfe14d3f556c772102271b4656e5d308f32eea5c` | `c06d0e05220a380b595a5ca1cfe14d3f556c772102271b4656e5d308f32eea5c` | ✅ |
| `runtime/saved.pptx` | `ce01fb7cd7819f5ee6e67c67d77aeda19829e431a2cf92bdfe396b7d76b09376` | `ce01fb7cd7819f5ee6e67c67d77aeda19829e431a2cf92bdfe396b7d76b09376` | ✅ |
| `runtime/deckcraft-host-reopen.png` | `ad7f5bb23798b640fca0f266fd516f50586f739fc93d2e4ced86bcaa2987cdea` | `ad7f5bb23798b640fca0f266fd516f50586f739fc93d2e4ced86bcaa2987cdea` | ✅ |
| `README.md` (bundle index) | `726db1c4d035b75eb637691ba3150d9da11867b8a760905e80bb82dadd945ae3` | `726db1c4d035b75eb637691ba3150d9da11867b8a760905e80bb82dadd945ae3` | ✅ |

**Fixture generation:** `python3 make_fixture.py` → deterministic 4,700-byte `synthetic.pptx` ✅
**Saved payload inspection:** `saved.pptx` slide XML contains `<a:t>gr044runtimeeditpassed</a:t>` ✅
**Hash consistency:** `saved.pptx` SHA-256 matches browser-computed hash in evidence (`ce01fb7...`) ✅

**Host protocol (`host.html`):**
- Same-origin `postMessage` with transferable `ArrayBuffer` for `deckcraft:open` ✅
- Origin + source validation on all inbound messages ✅
- Handles both `ArrayBuffer` and `Uint8Array` save payload shapes defensively ✅
- Computes SHA-256 via `crypto.subtle.digest` ✅
- **Stores captured bytes in parent page memory (`savedBytes` variable), not `sessionStorage`** ✅ (corrected post-R1)
- Returns `deckcraft:saveResult {ticket, ok:true}` with identical ticket ✅
- Fresh iframe reopen loads captured bytes via new `deckcraft:open` ✅
- No Seafile, gateway, or dispatcher code paths exercised ✅

**TEST-MATRIX.md updates (section 4 — DeckCraft):**
| Test | Status | Notes |
|---|---|---|
| 4.1 Open synthetic PPTX | `[x]` (GR-044) | Actual patched WASM in Chromium |
| 4.2 Edit slide | `[x]` (GR-044) | Visible text change, `dirty=true` observed |
| 4.3 Save → new Seafile version | `[ ]` NOT VERIFIED | Correctly bounded |
| 4.4 Reopen from Seafile | `[ ]` NOT VERIFIED | Correctly bounded |
| 4.5 Synthetic host save acknowledgement | `[x]` (GR-044) | 7,297 bytes, ticket `deckcraft:1`, ACK, clean, fresh iframe reopen |

---

## R1 Finding Resolution Check

| R1 Finding | Status in R2 Artifacts | Verified |
|---|---|---|
| R1 incorrectly stated host used `sessionStorage` for byte retention | **Corrected** — `host.html` lines 33, 41, 75 show `savedBytes` kept in page memory; no `sessionStorage` API calls present | ✅ |
| README now states "parent retains bytes only in browser page memory (`savedBytes`)" | **Confirmed** — README line 43 matches implementation | ✅ |
| Browser smoke repeated after correction | **Confirmed** — identical 7,297-byte payload, same SHA-256 `ce01fb7...`, same ACK/reopen screenshot hash | ✅ |
| Patch file not in GR-044 bundle | **Unresolved by design** — still referenced only by SHA-256 (`8d7f9846...`), not archived here | ⚠️ Stated limitation |
| Build logs not retained | **Unresolved by design** — claimed PASS but no logs in evidence | ⚠️ Stated limitation |
| No automated browser test script | **Unresolved by design** — manual Chromium interaction only | ⚠️ Stated limitation |
| Screenshot not visually inspectable by text-only reviewer | **Inherent limitation** — hash verified, content not | ⚠️ Stated limitation |
| Checkout pins / patch application not independently verifiable | **Unresolved** — cache directory not in bundle | ⚠️ Stated limitation |

All R1 findings have been addressed or remain explicitly bounded as documented. No new regressions introduced by the `sessionStorage` → page-memory correction.

---

## Claims Verified Within Stated Boundaries (Re-confirmed)

1. **Actual patched DeckCraft WASM loaded in Chromium** — supported by runtime artifacts and host harness loading `deckcraft/index.html?host=parent&webgl&blank` from Trunk-built bundle.
2. **Synthetic PPTX opened, edited, dirty=true observed** — consistent with host `deckcraft:dirty` handling and edit text appearing in saved payload.
3. **Ctrl+S emitted `deckcraft:save` with 7,297 bytes, ticket `deckcraft:1`** — captured `saved.pptx` is exactly 7,297 bytes; host echoes received ticket.
4. **Matching positive ACK returned, editor became clean** — host returns `ok:true` with same ticket; host observes `dirty=false` on reopen.
5. **Fresh iframe reopened captured bytes with edit intact** — reopen path loads `savedBytes` from page memory; `saved.pptx` contains the edit.
6. **No Seafile / ONLYOFFICE / dispatcher / production path exercised** — explicitly confirmed by host implementation (bytes stay in parent page memory).

---

## Unproven / Not Verified Claims (Explicitly Bounded — Unchanged from R1)

| Claim | Status | Reason |
|---|---|---|
| Local patched checkout matches DeckCraft pin `0f4fffcf6c71ffa16029d07ac23752fedd783547` | **NOT VERIFIED** | Cache directory not in evidence bundle |
| `cargo +1.95.0 build -p deckcraft-web --release --target wasm32-unknown-unknown --locked` passed | **NOT VERIFIED** | No build logs in evidence |
| `RUSTUP_TOOLCHAIN=1.95.0 trunk build --release` passed with `-Oz` | **NOT VERIFIED** | No Trunk output in bundle |
| GR-020 patch SHA-256 `8d7f9846...` applies cleanly to pinned source | **NOT VERIFIED** | Patch file not in evidence bundle |
| Chromium manual steps occurred as described | **NOT VERIFIED** | Only screenshot and saved artifact; no automated script or video |
| Font fallback did not affect open/edit/save/reopen | **NOT VERIFIED** | Stated as observation; no comparative test |

These limitations are **explicitly acknowledged** in the evidence documents. The review does not penalize stated boundaries.

---

## No Blocker or Major Findings (Re-confirmed)

- All artifact hashes are internally consistent (including refreshed `host.html` and `README.md`).
- The synthetic host correctly implements the `deckcraft:` message protocol with security checks (origin + source validation).
- The saved payload is byte-for-byte identical to what the host captured and hashed.
- The TEST-MATRIX correctly marks Seafile version creation and Seafile-backed reopen as `[ ]` NOT VERIFIED.
- No upstream changes, no production Seafile/ONLYOFFICE contact, no secrets in artifacts.
- The evidence bundle is self-contained and reproducible (fixture generator included).
- R1 `sessionStorage` error has been fully corrected in both implementation and documentation.

---

## Minor Observations (Non-Blocking, Consistent with R1)

1. **Manual-only browser run** — Relies on manual Chromium interaction. No Playwright/WebDriver script for CI reproducibility. Consistent with "smoke" scope but limits regression utility.
2. **Patch file not archived** — GR-020 patch SHA-256 referenced but not included in `docs/reviews/GR-044/`. For full reproducibility, the exact patch should be stored alongside evidence.
3. **Build logs absent** — Cargo/Trunk build success claimed but not evidenced. Build log artifact would strengthen "actual patched WASM" claim.
4. **Screenshot not human-inspectable by reviewer** — PNG hash matches; visual confirmation of editor state (clean, edit visible, ticket/hash displayed) cannot be performed by text-only model.
5. **Checkout/binary provenance chain not closed** — The WASM SHA-256 (`eebe27c9...`) is claimed but the built artifact is not in the bundle; the pin-to-WASM chain relies on unretained build logs.

---

## Verdict

**PROVISIONAL PASS** for the **bounded claim**:

> The GR-020 DeckCraft host-save adapter, when built from the pinned source with the GR-020 patch applied, loads as actual WASM in Chromium, opens a synthetic PPTX from a same-origin parent, accepts a visible text edit, serializes and emits save bytes over `postMessage`, receives a matching positive `saveResult`, transitions to clean state, and reopens the captured bytes in a fresh iframe with the edit intact.

**This does not verify:**
- Seafile version creation, Seafile-backed reopen, dispatcher integration, production deployment, ONLYOFFICE regression, cross-origin security, optimized bundle (`wasm-opt -Oz`), or any server-side persistence.
- The local checkout/build/patch chain (pins, logs, patch application) — these remain claims without independent evidence in this bundle.

**Per project rules:** All free-model verdicts are `PROVISIONAL`. Final disposition requires `GPT REVIEW PASS`. Upstream publication remains **LOCKED**.

---

## Reviewer Independence Statement

This review was conducted by reading only the artifacts in `docs/reviews/GR-044/` and `docs/GR-044-DECKCRAFT-WASM-SMOKE.md`. No implementation code was modified. The reviewer did not participate in the original implementation or the R1 remediation.

**Reviewer:** Nemotron 3 Ultra (artcraft-reviewer)
**Date:** 2026-10-25
**Evidence bundle:** `docs/reviews/GR-044/`