# GR-030 — SoundCraft browser host-save smoke

## Result

The GR-025 SoundCraft host-save adapter, with the GR-027/028 and GR-029 local
compatibility overlays, completed a same-origin browser round trip through an
in-memory parent:

```text
host sends .scraftz → SoundCraft Web opens
  → user adds an audio track → Ctrl+S sends bytes
  → parent returns matching success ACK → editor reports clean
  → fresh iframe instance opens the saved bytes and shows the added track
```

This is **browser protocol evidence only**. The parent retained the bytes in
JavaScript memory and acknowledged them immediately. It did not call Seafile,
create a Seafile version, or prove persistence after storage-backed reopen.
SoundCraft remains out of `integration/config/dispatch.json`.

## Run details

| Item | Value |
|---|---|
| SoundCraft source | `storytold/soundcraft` `d47abe484d4f9ef0cc9f8e872e0b3880a61a4588`, with the exact GR-025 → GR-027 → GR-028 → GR-029 overlay sequence documented in [`GR-029`](../GR-029-SOUNDCRAFT-EGUI-WASM.md) |
| Shared transport | `craft-platform` `56c5e16d79b77751106173c13111ef4fe0a2c0ec` |
| Browser | Chromium via the T3 collaborative preview; loopback static server on `localhost:18779` |
| Frame topology | Same-origin `host-smoke.html` parent and `index.html?host=parent` child; parent checked both `event.origin` and `event.source` |
| Build | Trunk release profile, `data-wasm-opt="0"`; functional browser build, **not an optimized production bundle** |
| Fixture | Synthetic `Midnight Groove` `.scraftz`, 66,201,744 bytes; SHA-256 `76bbe6c76e03768b877eae0836d8f5fcc20424a183d8f4fda4efcd322118984a` |
| Saved message | `Midnight Groove.scraftz`, 66,203,163 bytes; SHA-256 `a6dd338bc2fcfc714abbf26102e5732e31f208036dc5c1086a2a9afa55074133` |
| WebAssembly | 22,358,112 bytes; SHA-256 `c45d655fbb85ab115b03db7ff03a6f0d42c8c56eccce882b30dfabd1284cf264` |

The evidence bundle retains two static artifacts in [`runtime/`](reviews/GR-030/runtime/):
the parent harness (`host-smoke.html`) and one post-reopen screenshot
(`soundcraft-host-reopen-20261025.png`). It contains no video or browser
recording. The large generated fixture and build output stay in the local cache
and are not committed.

## Observed steps

1. The actual SoundCraft Web/WASM app sent `soundcraft:ready`. The parent sent
   the synthetic `.scraftz` as `soundcraft:open`; the editor displayed the
   session with nine tracks and reported `dirty: false`.
2. In the editor UI, clicked the track-add button and the dialog’s **Create**
   action. The new `Audio 1` track appeared and the parent observed
   `soundcraft:dirty {dirty:true}`.
3. Focused the editor and pressed Ctrl+S. The parent received the transferred
   `soundcraft:save` bytes, computed the SHA-256 above, retained a copy, and sent
   `soundcraft:saveResult` with the same ticket and `ok:true`.
4. The editor reported `dirty: false` after handling the acknowledgement.
5. Used the parent’s **Open saved bytes in a fresh editor** button. It replaced
   the iframe with a new `?host=parent&reopen=…` instance and supplied the
   retained save bytes on the new `soundcraft:ready`. The fresh session showed
   ten tracks, including `Audio 1`, and `dirty: false` (see screenshot).

## Limits and follow-up

- **Seafile save/version/reopen:** NOT VERIFIED. No Seafile API or gateway was
  involved; the parent’s JavaScript variable was the only storage.
- **Gateway payload size:** the gateway defaults `ARTCRAFT_MAX_BYTES` to 50 MiB
  (`integration/gateway/server.py`), while this app permits host saves up to
  64 MiB. This observed 66,203,163-byte save fits the app ceiling but exceeds
  the gateway default. Before a Seafile run, use a smaller synthetic session
  or deliberately configure and test a suitable gateway ceiling. No limit was
  changed in this work item.
- **Optimization:** `wasm-opt` was disabled for the functional browser build;
  production bundle size and performance are NOT VERIFIED.
- **Cross-origin/security:** only same-origin loopback framing was exercised.
  Production TLS, proxy, CSP, CSRF, adversarial-frame and permission behavior
  are NOT VERIFIED.
- **Production/ONLYOFFICE:** untouched.

This bounded result advances SoundCraft from source/build checks to a real
browser transport smoke. It does not satisfy the project’s Seafile MVP gate or
constitute a project-level GPT review PASS.
