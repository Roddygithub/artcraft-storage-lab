# GR-076 — Independent Review R1: PhotoCraft browser host adapter hardening

**Verdict: PROVISIONAL PASS** (no BLOCKER, no MAJOR)

---

## Evidence inspected

| Artifact | Location / lines |
|---|---|
| Combined patch (GR-026 + GR-032 hardening) | `docs/reviews/GR-076/photocraft-host-save.patch` |
| GR-026 design assessment | `docs/GR-026-PHOTOCRAFT-HOST-SAVE.md` |
| GR-032 evidence bundle | `docs/reviews/GR-032/README.md` |
| Patched engine source | `/home/roddy/.cache/artcraft-storage-lab/gr076-photocraft/crates/engine/src/lib.rs:304-374, 615-629` |
| Patched UI source (host mode, save flow, guards) | `/home/roddy/.cache/artcraft-storage-lab/gr076-photocraft/crates/ui-egui/src/lib.rs:565-570, 697-713, 1025-1084, 1259-1372, 1685-1777, 1806-1871, 2230-2240` |
| Host document policy module | `/home/roddy/.cache/artcraft-storage-lab/gr076-photocraft/crates/ui-egui/src/host_document.rs:1-74` |
| Web transport integration | `/home/roddy/.cache/artcraft-storage-lab/gr076-photocraft/apps/photocraft-web/src/web.rs:59-144, 404-423, 485-513` |
| Host inbox (bounded queue, listener error propagation) | `/home/roddy/.cache/artcraft-storage-lab/gr076-photocraft/apps/photocraft-web/src/host_inbox.rs:1-68` |
| Discard/close guards | `/home/roddy/.cache/artcraft-storage-lab/gr076-photocraft/crates/ui-egui/src/discard_ui.rs:69-77, 124-128` |
| Menu/command dispatch gate | `/home/roddy/.cache/artcraft-storage-lab/gr076-photocraft/crates/ui-egui/src/menus.rs:70-76` |
| File open/dialog guards | `/home/roddy/.cache/artcraft-storage-lab/gr076-photocraft/crates/ui-egui/src/file_open.rs:91-107, 112-115, 153-156, 176-183` / `file_dialog.rs:243-247, 265-268` |
| Engine saved snapshot tests (3 recovered + 1 new) | `/home/roddy/.cache/artcraft-storage-lab/gr076-photocraft/crates/engine/src/saved_snapshot_tests.rs:1-70` |
| UI host-mode tests | `/home/roddy/.cache/artcraft-storage-lab/gr076-photocraft/crates/ui-egui/src/file_open/tests.rs:511-568, 579-643, 646-683` |
| Web inbox tests | `/home/roddy/.cache/artcraft-storage-lab/gr076-photocraft/apps/photocraft-web/src/host_inbox.rs:44-68` |

---

## Scope of this review

This review covers the **combined patch** that incorporates:
- GR-026 core slice: pathless `.pcraft` open, `SavedSnapshot` primitive, `acknowledge_saved_snapshot`
- GR-032 remediation: bounded `HostInbox`, listener error propagation
- GR-076 hardening: host-mode policy (`host_document.rs`), one-document binding, save ticket lifecycle, ACK matching, timeout/unknown handling, bypass guards for all file commands except explicit exports, input/output size caps (50 MiB transport, 256 MiB decoded, 16 Mpx canvas), repaint-driven timeout tick

**Explicitly NOT VERIFIED** (per GR-026 §53-54, GR-032 §82-87, and this review):
- Browser iframe host / `postMessage` origin validation / CSP / token leakage / replay / session fixation
- Seafile login, library, version creation, readback, fresh-editor reopen
- `craft-platform` browser transport same-origin/source checks in a live browser
- Any production Seafile / ONLYOFFICE configuration

---

## Findings

### BLOCKER
*None.*

### MAJOR
*None.*

### MINOR

1. **Export payload not size-bounded in host mode**  
   `host_document.rs:17` explicitly permits `file.export.*` commands. `save_host_snapshot` (lib.rs:1042) bounds the **host save** payload at 50 MiB via `host_document::check_size`, but **exports** go through the regular `export` service (lib.rs:1040, 534-536) which has **no host-mode size check**. A malicious or buggy host could receive an arbitrarily large exported PNG/JPEG/PSD.  
   → **Suggested fix**: add `host_document::check_size(bytes.len())` in the export service when `host_mode` is true, or document this as a known limit (the GR-032 report §28 documents the *save* serialization peak-memory limit but not exports).

