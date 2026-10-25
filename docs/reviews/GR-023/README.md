# GR-023 — FilmCraft host-save acknowledgement prototype

**Status:** bounded local prototype; not in Seafile dispatch. This is not a
project-level GPT verdict or upstream authorization.

| Field | Value |
|---|---|
| Upstream base | `storytold/filmcraft` `fa550ce2d07bdfee6b1d7b6835e8abc8c6913d00` |
| Shared transport | `craft-platform` `56c5e16d79b77751106173c13111ef4fe0a2c0ec` |
| Patch SHA-256 | `16158f500b2ec12f93c8fcb14867e0b452030dbb338b2d4d7fa8612850a694d4` |
| Patch | [`filmcraft-host-save-ack.patch`](filmcraft-host-save-ack.patch) |
| Independent review | [`REVIEW-INDEPENDENT-R2.md`](REVIEW-INDEPENDENT-R2.md) |

Host mode opens one pathless `.fcproj` document. Save, Save All, keyboard
shortcuts and the exposed control/menu routes submit a ticketed serialized
snapshot. The document remains dirty until the matching host ACK. A negative
ACK keeps it dirty; timeout preserves an unknown pending outcome and does not
automatically retry. Save As, opening/replacing another project, recovery open,
template creation/copy and project close commands are refused in host mode.
Standalone browser download and native filesystem paths remain separate.

## Checks

- Engine host-save tests: 4 passed.
- UI host-save tests: 3 passed after the final engine guard.
- Rust 1.95 locked WASM check, formatting and `git diff --check`: passed after
  the final guard and transport re-pin.
- Independent source review confirmed the exact base/hash, transport pin,
  lifecycle guards, ACK/timeout behavior and origin/source checks. The reviewer
  did not rerun tests/builds.

Browser execution, host authorization, durable Seafile version creation, and
fresh Seafile reopen are **NOT VERIFIED**. This patch is not in the dispatch.
The stored raw diff retains the whitespace on blank context lines required for
its exact generated-patch identity; run whitespace checks on the surrounding
source and documentation separately from this serialized patch artifact.
