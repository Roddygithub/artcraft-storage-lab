# GR-020 — DeckCraft host-save adapter prototype

**Status: bounded local prototype.** This continues the one-connector/shared-transport approach by adapting DeckCraft's existing Rust serializer and Web `Services` seam. It does not add DeckCraft to the Seafile dispatcher and does not prove the mandatory Seafile workflow.

## Contract

In `?host=parent` mode, the parent supplies one supported presentation (`.deckcraft`, `.pptx`, `.potx`, or `.ppsx`). DeckCraft serializes the exact in-memory snapshot through its existing Rust format writer, sends a `deckcraft:save` message with an opaque ticket, and remains dirty until the parent returns the matching `deckcraft:saveResult` after durable storage. The engine records the snapshot as the saved baseline; any edits made after serialization remain dirty.

Host mode rejects a second document, host Save As, path opens, and recovery/duplicate/new-document commands. Open requests go back to the parent. Standalone browser download behavior and native filesystem saves remain on their existing paths. Incoming documents and serialized save payloads are capped at 256 MiB; only one host save may be outstanding, and an unanswered timeout is treated as an unknown result without automatic retry.

## Pinned evidence

- Source: DeckCraft `0f4fffcf6c71ffa16029d07ac23752fedd783547`.
- Shared transport: `craft-platform` pinned to lab commit `90c261de22ef75c4c7c5c5cd1c712d483be0bbc8`.
- Patch and exact hash: `docs/reviews/GR-020/README.md`.
- Independent bounded review: `docs/reviews/GR-020/REVIEW-LUNA-HIGH-R1.md`.

The native tests cover positive and negative acknowledgements, a later edit during an outstanding save, and reopening serialized bytes. The pinned WASM target compiles. A browser transport run, Seafile version creation/reopen, public deployment controls, and project-level GPT review remain **NOT VERIFIED**. Upstream publication remains locked.
