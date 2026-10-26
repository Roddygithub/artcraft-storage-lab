# Deployment

## Part 1 — Current real deployment (the reference environment)

Read-only survey of the Seafile instance owned by the project owner, performed
2026-10-22. After the survey, the erroneous global `.xlsx` third-party-editor
mapping was removed and Seahub restarted to restore OnlyOffice routing. No
OnlyOffice setting or document was changed. Every secret value is redacted here;
nothing sensitive is stored in this repository.

### Topology

```text
browser
   |
   | https://<private-seafile-tailnet-host>
   v
Nginx Proxy Manager (private LAN address omitted)
   |
   +-- /            ->  http://<seahub-private-address>:8000
   +-- /seafhttp/   ->  http://<fileserver-private-address>:8082
   +-- /onlyoffice/ ->  http://<onlyoffice-private-address>
   v
Seafile Server (Professional 12.0.14; private address omitted)
   - Seahub (Django)  : 8000
   - seafhttp         : 8082
   - ONLYOFFICE       : 24.04
```

The proxy host has a private internal DNS name (omitted) and is published on the Tailscale tailnet. **ONLYOFFICE is served from the same origin as Seafile** through the
reverse proxy (`/onlyoffice/`), which is why the browser sees a single origin
for both the host page and the editor frame.

### Installed components

| Component | Version | Notes |
| --- | --- | --- |
| Seafile Server | **12.0.14** | Professional edition (`pro-data/` present) |
| Seahub | shipped with 12.0.14 | source at `/opt/seafile/seafile-server-12.0.14/seahub/seahub/` |
| ONLYOFFICE Document Server | **24.04** | container `onlyoffice-documentserver`, LXC 112 |
| Reverse proxy | Nginx Proxy Manager | LXC 103 |

### ONLYOFFICE integration, as configured (secrets redacted)

From `/opt/seafile/conf/seahub_settings.py`:

```python
ENABLE_ONLYOFFICE = True
ONLYOFFICE_APIJS_URL = 'https://<private-seafile-tailnet-host>/onlyoffice/web-apps/apps/api/documents/api.js'
ONLYOFFICE_FILE_EXTENSION = ('doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'odt', 'fodt', 'odp', 'fodp', 'ods', 'fods', 'csv', 'ppsx', 'pps')
ONLYOFFICE_EDIT_FILE_EXTENSION = ('docx', 'pptx', 'xlsx')
ONLYOFFICE_JWT_SECRET = <REDACTED>
```

Defaults that were **not** overridden (from `seahub/onlyoffice/settings.py`):

```python
VERIFY_ONLYOFFICE_CERTIFICATE = True
ONLYOFFICE_JWT_HEADER = 'Authorization'
ONLYOFFICE_FORCE_SAVE = False
ONLYOFFICE_DESKTOP_EDITOR_HTTP_USER_AGENT = 'AscDesktopEditor'
ONLYOFFICE_CONVERTER_URL = <derived from ONLYOFFICE_APIJS_URL>
```

### The Seahub URLs the integration exposes

```text
/onlyoffice/editor-callback/                -> onlyoffice_editor_callback   (csrf_exempt)
/onlyoffice-api/convert/                    -> OnlyofficeConvert
/onlyoffice-api/file-history/               -> OnlyofficeFileHistory
/onlyoffice-api/get-history-file-access-token/ -> OnlyofficeGetHistoryFileAccessToken
/onlyoffice-api/get-reference-data/         -> OnlyofficeGetReferenceData
```

Registered only when `ENABLE_ONLYOFFICE` or `ENABLE_MULTIPLE_OFFICE_SUITE` is
true (`seahub/urls.py`).

### Multi-office-suite mechanism (Professional)

Seafile 12.0.14 ships a **per-library office-suite selection**:

* `seahub/settings.py` defines `OFFICE_SUITE_LIST`, `ROLES_DEFAULT_OFFCICE_SUITE`,
  `OFFICE_SUITE_ENABLED_FILE_TYPES`, `OFFICE_SUITE_ENABLED_EDIT_FILE_TYPES`.
  The shipped list contains `onlyoffice` (default) and `collabora`.
* `seahub/views/file.py::get_office_feature_by_repo()` resolves the suite for a
  library, in this order: explicit per-repo `RepoExtraConfig` (`config_type='office'`)
  -> role default (`ROLES_DEFAULT_OFFCICE_SUITE`) -> the `is_default` entry of
  `OFFICE_SUITE_LIST`.
* `seahub/api2/endpoints/repo_office_suite.py::OfficeSuiteConfig` exposes the
  per-repo suite choice over the API (Pro version only, `IsProVersion` permission).

