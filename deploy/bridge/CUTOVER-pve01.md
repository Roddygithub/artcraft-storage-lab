# Production cutover runbook — pve01 homelab (PREPARED, NOT EXECUTED)

Status: **PREPARED 2026-11-17, execution requires explicit owner authorization.**
Everything below was verified read-only against the real environment. Nothing on
the production Seafile (LXC 108) was changed. `UPSTREAM_STATUS=LOCKED`.

## Discovered production facts (read-only inspection)

| Item | Value | Evidence |
| --- | --- | --- |
| Proxmox host | pve01, pve-manager 9.2.26, 4 cores, 7.6G RAM (3.1G avail), thin pool 155G @ 68.7% | `pveversion`, `free`, `lvs` 2026-11-16 |
| Production Seafile | LXC 108, unprivileged Debian, **native** Seafile 12.0.14 at `/opt/seafile`, nginx + tailscaled inside CT | `pct config 108`, processes, `SEAFILE_VERSION` |
| Public origin | `https://svc-seafile-host.tailb64fb1.ts.net` (tailscale, valid cert) | `seahub_settings.py` (read-only) |
| Data location | everything inside rootfs `/dev/mapper/pve-vm--108--disk--0` (20G, 14G used); **no bind mounts** | `pct config 108`, `df` |
| Backups | vzdump daily 03:00, mode snapshot, all guests → `/mnt/backup-ssd`, keep 3/2/2; snapshot covers the **entire** CT (rootfs-only, no external volumes) | `/etc/pve/jobs.cfg`, `storage.cfg` |
| Backup verified | `vzdump-lxc-108-2026_11_17-03_12_13.tar.zst` (12G), `zstd -t` → INTEGRITY_OK | read-only check 2026-11-17 |
| WOPI state | **disabled** (no `ENABLE_OFFICE_WEB_APP` in seahub_settings.py) | read-only grep |
| Legacy ArtCraft route | custom Seahub settings: `ARTCRAFT_REPO_IDS` (one synthetic library), `ARTCRAFT_ACTION_URL=https://omarchydesktop-1.tailb64fb1.ts.net/open/`, docx/xlsx/pdf/svg/pptx extensions | read-only grep |
| Legacy gateway | LXC 114 (running) + desktop user services `artcraft-gateway.service`, `artcraft-tunnels.service` (tunnels 18000/18082/18777 via pve01) + desktop `tailscale serve` 443→127.0.0.1:8777 | running processes, `tailscale serve status` |
| Reverse proxy | NPM LXC 103 routes `seafile.home.arpa` (LAN name); prod public route is the CT's own nginx + tailscale | NPM config (read-only) |

## Validated isolated deployment (candidate `aec8e95` / bridge `123d2a0`, 2026-11-16/17)

Isolated clone of the production shape on LXC 115 `craft-test` (disposable):
Seafile CE 12.0.14 (pinned image digest `sha256:7bbe7043…`, same as lab evidence)
+ the bridge built from `deploy/bridge/Dockerfile` at candidate
`aec8e95` (bridge `123d2a0`) + the three verified editor bundles (wordcraft
v0.13.2, gridcraft v0.14.2, deckcraft v0.16.0; SHA-256 manifest matches the
2026-11-16 byteproof run). HTTPS via `tailscale serve` on omarchydesktop-1
(ports 8443/8444, valid certs; production 443 route untouched).

Result: **66/66 automated real-browser assertions** (WordCraft 24, GridCraft 27,
DeckCraft 15): open → edit → save → new version attributed to the opener →
fresh-browser-context reopen with bytes identical (relay==readback), second edit
persisted, `downloads=0`. Evidence: private run `deploy-proxmox/e2e/results/`,
sanitized copies under `lab/real-seafile/results/2026-11-17-proxmox-isolated/`.

