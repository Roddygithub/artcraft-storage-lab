# GR-036 — PhotoCraft Seafile version and reopen

## Result

Reproduced a bounded PhotoCraft Web/WASM workflow against the isolated
synthetic Seafile stack: Seahub file open → PhotoCraft host Open → add a layer
→ Ctrl+S → Seafile version/readback → fresh Seahub open. The editor displayed
“Saved to host” after the gateway save returned successfully. A fresh editor
session loaded the saved layer from Seafile.

This is the first recorded PhotoCraft storage-backed round trip. It does not
change the committed dispatcher or establish production deployment readiness.

## Exact scope and evidence

| Item | Evidence |
|---|---|
| PhotoCraft source | `storytold/photocraft` base `a02f2ee41059d3312e7ff24a5af5edcac7b6435a`, plus the GR-032 adapter and GR-036 repaint fix |
| GR-036 incremental patch | [`photocraft-host-repaint.patch`](reviews/GR-036/photocraft-host-repaint.patch), SHA-256 `e3af083933f035ddb557f67a1d3d148a9056780dc46c135e93f1722e5acf584e` |
| Functional browser build | `trunk build --release`; `wasm-opt=0` for this reproduction. WASM: 35,820,040 bytes, SHA-256 `d4f339df6312429fa15de653a37b3ef156cee84a3c58eee1358caee34523324c` |
| Initial Seafile object | 4,000 bytes, SHA-256 `c5fe5c8fb2bd9b38b4a0de1ad4ebc9c6e97006100e2b25e147265e2666b5a3c2` |
| Saved object readback | 4,984 bytes, SHA-256 `92e93c2b993b7de073a2c870aba522d7f9112647d9d1181d2b8592df665936b3`; ZIP manifest contains `Layer 1` |
| Seafile history | 1 → 2 versions. New head commit `a19b117254ed9c0382b6a55a2cd53ccd3c33068a`; file ID changed from `2be21dab7ba8a2b5843bb965ad25616d59ba1415` to `555181a4a3fa85916107c4fc3af75eb13ab67373`; current size 4,984 bytes |
| Fresh reopen | Fresh Seahub file route created a new host session; its document GET returned 200 and PhotoCraft displayed `Layer 1`. Screenshot: [`photocraft-seafile-reopen-20261025.png`](reviews/GR-036/runtime/photocraft-seafile-reopen-20261025.png), SHA-256 `70d28c90f7ece27782863fbb15d98be74ac81ac89d9535782fe0aae13f0aecab` |

After the independent reviewer noted that the screenshot alone could not
substantiate Seafile metadata, a separate read-only API check was run and its
redacted result retained as
[`seafile-readback.json`](reviews/GR-036/runtime/seafile-readback.json). It
confirmed the two history entries, IDs, byte count, hash and manifest content.
The check can be rerun against the synthetic test library with credentials
provided only through the environment:

```sh
python3 docs/reviews/GR-036/runtime/verify_seafile_readback.py \
  a1a2768f-a6ea-4e18-858f-b09e3f64a11d /photocraft-gr035.pcraft
```

The script performs GET requests only and prints no credential or download
capability URL. Set `ARTCRAFT_SEAFILE_URL` and `ARTCRAFT_SEAFILE_TOKEN` in the
environment before running it.

The host listener queues asynchronous events. The GR-036 change requests an egui repaint after queueing, so the idle frame processes the delayed host Open/ACK. The observed browser run then opened the received document; the evidence establishes the behavior with this fix, not a universal diagnosis of every previous non-opening run.

The temporary synthetic gateway configuration routed `.pcraft` to PhotoCraft. The repository's `integration/config/dispatch.json` was not changed. The saved file was small enough for the gateway's default 50 MiB limit.

## Limits

- Synthetic loopback Seahub/gateway only; no production Seafile, TLS, proxy, CSP, CSRF, cross-origin, permission-revocation or adversarial-frame validation.
- `wasm-opt=0`: this is a functional release-profile bundle, not optimized production output.
- The screenshot shows the reopened editor state; request/status observations and Seafile history/readback establish the save path. The exact browser `postMessage` payload was not separately captured and hashed at the editor-to-gateway boundary.
- ONLYOFFICE regression was not tested. Its configuration was not changed.
- PhotoCraft remains excluded from the committed dispatch. This bounded E2E is not a project-level GPT PASS and does not authorize upstream publication.

## Review state

Independent bounded review returned PROVISIONAL ACCEPT with no blocker/major.
The reviewer correctly noted that Seafile metadata was not in the original
bundle; the read-only result above was added afterward. This is a bounded
evidence review, not a project GPT verdict. No upstream repository was
modified.
