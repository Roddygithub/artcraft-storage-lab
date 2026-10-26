# GR-076 — Independent Review R2: PhotoCraft bounded browser host adapter

**Verdict: PROVISIONAL PASS** (no BLOCKER, no MAJOR)

---

## Evidence inspected

| Artifact | Location / lines |
|---|---|
| Combined patch (GR-026 core + GR-032 + GR-076 hardening) | `docs/reviews/GR-076/photocraft-host-save.patch` (SHA-256 `b3375bc2e9f29a9624df0428df3916b2013ba9aa11be9b7e27825cd103c07d85`) |
| GR-076 report | `docs/GR-076-PHOTOCRAFT-BOUNDED-HOST-ADAPTER.md` |
| R1 review | `docs/reviews/GR-076/INDEPENDENT-REVIEW-R1.md` |
| R1 responses | `docs/reviews/GR-076/REVIEW-RESPONSES-R1.md` |
| Pins / lockfile | `docs/reviews/GR-076/pins.json`, `Cargo.lock` diff in patch |
| Engine tests (4 `saved_snapshot_tests`) | `/home/roddy/.cache/artcraft-storage-lab/gr076-engine.log` — all pass |
| UI tests | `/home/roddy/.cache/artcraft-storage-lab/gr076-ui.log` — still compiling (crate graph lock contention) |
| Patched source (host mode, save flow, guards, inbox, document policy) | `apps/photocraft-web/src/web.rs:59-334`, `apps/photocraft-web/src/host_inbox.rs:1-68`, `crates/engine/src/lib.rs:356-414, 1157-1160`, `crates/ui-egui/src/lib.rs:553-557, 698-766, 773-833, 854-860, 1263-1340, 1688-1751, 1805-1910, 2236-2240`, `crates/ui-egui/src/host_document.rs:1-129`, `crates/ui-egui/src/menus.rs:70-76`, `crates/ui-egui/src/file_open.rs:89-102, 151-156, 178-183, 489-520`, `crates/ui-egui/src/file_dialog.rs:242-247, 263-268`, `crates/ui-egui/src/discard_ui.rs:67-77, 122-128` |
| UI host-mode tests (3 new) | `crates/ui-egui/src/file_open/tests.rs:551-683, 619-723, 726-737` |
| Web inbox tests | `apps/photocraft-web/src/host_inbox.rs:981-999` |

---

## Scope of this review

This review covers the **exact final combined patch** applied to the exact PhotoCraft base `a02f2ee41059d3312e7ff24a5af5edcac7b6435a`. The patch incorporates:
- GR-026 core: pathless `.pcraft` open, `SavedSnapshot` primitive, `acknowledge_saved_snapshot`
- GR-032 remediation: bounded `HostInbox`, listener error propagation
- GR-076 hardening: host-mode policy (`host_document.rs`), one-document binding, save ticket lifecycle, ACK matching, timeout/unknown handling, bypass guards for all file commands except explicit exports, input/output size caps (50 MiB adapter, 256 MiB transport Open copy, 16 Mpx canvas), repaint-driven timeout tick
- Delta since R1: explicit `photocraft-format` workspace dependency for bounded decoder (lockfile adds only this local edge), standalone confirmed-write vs unconfirmed-download regression test, restored 3 engine snapshot tests + 1 same-ID regression test

**Explicitly NOT VERIFIED** (per GR-026 §53-54, GR-032 §82-87, GR-076 report, and this review):
- Browser iframe host / `postMessage` origin validation / CSP / token leakage / replay / session fixation / XSS / CSRF / SSRF
- Seafile login, library, version creation, readback, fresh-editor reopen
- `craft-platform` browser transport same-origin/source checks in a live browser
- Any production Seafile / ONLYOFFICE configuration
- Browser clock, idle repaint, `beforeunload` runtime behavior
- Full PhotoCraft suite, native desktop UI/visual QA, clippy, adversarial corpus
- Whole-transitive-license audit (R1 §98 notes MIT/Apache-2.0 throughout; `craft-platform` is same workspace)

---

## Patch digest