Hardware acceptance (headed Chromium on real Omarchy/Wayland, GTX 1060):
- GPU/WebGPU identity confirmed (ANGLE NVIDIA, WebGPU vendor=nvidia pascal, isFallback=null)
- Clipboard OS→editor: visually accepted but NOT persisted in saved DOCX (WordCraft canvas limitation) — NOT VERIFIED
- Clipboard editor→OS: NOT VERIFIED (canvas WASM editor cannot write OS clipboard)
- Dirty close: beforeunload prompted, unsaved edit discarded, saved version intact — PASS
- Read-only user save refused via bridge relay — PASS (Seafile CE 12.0.14 limitation: personal repo shares don't propagate to web API for recipient)
- Network outage (container stop/start): save fails dirty kept, recovery succeeds — PASS
- Session expiry (TTL 120s): expired save downloads file, reopen works, new save creates version — PASS

Evidence retained: `lab/real-seafile/results/2026-11-17-proxmox-isolated/` (sanitized JSON, byte-proof artifacts, screenshots, provenance.json, SHA256SUMS, verify.py).

## Prepared change scope (NOT EXECUTED)

1. `pct snapshot 108 pre-artcraft-wopi-20261117` (rollback anchor; seconds).
2. Create production bridge LXC 116 `craft-bridge` (1 core, 1G RAM, 8G rootfs):
   same `deploy/bridge` image + verified bundles; `BRIDGE_PUBLIC_URL=https://pve01.tailb64fb1.ts.net:8445`,
   `BRIDGE_SEAHUB_ORIGIN=https://svc-seafile-host.tailb64fb1.ts.net`;
   `tailscale serve --bg --https=8445 http://192.168.1.116:8778` on pve01
   (valid cert, tailnet-only); relay leg `socat TCP-LISTEN:443,bind=192.168.1.10,fork TCP:100.96.244.20:443`
   on pve01 + `extra_hosts: svc-seafile-host…→192.168.1.10` (same split-horizon
   pattern proven on the isolated deployment).
3. Append to LXC 108 `seahub_settings.py` (the **only** production file change):
   ```python
   ENABLE_OFFICE_WEB_APP = True
   OFFICE_WEB_APP_BASE_URL = 'http://192.168.1.116:8778/wopi/discovery.xml'
   OFFICE_WEB_APP_FILE_EXTENSION = ('docx', 'xlsx', 'pptx')
   ENABLE_OFFICE_WEB_APP_EDIT = True
   OFFICE_WEB_APP_EDIT_FILE_EXTENSION = ('docx', 'xlsx', 'pptx')
   ```
   Do **not** enable view-only legacy routes (odt/ods/csv/ppsx): Seahub PutFile
   ignores the token's `can_edit` (see `docs/security/HOST_PERMISSION_BOUNDARY.md`),
   so view tokens are unsafe for any untrusted viewer.
4. Restart Seahub (~30–60 s interruption; Seafile file service keeps running).
5. Create a dedicated synthetic test account + synthetic library (never the
   owner's account), then run the 66-assertion browser suite against production.

## Coexistence findings that gate the cutover

**Routing precedence (verified in Seahub 12.0.14 source):**

| Route | Priority | Scope |
| --- | --- | --- |
| **ARTCRAFT** (legacy gateway) | 1st | Only repo `d2f6e03c-b171-46b4-b7f3-255c6b9eeee9` for docx/xlsx/pptx/pdf/svg/designcraft/fcproj/pcraft |
| **THIRDPARTY_EDITOR** | 2nd | Any repo with matching extension in `THIRDPARTY_EDITOR_ACTION_URL_DICT` |
| **WOPI** (new bridge) | 3rd | ALL repos for extensions in `OFFICE_WEB_APP_FILE_EXTENSION` / `OFFICE_WEB_APP_EDIT_FILE_EXTENSION` |
| **ONLYOFFICE** | 4th | ALL repos for extensions in `ONLYOFFICE_FILE_EXTENSION` |

- The legacy `ARTCRAFT_*` Seahub patch routes docx/xlsx/pptx clicks to the old gateway for **one allowlisted repo**. With WOPI enabled for those extensions, **ARTCRAFT wins for that repo** (checked first in `seahub/views/file.py`). WOPI handles all other repos.
- Stock Seahub 12 WOPI routing is **extension-wide**: enabling docx/xlsx/pptx WOPI affects **every** library, not only a canary library. Verify affected users with the owner first.
- The old gateway must keep running until the new route is verified; removal is a separate, later, explicitly authorized change.
- **No canary possible** for WOPI on docx/xlsx/pptx without also affecting the ARTCRAFT repo (which would change its behavior).

## Health checks and rollback criteria

| Check | Command | Pass |
| --- | --- | --- |
| Bridge alive | `curl -f https://pve01.tailb64fb1.ts.net:8445/healthz` | `ok` |
| Seahub alive | `curl -f https://svc-seafile-host…/api2/ping/` | `pong` |
| Discovery reachable from Seahub | inside CT 108: `curl -sf http://192.168.1.116:8778/wopi/discovery.xml` | XML |
| E2E | synthetic account browser suite | 66/66 |

Rollback (any failed check): remove the appended settings block from
`seahub_settings.py`, restart Seahub, verify `/api2/ping/` and a manual file
open; optionally `pct rollback 108 pre-artcraft-wopi-20261117` (destroys the
post-snapshot delta — use only if the settings edit is lost). The bridge LXC is
deleted with `pct destroy 116`; tailscale serve / socat entries on pve01 are
removed with `tailscale serve --https=8445 off` + `systemctl disable --now`.
Never roll back by deleting the old gateway or production containers.

**Rollback warning**: `pct rollback` destroys all changes since the snapshot.
Only use if the settings edit is lost and cannot be reverted by editing the file.

## Security gates that still bind

1. `can_edit` host boundary: fine for the owner's trusted single-user scope;
   any untrusted viewer of an edit-routed library must be treated as able to
   overwrite files via direct Seahub `PutFile` until Seafile fixes it.
   (See `docs/security/HOST_PERMISSION_BOUNDARY.md`)
2. Concurrency: documented non-atomic preflight; sequential saves verified
   (stale-version rejection), concurrent safety NOT claimed.
3. Reverse proxy: tailscale serve imposes no body-size limit; the bridge caps
   request bodies at `max_bytes` (256 MB default) and rejects oversize with 413.
   Set a smaller cap if untrusted clients appear.
4. Token TTL: bridge validates token format; Seahub controls expiration via
   `WOPI_ACCESS_TOKEN_EXPIRATION` (default 30 min). Verified expiry flow works.

## Hardware acceptance limitations (honestly recorded)

| Check | Status | Reason |
| --- | --- | --- |
| Clipboard OS → editor | NOT VERIFIED | Paste visually accepted but NOT persisted in saved DOCX (WordCraft canvas limitation) |
| Clipboard editor → OS | NOT VERIFIED | Canvas WASM editor cannot write OS clipboard |
| Read-only user access | NOT VERIFIED | Seafile CE 12.0.14: personal repo share via RPC doesn't propagate to web API for recipient |

These are **editor/Seafile limitations**, not bridge failures. Documented for transparency.

---

**PRODUCTION_CUTOVER: NOT EXECUTED**  
**PRODUCTION_APPROVAL: PENDING**  
**GPT_FINAL_GATE: PENDING**  
**UPSTREAM_STATUS: LOCKED**