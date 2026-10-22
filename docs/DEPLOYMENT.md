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

## Part 2 — Target deployment design

> Pending GR-002 and GR-003. The candidate shapes to evaluate are:
>
> * a Seahub extension / app (no core patch),
> * a small integration service behind the existing reverse proxy (additive path),
> * a containerised sidecar,
> * a purely static Craft Web host plus a callback service.
>
> Constraints already established:
>
> * 100 % self-hosted, free / open-source.
> * Must not require a permanent fork of Seafile.
> * Must not degrade, disable or replace the existing ONLYOFFICE integration.
> * The Craft side must not know about Seafile repository ids, tokens or URLs.
>
> Decision: see `docs/SEAFILE-INTEGRATION-POINTS.md` (GR-002) and
> `docs/HOST-CONTRACT.md` (GR-004).
