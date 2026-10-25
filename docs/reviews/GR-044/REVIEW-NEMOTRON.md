# GR-044 Independent Free Review — Nemotron 3 Ultra

**Date:** 2026-10-25
**Reviewer:** artcraft-reviewer (Nemotron 3 Ultra 550B A55B, high)
**Scope:** `docs/GR-044-DECKCRAFT-WASM-SMOKE.md`, `docs/reviews/GR-044/`
**Verdict:** **PROVISIONAL PASS** (bounded browser runtime smoke only)

---

## Summary of Verified Evidence

| Artifact | Claimed SHA-256 | Actual SHA-256 | Match |
|---|---|---|---|
| `runtime/host.html` | `2a594b6261ab9cffdf9622dd3d364614fd7e76689f2e64c07ddca25669c53f57` | `2a594b6261ab9cffdf9622dd3d364614fd7e76689f2e64c07ddca25669c53f57` | ✅ |
| `runtime/make_fixture.py` | `b10e5c99acfd45c7b610bee21735a94c8a71e60c35ea2858d3580c439c2baf69` | `b10e5c99acfd45c7b610bee21735a94c8a71e60c35ea2858d3580c439c2baf69` | ✅ |
| `runtime/synthetic.pptx` | `c06d0e05220a380b595a5ca1cfe14d3f556c772102271b4656e5d308f32eea5c` | `c06d0e05220a380b595a5ca1cfe14d3f556c772102271b4656e5d308f32eea5c` | ✅ |
| `runtime/saved.pptx` | `ce01fb7cd7819f5ee6e67c67d77aeda19829e431a2cf92bdfe396b7d76b09376` | `ce01fb7cd7819f5ee6e67c67d77aeda19829e431a2cf92bdfe396b7d76b09376` | ✅ |
| `runtime/deckcraft-host-reopen.png` | `ad7f5bb23798b640fca0f266fd516f50586f739fc93d2e4ced86bcaa2987cdea` | `ad7f5bb23798b640fca0f266fd516f50586f739fc93d2e4ced86bcaa2987cdea` | ✅ |

**Fixture generation:** `python3 make_fixture.py` → deterministic 4,700-byte `synthetic.pptx` ✅

**Saved payload inspection:** `saved.pptx` slide XML (`ppt/slides/slide1.xml`) contains `<a:t>gr044runtimeeditpassed</a:t>` ✅
**Hash consistency:** `saved.pptx` SHA-256 matches the browser-computed hash reported in the evidence (`ce01fb7...`) ✅

**Host protocol (`host.html`):**
- Same-origin `postMessage` with transferable `ArrayBuffer` for `deckcraft:open` ✅
- Origin + source validation on all inbound messages ✅
- Handles both `ArrayBuffer` and `Uint8Array` save payload shapes defensively ✅
- Computes SHA-256 via `crypto.subtle.digest` ✅
- Stores captured bytes in `sessionStorage` (browser memory only) ✅
- Returns `deckcraft:saveResult {ticket, ok:true}` with identical ticket ✅
- Fresh iframe reopen loads captured bytes via new `deckcraft:open` ✅
- No Seafile, gateway, or dispatcher code paths exercised ✅

**TEST-MATRIX.md updates (section 4 — DeckCraft):**
- 4.1 Open synthetic PPTX → `[x]` (GR-044) ✅
- 4.2 Edit slide → `[x]` (GR-044) ✅
- 4.3 Save → new Seafile version → `[ ]` **NOT VERIFIED** (correct) ✅
- 4.4 Reopen from Seafile → `[ ]` **NOT VERIFIED** (correct) ✅
- 4.5 Synthetic host save acknowledgement → `[x]` (GR-044) ✅

---

## Claims Verified Within Stated Boundaries

1. **Actual patched DeckCraft WASM loaded in Chromium** — supported by the runtime artifacts and host harness; the harness loads `deckcraft/index.html?host=parent&webgl&blank` from a Trunk-built bundle.

2. **Synthetic PPTX opened, edited, dirty=true observed** — consistent with host `deckcraft:dirty` handling and the edit text appearing in the saved payload.

3. **Ctrl+S emitted `deckcraft:save` with 7,297 bytes, ticket `deckcraft:1`** — the captured `saved.pptx` is exactly 7,297 bytes; the host code echoes the received ticket.

