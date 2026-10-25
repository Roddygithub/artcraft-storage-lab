# GR-033 — PhotoCraft browser host-protocol smoke

## Result

**Bounded browser protocol smoke reproduced; Seafile persistence NOT VERIFIED.**
In a local same-origin Chromium preview, the actual PhotoCraft Web/WASM app opened
a synthetic `.pcraft`, accepted a real UI edit, serialized and sent save bytes,
remained dirty until a ticket-matched positive ACK, then reported clean. A fresh
iframe reopened the parent-retained save bytes and displayed the added layer.

The parent held bytes only in JavaScript memory. No Seafile API, gateway write,
new server version, or production instance was involved. This is not the
Seafile MVP gate, a project GPT review PASS, or upstream publication approval.

## Evidence

| Item | Evidence |
|---|---|
| Application | PhotoCraft Web/WASM 0.15.1, built from the GR-032 patch on pinned source SHA `a02f2ee41059d3312e7ff24a5af5edcac7b6435a` |
| Host protocol | Same-origin parent harness; exact parent source and origin checked |
| Input | Synthetic 8×8 RGB `.pcraft`, 4,000 bytes, SHA-256 `c5fe5c8fb2bd9b38b4a0de1ad4ebc9c6e97006100e2b25e147265e2666b5a3c2` |
| Edit | Created a layer named `GR-033 saved layer` in the editor UI |
| Save | Ticket `photocraft:6456eeeb370a2f687d0da2e37209279c:1`; `photocraft-smoke.pcraft`; `saveAs=false`; 4,995 bytes; SHA-256 `cbaa7b458588780210d1da7a267d2d5223d6808e0b15ea9e80e84d23ea980f34` |
| ACK | Parent sent a positive result for the matching ticket; editor reported `dirty=false` |
| Reopen | New iframe instance opened those exact retained bytes; screenshot shows the added layer and clean state |
| Capture | [`photocraft-host-reopen-20261025.png`](reviews/GR-033/runtime/photocraft-host-reopen-20261025.png), SHA-256 `d29264293f53dd014383a1d3cf82347e34b2c509ebda887a71637ab860158697` |
| Harness | [`host.html`](reviews/GR-033/runtime/host.html), SHA-256 `e3c09714ff5dcca51cff43b5d80ae0202286057c34a3ed3ebaa27193947e5feb` |

Build details, repeatable local commands and the browser event log are recorded
in [`docs/reviews/GR-033/README.md`](reviews/GR-033/README.md). The smoke build
used a release profile with `wasm-opt=0`; it is functional build evidence, not
an optimized production bundle. The browser emitted a 404 for the optional
font manifest; this did not prevent the tested flow.

## Limits and next step

This run does not prove durable storage, a new Seafile version, conflict or
permission handling against Seafile, cross-origin deployment, ONLYOFFICE
non-regression, or general PhotoCraft support. PhotoCraft remains absent from
the committed dispatch. Next meaningful milestone is an isolated synthetic
Seafile run with a real Seahub file selection, user-bound save, new version,
and fresh storage-backed reopen; the 50 MiB gateway request ceiling and
PhotoCraft's post-serialization size check must be respected.

No upstream app source, production Seafile, or ONLYOFFICE configuration was
changed.
