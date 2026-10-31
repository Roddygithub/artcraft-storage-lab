# DeckCraft `?host=parent` bridge — DRAFT port, unpublished

`host.rs` is the file to add at `apps/deckcraft-web/src/host.rs`; `apply.py <repo>` makes the
three shell changes (`main.rs`: `mod host;`, `web.rs`: create the bridge on `?host=parent`, hook
`write`/`download`, drain host files into the inbox with `begin_external_file("drop")`, start
blank instead of the sample deck, post `ready`/`failed`). Based on storytold/deckcraft `a3fbf02`
(v0.13.1). Modeled line by line on upstream WordCraft's `host.rs`.

Differences from WordCraft's: DeckCraft's `Services` has no `on_dirty`, so `deckcraft:dirty` is not
sent (the host's unload guard is weaker); `saveAs` is derived from the name (not from the engine).

Build: `cd apps/deckcraft-web && trunk build --release`. Lab result: see `lab/real-seafile/results/`
once the bundle is wired as `editors/deckcraft` (provenance will say "patched: host bridge port").
