# Seafile WOPI editor bridge — prototype

Status: **prototype, validated against a stock Seafile CE 13.0.28** (`lab/real-seafile/`: 45 HTTP checks +
21 headless-browser checks with the unpatched upstream WordCraft/GridCraft/PdfCraft/CADCraft bundles and VectorCraft through a page-API shim), and
unit-tested against a fake Seahub WOPI host (`tests/bridge/`, 21 tests). Not yet run on HTTPS with a human
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

## What the bridge enforces that Seahub's PutFile does not

| Check | Where | Why |
| --- | --- | --- |
| `UserCanWrite` | `/relay/save` | Seahub's `WOPIFilesContentsView.post` never reads `can_edit` |
| Version precondition (`X-Expected-Version` vs CheckFileInfo `Version`) | `/relay/save` | optimistic concurrency; Seahub merges/overwrites otherwise |
| File name unchanged, content signature matches extension | `/relay/save` | no Save-As, no PDF bytes into a `.docx` |
| Lost-response reconciliation | `/relay/save` | re-read `Version` + bytes before reporting failure |
| `WOPISrc` origin allow-list, same-origin relay calls, nonce CSP, `frame-ancestors` = Seahub | everywhere | SSRF / CSRF / clickjacking |

Identical bytes are a fileserver no-op, so retrying a save is idempotent without receipts.

## Seahub configuration (target, Seahub ≥ 13 for non-office extensions)

```python
ENABLE_OFFICE_WEB_APP = True
OFFICE_WEB_APP_BASE_URL = 'https://craft.example/wopi/discovery.xml'
OFFICE_WEB_APP_FILE_EXTENSION = ('svg', 'drawio')          # only extensions ONLYOFFICE should NOT take
ENABLE_OFFICE_WEB_APP_EDIT = True
OFFICE_WEB_APP_EDIT_FILE_EXTENSION = ('svg', 'drawio')
WOPI_ACCESS_TOKEN_EXPIRATION = 30 * 60                       # default is 12 h; keep it short
```

On Seahub 12.0 the WOPI branch is only reached for office/PDF file types (see the report §2.1).

## Serving

`python -m bridge` runs a threaded stdlib server (one thread per request: a browser streaming an
80 MB editor bundle must not block the relay calls of other tabs). For production put a reverse
proxy in front for TLS and compression (`deploy/bridge/`), or run `bridge.app:Bridge` under any WSGI
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
tests/bridge/test_bridge.py   20 HTTP end-to-end tests
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
