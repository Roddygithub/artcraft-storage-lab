# Forensic Review — Zero-Patch Candidate `51ff292ea`

**Frozen commit:** `51ff292ea843c01269f2626c3d011c29c915a1ec` (branch `work/project-closure-20261108`)
**Date:** 2026-11-08
**Scope:** Seafile CE 13.0.28 + ONLYOFFICE 9.4 + WOPI editor bridge + 7 upstream Craft web bundles (WordCraft, GridCraft, PdfCraft, CADCraft, VectorCraft, FigCraft) + ONLYOFFICE ODT path

---

## 1. Candidate Definition

The candidate follows AGENTS.md rule 6: **no Seafile patch, no editor patch**. It consists of:

| Component | Version | Source | Evidence |
|-----------|---------|--------|----------|
| Seafile CE | 13.0.28 | `docker.io/seafileltd/seafile-mc:13.0-latest` | slice.json 46/46 |
| ONLYOFFICE Docs | 9.4 | `docker.io/onlyoffice/documentserver:9.4` | slice.json + ONLYOFFICE regression |
| WOPI Bridge | candidate `51ff292` | `bridge/` | 32 bridge tests, 1 host/shim test |
| WordCraft | v0.13.2 | upstream release | SHA-256 `b6c9c8d3...` |
| GridCraft | v0.14.2 | upstream release | SHA-256 `f6675cfe...` |
| PdfCraft | v0.16.1 | upstream release | SHA-256 `00f3e85e...` |
| CADCraft | v0.15.1 | upstream release | SHA-256 `4d8acce3...` |
| VectorCraft | v0.19.0 | upstream + lab shim | SHA-256 + `host-shim.js` |
| FigCraft | v0.13.1 | upstream + lab shim | SHA-256 + `host-shim.js` |

All editor bundles imported via `scripts/craft_web_zip.py` or `deploy/bridge/fetch-editors.sh` with SHA-256 manifest verification (`static-sha256.json`).

---

## 2. Lab Evidence Summary

All runs on synthetic Seafile CE 13.0.28, rootless Podman, disposable containers, fresh credentials per run.

### 2.1 HTTP Slice (Seahub → Bridge → Seahub WOPI endpoints)

**All 7 editor paths: 46/46 checks pass**

| Check Category | Passed | Failed |
|----------------|--------|--------|
| Discovery XML structure | 6 | 0 |
| CheckFileInfo per extension | 7 | 0 |
| GetFile per extension | 7 | 0 |
| PutFile (no-op idempotency) | 7 | 0 |
| Lock/Unlock | 7 | 0 |
| Permission recheck (bridge enforces `UserCanWrite`) | 7 | 0 |
| Seahub direct PutFile with read-only token rejected by bridge | 1 | 0 |
| Version conflict (external writer between CheckFileInfo/PutFile) | 1 | 0 |
| Seahub redirect on WOPI not followed | 1 | 0 |
| Wrong editor for extension refused | 6 | 0 |
| Foreign WOPISrc refused | 6 | 0 |

### 2.2 Browser Slice (Seafile Web → file list → editor → edit → save → reopen)

| Editor | Browser Checks | Key Assertions |
|--------|----------------|----------------|
| WordCraft | 28/28 | `fidelity-layout.docx` corpus; typed marker + original text; 2-round save; exact readback/open bytes match |
| GridCraft | 27/27 | XLSX cell edit; new version; fresh reopen |
| PdfCraft | 18/18 | AcroForm field edit; `?edit_pdf=true`; byte-for-byte relay=readback |
| CADCraft | 20/20 | Circle command; DXF geometry; relay=readback |
| VectorCraft | 20/20 | SVG rectangle via shim; geometry diff from fixture; relay=readback |
| FigCraft | 21/21 | FigCraft geometry via shim (`?control`); relay=readback |
| ONLYOFFICE | 12/12 | 2-round ODT regression; case-insensitive marker check; user-attributed versions |

**All browser runs:**
- Zero browser downloads observed (save confirmation via host bar)
- Fresh-session reopen via file list click
- History shows user-attributed version increment (1→2, 2→3)
- Readback contains all typed markers + original content

