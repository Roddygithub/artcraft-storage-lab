# GR-021 — DesignCraft host-save prototype

**Status:** bounded local prototype; not in Seafile dispatch. This is not a
project-level GPT verdict or upstream authorization.

| Field | Value |
|---|---|
| Upstream base | `storytold/designcraft` `80d13911b2d20fbb5cd9398696627bb3a715417b` |
| Shared transport | `craft-platform` `91836a9ebad5ffcd8f1966fb4f36dc84387f2cdd` |
| Patch SHA-256 | `1333c9d24f19cbc458a436fac77a94f15924f5c9d1ec428c630fbadd0b2cbb30` |
| Patch | [`designcraft-host-save-ack.patch`](designcraft-host-save-ack.patch) |

The local adapter opens one pathless native `.designcraft` document, serializes
a captured snapshot, and only marks that snapshot saved after a matching durable
host ACK. Later edits remain dirty. Host Save As, document replacement, branch
and preview flows are rejected for this slice. Standalone browser downloads and
native filesystem saves retain their upstream path.

## Checks

- Five focused tests passed under Rust 1.95 with `--locked` (engine snapshot,
  stale/path rejection, UI matching ACK/later edits, fail-closed save/open
  guards, and one-document host open).
- `cargo +1.95.0 check -p designcraft-web --target wasm32-unknown-unknown
  --locked` passed.
- `cargo +1.95.0 fmt --all -- --check` and `git diff --check` passed.
- Independent Luna high R3 review: no code-level blocker or major found; exact
  patch hash and base matched. R2 noted one resource qualification below.

## Limits

The adapter's 64 MiB outbound payload check runs after the engine serializer has
allocated its `Vec`; it caps submitted/pending payload size but not peak
serialization memory for an oversized document. Browser messaging, Seafile
version creation, and fresh-storage reopen are **NOT VERIFIED**. This patch is
not added to `integration/config/dispatch.json`.
