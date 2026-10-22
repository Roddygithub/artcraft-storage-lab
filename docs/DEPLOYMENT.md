# Deployment

## Part 1 — Current real deployment (the reference environment)

Read-only survey of the Seafile instance owned by the project owner, performed
2026-10-22. **No change was made to any running service.** Every secret value is
redacted here; nothing sensitive is stored in this repository.

### Topology

```text
browser
   |
   | https://svc-seafile-host.tailb64fb1.ts.net   (Tailscale hostname, -> 192.168.1.103)
   v
Nginx Proxy Manager  (LXC 103, 192.168.1.103)
   |
   +-- /            ->  http://192.168.1.108:8000   (Seahub)
   +-- /seafhttp/   ->  http://192.168.1.108:8082   (Seafile file server)
   +-- /onlyoffice/  ->  http://192.168.1.112        (ONLYOFFICE Document Server)
   v
Seafile Server (Professional 12.0.14)   (LXC 108, 192.168.1.108)
   - Seahub (Django)  : 8000
   - seafhttp         : 8082
   - /opt/seafile/seafile-server-12.0.14/
   - pro-data/ present  -> Professional edition
```

The proxy host is `seafile.home.arpa` (internal), published on the Tailscale
hostname. **ONLYOFFICE is served from the same origin as Seafile** through the
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
ONLYOFFICE_APIJS_URL = 'https://svc-seafile-host.tailb64fb1.ts.net/onlyoffice/web-apps/apps/api/documents/api.js'
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

The installed Seahub is the **Professional** build. The open-source upstream
(`haiwen/seahub`) is GPLv2; the Professional build adds proprietary modules
(`pro-data/`, `IsProVersion` permission class, `repo_office_suite` endpoint).

Consequences for this project:

1. **We must not copy Seahub code into this repository.** We may *read* it and
   *document* facts and interfaces; we may not ship it.
2. The **upstream contribution target** is the open-source `haiwen/seahub`
   (GPLv2), not the Professional build. Any patch we prepare must be written
   against the open-source tree.
3. GPLv2 is **not** compatible with Apache-2.0 (only GPLv3 is). Therefore our
   own connector should reach Seafile over its **HTTP API** (a network boundary,
   not a link) so that this repository can stay MIT/Apache. This is a first-class
   architectural constraint, tracked in `docs/LICENSING.md`.

### Rollback posture

Nothing has been changed on the server. When the integration is eventually
deployed, the rollback path is:

1. The ONLYOFFICE configuration in `seahub_settings.py` is untouched and
   reversible by removing the added keys (the file is a plain Python module, and
   a timestamped backup must be taken before any edit).
2. The reverse proxy configuration in Nginx Proxy Manager is edited through its
   own UI/DB, and a snapshot of the affected proxy host must be exported first.
3. Any new path (`/artcraft/...`) is additive: removing the location block
   restores the previous behaviour with no change to Seafile or ONLYOFFICE.
4. The integration service is stateless and can be stopped independently.

## Part 2 — The target deployment design

### 2.1 The decision

```text
   Seafile (unchanged, unforked)
        |  one setting: THIRDPARTY_EDITOR_ACTION_URL_DICT
        |  one URL per extension
        v
   the reverse proxy
        |
        +-- /            ->  Seafile          (unchanged)
        +-- /seafhttp/   ->  Seafile          (unchanged)
        +-- /onlyoffice/ ->  ONLYOFFICE       (unchanged)
        +-- /artcraft/   ->  the gateway      (NEW, additive)
                |
                +-- /artcraft/open/          the host page
                +-- /artcraft/<app>/         the Craft web build, static
                +-- /artcraft/api/           the session endpoints
```

**One new service, one new path, no change to Seafile's code, no change to
ONLYOFFICE.** Everything is additive and reversible.

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
it, and it frames the Craft app), and it must be able to reach **Seafile** (to
read the document and to write it back).

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
location /artcraft/ {
    proxy_pass http://<gateway>:8777;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-Scheme $scheme;
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

**To add before a public deployment** (they are listed in `docs/SECURITY.md` §7):
a `Content-Security-Policy` for the gateway's pages, an `Origin` check on the
state-changing endpoints, and a rate limit on `/open/`.

### 2.6 The self-hosting constraints

| Constraint | How it is met |
| --- | --- |
| 100 % self-hosted | the gateway, the Craft builds and Seafile all run on the operator's own machines; nothing calls out |
| free / open-source | the gateway is original code under MIT/Apache-2.0; the Craft builds are MIT/Apache-2.0; Seafile and ONLYOFFICE are the operator's own |
| no permanent fork | the MVP needs **no** Seafile code change; the one upstream patch is prepared separately and is optional |
| ONLYOFFICE keeps working | it is not touched; the extension the hook claims (`.xlsx`) is one that ONLYOFFICE does not claim on this instance, and no file in any other library uses it. The per-library `artcraft` office-suite id (upstream) removes even that constraint |
| the Craft side knows nothing about Seafile | the Craft app receives bytes and returns bytes; the gateway is the only thing that knows the platform |
| the browser holds no credential | the browser holds one opaque session id |

### 2.7 On the Proxmox host

The reference deployment runs the gateway **on the owner's workstation**, because
the browser is there and the URL in Seafile's setting has to be reachable from
it. On a real deployment the gateway would run where the operator wants it: a
container on the Proxmox host, a small LXC, or the same machine as the reverse
proxy. **Nothing in the design requires a new virtual machine** — it is one
container behind one path.

### 2.8 The test environment versus production

| | Reference instance | What a test instance would add |
| --- | --- | --- |
| the Seafile code | **Professional 12.0.14, unforked** | the Community edition, or a second Professional instance |
| the change | one extension in one dict, backed up | none needed |
| the ONLYOFFICE integration | present and **untouched** | present, or absent |
| the data | one **empty** library (`OnlyOffice`) with synthetic files | the same |
| the real data | **never touched** | — |

The reference instance was chosen because it is the one the operator can test,
and because the change is small enough to be provably harmless: one extension
that nothing else uses. A dedicated instance would be the right answer for a
*production* deployment, where `.docx` has to be claimed without taking it from
ONLYOFFICE — and that is what the upstream per-library suite id is for.