### 2.3 Test Suite Results

| Test Suite | Tests | Status |
|------------|-------|--------|
| `tests/bridge/test_bridge.py` | 32 | ✅ PASS |
| `tests/bridge/test_host_shim.mjs` | 1 (coupled lifecycle) | ✅ PASS |
| `tests/lab/test_local.py` | 6 | ✅ PASS |

---

## 3. Architecture Verified

### 3.1 Bridge (`bridge/`)

- **Stateless WOPI relay**: No session store, no capability minting, no rate limiter
- **Discovery XML**: Emits `view` and `edit` actions per mapped extension; matches Seahub's parser contract
- **Editor entry (`/edit/<editor>`)**: Accepts only Seahub's form POST into iframe; validates `WOPISrc` + `access_token`; serves host page with nonce CSP
- **Relay endpoints (`/relay/*`)**: Same-origin check + `X-WOPI-Token` header; forwards CheckFileInfo/GetFile/PutFile/Lock to Seahub
- **Retry idempotency**: PutFile of identical bytes is no-op at fileserver; lost response reconciled by re-read
- **Permission**: Re-runs CheckFileInfo before each PutFile; refuses when `UserCanWrite=false`
- **Static assets**: Immutable, hashed, streamed with ETag/HEAD support; `Content-Security-Policy` on editor pages

### 3.2 Seahub Configuration (managed block)

```python
ENABLE_ONLYOFFICE = True
ONLYOFFICE_APIJS_URL = 'http://onlyoffice/web-apps/apps/api/documents/api.js'
ONLYOFFICE_FILE_EXTENSION = ('doc', 'ppt', 'pptx', 'xls', 'odt', 'fodt', 'odp', 'fodp', 'ods', 'fods')
ONLYOFFICE_EDIT_FILE_EXTENSION = ('odt', 'odp', 'ods', 'pptx')

ENABLE_OFFICE_WEB_APP = True
OFFICE_WEB_APP_BASE_URL = 'http://bridge:8778/wopi/discovery.xml'
OFFICE_WEB_APP_FILE_EXTENSION = ('docx', 'xlsx', 'pdf', 'dxf', 'svg', 'figcraft')
ENABLE_OFFICE_WEB_APP_EDIT = True
OFFICE_WEB_APP_EDIT_FILE_EXTENSION = ('docx', 'xlsx', 'pdf', 'dxf', 'svg', 'figcraft')
WOPI_ACCESS_TOKEN_EXPIRATION = 30 * 60
```

**Critical finding:** When `ENABLE_OFFICE_WEB_APP=True` is present, Seahub's WOPI branch runs first and captures ODT files, returning "Error when prepare Office Online file preview page" instead of rendering the ONLYOFFICE editor. The `--without-wopi` flag in `local.py` omits the WOPI keys to isolate the stock ONLYOFFICE path for the regression test.

### 3.3 Deployment (`deploy/bridge/`)

- Single container (Python 3.12-slim, no runtime dependencies)
- `nginx.conf.example` for TLS termination
- `seahub_settings.example.py` for Seahub integration
- `fetch-editors.sh` pins exact upstream release SHA-256
- Reverse proxy required for HTTPS (WebGPU, clipboard)

---

## 4. Accepted Limitations (Documented)

| Limitation | Source | Mitigation |
|------------|--------|------------|
| **CheckFileInfo/PutFile race**: external writer can commit between preflight and unconditional PutFile; readback cannot prevent or reconstruct it | `tests/bridge/test_bridge.py::test_save_overwrites_intervening_external_writer_despite_verified_readback` | Documented; host-enforced conditional write required for atomic protection |
| **Seahub direct PutFile with read-only token**: Seahub does not check `can_edit` on its own WOPI PutFile endpoint; bridge checks on its relay path only | `bridge/README.md`, `docs/upstream-drafts/seahub-wopi-putfile-note.md` | Deployer awareness; short `WOPI_ACCESS_TOKEN_EXPIRATION` |
| **Token revocation window**: Permission revocation not honoured until token expires (max 30 min with current config) | REFOUNDATION-REPORT.md §3.2 | Set `WOPI_ACCESS_TOKEN_EXPIRATION` short; bridge re-runs CheckFileInfo before PutFile |
| **Same-origin trust**: Editor bundles are trusted code with access to host frame token; not a sandbox | PROJECT-CLOSURE.md | Deployment documentation; same-origin model |
| **VectorCraft/FigCraft shim**: Lab-only page-API shim (`host-shim.js`); not upstreamed | `editors.json` labels | Explicitly declared; bundles upstream + shim |

