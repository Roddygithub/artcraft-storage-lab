> **Deployment blocked:** packaged Seahub CE 13.0.28 can break ONLYOFFICE
> pages when WOPI is enabled. See `docs/PROJECT-CLOSURE.md`; this split is not
> production-ready. Isolated ONLYOFFICE-only tests do not prove coexistence.

# Deploying the bridge next to an existing Seafile

What you get: Seafile Web opens `.dxf` by default in a Craft web editor,
Save writes a new Seafile version attributed to the user (lab evidence: `lab/real-seafile/results/browser.json`, DXF history 1→2). No Seafile patch,
no editor patch, no SeaDrive, no desktop app.

```text
browser ──▶ https://seafile.example.org  (Seahub: file page posts a WOPI token to the bridge)
browser ──▶ https://craft.example.org    (bridge: host page + editor bundle + /relay/* → Seahub WOPI)
bridge  ──▶ https://seafile.example.org/api2/wopi/files/<id>  (Seahub 13: /api2/…; CheckFileInfo / GetFile / PutFile / Lock)
```

## Steps

1. Fetch CADCraft using the pinned command below — bundles land in `./editors/<app>/`.
2. Edit `editors.json` (extension → editor). Only list what you want the bridge to take.
3. `BRIDGE_PUBLIC_URL=https://craft.example.org BRIDGE_SEAHUB_ORIGIN=https://seafile.example.org docker compose up -d --build`
4. Reverse proxy: `nginx.conf.example`. HTTPS is required for WebGPU and the clipboard in the editors.
5. Seahub: append `seahub_settings.example.py` to `seahub_settings.py`, restart Seahub.
   Seahub fetches the discovery XML from `OFFICE_WEB_APP_BASE_URL` **from the server**, so the bridge
   must be reachable from the Seahub host under that URL. Seahub caches the discovery result;
   restart Seahub (or clear its cache) after changing `editors.json`.
6. Open a mapped file in Seafile Web.

## Default and opt-in routes

The shipped `editors.json` discovery and both Seahub extension tuples contain only `dxf`.
Keep existing ONLYOFFICE configuration enabled and unchanged. SVG is not shipped here: the
tracked VectorCraft bundle needs a lab shim, unlike the four upstream bundles below.

For an explicit DOCX/XLSX/PDF trial, add only the chosen extensions to **both** Seahub tuples
and add the corresponding entries below to `editors.json` (retaining CADCraft). WOPI takes
precedence for those selected extensions; other ONLYOFFICE routes stay in place. PDF opens
Seahub's viewer first; use `?edit_pdf=true` on its file URL to reach the editor.

```json
{
"wordcraft": {"app": "wordcraft", "label": "WordCraft", "extensions": ["docx"], "url": "/editors/wordcraft/index.html?host=parent"},
"gridcraft": {"app": "gridcraft", "label": "GridCraft", "extensions": ["xlsx"], "url": "/editors/gridcraft/index.html?host=parent"},
"pdfcraft": {"app": "pdfcraft", "label": "PdfCraft", "extensions": ["pdf"], "url": "/editors/pdfcraft/index.html?host=parent"}
}
```

Run from `deploy/bridge/`. These exact tags and archive SHA-256 values come from the tracked
`lab/real-seafile/static/{cadcraft,wordcraft,gridcraft,pdfcraft}-PROVENANCE.txt` files; the fetcher
checks the digest and writes provenance. Fetch only the bundles for routes you enable.

```bash
# Default
./fetch-editors.sh cadcraft v0.15.1 4d8acce3209082699078aa868ef79fedd4437ba0d18014a0f031d118a0abceb8
# Optional upstream bundles
./fetch-editors.sh wordcraft v0.13.2 b6c9c8d3a730495189ba0c213fe64313f317be8fc0611ac1ff8cdd6a4b20880c
./fetch-editors.sh gridcraft v0.14.2 f6675cfe26f89f07cb9d9ff23a5ae0a946088eef6e22c93ac1141f0279f741f8
./fetch-editors.sh pdfcraft v0.16.1 00f3e85e29bb9dfa3d43a655cc4197cdc679f4ec7e8ef1bb5e623dc3603c0edf
```

Rollback: keep a copy of your prior Seahub settings and `editors.json`; restore them and restart
Seahub to restore routing. No ONLYOFFICE configuration changes are needed.

## Checks

- `curl https://craft.example.org/healthz` → `ok`
- `curl https://craft.example.org/wopi/discovery.xml` lists a `view` and an `edit` action per extension.
- On the file page, the browser's console must show no `frame-ancestors` error. The bridge sends
  `frame-ancestors <BRIDGE_SEAHUB_ORIGIN>` on the host page and `'self' <BRIDGE_SEAHUB_ORIGIN>` on
  editor pages; `BRIDGE_SEAHUB_ORIGIN` must be exactly the origin users type (scheme + host [+ port]).

## What the bridge guarantees

A save through the bridge is either verified in Seafile (read back after PutFile) or reported as
failed; a read-only user cannot save through the bridge; Save As / Export becomes a download.
The version preflight rejects an already-visible change with 409 unless the bytes match a retry.
**An intervening external writer can be overwritten** between CheckFileInfo and unconditional
PutFile, even with a 200 / `verified: true` readback. Readback only detects differing bytes still
visible when read; it does not provide atomic concurrency protection. Host conditional writes
would be required (no Seafile/editor patch is introduced). The offline regression in
`tests/bridge/test_bridge.py` demonstrates this residual limitation; the project is not complete.

Seahub's own `PutFile` stays writable to anyone
holding a token (Seahub does not check `can_edit`), which the bridge cannot change — see
`bridge/README.md` and `docs/upstream-drafts/seahub-wopi-putfile-note.md`.

## Smoke-tested

The image builds from this Dockerfile (python:3.12-slim, no dependencies) and, started on the
lab's Docker network with the lab's bundles mounted at `/editors`, answers `/healthz`, serves a
discovery XML with a view and an edit action per mapped extension, and serves the editor pages
(2026-10-31, lab VM).

## Validated against

Stock Seafile CE 13.0.28 and ONLYOFFICE Docs 9.4 with WordCraft, GridCraft, PdfCraft, CADCraft
upstream bundles (unpatched) and VectorCraft/FigCraft through a lab page-API shim:
`lab/real-seafile/results/`. Not yet run by a human on HTTPS in a desktop browser.

Nothing here is published upstream; the GPT gate and the owner's approval still apply to that.