**Important limitation, verified in the deployed code:** the dispatcher is
*not* generic. It hardcodes exactly two suite ids:

```python
if default_suite.get('id') == 'onlyoffice':   enable_onlyoffice = True
if default_suite.get('id') == 'collabora':    enable_office_app = True
```

So the "register a new office suite" idea is **not** configuration-only: adding
an `artcraft` suite requires a code change in `seahub/views/file.py` (and the
corresponding editor views). This is the central input to **GR-002**.

### Licensing consequence of running the Professional edition

The installed Seahub is the **Professional** build. The inspected upstream
Seahub revision `c01d46bc` is Apache-2.0; the inspected Seafile Server revision
`a652460e` is AGPLv3 with an OpenSSL exception. The Professional build adds proprietary modules
(`pro-data/`, `IsProVersion` permission class, `repo_office_suite` endpoint).

Consequences for this project:

1. **We must not copy Seahub code into this repository.** We may *read* it and
   *document* facts and interfaces; we may not ship it.
2. The **upstream contribution target** is the open-source `haiwen/seahub`
   not the Professional build. Any patch we prepare must be written against a
   specifically identified upstream tree and its licence must be re-verified.
3. The connector reaches Seafile over its **HTTP API** (a network boundary, not
   a link), and exact upstream licensing must be re-verified before any code is
   derived or contributed. This is tracked in `docs/LICENSING.md`.

### Current live state and rollback

The live `.xlsx -> http://127.0.0.1:8777/open/` third-party mapping was removed
from `/opt/seafile/conf/seahub_settings.py` on LXC 108. Its exact backup is
`/root/seahub_settings.py.artcraft-rollback-20261022`. `ENABLE_ONLYOFFICE` and
its 15-format extension list were left unchanged. Seahub, Nginx, Seafile and
LXC 112 OnlyOffice were active after the restart. The gateway is not installed
on LXC 108, and no ArtCraft path has been added to the reverse proxy.

Rollback means restoring that backup and restarting `seahub.service`. Before a
future deployment, save the current Nginx Proxy Manager host config; its
`/open/`, `/session/` and `/artcraft/` locations will be additive and removable.

## Part 2 — The target deployment design

### 2.1 The decision

```text
   https://seafile.example (Seahub)
        | allow-listed repository + supported extension
        | one-time third-party-editor capability, form POST
        v
   https://craft.example (gateway + Craft builds; separate origin)
        | host page and editor frame are same-origin with each other
        +-- /open/             capability handoff, accepts configured Seafile Origin only
        +-- /session/          one-document browser API, same-origin POSTs only
        +-- /artcraft/<app>/   Craft web build

   https://seafile.example remains unchanged:
        +-- /, /seafhttp/      Seafile
        +-- /onlyoffice/       ONLYOFFICE
```

The Seafile and ArtCraft origins **must differ**. The untrusted Craft frame is
same-origin with the gateway host page so the existing bridge works; that host
page must not share the Seahub origin, cookies, or DOM containing the submitted
capability. Configure `ARTCRAFT_SEAFILE_ORIGIN` to the exact Seahub origin. The
gateway permits that origin only on `POST /open/`; all session mutations still
require the gateway's own origin. This form-navigation flow does not require
CORS.

**One Seafile connector, one gateway and per-library routing.** The current
third-party-editor hook is read-only, so a user-bound save endpoint and a
fileserver conditional-update change are required for durable writes. The
ArtCraft route must be scoped by repository so its extensions never take files
away from ONLYOFFICE in other libraries.

### 2.2 The candidates, and why they lost

| Candidate | Why it lost |
| --- | --- |
| a Seahub **extension** (a "seahub app") | a Seahub app gives URLs and views, but the *file list* and the *onlyoffice branch* are core. It would still need a patch, and it adds a moving part inside the product we must not destabilise. |
| a **patched Seahub** (a fork) | a permanent fork of a product the user does not develop is a maintenance trap, and it puts the "never break ONLYOFFICE" rule at risk on every upgrade. The one patch we do need (a write endpoint) is prepared **separately** and is small enough to propose upstream. |
| a **browser-only** solution (no service) | the browser would need a Seafile credential, and an `op=update` token is library-wide. Not acceptable. |
| a **desktop client** | out of scope, and it is not the target experience. |
| **SeaDrive** | explicitly out of scope. |
| a **static site + a callback service** | close to the decision, but the host page has to be served by the service anyway (it holds the session), so the split buys nothing. |

### 2.3 What the gateway is

A small HTTP service. In the reference implementation it is **Python, standard
library only** (`integration/gateway/`), because the point of the prototype is the
*contract*, not the service.

For a real deployment it would be a container:

