# GR-022 — EffectCraft host-save acknowledgement prototype

**Status:** bounded local prototype; not in Seafile dispatch. The project
verdict remains GPT REVIEW FAIL on `0edbe524`; this is not upstream approval.

| Field | Value |
|---|---|
| Upstream base | `storytold/effectcraft` `049070d65c66a73f322b496b22521816e0018f14` |
| Shared transport | `craft-platform` `56c5e16d79b77751106173c13111ef4fe0a2c0ec` |
| Patch SHA-256 | `4e0a1799e36209e1234a1b3ff504ab5ed647cf3bd066af6dec90dacd46ab7407` |
| Patch | [`effectcraft-host-save.patch`](effectcraft-host-save.patch) |
| Independent review | [`REVIEW-INDEPENDENT-R1.md`](REVIEW-INDEPENDENT-R1.md) |

Host mode binds one pathless project opened by the parent. Save submits a
captured snapshot under a ticket; the saved baseline advances only on the
matching success acknowledgement. Rejected, unknown, duplicate, or timed-out
results do not falsely mark it saved. Host-mode template replacement and
unsupported save routes are guarded. Initial Open refuses to replace edits made
before the host document arrives; the message explains those edits cannot be
saved and retry requires reloading the iframe. Normal undo-then-edit history is
retained while the serialized snapshot remains the saved baseline.

## Checks

- Host-save engine tests: 2 passed; UI host-save tests: 4 passed.
- Rust 1.95 locked WebAssembly check, formatting, and `git diff --check`: pass
  per implementer; one pre-existing unused-field warning remains.
- Independent source review confirmed exact base, patch hash, immutable pin,
  host replacement guards, snapshot ACK behavior, and transport origin/source
  checks. Reviewer did not build or run tests.

Browser messaging, host authorization, durable Seafile version creation, and
fresh-storage reopen are **NOT VERIFIED**. The patch is not in dispatch.
