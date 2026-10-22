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

The gateway is the **trust boundary**: it holds the Seafile credential, and the
browser never sees one.

## What it is

| File | What it does |
| --- | --- |
| `gateway/seafile.py` | the Seafile client: the third-party-editor hook API, `file/detail`, `file/history`, the seafhttp write |
| `gateway/sessions.py` | the editing sessions: an opaque id, bound to one document, short-lived |
| `gateway/hostpage.py` | the host page: the parent side of the Craft `?host=parent` bridge |
| `gateway/server.py` | the HTTP server |
| `config/dispatch.json` | extension -> Craft application |

**Standard library only.** No dependency, no framework.

## Running it

```sh
export ARTCRAFT_SEAFILE_URL=https://seafile.example.org
export ARTCRAFT_SEAFILE_TOKEN=<an account token>       # server-side only
cd integration
python3 -m gateway --host 127.0.0.1 --port 8777
```

| Environment variable | Meaning | Default |
| --- | --- | --- |
| `ARTCRAFT_SEAFILE_URL` | the Seafile base URL | required |
| `ARTCRAFT_SEAFILE_TOKEN` | an account token, sent as `Authorization: Token` | required |
| `ARTCRAFT_MAX_BYTES` | the largest document the gateway will read or write | 50 MiB |
| `ARTCRAFT_GATEWAY_HOST` / `ARTCRAFT_GATEWAY_PORT` | where to listen | `127.0.0.1` / `8777` |
| `ARTCRAFT_GATEWAY_VERBOSE` | log every request | off |

**The token is read from the environment and never written to disk.** It is the
gateway's own credential; the browser gets an opaque session id and nothing else.

## The endpoints

| Endpoint | What it does |
| --- | --- |
| `GET /healthz` | liveness |
| `POST /open/` | open a session. Either `access_token` (what Seahub's hook posts) or `repo_id` + `path` (the direct form). `?format=json` returns the session as data instead of the page. |
| `GET /session/<sid>/document` | the document's bytes |
| `POST /session/<sid>/save` | store the bytes: the conflict check, then the write |
| `POST /session/<sid>/dirty` | the editor's dirty state |
| `GET /artcraft/<app>/…` | the Craft web build, statically |

## The Craft web builds

They are not in the repository: they are upstream release artifacts.

```sh
./scripts/fetch-craft-web.sh            # every application in dispatch.json
./scripts/fetch-craft-web.sh gridcraft  # just one
```

The script fetches `<app>-web-<version>.zip` from the application's GitHub
release and unpacks it into `integration/static/<app>/`. No Rust toolchain is
needed — the release build is what the applications publish.

The **WordCraft** build with the host bridge is built from source instead (the
patch in `docs/reviews/GR-014/`); see that bundle for the commands.

## The tests

```sh
export ARTCRAFT_SEAFILE_URL=... ARTCRAFT_SEAFILE_TOKEN=...
export ARTCRAFT_GATEWAY=http://127.0.0.1:8777

# the Seafile side: open, save, a new version, a refused stale save, a file
# that is gone, a symlink escape
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

The gateway is a plain HTTP service. In the reference deployment it sits behind
the same reverse proxy as Seafile, on **its own path**, and the Craft builds are
served from it, so the host page and the Craft app are **same-origin** — which
the `?host=parent` bridge requires.

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
