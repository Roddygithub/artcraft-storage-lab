# GR-076 runtime evidence

## Result

The low-optimization GR-076 PhotoCraft Web bundle completed the required
synthetic Seafile workflow: open from the Seafile file list, edit, save, observe
the editor's “Saved to host” confirmation, close, reopen from the file list, and
see both edits intact. Seafile history gained a version for each save. The
sanitized readback record is [seafile-readback.json](seafile-readback.json);
the final save and fresh reopen screenshots are retained below.

This is a functional lab result for one synthetic `.pcraft` document and the
synthetic ArtCraft library. It is not a production readiness or broad
compatibility claim. The bundle used `wasm-opt=0` and disabled LTO to keep the
laptop responsive. Optimized bundle, browser unload/clock behavior, proxy/CSP
behavior and production remain **NOT VERIFIED**.

## Workflow observations

| Step | Result |
|---|---|
| Initial fixture | 4,000 bytes; SHA-256 `c5fe5c8fb2bd9b38b4a0de1ad4ebc9c6e97006100e2b25e147265e2666b5a3c2` |
| Open from Seafile | File-list click routed to PhotoCraft; gateway `/open/` returned HTTP 200 and editor document fetch returned HTTP 200 |
| First edit/save | Added `Layer 1`; gateway save returned HTTP 200; editor displayed “Saved to host”; Seafile history contained a 4,984-byte new version |
| Second edit/save | Reopened via Seafile file list, added `Layer 2`, saved; gateway save returned HTTP 200 and editor displayed “Saved to host” |
| Version/readback | Seafile history showed 3 versions, sizes 5,968 / 4,984 / 4,000 bytes. Current file size was 5,968 bytes and matched the latest history entry. Browser readback SHA-256 `38ec64312bc6220f8afdaebb61120d027a826abfe0f3c8152812faaf124f101d` |
| Close/reopen | Closed the editor, clicked the file in the Seafile list again; new `/open/` and document fetch returned HTTP 200. Reopened editor showed `Layer 1`, `Layer 2`, and “no changes” |

The browser readback used the authenticated Seafile page context and kept bytes
in memory; no download or manual upload was used. No cookie, credential, user
name, server address, session identifier or capability URL is retained here.

## Runtime changes and rollback

| Item | Before / after |
|---|---|
| Gateway dispatch | Before SHA-256 `af3c4cbbb76f3583b0bb70118c48ebd7445bc2841e577658918edd7c43f83c2d`; after `5626251152dc05fb1949a8fcc1dc6cd18d55bce75c2abd8b0e9b70b822fcf3d3`. Existing seven routes retained; one `pcraft` route added |
| Seafile settings | Before SHA-256 `38162e03aef79c048e5a9334e2fd70ae04ca145b62703027f9caddacb0f69741`; after `52ad0470c2c63c72605e9d129df0be25522a3ffd670c0fa644e387996d95f23b`. Only `ARTCRAFT_FILE_EXTENSIONS` changed, adding `pcraft` |
| ONLYOFFICE | `ENABLE_ONLYOFFICE=True` before and after; no ONLYOFFICE config or service change |
| Static bundle | PhotoCraft static directory was absent before deployment. Deployed WASM SHA-256 `71e6594e78d33fa75ceebec5d981e7efaa1ab8bbafd21f86fdf2412f8f14a23a`, JS `f5280d32f337882597b4118ea6d528d975374933c3cfd865a1be6c417dd76484`, index `a60830b647db7dcacfb43e7de45cd4bdd9cf7f1174a71b502a89d4bef7c7772d` |
| Rollback copies | Seafile settings backup: `/root/artcraft-rollbacks/gr077-20261026-122115/seahub_settings.py`; gateway dispatch baseline: `/home/roddy/.cache/artcraft-storage-lab/gr077-dispatch.base.json` (SHA-256 matches the recorded pre-change dispatch) |

The allowlist is scoped by the pre-existing `ARTCRAFT_REPO_IDS` setting to the
synthetic library. If rollback is needed, restore the two backups and remove
the newly created PhotoCraft static directory, then restart only the gateway
and Seafile web service. No production library was targeted. The runtime
change is reversible; no rollback was performed after the successful smoke.

## ONLYOFFICE regression status

After the Seafile extension update, a synthetic DOCX was selected in Seafile.
The route rendered a blank preview and no ONLYOFFICE editor or editor network
assets appeared. This attempt is **INCONCLUSIVE / NOT VERIFIED**, not a pass.
ONLYOFFICE settings were read before and after and remained enabled and
unchanged. A separate GR-072 synthetic-document smoke had previously exercised
ONLYOFFICE; it does not establish this post-change UI check.

## Bundle and prior in-memory smoke

This is a functional build, not an optimized production bundle. Build settings
were `CARGO_BUILD_JOBS=1`, `CARGO_PROFILE_WASM_RELEASE_LTO=false`, and temporary
`data-wasm-opt=0`; the tracked source index was restored after building. Rust
was 1.95.0 and Trunk 0.22.0. The initial local in-memory host smoke is retained
in the screenshot below and its original event/hash observations remain in
repository history; the Seafile workflow above is the decisive persistence
evidence.

## Screenshots and evidence

- [Final save confirmation](photocraft-seafile-saved.png), SHA-256
  `b125c49e403c1a31a9cdb3bfb9ca4145a26e2014fe10086a1de97b8148873287`.
- [Fresh Seafile reopen with both layers](photocraft-seafile-reopen.png),
  SHA-256 `b60193ba19e61fdc935e75977cf004d58f386a122e41b36a280fda49e9c7ad0e`.
- [Earlier in-memory fresh iframe smoke](photocraft-browser-reopen.png), SHA-256
  `c1953f36319a5a2c5d0a523d70a68a3e1f3cd2a37c044c453aa40dfcbab03fb6`.

All claims are bounded by this synthetic run. They do not establish concurrency
conflict handling, token expiry/revocation, maximum-size behavior, proxy
configuration, optimized assets or production readiness.