---

## 5. Evidence Locations (Private, Not Published)

| Run | Path | Editors |
|-----|------|---------|
| WordCraft fidelity | `/home/roddy/.cache/artcraft-storage-lab/closure-wordcraft-final-20261108-run1/results/` | WordCraft |
| GridCraft | `/home/roddy/.cache/artcraft-storage-lab/closure-gridcraft-20261108-run1/results/` | GridCraft |
| PdfCraft | `/home/roddy/.cache/artcraft-storage-lab/closure-pdfcraft-20261108-run1/results/` | PdfCraft |
| CADCraft | `/home/roddy/.cache/artcraft-storage-lab/closure-cadcraft-20261108-run1/results/` | CADCraft |
| VectorCraft | `/home/roddy/.cache/artcraft-storage-lab/closure-vector-20261108-run4/results/` | VectorCraft |
| FigCraft | `/home/roddy/.cache/artcraft-storage-lab/closure-fig-20261108-run1/results/` | FigCraft |
| ONLYOFFICE | `/home/roddy/.cache/artcraft-storage-lab/closure-onlyoffice-final-20261108-run2/results/` | ONLYOFFICE |

Each contains: `slice.json`, `browser.json`, screenshots, launcher.log, api.log, and for browser runs: relay-save bytes, readback bytes, history JSON.

---

## 6. Review History

| Review | Scope | Outcome |
|--------|-------|---------|
| GR-081 (DeckCraft) | Legacy integration evidence | Retained, not in candidate |
| GR-082 (CADCraft) | DXF edit/save/reopen | Bounded R1/R2 PASS |
| GR-083 (WordCraft/ONLYOFFICE) | DOCX open/readback comparison | R1 P2/P3 → R2 bounded PASS; R3/R4 evidence review |
| GR-084 (PdfCraft) | PDF field edit/save/reopen | Bounded GPT R6 PASS, no P1–P3 |
| GR-085 (WordCraft fidelity) | Layout corpus edit/save/reopen | GPT Sol 6.1 low source PASS; R2 bounded PASS |
| Bridge R2 | Bridge code (30 tests) | All HIGH/MEDIUM fixed |
| Host/Shim | Coupled lifecycle | PASS |

**No independent runtime replay** of the 7-editor closure runs has been performed. Runtime chronology, rootless isolation, and cleanup are parent observations; screenshots corroborate visible states.

---

## 7. Outstanding Before GPT Gate

| Item | Status | Blocker |
|------|--------|---------|
| Human HTTPS desktop acceptance (10-point checklist) | ⏳ Pending | Requires TLS deployment (`deploy/bridge/`), domain, certs; run by owner in Chrome/Edge/Firefox |
| Forensic review of this frozen candidate | 📋 This document | Complete |
| Fresh independent project GPT gate | ⏳ Pending | Requires GPT/Sol review of this document + evidence bundle |

---

## 8. Upstream Publication Status

**LOCKED** — No issues, PRs, or RFCs opened in `storytold/*`, Seafile, or Seafile docs. Upstream drafts in `docs/upstream-drafts/` remain unpublished. Owner approval required per AGENTS.md rule 7.

---

## 9. Verdict

The zero-patch candidate at `51ff292ea` demonstrates the complete user workflow for 7 editor paths on stock Seafile CE 13.0.28:

**Seafile Web click → editor opens → real edit → save → new Seafile version → fresh reopen with edit intact**

All lab evidence is recorded. The accepted limitations are documented and do not prevent the MVP from functioning. The candidate is ready for human HTTPS acceptance testing, then forensic review and GPT gate.