# Source provenance

This standalone crate is copied from `storytold/craft-libs` at
`f180fc0d35d521c5d18e118c881d3efde1ec1eee`, with the GR-016 working-tree
changes from `/tmp/artcraft-gr016-craft-libs` applied. Those changes add the
host protocol and browser host transport, and enable the required `web-sys`
features. The browser message parser is locally hardened to bound incoming
ArrayBuffer/Uint8Array lengths and metadata strings before copying them into
Rust-owned buffers, and bounds cumulative Open bytes and message count per
app runtime before payload copies, shared across transport instances. The source checkout's own `crates/platform` Cargo manifest inherited
workspace package, dependency, and lint keys; this artifact replaces those
inheritance entries with their explicit values so it can build independently. A malformed host `saveResult` with a
missing or non-boolean `ok` field is ignored rather than converted into a false failure acknowledgement; the save ticket
therefore remains pending until a valid acknowledgement or its timeout/unknown-outcome path.
The repository root has a minimal Cargo workspace that exposes this nested
package to future Cargo `git` dependencies; it defines no inherited settings.

`SHA256SUMS` records the exact packaged source and attribution files, plus the
root workspace manifest and lockfile, excluding this provenance note. The
copy was inspected before packaging: it contains crate code/tests, its README,
MIT and Apache license texts, and NOTICE attribution only. A credential-pattern
scan found no credentials, keys, cookies, or production data.
Verify the manifest from this directory with `sha256sum -c SHA256SUMS`.

Copyright and third-party attribution are preserved in `LICENSE-MIT`,
`LICENSE-APACHE`, and `NOTICE`.