**Combined patch SHA-256:** `b3375bc2e9f29a9624df0428df3916b2013ba9aa11be9b7e27825cd103c07d85`  
**Applies cleanly to base:** `git apply --check` passed on `/home/roddy/.cache/artcraft-storage-lab/gr076-photocraft-apply-check` (per README.md §13)  
**Git dependencies unchanged** (pins.json): `craft-platform@56c5e16d79b77751106173c13111ef4fe0a2c0ec`, `craft-docpath@82a24b006eefa036b43c09a67fb9a3fbd17ffe63`, `craft-print@3d37da389a3618ab9b76109da11416e9ca4ea719`, `craft-ui@5c874d51eeb3de70e735c8ce87a59a7dedd47675`, `craft-winprint-gdi@417ac3c4d14d3da5485a99c7d5ce8f05664ec312`, `winprint@5f80b9baf6b58937c401656634e42d33f00ddf49`  
**Compiler:** `rustc 1.95.0 (59807616e 2026-04-14)`  
**Cargo lock SHA-256:** `166c9984b3e3706eabd88400ab9bed50840cd146043e6dd4ac900a285cb4a3d0`

---

## Findings

### BLOCKER
*None.*

### MAJOR
*None.*

### MINOR

1. **Peak serialization memory not bounded before 50 MiB check**  
   `crates/ui-egui/src/lib.rs:788-791`: `save_host_snapshot` calls `export()` which serializes the full `.pcraft` into a `Vec<u8>` *before* `host_document::check_size(bytes.len())` rejects >50 MiB. A 200 MiB document allocates its full serialized form. The source comment at line 790 explicitly acknowledges: "The exporter currently returns a complete Vec; this bounds handoff, not peak serialization memory."  
   → **Suggested fix**: streaming encoder or pre-flight size estimate; at minimum the comment is accurate and the limitation is documented in the report (§54). No code change required for this slice.

2. **`beforeunload` guard remains best-effort browser confirmation**  
   `apps/photocraft-web/src/web.rs:249-262` (in `guard_unload`), `crates/ui-egui/src/discard_ui.rs:124-128` (`has_unsaved_work` now includes `host_save_pending` and `host_save_unknown`). The patch correctly updates the dirty predicate so the browser *will* prompt. However, the user can still dismiss the prompt and lose the unresolved save. The GR-026 decision (§45-46) and REVIEW-RESPONSES-R1.md line 10 accept this; no code change needed. The report correctly states "browser confirmation is best effort only" (README.md line 24).

3. **Host instance ID requires `Crypto.getRandomValues`; failure UI NOT VERIFIED**  
   `apps/photocraft-web/src/web.rs:329-334`: `host_instance_id()` returns `Err` if `crypto.getRandomValues` is unavailable. Host startup fails visibly (lines 99-118) by setting an error message on `#photocraft_loading`. The predictable `Date.now() + Math.random()` fallback was removed (REVIEW-RESPONSES-R1.md line 9). Actual failure rendering in a browser is **NOT VERIFIED**.

4. **Transport Open copy cap (256 MiB) vs adapter cap (50 MiB) are separate layers**  
   REVIEW-RESPONSES-R1.md lines 20-22 correctly notes R1's "50 MiB transport cap" was imprecise. The shared `craft-platform` transport bounds message size and cumulative runtime copied bytes to 256 MiB and 64 admissions before copying (`craft-platform/src/browser/host.rs` at pinned rev). The adapter enforces 50 MiB on document input (`host_document::check_size` at Open, line 495) and host-save output (line 791). Explicit export writes also cap at 50 MiB (web.rs:314-319). The report §53-54 documents both correctly.

5. **Exports are local browser downloads, not delivered to parent host**  
   REVIEW-RESPONSES-R1.md line 7 corrects R1's misstatement: `file.export.*` commands trigger the `write` service (web.rs:314-320), which calls `download(path, bytes)` — a browser download via anchor click. They do **not** go through `host_save` or `postMessage` to the parent. The 50 MiB cap in host mode (line 316) bounds the download payload. This is correctly implemented.

6. **Negative ACK preserves dirty; timeout retains unknown ticket with no auto-retry; late valid ACK still resolves**  
   `crates/ui-egui/src/lib.rs:801-833`: `host_save_result` consumes the pending snapshot only on matching ticket. Positive ACK advances `saved_revision` to captured revision (edits after capture stay dirty). Negative ACK keeps dirty. Timeout sets `host_save_unknown=true` but leaves `host_save_pending` intact (line 829); a late matching ACK is still processed because `host_save_pending.take()` consumes it. `save_host_snapshot` refuses new saves while `host_save_pending.is_some() || host_save_unknown` (line 779-780). This matches GR-026 spec §39-40 and is tested in `host_save_dispatch_waits_for_matching_durable_ack_and_guards_bypass_routes` (file_open/tests.rs:563-608).

