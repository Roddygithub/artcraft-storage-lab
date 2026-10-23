# Interim Sol 6.1 low review — all-app Rust integration plan

Date: 2026-10-23  
Reviewed source SHA: `0dc5e13abbb8d940390484e6dca8338cc3a9a849`  
Review mode: read-only interim review; not a final candidate gate.

## Findings verified for follow-up

1. Current local integration work consists of a Python Seafile gateway and
   browser host controller, four dispatch entries (DOCX/XLSX/PDF/SVG), a
   WordCraft Rust/WASM bridge patch and a GridCraft durable-save patch. A shared
   Rust host crate and all-app adoption are plans, not implemented code.
2. WordCraft and GridCraft encode save tickets differently (number versus
   string). The proposed shared contract examples do not yet define one
   correlation representation. Preserve each app's snapshot/dirty lifecycle
   while standardizing transport and durable-result semantics.
3. VectorCraft's host poll used a 32-bit FNV fingerprint. Two distinct
   equal-length values were found with the same fingerprint:
   `46e9bb16c707a921` and `33d4b4702b82e0e2` (both hash to `4d10285d`). This
   could suppress a changed serialized document. The prior claim that identical
   byte output still signals a save was incorrect because the API exposes no
   dirty/save event.
4. `docs/HOST-CONTRACT.md` incorrectly listed CADCraft as lacking a bridge,
   conflicting with the capability inventory. `docs/UPSTREAM-PLAN.md` had
   stale DOCX verification wording and described each remaining app bridge as
   “a few lines,” unsupported by the app-specific serialization and persistence
   seams.
5. The gateway is Python, but substantial browser protocol code is generated
   JavaScript. Python owns Seafile-facing persistence; Rust/WASM should own
   editor lifecycle and serialization. Stock Seafile still lacks the
   conditional-save endpoint required by this prototype.

## Bounded recommendation

After the parallel app capability audits complete, extract the common Rust/WASM
transport and migrate only WordCraft and GridCraft as the first two distinct
save lifecycles. Keep serialization, document identity and snapshots inside
each app adapter. Cover durable success/failure, unknown/duplicate tickets,
edits during pending saves, origin/source validation and exports that must not
mark the source document clean. Do not imply this completes all ArtCraft apps.

## Remediation status

The VectorCraft poll now compares exact serialized bytes, and
`/tmp/artcraft-review-pw/bin/python tests/test_hostpage_protocol.py` passes a
synthetic Chromium regression using the colliding pair above. The actual
VectorCraft/Seafile flow was subsequently rerun in the isolated container:
changed SVG bytes were saved, read back byte-identically, and parsed on a fresh
route load. See `docs/reviews/GR-012/VECTORCRAFT-SEAFILE-E2E-20261023.md`. The
exact collision itself remains a synthetic Chromium regression case.

This report records an interim review only. It does not supersede the prior Sol
FAIL, establish GPT candidate readiness, or unlock upstream publication.