```text
artcraft-gateway
  image: a small Python or Go service
  configuration:
    ARTCRAFT_SEAFILE_URL        the Seafile base URL
    ARTCRAFT_SEAFILE_TOKEN      the account token, from the secret store
    ARTCRAFT_MAX_BYTES          the document size limit
  volumes:
    /srv/artcraft/wordcraft      the Craft web build (static)
  ports:
    8777                        behind the reverse proxy, not exposed
```

**It must be reachable from the browser** (the browser POSTs the access token to
it, and it frames the Craft app), and it must be able to reach **Seafile**. The
current client reads with the user-bound token and sends saves to the planned
Seahub endpoint; it no longer needs a broad service-account token for writes.

### 2.4 Where the Craft web builds live

They are **static files** and they are the largest part of the deployment:
13 MB compressed for WordCraft, 7 MB for GridCraft.

Two options:

| Option | How | Notes |
| --- | --- | --- |
| **the gateway serves them** | they sit next to the gateway and it serves them with the right MIME types | **the simplest**, and it guarantees the host page and the app are **same-origin**, which the `?host=parent` bridge requires |
| the reverse proxy serves them | a second `location` with a `root` | they must still be on the **same origin** as the host page, so they would have to be a path of the *same* vhost that serves the gateway — which is what the option above does anyway |

The Craft build's own documentation gives the exact requirements:
`application/wasm` for the module, gzip or Brotli, immutable caching for the
hashed assets, `no-cache` for `index.html`, and **HTTPS** (WebGPU and the
clipboard need a secure context; without it the app falls back to WebGL2).

### 2.5 The nginx rules

```nginx
    location = /open/ {
        proxy_pass http://<gateway>:8777;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    location /session/ {
        proxy_pass http://<gateway>:8777;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    location /artcraft/ {
    proxy_pass http://<gateway>:8777;
    proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-For $remote_addr;
    client_max_body_size 64m;          # the document limit, plus room
    proxy_read_timeout 120s;
}
```

And, in the gateway's own responses (already implemented):

```text
Content-Type: application/wasm      for .wasm
Cache-Control: immutable             for the hashed assets
Cache-Control: no-cache              for index.html
X-Content-Type-Options: nosniff
Referrer-Policy: no-referrer
```

**Still required before public deployment** (see `docs/SECURITY.md` §7): a
`Content-Security-Policy` and a rate limit on `/open/`. The gateway permits the
configured Seahub origin only for the `/open/` form handoff and checks the
gateway origin on session mutations; proxy behavior remains unverified. This
does not approve public exposure.

### 2.6 The self-hosting constraints

| Constraint | How it is met |
| --- | --- |
| 100 % self-hosted | the gateway, the Craft builds and Seafile all run on the operator's own machines; nothing calls out |
| free / open-source | the gateway is original code under MIT/Apache-2.0; the Craft builds are MIT/Apache-2.0; Seafile and ONLYOFFICE are the operator's own |
| no permanent fork | the current gateway source does not need a permanent fork, but safe user-bound conditional writes require a Seahub endpoint and a Seafile Server CAS change; draft patches are in `docs/reviews/GR-015/` |
| ONLYOFFICE keeps working | only repository-scoped ArtCraft dispatch can claim formats in the synthetic library; the old global `.xlsx` map is removed, and ONLYOFFICE's settings are unchanged |
| the Craft side knows nothing about Seafile | the Craft app receives bytes and returns bytes; the gateway is the only thing that knows the platform |
| the Craft frame cannot read Seahub credentials or the handoff form | Seahub and ArtCraft use distinct origins; this topology is required, not optional |
| the browser holds no reusable storage credential | after the form handoff it holds only an opaque one-document gateway session id |

### 2.7 On the Proxmox host

The gateway currently runs in the **development workspace only**. The target is
to install it on the Seafile LXC or a dedicated LXC and expose it through the
existing Nginx Proxy Manager hostname. No new virtual machine is required.

### 2.8 The test environment versus production

| | Reference instance | What a test instance would add |
| --- | --- | --- |
| the Seafile code | **Professional 12.0.14, unforked** | the Community edition, or a second Professional instance |
| the change | no ArtCraft route currently; former global `.xlsx` map removed and backed up | repository-scoped routing patch |
| the ONLYOFFICE integration | present and **untouched** | present, or absent |
| the data | one **empty** library (`OnlyOffice`) with synthetic files | the same |
| the real data | **never touched** | — |

The reference instance is the operator's test system, and its synthetic library
is the only permitted target for the first live test. The prior extension hook
was not safely scoped and has been removed. Per-library routing is part of the
local Seahub patch in `docs/reviews/GR-015/`; it has not been built or deployed.
