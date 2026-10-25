# GR-030 evidence bundle

Scope: local SoundCraft Web browser host-save smoke, using the GR-025 adapter
and local GR-027/028/029 compatibility overlays.

| Artifact | SHA-256 | Purpose |
|---|---|---|
| [`host-smoke.html`](runtime/host-smoke.html) | `532f195313aa300e93db3cfc009e9f3cdfdec7fabbf7c51f5135028b48352e0d` | Same-origin synthetic parent; sends Open bytes, acknowledges the exact save ticket, and reopens the retained bytes in a fresh iframe |
| [`soundcraft-host-reopen-20261025.png`](runtime/soundcraft-host-reopen-20261025.png) | `901e103ab19efd1a132861fdc5e055ca3f71f57f0a0cbf9b86b38c84373c7496` | Post-reopen screenshot: fresh editor shows the saved `Audio 1` track and ten-track project |

These are the two retained static artifacts: the synthetic parent harness and
one post-reopen screenshot. No video or browser recording is included. The
generated `.scraftz` fixture (66,201,744 bytes) and build output are not
included. Their hashes and the observed save hash/size are recorded in
[`GR-030-SOUNDCRAFT-BROWSER-SMOKE.md`](../../GR-030-SOUNDCRAFT-BROWSER-SMOKE.md).

The save ACK in this harness is synthetic and immediate. The harness does not
persist bytes to Seafile. Seafile version creation, storage-backed reopen,
gateway authorization, optimized WASM, and production security remain
**NOT VERIFIED**. SoundCraft is not in the dispatch configuration.
