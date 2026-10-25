# GR-046 — EffectCraft host-save browser smoke

**Result:** the exact GR-022 patched EffectCraft WASM passed the bounded
synthetic Chromium open/edit/save/ACK/reopen flow. A same-origin parent opened
a native `.ecproj`, the visible project became dirty after adding a text layer,
Ctrl+S emitted serialized bytes, a matching positive ACK cleared dirty, and a
fresh iframe reopened the captured bytes with the edit visible. The parent kept
the captured bytes in memory; this is not a durable Seafile write. Seafile
version creation/readback, dispatcher routing, deployment and ONLYOFFICE remain
**NOT VERIFIED**. No production or upstream system was contacted or changed.
Independent R1/R2 evidence reviews returned bounded **PROVISIONAL PASS** with
no remaining findings; project GPT review remains pending.

| Check | Observation |
|---|---|
| EffectCraft base | `storytold/effectcraft` `049070d65c66a73f322b496b22521816e0018f14` |
| Shared transport | `craft-platform` `56c5e16d79b77751106173c13111ef4fe0a2c0ec` (Cargo.lock) |
| Stored GR-022 patch SHA-256 | `4e0a1799e36209e1234a1b3ff504ab5ed647cf3bd066af6dec90dacd46ab7407` |
| Built WebAssembly SHA-256 / size | `f7b608a8ce3f768f9f81c75df3431eb9fefd23cd38cd3447d029f7ec9cca1e39` / 56,691,300 bytes |
| Input | Native synthetic `.ecproj`, 32,280 bytes; SHA-256 `cb7852f97d55e8048d8d5cb9f1649085b5cf06ff301104d7fcb608188c0a4ec0` |
| Edit | Added visible text layer `GR-046 runtime edit passed` through EffectCraft's in-app `effectcraft.execute("layer.newText", …)` API; parent observed `dirty=true` |
| Save | Ctrl+S emitted 62,136 bytes; SHA-256 `0828d978e619e0b3afdfd9a8bfba3578b3844aebb9e18f24f412d3eadba2b3d6` |
| ACK | Same-origin parent returned `effectcraft:saveResult` with matching ticket `effectcraft:1` and `ok: true`; editor reported `dirty=false` |
| Reopen | New iframe received the captured in-memory bytes; parent observed clean state and the screenshot shows the edited green text in the composition |
| Browser | T3 collaborative Chromium preview, WebGL2 via SwiftShader software rasterizer |

Evidence bundle and runnable reproduction details are in
[`reviews/GR-046/`](reviews/GR-046/). The browser host is synthetic and stores
the payload only in page memory. This smoke does not prove Seafile persistence,
file dispatch, production authorization/deployment, or ONLYOFFICE behavior.
Independent R1/R2 evidence reviews returned bounded **PROVISIONAL PASS** with
no remaining findings; disposition is **GPT REVIEW PENDING**.
