# Deploying the bridge next to an existing Seafile

What you get: Seafile Web opens `.dxf`, `.svg` (and any extension you map) in a Craft web editor,
Save writes a new Seafile version attributed to the user, version history works. No Seafile patch,
no editor patch, no SeaDrive, no desktop app.

```text
browser ──▶ https://seafile.example.org  (Seahub: file page posts a WOPI token to the bridge)
browser ──▶ https://craft.example.org    (bridge: host page + editor bundle + /relay/* → Seahub WOPI)
bridge  ──▶ https://seafile.example.org/api2/wopi/files/…  (CheckFileInfo / GetFile / PutFile / Lock)
```

## Steps

1. `./fetch-editors.sh wordcraft v0.13.2 <sha256> ...` — bundles land in `./editors/<app>/`.
   The SHA-256 values the lab verified are in `lab/real-seafile/static/*-PROVENANCE.txt`.
2. Edit `editors.json` (extension → editor). Only list what you want the bridge to take.
3. `BRIDGE_PUBLIC_URL=https://craft.example.org BRIDGE_SEAHUB_ORIGIN=https://seafile.example.org docker compose up -d --build`
4. Reverse proxy: `nginx.conf.example`. HTTPS is required for WebGPU and the clipboard in the editors.
5. Seahub: append `seahub_settings.example.py` to `seahub_settings.py`, restart Seahub.
   Seahub fetches the discovery XML from `OFFICE_WEB_APP_BASE_URL` **from the server**, so the bridge
   must be reachable from the Seahub host under that URL. Seahub caches the discovery result;
   restart Seahub (or clear its cache) after changing `editors.json`.
6. Open a mapped file in Seafile Web.

## Checks

- `curl https://craft.example.org/healthz` → `ok`
- `curl https://craft.example.org/wopi/discovery.xml` lists a `view` and an `edit` action per extension.
- On the file page, the browser's console must show no `frame-ancestors` error. The bridge sends
  `frame-ancestors <BRIDGE_SEAHUB_ORIGIN>` on the host page and `'self' <BRIDGE_SEAHUB_ORIGIN>` on
  editor pages; `BRIDGE_SEAHUB_ORIGIN` must be exactly the origin users type (scheme + host [+ port]).

## What the bridge enforces (Seahub's WOPI host does not)

`UserCanWrite` on save, version precondition (409 on a concurrent change, nothing overwritten),
file name and content signature, reconciliation after a lost response, WOPI locks. See `bridge/README.md`.

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
