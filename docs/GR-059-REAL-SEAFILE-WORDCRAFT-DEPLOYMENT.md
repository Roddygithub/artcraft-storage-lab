# GR-059 — Real synthetic Seafile WordCraft deployment and roundtrip

Date: 2026-10-25  
Status: **GPT REVIEW PENDING**  
Scope: one explicitly synthetic DOCX in the owner-managed Seafile instance; one-file allowlist; WordCraft candidate from GR-055. No production content or unrelated libraries were edited.

## Result

The previously missing `/thirdparty-editor/file-save/` route is now deployed and the exact GR-055 WordCraft candidate completed the real browser flow:

1. Clicked `synthetic.docx` from the synthetic library’s Seafile file list.
2. Seafile opened the WordCraft WASM candidate through the configured host page. The editor displayed the document and `synthetic.docx opened`.
3. Added the visible paragraph `ArtCraft Seafile integration test — 25 Oct 2026` through the WordCraft UI, then pressed Ctrl+S.
4. WordCraft displayed `Saved — new version …`; the browser observed the gateway save POST return HTTP 200 and the editor returned to its clean/saved state.
5. Seafile’s file-history UI showed a new current version at 20:38:18 on 2026-10-25 (15.8 KB), above the prior 25.3 KB and 1.6 KB versions.
6. Returned to the file list and clicked the file again. This created a fresh editor iframe/session; WordCraft fetched the document from the gateway and rendered the added paragraph (15 words). The retained screenshot records the reopened content.

This is the first recorded real Seafile version-and-reopen result for the exact deployed WordCraft candidate. It is not a browser download or manual upload. The parent gateway used the user-bound conditional save path; no direct upload command was used.

## Route and deployment record

- Seafile version: 12.0.14 Pro. Only the app’s synthetic DOCX library was placed in `ARTCRAFT_REPO_IDS`; allowed extension is `docx`; max editor file size is 50 MiB. Private repository identifiers and service hostnames are intentionally omitted.
- Seahub patch: `docs/reviews/GR-015/seahub-12.0.14.patch`, SHA-256 `3ace48b53d8ed8468384f75b50f47f49ae19d780ee912a97905258f08b6f8eab` (base `1e9bde801b4360c14d784d9681d4261abc233a8b`). It registers the editor save route and dispatch only for the configured library/extension.
- Seafile C patch: `docs/reviews/GR-015/seafile-server-12.0.14.patch`, SHA-256 `69abef7b322721ce9d5a2c9cdb55f7812ce44acd9dd3db199416997c1b729c9e` (base `32ed9c69594c9faa5cea28024403fcde362589ec`). It registers the conditional upload endpoint.
- Installed `seaf-server` SHA-256: `d7c404143cc583b19ea98058e9b42ef4a1a35b085ddd9c244158b7b425140ebb`. Candidate linked against the Seafile LXC runtime with no missing or undefined dependencies. The route answered 400 to a GET lacking required upload parameters (expected method/validation behavior); the actual browser workflow subsequently exercised the POST path successfully.
- WordCraft was staged outside dispatch from GR-055. The deployed four files were rechecked against the GR-055 inventory (`verify_candidate.py --static-root …`): exact membership, sizes, hashes, and index references passed. Bundle remains outside tracked `integration/static` and dispatch.
- Before live changes, a rollback archive containing the original server binary, Seahub settings, and touched Seahub source files was created and SHA-256 verified on the host and hypervisor: `8fe58dba5eecc218b72d0277a5b0de3340324f354d7b9272ec721be895eba836`. The archive is private and is not in Git. Retain until independent review and post-deployment checks are complete.
- `seafile.service` and `seahub.service` are active after deployment; the synthetic test completed through the deployed stack.

## ONLYOFFICE preservation check

After the restart, opened `synthetic.docx` from the existing synthetic `OnlyOffice/artcraft-lab` folder in a library not included in the ArtCraft allowlist. The Seafile UI opened ONLYOFFICE; representative `/onlyoffice/9.4.0…` assets returned HTTP 200. The document was not edited or saved. `ENABLE_ONLYOFFICE=True` remained set. This is a post-deployment open smoke, not a full post-deployment ONLYOFFICE save/version regression; the latter remains **NOT VERIFIED**. GR-040 retains the separate isolated-stack save/version/reopen evidence.

## Evidence

- Browser observations and sanitized request summary: [runtime transcript](reviews/GR-059/runtime/browser-observations.txt)
- [WordCraft save confirmation screenshot](reviews/GR-059/runtime/wordcraft-save-confirmed.png)
- [Fresh Seafile reopen screenshot](reviews/GR-059/runtime/wordcraft-fresh-reopen.png)
- [Post-deployment ONLYOFFICE open screenshot](reviews/GR-059/runtime/onlyoffice-post-deploy-open.png)
- Screenshot hashes and sizes: [SHA256SUMS](reviews/GR-059/SHA256SUMS)
- Prior synthetic stack and source/patch review: [GR-015 runtime evidence](reviews/GR-015/ISOLATED-RUNTIME-E2E-20261023.md), [GR-055 exact candidate](GR-055-WORDCRAFT-REPRODUCIBLE-CANDIDATE.md).

## Limits / next checks

- **Proven:** exact deployed WordCraft candidate, real Seafile file-list click, user-visible edit, durable new Seafile version/history entry, editor save confirmation, fresh editor session reopening the edit; ONLYOFFICE still opens an out-of-allowlist synthetic DOCX.
- **Not verified:** ONLYOFFICE edit/save after this deployment; permission revocation, capability expiry/replay, external Seafile writers, response-loss and recovery on this live instance; other file types/apps; cross-origin/TLS/proxy/CSP production topology; broader security/deployment readiness; optimized bundle performance; production library behavior.
- Gateway size remains 50 MiB; only the configured synthetic DOCX library is dispatched to WordCraft. No dispatch table was changed.
- This bounded result does not change project verdict **INCOMPLETE**, does not establish public deployment readiness, and does not unlock upstream publication. The route rollout was authorized for the synthetic target and has a verified rollback archive; no Seafile or ONLYOFFICE uninstall, disable, or broad config change occurred.

## Reproduction boundary

The deployment is attached to an owner-specific live Seafile and tailnet. This report intentionally omits its private hostname, repository UUID, session capability, and user details. Reproduction requires the owner’s logged-in browser and the private deployment config; do not copy credentials or private host identifiers into repository files.
