# DesignCraft `?host=parent` bridge — DRAFT port, unpublished

`host.rs` goes to `apps/designcraft-web/src/host.rs`; `apply.py <repo>` makes the shell changes
(`main.rs`: `mod host;`, `Cargo.toml`: web-sys `MessageEvent`, `web.rs`: create the bridge on
`?host=parent`, hook `Services::write`/`download`, drain host files into the inbox with
`import_request("drop")` inside the graphics-health guard, post `ready`/`failed` after the runner
starts). Based on storytold/designcraft `ea214dd` (v0.15.2). No `on_dirty` in `Services`, so no
dirty signal. Supersedes the lab's GR-021 patch (engine command changes): the bridge needs none.