2. **Peak serialization memory not bounded before 50 MiB check**  
   `save_host_snapshot` (lib.rs:1039-1042) calls `export()` which serializes the full `.pcraft` into a `Vec<u8>` *before* `host_document::check_size(bytes.len())` rejects >50 MiB. A 200 MiB document allocates its full serialized form. GR-032 §28 acknowledges this for the save path; the same applies to exports (see MINOR #1).  
   → **Suggested fix**: streaming encoder or pre-flight size estimate; at minimum document in `host_document.rs` comments.

3. **`host_instance_id()` falls back to `Date.now() + Math.random()` when `crypto.getRandomValues` unavailable**  
   `web.rs:286-294`. The fallback is predictable and could allow ticket collision across tabs if the host opens multiple PhotoCraft iframes in the same millisecond. The monotonic counter (`host_save_counter`) mitigates replay *within* one instance, but cross-instance collision weakens the per-page namespace guarantee.  
   → **Suggested fix**: require `crypto.getRandomValues` (available in all target browsers) or use `crypto.subtle.digest` over a larger seed.

4. **`beforeunload` guard remains best-effort browser confirmation**  
   `web.rs:249-262`, `discard_ui.rs:124-128`. The patch correctly updates `has_unsaved_work()` to include `host_save_pending` and `host_save_unknown`, so the browser *will* prompt. However, the user can still dismiss the prompt and lose the unresolved save. The GR-026 decision (§45-46) accepts this; no code change needed, but the claim "impossible-to-close" must not appear in docs.

5. **`actions.play` blocked but individual scripted `file.*` steps could still reach engine if `automation_authorize` is misconfigured**  
   `host_document.rs:18` blocks `actions.play`. `lib.rs:1340-1360` runs `automation_authorize` for `actions.play` steps *only when `automation_input` is true*. In host mode, `session.authorize` is set to `host_document::authorize` (lib.rs:1089), which blocks all `file.*` (except exports). This is correct *if* `automation_input` is false (the default). A control client that sets `automation_input=true` without providing its own `automation_authorize` would fall through to `session.authorize` and be blocked — safe. No bypass found, but the interaction is subtle.

6. **`edit.paste` blocked before first host Open, but `file.newFromClipboard` not explicitly listed in `authorize_waiting`**  
   `host_document.rs:71-73` blocks `edit.paste*`. `file.newFromClipboard` is blocked by the generic `file.` prefix rule (line 17). Verified in test `host_guards_cover_direct_picker_drop_duplicate_replacement_and_close_routes` (file_open/tests.rs:592). Correct.

7. **`host_save_timed_out` clears `host_save_started` but leaves `host_save_pending` set**  
   `lib.rs:1078-1083`: `host_save_timed_out()` sets `host_save_unknown = true` but does **not** clear `host_save_pending`. The pending snapshot remains stored. A subsequent matching ACK (if the host *did* eventually succeed) would still be processed by `host_save_result` (lib.rs:1052-1074) because it takes `host_save_pending.take()`. This is correct: the unknown state is informational; a late valid ACK should still advance the baseline. However, `save_host_snapshot` (lib.rs:1031) refuses a new save while `host_save_pending.is_some() || host_save_unknown`. After timeout, `host_save_unknown=true` blocks retry until the user reconciles (clears via positive/negative ACK). This matches the GR-026 spec §39-40.

---

## Test gaps

| Missing test | Why it matters |
|---|---|
| Export payload size in host mode | Exports are permitted and unbounded (MINOR #1). |
| Large document serialization peak memory | 200 MiB `.pcraft` allocates full serialized bytes before 50 MiB check (MINOR #2, GR-032 §28). |
| Cross-tab `host_instance_id` collision | Fallback RNG could produce duplicate instance IDs (MINOR #3). |
| Listener error propagation in live browser | `require_listener` test passes (host_inbox.rs:64-68) but actual browser startup-failure rendering not exercised (GR-032 §20). |
| Concurrent host Open race | Spec says one Open; inbox accepts only first (host_inbox.rs:20-22). No test for two rapid `postMessage` Opens. |
| Seafile version creation / fresh reopen | Entire browser/Seafile MVP NOT VERIFIED. |
| `craft-platform` origin validation | Transport dependency pinned at rev `56c5e16d...`; same-origin/source checks documented at `craft-platform/src/browser/host.rs:84-93, 158-175` but not exercised in this slice. |

---

## Notes

- **Architecture**: The one-document pathless host mode is correctly implemented as a Rust-only primitive. The `SavedSnapshot` + `incarnation` + ticketed ACK design satisfies the GR-026 contract: only the exact captured revision advances the baseline; edits after capture stay dirty; negative ACK preserves dirty; timeout retains unknown ticket with no auto-retry.
- **Security**: The `host_document::authorize` policy is comprehensive — it blocks all `file.*` except `file.export.*`, plus `actions.play`, `image.duplicate`, `history.newDocument`, `channel.split/merge`, `layer.smartObjects.editContents`, and `document=new` variants of `layer.duplicate/copyToDocument/channel.duplicate`, `select.refineEdge`, `image.calculations`. Direct engine dispatch (`session.execute`), menu (`menus::invoke`), and `app.run` all gate through this policy (lib.rs:1340, menus.rs:71-75). Nested/scripted commands are covered by installing `session.authorize` (lib.rs:1089).
- **Standalone preservation**: `host_mode` is false by default. All guards are conditional on `services.host_mode`. Native `write` (browser download) and filesystem paths are untouched. `write_unconfirmed: true` remains for standalone web builds.
- **Licensing**: MIT/Apache-2.0 throughout. `craft-platform` is from the same workspace (ArtCraft Storage Lab). No copyleft dependencies introduced.
- **Upstream suitability**: The patch is a local prototype only. The `?host=parent` query parameter and `craft-platform` browser transport are ArtCraft-internal. No upstream Seafile/ONLYOFFICE changes proposed.

---

## Review artifacts

- This report: `docs/reviews/GR-076/INDEPENDENT-REVIEW-R1.md`
- Evidence bundle: `docs/reviews/GR-076/` (patch, GR-026, GR-032 README, test logs)
- Test matrix update: pending (owner responsibility per AGENTS.md §68.4)

---

**REVIEW RESULT: PASS** (PROVISIONAL — FREE REVIEW PASS, GPT REVIEW PENDING)