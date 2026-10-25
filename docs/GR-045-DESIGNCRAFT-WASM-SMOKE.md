# GR-045 — DesignCraft host-save browser smoke

**Result:** synthetic runtime smoke passed in Chromium using the actual GR-021
patched DesignCraft WASM. The parent kept bytes in page memory and returned a
matching positive ACK. No Seafile write occurred; persistence remains **NOT
VERIFIED**. No upstream or production changes were made. Independent bounded
reviews R1 and R2 returned **PROVISIONAL PASS** with no remaining findings;
GPT review is pending.

| Item | Result |
| --- | --- |
| DesignCraft source | `storytold/designcraft` `80d13911b2d20fbb5cd9398696627bb3a715417b` |
| Shared transport | `craft-platform` `56c5e16d79b77751106173c13111ef4fe0a2c0ec` (Cargo.lock) |
| GR-021 patch SHA-256 | `519c03180b17f035ef8fbfcd08a85bda312f6f0721bfbdf9dc1d9d5992fdf972` |
| WASM SHA-256 / size | `e06f61ce6f004653ed2d9adfb1d3db1b363b2c6bab0c1b025b760b57aeec446c` / 49,467,912 bytes |
| Input | Synthetic native `.designcraft`, 6,585 bytes |
| Edit | Changed the visible text frame to `GR045 runtime edit passed`; parent observed `dirty=true` |
| Save | Ctrl+S emitted 3,184 bytes; SHA-256 `77e282dbc6c3cc5a29f541193a356e6029b785199c38d859eb074983b01f7cce` |
| ACK | Parent sent matching positive `designcraft:saveResult` for `designcraft:1:1`; app reported `dirty=false` |
| Reopen | Fresh iframe opened the captured bytes; the visible edit remained and app was clean |
| Browser renderer | Chromium WebGL2 via SwiftShader software rasterizer |

The same-origin synthetic parent and exact input/output bytes are in
[`reviews/GR-045/`](reviews/GR-045/). The screenshot shows the fresh iframe and
the edited text. This proves the patched app's browser open/edit/save/ACK/reopen
path only. It does not prove a Seafile version, gateway/dispatcher routing,
production behavior, or ONLYOFFICE behavior.
