# The ArtCraft gateway

A small service that lets a **Seafile** page hand a document to a **Craft web
editor** and take the saved bytes back.

```text
Seafile Web  --(form POST, access_token)-->  the gateway  -->  the Craft app
                    |                             |                (iframe,
                    |                             |                 same origin,
                    |                             |                 ?host=parent)
                    |                             |
                    +-- the gateway serves the host page and the Craft build
```

The gateway is the **trust boundary**: it keeps the Seafile third-party-editor
capability server-side, and the browser receives only a short-lived opaque
session id. Production save requires the user-bound conditional endpoint in
`docs/reviews/GR-015/`; that patch is not deployed yet.

## What it is

| File | What it does |
| --- | --- |
| `gateway/seafile.py` | the Seafile client: user-bound file info/content/save calls |
| `gateway/sessions.py` | the editing sessions: an opaque id, bound to one document, short-lived |
| `gateway/hostpage.py` | the host page: the parent side of the Craft `?host=parent` bridge |
| `gateway/server.py` | the HTTP server |
| `config/dispatch.json` | extension -> Craft application |

**Standard library only.** No dependency, no framework.

## Running it

```sh
export ARTCRAFT_SEAFILE_URL=https://seafile.example.org
cd integration
python3 -m gateway --host 127.0.0.1 --port 8777
```

| Environment variable | Meaning | Default |
| --- | --- | --- |
| `ARTCRAFT_SEAFILE_URL` | the Seafile base URL | required |
| `ARTCRAFT_SEAFILE_TOKEN` | optional token for test fixture upload/diagnostics; not required by the gateway |
| `ARTCRAFT_SEAFILE_ACCESS_TOKEN` | test-only Seafile hook token for integration runs | not set |
| `ARTCRAFT_MAX_BYTES` | the largest document the gateway will read or write | 50 MiB |
| `ARTCRAFT_GATEWAY_HOST` / `ARTCRAFT_GATEWAY_PORT` | where to listen | `127.0.0.1` / `8777` |
| `ARTCRAFT_GATEWAY_VERBOSE` | log every request | off |

Test scripts that reset/upload fixtures still need a synthetic library account
token. The deployed gateway should use the per-file capability Seahub posts to
it; it must not use a broad service-account write credential.

## The endpoints

| Endpoint | What it does |
| --- | --- |
| `GET /healthz` | liveness |
| `POST /open/` | open a session from Seafile's `access_token` only. Direct `repo_id` + `path` opening is disabled because it has no editing-user identity. `?format=json` returns the session as data instead of the page. |
| `GET /session/<sid>/document` | the document's bytes |
| `POST /session/<sid>/save` | user-bound save with original file id and repository head; the server patch must commit the version before acknowledgement |
| `POST /session/<sid>/dirty` | the editor's dirty state |
| `GET /artcraft/<app>/…` | the Craft web build, statically |

## The Craft web builds

They are not in the repository: they are upstream release artifacts. The
fetcher stages an exact, SHA-256-checked release candidate; it never writes to
the active `integration/static/<app>/` directory.

```sh
# Use the exact release tag and the SHA-256 of its `<app>-web-*.zip` asset.
./scripts/fetch-craft-web.sh wordcraft vX.Y.Z <asset-sha256>
```

The candidate is unpacked under
`integration/static/candidates/<app>/<tag>-<sha256>/` with a provenance file.
That path is not selected by the dispatcher. Before manually promoting a
candidate into `integration/static/<app>/`, verify it contains the required
host protocol and passes the app's save/version/reopen smoke. The fetcher does
not claim host compatibility. See [`docs/ASSET-INGESTION.md`](../docs/ASSET-INGESTION.md).

Older reproduction commands in review reports document the fetcher as it
existed at the time; use the pinned staging flow above for new work.

The **WordCraft** build with the host bridge is built from source instead (the
patch in `docs/reviews/GR-014/`); see that bundle for the commands.

## The tests

```sh
export ARTCRAFT_SEAFILE_URL=... ARTCRAFT_SEAFILE_TOKEN=...
export ARTCRAFT_GATEWAY=http://127.0.0.1:8777

# the Seafile side: reset the synthetic fixture, then open, save, a new version,
# a refused stale save, a file that is gone, and a symlink escape
python3 tests/test_integration.py <repo_id> /artcraft-lab/synthetic.xlsx

# the whole thing, in a real browser
python3 tests/test_browser.py <repo_id> /artcraft-lab/synthetic.docx
```

The browser test needs Playwright:

```sh
npm i playwright && npx playwright install chromium
uv venv /tmp/pwvenv && uv pip install --python /tmp/pwvenv/bin/python playwright
```

It drives the **editor's own Save command**, so the bytes that reach Seafile are
the ones the editor produced. It found three real bugs the HTTP test could not
see — see `docs/reviews/GR-005/README.md` §4.2.

## The deployment shape

The gateway is a plain HTTP service. It must sit behind the same HTTPS origin as
Seafile on `/open/`, `/session/`, and `/artcraft/`, so the host page and Craft
app are **same-origin** — required by the existing `?host=parent` bridges.

```nginx
location /artcraft/ {
    proxy_pass http://<gateway>:8777;
    client_max_body_size 64m;
}
```

The design, the alternatives and the self-hosting constraints are in
`docs/DEPLOYMENT.md`.

## What it does not do

* it does not reimplement Seafile's file view;
* it does not mount anything locally, and it is not a sync client;
* it does not use SeaDrive or WebDAV;
* it does not talk to the Craft application in any way that is specific to
  Seafile — the Craft side receives bytes and returns bytes.
