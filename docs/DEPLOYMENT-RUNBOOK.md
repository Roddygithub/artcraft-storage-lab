# Deployment Runbook — WOPI Editor Bridge

For the zero-patch candidate (`bridge/` + upstream bundles + Seahub config only).  
Target: self-hosted Seafile CE/Pro ≥ 13.0 behind TLS.

---

## 0. Prerequisites (check before starting)

| Item | Required | Notes |
|------|----------|-------|
| Seafile version | ≥ 13.0 | WOPI slot for non-office extensions needs Seahub 13+ |
| Domain for bridge | `craft.example.org` | **Separate origin** from Seafile (cookie isolation, CSP `frame-ancestors`) |
| Domain for Seafile | `seafile.example.org` | Already running |
| TLS certificates | Valid certs for both domains | Let's Encrypt, ACME, or your CA |
| DNS | A/AAAA for both domains → your server | |
| Docker + Compose v2 | On target server | `docker compose version` |
| RAM | ≥ 2 GiB free for bridge + editors | Editors are static; bridge is ~50 MiB |
| Disk | ≥ 1 GiB for editor bundles | 5 apps × ~150 MB |

---

## 1. Prepare the bridge host

```bash
# On your server
mkdir -p /opt/artcraft-bridge && cd /opt/artcraft-bridge

# Copy the entire deploy/bridge/ directory here (or clone the repo and use that path)
# Assuming you have the repo at ~/artcraft-storage-lab:
cp -r ~/artcraft-storage-lab/deploy/bridge/* .
# Or: git clone https://github.com/Roddygithub/artcraft-storage-lab.git /tmp/acs && cp -r /tmp/acs/deploy/bridge/* .
```

---

## 2. Fetch editor bundles (exact upstream releases, SHA-256 verified)

```bash
cd /opt/artcraft-bridge

# Default: CADCraft only (DXF)
./fetch-editors.sh cadcraft v0.15.1 4d8acce3209082699078aa868ef79fedd4437ba0d18014a0f031d118a0abceb8

# Optional: add WordCraft (DOCX), GridCraft (XLSX), PdfCraft (PDF)
# Each line is independent; run only what you need.
./fetch-editors.sh wordcraft v0.13.2 b6c9c8d3a730495189ba0c213fe64313f317be8fc0611ac1ff8cdd6a4b20880c
./fetch-editors.sh gridcraft v0.14.2 f6675cfe26f89f07cb9d9ff23a5ae0a946088eef6e22c93ac1141f0279f741f8
./fetch-editors.sh pdfcraft v0.16.1 00f3e85e29bb9dfa3d43a655cc4197cdc679f4ec7e8ef1bb5e623dc3603c0edf

# Verify
ls -la editors/
# Should show: cadcraft/  wordcraft/  gridcraft/  pdfcraft/
# Each with PROVENANCE.txt containing the exact release tag + SHA-256
```

**To update later**: re-run the same command with a new tag/SHA — the script overwrites atomically.

---

## 3. Configure `editors.json`

```bash
cd /opt/artcraft-bridge

# Default (CADCraft only) is already correct:
cat editors.json
# {
#   "cadcraft": {"app": "cadcraft", "label": "CADCraft", "extensions": ["dxf"], "url": "/editors/cadcraft/index.html?host=parent"}
# }

# If you added WordCraft/GridCraft/PdfCraft, edit editors.json:
cat > editors.json <<'EOF'
{
  "cadcraft":  {"app": "cadcraft",  "label": "CADCraft",  "extensions": ["dxf"],  "url": "/editors/cadcraft/index.html?host=parent"},
  "wordcraft": {"app": "wordcraft", "label": "WordCraft", "extensions": ["docx"], "url": "/editors/wordcraft/index.html?host=parent"},
  "gridcraft": {"app": "gridcraft", "label": "GridCraft", "extensions": ["xlsx"], "url": "/editors/gridcraft/index.html?host=parent"},
  "pdfcraft":  {"app": "pdfcraft",  "label": "PdfCraft",  "extensions": ["pdf"],  "url": "/editors/pdfcraft/index.html?host=parent"}
}
EOF
```

**Rule**: Every extension in `editors.json` must also be in **both** `OFFICE_WEB_APP_FILE_EXTENSION` and `OFFICE_WEB_APP_EDIT_FILE_EXTENSION` in Seahub (step 6).

---

## 4. Create `.env` with your domains

```bash
cd /opt/artcraft-bridge
cat > .env <<'EOF'
# PUBLIC HTTPS origin of the bridge (what users type in browser)
BRIDGE_PUBLIC_URL=https://craft.example.org
# HTTPS origin of your Seafile (what users type for Seafile)
BRIDGE_SEAHUB_ORIGIN=https://seafile.example.org
EOF
chmod 600 .env
```

---

## 5. Configure nginx (TLS termination + proxy)

