# GR-035 — PhotoCraft optimized Web host-protocol smoke

**Status:** bounded browser smoke on an optimized local Web bundle. This is not
Seafile persistence, a project GPT PASS, or publication approval.

## Result

The GR-032 PhotoCraft host adapter was rebuilt as a release Web bundle with
Trunk's `wasm-opt -Oz` stage enabled, then loaded in Chromium inside the
same-origin GR-033 parent harness. A synthetic `.pcraft` opened, a new
PhotoCraft layer was created, Save emitted bytes and a ticket, the harness
returned a matching positive ACK, and a fresh iframe reopened those bytes with
the layer present and the editor clean.

This improves the build/runtime evidence for PhotoCraft. The harness retained
the save bytes in JavaScript memory only. It did not contact Seafile, create a
Seafile version, or prove storage-backed reopen.

## Reproduction record

| Item | Evidence |
|---|---|
| PhotoCraft base | `storytold/photocraft` `a02f2ee41059d3312e7ff24a5af5edcac7b6435a` |
| Adapter | GR-032 combined patch SHA-256 `487935d8f6db33cf82c85f8d9c8aa0686016612510f15cf34f6b3f05a2c53fe7` |
| Build | `trunk build --release` from `apps/photocraft-web`; Trunk 0.22.0; release WASM and `wasm-opt -Oz` completed successfully |
| Bundle | WASM 26,342,447 bytes; SHA-256 `f67193223bc7367bade2bca00e105ee856eafc892eda538a2112a86df13f155b` |
| Browser | T3 Chromium, same-origin static parent and iframe, local only |
| Open fixture | 4,000-byte GR-033 synthetic PhotoCraft fixture |
| Save result | Ticket `photocraft:73ca0f8a5ac6f87c3dd6fdc34c4a67c2:1`; 4,984 bytes; SHA-256 `92e93c2b993b7de073a2c870aba522d7f9112647d9d1181d2b8592df665936b3` |
| Reopen | Fresh iframe received the retained save bytes; `Layer 1` visible and host reports `dirty=false` |

The screenshot is in [the evidence bundle](reviews/GR-035/README.md). The
build came from the local GR-033 apply-check checkout and was served through a
temporary cache directory; no app bundle or dispatcher change was added to
the repository.

## Independent review

Nemotron 3 Ultra returned **PROVISIONAL ACCEPT** for this bounded smoke, with no
blocker or major finding. The screenshot does not identify the WASM resource
hash Chromium loaded; although the optimized artifact and source configuration
were independently inspected, that exact browser-to-artifact binding remains
NOT VERIFIED.

## Limits

- The parent stores saved bytes in memory; no gateway request or Seafile write
  occurred. Durable version creation and a fresh read from Seafile remain
  **NOT VERIFIED**.
- The PhotoCraft runtime was not wired into the temporary Seafile dispatcher;
  `.pcraft` remains excluded from the committed dispatch table.
- The screenshot and payload hash establish this local smoke only. They do not
  verify production deployment, authorization, conflict handling, ONLYOFFICE
  behavior, or all PhotoCraft features.
- This smoke does not change the project's GPT review status or authorize
  upstream publication.