4. **Matching positive ACK returned, editor became clean** — host returns `ok:true` with same ticket; host observes `dirty=false` on reopen.

5. **Fresh iframe reopened captured bytes with edit intact** — reopen path loads `savedBytes` from `sessionStorage`; `saved.pptx` contains the edit.

6. **No Seafile / ONLYOFFICE / dispatcher / production path exercised** — explicitly stated and confirmed by host implementation (bytes stay in `sessionStorage`).

---

## Unproven / Not Verified Claims (Explicitly Bounded)

| Claim | Status | Reason |
|---|---|---|
| Local patched checkout at `/home/roddy/.cache/artcraft-deckcraft-gr020` matches DeckCraft pin `0f4fffcf6c71ffa16029d07ac23752fedd783547` | **NOT VERIFIED** | Cache directory not in evidence bundle; cannot independently verify git HEAD or Cargo.lock |
| `cargo +1.95.0 build -p deckcraft-web --release --target wasm32-unknown-unknown --locked` passed | **NOT VERIFIED** | No build logs in evidence; claim only |
| `RUSTUP_TOOLCHAIN=1.95.0 trunk build --release` from `apps/deckcraft-web` passed with `-Oz` | **NOT VERIFIED** | No build logs; Trunk output not in bundle |
| GR-020 patch SHA-256 `8d7f98468ce446add5357e10ed8e10e729eb3306fee359d320f09805acc3ee4a` applies cleanly to pinned source | **NOT VERIFIED** | Patch file not in evidence bundle; cannot verify application |
| Chromium manual steps (double-click, type, Ctrl+S, click Reopen) occurred as described | **NOT VERIFIED** | Only screenshot and saved artifact exist; no automated test script or video |
| Font fallback (missing `craft-fonts`) did not affect open/edit/save/reopen | **NOT VERIFIED** | Stated as observation; no comparative test with fonts present |

These limitations are **explicitly acknowledged** in the evidence documents. The review does not penalize stated boundaries.

---

## No Blocker or Major Findings

- All artifact hashes are internally consistent.
- The synthetic host correctly implements the `deckcraft:` message protocol with security checks.
- The saved payload is byte-for-byte identical to what the host captured and hashed.
- The TEST-MATRIX correctly marks Seafile version creation and Seafile-backed reopen as `[ ]` NOT VERIFIED.
- No upstream changes, no production Seafile/ONLYOFFICE contact, no secrets in artifacts.
- The evidence bundle is self-contained and reproducible (fixture generator included).

---

## Minor Observations (Non-Blocking)

1. **Manual-only browser run** — The test relies on manual Chromium interaction. No Playwright / WebDriver script is provided for CI reproducibility. This is consistent with a "smoke" scope but limits regression utility.

2. **Patch file not archived** — The GR-020 patch (SHA-256 `8d7f9846...`) is referenced but not included in `docs/reviews/GR-044/`. For full reproducibility, the exact patch should be stored alongside the evidence.

3. **Build logs absent** — Cargo/Trunk build success is claimed but not evidenced. A build log artifact would strengthen the "actual patched WASM" claim.

4. **Screenshot not human-inspectable by reviewer** — The PNG hash matches, but visual confirmation of the editor state (clean, edit visible, ticket/hash displayed) cannot be performed by a text-only model.

---

## Verdict

**PROVISIONAL PASS** for the **bounded claim**:

> The GR-020 DeckCraft host-save adapter, when built from the pinned source with the GR-020 patch applied, loads as actual WASM in Chromium, opens a synthetic PPTX from a same-origin parent, accepts a visible text edit, serializes and emits save bytes over `postMessage`, receives a matching positive `saveResult`, transitions to clean state, and reopens the captured bytes in a fresh iframe with the edit intact.

**This does not verify:**
- Seafile version creation, Seafile-backed reopen, dispatcher integration, production deployment, ONLYOFFICE regression, cross-origin security, optimized bundle (`wasm-opt -Oz`), or any server-side persistence.

**Per project rules:** All free-model verdicts are `PROVISIONAL`. Final disposition requires `GPT REVIEW PASS`. Upstream publication remains **LOCKED**.

---

**Reviewer:** Nemotron 3 Ultra (artcraft-reviewer)
**Date:** 2026-10-25
**Evidence bundle:** `docs/reviews/GR-044/`