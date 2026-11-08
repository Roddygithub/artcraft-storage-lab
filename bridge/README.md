# Seafile WOPI editor bridge — prototype

Status: **prototype, validated against a stock Seafile CE 13.0.28** (`lab/real-seafile/`: 45 HTTP checks +
21 headless-browser checks with the unpatched upstream WordCraft/GridCraft/PdfCraft/CADCraft bundles and VectorCraft through a page-API shim), and
unit-tested against a fake Seahub WOPI host (`tests/bridge/`, 32 tests, with fault injection: lost answer, 5xx after commit, redirect, acknowledged-but-not-stored). Not yet run on HTTPS with a human
in a real browser. See `docs/REFOUNDATION-REPORT.md` §5 and §7.

## What it is

A stateless service that lets Seahub's existing WOPI host (`seahub/wopi/`, CE and Pro)
drive web editors that do not speak WOPI themselves — ArtCraft apps with the upstream
`?host=parent` bridge, draw.io embed mode, SVG-edit, etc.

```text
Seahub (view_lib_file, WOPI branch)                       bridge origin (this service)
  GET  /wopi/discovery.xml  ─────────────────────────────▶  ext → urlsrc per editor
  form POST access_token to urlsrc?WOPISrc=…  ───────────▶  POST /edit/<editor>   → host page + CSP
                                                            iframe /editors/<editor>/… (same origin)
  WOPI CheckFileInfo / GetFile / PutFile / Lock  ◀────────  POST /relay/{info,file,save,lock}
```

* **No Seafile patch.** Configuration only (five `seahub_settings.py` keys).
* **No editor patch.** Uses the message protocol upstream already merged in WordCraft,
  GridCraft, PdfCraft and CADCraft; honours a `ticket` / `saveResult` ack when the editor
  sends one (the lab's proposed extension).
* **No server-side state.** The WOPI access token Seahub posts into the iframe stays in the
  host page's memory and travels in request headers to the same-origin relay.

## What the bridge enforces on its own save path

Seahub's `PutFile` accepts any valid token, read-only or not, with no lock and no version check
(measured on CE 13.0.28). The bridge does not and cannot close that gap: the token Seahub mints is
posted into the user's own browser, and a user who extracts it can call Seahub directly. What the
bridge guarantees is narrower and honest: **a save that goes through the bridge is either verified
in Seafile or reported as failed.**

| Check | Where | Why |
| --- | --- | --- |
| `UserCanWrite` | `/relay/save` | the bridge's editors never write for a read-only user (Seahub itself would) |
| `X-Expected-Version` required and equal to CheckFileInfo `Version` | `/relay/save` | preflight of the currently visible version; a mismatch is 409 unless the stored bytes already equal the document (a retry) |
| Read-back verification after PutFile | `/relay/save` | 200 only when readback observes these bytes; "acknowledged but not stored" is 502, differing bytes with a changed version are 409 |
| Reconciliation on lost answer, 5xx or redirect | `/relay/save` | PutFile is never retried blindly; redirects are refused (urllib would turn PutFile into a GET) |
| File name unchanged, content signature matches extension | `/relay/save` | no PDF bytes into a `.docx`; a Save As / Export from the editor becomes a browser download from the host page and is reported to the editor as *not* stored |
| `WOPISrc` must be a Seahub WOPI file endpoint on the configured origin; relay calls same-origin with a custom header; nonce CSP on the host page; full CSP on editor pages (`connect-src 'self'`); `frame-ancestors` = Seahub | everywhere | SSRF / CSRF / token exfiltration / clickjacking |
| A refused save keeps the page dirty; an expired token downloads the document instead of losing it | `host.js` | the editor may believe it saved; the host page does not |

WOPI locks are taken and refreshed for other WOPI clients' benefit; Seahub ignores them on PutFile,
so they are advisory. **There is no atomic protection against external writers.** A change already
visible to the CheckFileInfo preflight is rejected with 409 (unless its bytes match the save).
An external writer arriving after that check but before the unconditional PutFile commits can be
overwritten; readback can still return 200 with `verified: true` because it sees the bridge's bytes.
Readback detects differing bytes only if they are still visible when read. Actual atomic protection
requires host-enforced conditional writes; server state in the bridge cannot provide that guarantee,
and Seafile/editor patches are outside this design. See `bridge/app.py` (`_relay_save`) and
`tests/bridge/test_bridge.py` (`test_save_overwrites_intervening_external_writer_despite_verified_readback`).

The bridge → Seahub hop carries the token in the query string (that is WOPI); keep it on TLS or an
internal network and scrub query strings from Seahub's access logs.

## Seahub configuration (target, Seahub ≥ 13 for non-office extensions)

```python
ENABLE_OFFICE_WEB_APP = True
OFFICE_WEB_APP_BASE_URL = 'https://craft.example/wopi/discovery.xml'
OFFICE_WEB_APP_FILE_EXTENSION = ('dxf',)          # only extensions ONLYOFFICE should NOT take
ENABLE_OFFICE_WEB_APP_EDIT = True
OFFICE_WEB_APP_EDIT_FILE_EXTENSION = ('dxf',)
WOPI_ACCESS_TOKEN_EXPIRATION = 30 * 60                       # default is 12 h; keep it short
```

This DXF-only default matches `deploy/bridge/editors.json` and preserves existing ONLYOFFICE
routes. See `deploy/bridge/README.md` for explicit DOCX/XLSX/PDF opt-in routes and pinned bundles.

On Seahub 12.0 the WOPI branch is only reached for office/PDF file types (see the report §2.1).

## Serving

`python -m bridge` runs a threaded stdlib server (one thread per request: a browser streaming an
80 MB editor bundle must not block the relay calls of other tabs). For production put a reverse
proxy in front for TLS and compression (`deploy/bridge/`), or run `bridge.wsgi:application` under any WSGI
server. The bridge keeps no state between requests, so several workers are fine.

## Run locally

```bash
BRIDGE_PUBLIC_URL=http://127.0.0.1:8778 BRIDGE_SEAHUB_ORIGIN=https://seafile.example \
BRIDGE_EDITORS=bridge/editors.example.json BRIDGE_STATIC_DIR=integration/static python3 -m bridge
```

```bash
python3 tests/bridge/test_bridge.py
```

## Layout

```text
bridge/app.py            WSGI app: discovery, /edit, /relay, static editors
bridge/static/host.html  host page template (nonce CSP)
bridge/static/host.js    editor protocol, save discipline, locks
bridge/editors.example.json
tests/bridge/fake_seahub.py   fake of seahub/wopi/views.py semantics (incl. its missing can_edit check)
tests/bridge/test_bridge.py   32 offline checks
```

## Real-Seafile lab

`lab/real-seafile/up.sh up|configure|slice|browser|down` drives a dedicated Lima VM (Docker) with Seafile
CE 13, ONLYOFFICE Docs, the bridge and the upstream editor bundles. Results and screenshots land in
`lab/real-seafile/results/`. Findings that changed this code: editor pages need
`frame-ancestors 'self' <seahub-origin>` (Chromium checks the whole ancestor chain).

## Not done

* Human pass on HTTPS in a real (non-headless) browser: WebGPU, clipboard, fonts, dirty-state UX.
* draw.io / SVG-edit adapters (host.js currently speaks the ArtCraft parent protocol only); VectorCraft and
  PhotoCraft have no host protocol upstream yet.
* Aggregated discovery XML for running Collabora alongside (report U3).
* `lang_dict`/locale, `PostMessageOrigin`, `CloseUrl` niceties from CheckFileInfo are read but unused.
