# SoundCraft `?host=parent` bridge — DRAFT port, unpublished

`host.rs` goes to `apps/soundcraft-web/src/host.rs`; `apply.py <repo>` makes the shell changes
(`main.rs`: `mod host;`, `Cargo.toml`: web-sys `MessageEvent`, `web.rs`: create the bridge on
`?host=parent`, install `host::deliver` as the engine's delivery hook instead of the download,
start with an empty engine instead of the demo, drain host files into the inbox by extension
(`Purpose::of`), post `ready`/`failed`). Based on storytold/soundcraft `444a716` (v0.15.0).

Particularity: SoundCraft's engine delivers files through a global `fn` hook
(`soundcraft_engine::io::set_deliver`), not a `Services` closure, so the bridge lives in a
thread-local and `deliver` forwards to it. Session files are `.scraft` / `.scraftz`; any other
extension sent by the host imports as audio or MIDI, as a dropped file would. No dirty signal.
