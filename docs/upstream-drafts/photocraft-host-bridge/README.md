# PhotoCraft `?host=parent` bridge — DRAFT port, unpublished

`host.rs` goes to `apps/photocraft-web/src/host.rs`; `apply.py <repo>` makes the shell changes
(`main.rs`: `mod host;`, `Cargo.toml`: web-sys `MessageEvent`, `web.rs`: create the bridge on
`?host=parent`, hook `Services::write`, set `write_unconfirmed = false` (the parent stores the
file; no cancellable download is involved), push host files into the app's open inbox, post
`dirty` from `has_unsaved_work()` on change, post `ready`/`failed`). Based on
storytold/photocraft `799e129` (v0.18.0).

Unlike DeckCraft and SoundCraft, PhotoCraft has a dirty signal, so the host's unload guard and
"unsaved changes" state are exact. Supersedes the lab's GR-076 patch (14 files, engine changes):
the bridge needs none of them.