```bash
# Install nginx if not present
# Ubuntu/Debian: apt-get install nginx
# Or use your existing reverse proxy (Nginx Proxy Manager, Traefik, Caddy...)

# Copy the example and edit
cp nginx.conf.example /etc/nginx/sites-available/craft-bridge
# Edit: server_name, ssl_certificate, ssl_certificate_key paths
# If using Let's Encrypt + certbot:
# certbot --nginx -d craft.example.org

# Enable and test
ln -sf /etc/nginx/sites-available/craft-bridge /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
```

**Key nginx settings** (already in `nginx.conf.example`):

- `client_max_body_size 256m` — documents saved via `/relay/save`
- `proxy_request_buffering off` on `/relay/save` — streams large bodies
- `proxy_read_timeout 600s` on `/relay/save` — PutFile + Seafile commit can take >2 min
- **No `Cache-Control` override** — bridge sets correct headers itself

---

## 6. Configure Seahub (append to `seahub_settings.py`)

```bash
# On the Seafile host (may be different from bridge host)
SEAHUB_CONF=/opt/seafile/conf/seahub_settings.py  # or wherever yours lives

# Backup first!
cp "$SEAHUB_CONF" "$SEAHUB_CONF.backup-$(date +%F-%H%M)"

# Append the managed block (edit OFFICE_WEB_APP_BASE_URL to your bridge domain)
cat >> "$SEAHUB_CONF" <<'EOF'

# >>> artcraft-bridge (managed block)
ENABLE_OFFICE_WEB_APP = True
OFFICE_WEB_APP_BASE_URL = 'https://craft.example.org/wopi/discovery.xml'
OFFICE_WEB_APP_FILE_EXTENSION = ('dxf', 'docx', 'xlsx', 'pdf')   # view
ENABLE_OFFICE_WEB_APP_EDIT = True
OFFICE_WEB_APP_EDIT_FILE_EXTENSION = ('dxf', 'docx', 'xlsx', 'pdf')  # edit
WOPI_ACCESS_TOKEN_EXPIRATION = 30 * 60
# <<< artcraft-bridge
EOF

# IMPORTANT: match the extensions above with your editors.json exactly!
# Only list extensions you actually fetched bundles for.
```

---

## 7. Start the bridge

```bash
cd /opt/artcraft-bridge
docker compose up -d --build

# Wait for healthy
docker compose ps
# bridge should show: Up X minutes (healthy)

# Verify endpoints
curl -s https://craft.example.org/healthz
# → ok

curl -s https://craft.example.org/wopi/discovery.xml | head -30
# → <wopi-discovery> with <action name="view" ext="dxf" ...> and <action name="edit" ext="dxf" ...>
```

---

## 8. Restart Seahub (picks up new WOPI discovery)

```bash
# On Seafile host
systemctl restart seahub
# Or: docker restart seafile  (if containerized)
```

Wait ~10 s for Seahub to fetch the discovery XML from the bridge.

---

## 9. Quick smoke test (before full checklist)

```bash
# In browser: https://seafile.example.org
# 1. Log in
# 2. Upload a .dxf file to a library
# 3. Click the file in the file list
# 4. Should open in CADCraft inside the Seafile page
# 5. Type something, Ctrl+S
# 6. Host bar should say "saved to Seafile"
# 7. Refresh history → new version by you
```

If this works, proceed to **Full Acceptance Checklist** below.

---

## 10. Full HTTPS Acceptance Checklist (10 points)

Run in **Chrome/Edge AND Firefox** on **desktop** (not headless).

| # | Test | Pass? | Notes |
|---|------|-------|-------|
| 1 | Open `.docx` from Seafile Web → WordCraft appears inside Seafile page; host bar shows file name + `ready`; no CSP/`frame-ancestors` error in console | ☐ | WebGPU must be used |
| 2 | Console says **WebGPU** (not WebGL2 fallback) | ☐ | DevTools → Console → look for "WebGPU" log |
| 3 | Type text, see host bar `unsaved changes`; press Ctrl+S → bar says `saved to Seafile`; Seafile history shows new version by you | ☐ | |
| 4 | Close tab with unsaved changes → browser's leave-page prompt appears | ☐ | `beforeunload` |
| 5 | Copy/paste text within editor; copy from another app → paste in editor | ☐ | System clipboard |
| 6 | Open same file in second tab, save there, then save in first → first gets "file changed in Seafile since it was opened" and nothing overwritten | ☐ | Concurrency |
| 7 | Share library read-only with another user → for them bar says `read-only` and Ctrl+S is refused | ☐ | Permissions |
| 8 | Wait past `WOPI_ACCESS_TOKEN_EXPIRATION` (default 30 min) → save says token expired; reopen works | ☐ | Token lifecycle |
| 9 | `.pdf` opens Seafile viewer; `?edit_pdf=true` on file URL opens PdfCraft | ☐ | PDF route |
| 10 | `.pptx` still opens in ONLYOFFICE | ☐ | ONLYOFFICE unchanged |