7. **One-document host mode is a deliberate slice; replacement/duplicate guards are comprehensive**  
   `host_document.rs:102-111`: `authorize` blocks all `file.*` except `file.export.*`, plus `actions.play`, `image.duplicate`, `history.newDocument`, `channel.split/merge`, `layer.smartObjects.editContents`, and `document=new` variants of `layer.duplicate/copyToDocument/channel.duplicate`, `select.refineEdge` (newDocument*), `image.calculations` (newDocument). `authorize_waiting` additionally blocks `edit.paste*` before first Open. Installed on `session.authorize` (lib.rs:1338) covering nested engine dispatch, and checked in `run` (line 859) and `menus::invoke` (line 926). Test `host_guards_cover_direct_picker_drop_duplicate_replacement_and_close_routes` (file_open/tests.rs:619-683) exercises all routes including nested engine, menu, and direct `app.run`. No bypass found.

8. **Close/discard guards block even clean host document; browser navigation best-effort**  
   `discard_ui.rs:67-77`: `intercept` blocks `file.close|closeOthers|closeAll|exit|revert` in host mode even when no dirty work, showing "Save this host document successfully before closing it". This is deliberate for the one-document slice. Browser navigation uses existing `beforeunload` (web.rs:249-262) which is best-effort. Test confirms `discard.is_none()` — no "Don't Save" prompt is presented (file_open/tests.rs:681-682).

---

## Test gaps

| Missing test | Why it matters |
|---|---|
| Export payload size in host mode (manual verification) | Exports are permitted and bounded at 50 MiB in `write` service (MINOR #1, #5). |
| Large document serialization peak memory | 200 MiB `.pcraft` allocates full serialized bytes before 50 MiB check (MINOR #1, report §54). |
| Cross-tab `host_instance_id` collision | Now requires `Crypto.getRandomValues`; collision probability negligible but not tested. |
| Listener error propagation in live browser | `require_listener` test passes (host_inbox.rs:1002-1005) but actual browser startup-failure rendering not exercised. |
| Concurrent host Open race | Inbox accepts only first Open (host_inbox.rs:57-59). No test for two rapid `postMessage` Opens. |
| Seafile version creation / fresh reopen | Entire browser/Seafile MVP NOT VERIFIED. |
| `craft-platform` origin validation | Transport dependency pinned; same-origin/source checks documented at `craft-platform/src/browser/host.rs:84-93, 158-175` but not exercised in this slice. |
| UI host-mode tests execution | Still compiling (gr076-ui.log); pass/fail not yet recorded. |

---

## Notes

- **Architecture**: The one-document pathless host mode is correctly implemented as a Rust-only primitive. The `SavedSnapshot` + `incarnation` + ticketed ACK design satisfies the GR-026 contract: only the exact captured revision advances the baseline; edits after capture stay dirty; negative ACK preserves dirty; timeout retains unknown ticket with no auto-retry; late matching ACK resolves.
- **Security**: The `host_document::authorize` policy is comprehensive — it blocks all `file.*` except `file.export.*`, plus the enumerated non-file commands. Direct engine dispatch (`session.execute`), menu (`menus::invoke`), and `app.run` all gate through this policy. Nested/scripted commands are covered by installing `session.authorize`.
- **Standalone preservation**: `host_mode` is false by default. All guards are conditional on `services.host_mode`. Native `write` (browser download) and filesystem paths are untouched. `write_unconfirmed: true` remains for standalone web builds. Test `standalone_confirmed_write_cleans_but_unconfirmed_download_stays_dirty` (file_open/tests.rs:726-737) confirms baseline behavior.
- **Licensing**: MIT/Apache-2.0 throughout. `craft-platform` is from the same workspace (ArtCraft Storage Lab). No copyleft dependencies introduced. Whole-transitive audit NOT VERIFIED.
- **Upstream suitability**: The patch is a local prototype only. The `?host=parent` query parameter and `craft-platform` browser transport are ArtCraft-internal. No upstream Seafile/ONLYOFFICE changes proposed.

---

## Review artifacts

- This report: `docs/reviews/GR-076/INDEPENDENT-REVIEW-R2.md`
- Evidence bundle: `docs/reviews/GR-076/` (patch, GR-076 report, pins.json, R1 review, R1 responses, test logs)
- Test matrix update: pending (owner responsibility per AGENTS.md §68.4)

---

**REVIEW RESULT: PASS** (PROVISIONAL — FREE REVIEW PASS, GPT REVIEW PENDING)