**Record**: Date, browser, Seafile version, bridge commit (`git rev-parse HEAD`), any failures with screenshots/console logs.

---

## 11. Rollback Procedure

```bash
# 1. Stop bridge
cd /opt/artcraft-bridge && docker compose down

# 2. Restore Seahub settings
cp /opt/seafile/conf/seahub_settings.py.backup-YYYY-MM-DD-HHMM /opt/seafile/conf/seahub_settings.py
systemctl restart seahub

# 3. Restore nginx (disable bridge site)
rm /etc/nginx/sites-enabled/craft-bridge
nginx -t && systemctl reload nginx

# 4. ONLYOFFICE config was never touched — no action needed
```

---

## 12. Monitoring & Logs

| Component | Where to look | What to watch |
|-----------|---------------|---------------|
| Bridge | `docker compose logs -f bridge` | `/healthz`, discovery XML, editor opens, relay save, errors |
| Seahub | `/opt/seafile/logs/seahub.log` | WOPI fetch, editor callback, file save |
| ONLYOFFICE | `/opt/seafile/logs/onlyoffice.log` | Callback status 1/2/4, doc_key |
| Nginx | `/var/log/nginx/access.log`, `error.log` | 5xx, timeouts, large body uploads |

**Bridge health**: `curl -s https://craft.example.org/healthz` → `ok` (used by compose healthcheck).

---

## 13. Troubleshooting Quick Reference

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| "Error when prepare Office Online file preview page" | Seahub WOPI branch captured the file; `ENABLE_OFFICE_WEB_APP` present but file ext not in `OFFICE_WEB_APP_FILE_EXTENSION` | Add extension to both tuples in Seahub, restart Seahub |
| CSP `frame-ancestors` error | `BRIDGE_SEAHUB_ORIGIN` in `.env` doesn't match actual Seafile origin (scheme+host+port) | Fix `.env`, `docker compose up -d --force-recreate bridge` |
| WebGPU not used (WebGL2 fallback) | Not HTTPS, or browser doesn't support WebGPU, or GPU process crashed | Must be HTTPS; try Chrome/Edge; check `chrome://gpu` |
| Save hangs / times out | `proxy_read_timeout` too low on `/relay/save`; Seafile commit slow | Increase to 600s in nginx; check Seahub/filerserver logs |
| ONLYOFFICE 502 on `api.js` | ONLYOFFICE DocServer not reachable from Seahub container | Check `ONLYOFFICE_APIJS_URL` in Seahub settings; network connectivity |
| "File changed in Seafile" on every save | Concurrent editor, or `WOPI_ACCESS_TOKEN_EXPIRATION` too short | Normal for concurrency; increase token TTL if spurious |
| Bridge healthcheck fails | Bridge not starting, or port 8778 blocked | `docker compose logs bridge`; check `BRIDGE_PUBLIC_URL` reachable from container |

---

## 14. Upgrading the Bridge

```bash
cd /opt/artcraft-bridge
git pull  # if you cloned the repo
# or copy new deploy/bridge/ files
docker compose build --pull
docker compose up -d --force-recreate
# No Seahub restart needed unless editors.json changed (then restart Seahub)
```

---

## 15. Security Notes

- **Bridge origin must be separate from Seafile origin** — prevents cookie leakage, enforces `frame-ancestors` CSP
- **HTTPS mandatory** — WebGPU, clipboard, secure cookies require TLS
- **`WOPI_ACCESS_TOKEN_EXPIRATION = 30 min`** — limits permission revocation window; bridge re-checks `CheckFileInfo` before each `PutFile`
- **Seahub direct `PutFile` accepts read-only tokens** — bridge enforces `UserCanWrite` on its relay path; deployer must accept this limitation
- **Same-origin editor bundles are trusted code** — they have access to the host frame's token; not a sandbox

---

## Appendix: File Layout on Server

```
/opt/artcraft-bridge/
├── .env                          # BRIDGE_PUBLIC_URL, BRIDGE_SEAHUB_ORIGIN
├── compose.yml                   # docker compose file
├── Dockerfile                    # bridge image
├── nginx.conf.example            # nginx config (copy to /etc/nginx/sites-available/)
├── editors.json                  # extension → editor mapping
├── editors/                      # fetched bundles (gitignored)
│   ├── cadcraft/                 # PROVENANCE.txt + index.html + wasm + assets
│   ├── wordcraft/                # (if fetched)
│   ├── gridcraft/                # (if fetched)
│   └── pdfcraft/                 # (if fetched)
├── seahub_settings.example.py    # reference for Seahub config
└── fetch-editors.sh              # bundle fetcher (verify SHA-256)
```

---

*Generated for zero-patch candidate `51ff292ea` (2026-11-08).  
Upstream publication LOCKED until GPT REVIEW PASS + owner approval.*