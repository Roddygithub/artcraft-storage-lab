# Real-Seafile lab

ONLYOFFICE was retired by owner instruction on 2026-11-08. The active Compose
file and launchers no longer start it; its regression runner is historical.
Earlier mixed-suite instructions/results below are retained history, not the
current acceptance plan. Unsupported office formats remain NOT VERIFIED.

A stock Seafile CE 13 + the bridge + upstream Craft web bundles, in a
dedicated Lima VM with Docker. Nothing here touches a production system; the VM is disposable.

## Optional official DeckCraft PPTX candidate

With the verified official v0.16.0 bundle under `static/deckcraft/`, pass
`--pptx --editor deckcraft` to validate same-format PPTX persistence, or just
`--pptx` to exercise all seven editors. This modifies only the fresh private
lab snapshot. The default six-editor configuration is unchanged; the option
cannot be combined with experimental Rust ports. Focused retained evidence:
`results/2026-11-08-pptx-official/`. Broader PPTX/font fidelity is unverified.

## Linux rootless Podman candidate

`local.py` uses the same Compose file as Lima. Prerequisites: Linux, Python 3.11+,
working **rootless** local Podman (subuid/subgid mappings, rootless networking and storage),
`podman-compose` supporting `--podman-args`, or the Docker Compose v2 plugin,
free loopback ports 8000/8778, and enough disk/RAM for Seafile and Chromium.
Images and browser pip packages require network access on the eventual real run. The Docker
Compose fallback starts and removes its own private Podman API socket; the shared user socket
and its service are untouched. No global socket or
systemd unit is started, stopped or reused; Podman is explicitly local (`--remote=false`).

Supply static assets previously acquired through `scripts/craft_web_zip.py` or
`deploy/bridge/fetch-editors.sh`. Supply an **independently checked** JSON manifest mapping every
relative POSIX file path under that static directory to its lowercase SHA-256, including any
provenance files. Example shape: `{"wordcraft/index.html": "<64 hex characters>", ...}`.
There are no excluded static files. Directories do not count; symlinks and special files are
rejected. Missing, extra or changed files abort before any Podman call. Do not derive expected
hashes from an untrusted runtime or its provenance label: GR085 found an old four-file WordCraft
runtime labeled v0.13.2. The manifest establishes byte identity, not release authenticity.

```bash
python3 lab/real-seafile/local.py \
  --run-dir "$HOME/seafile-lab-runs/candidate-001" \
  --static /absolute/path/to/verified-static \
  --manifest /absolute/path/to/independently-verified-static-sha256.json
```

The explicit run directory must not exist and must be outside this checkout. It is created
mode 0700; fresh random synthetic credentials are written mode 0600 in its `.env`. Current
`bridge/` and `lab/` source are copied there excluding `results`, `static`, `cache`, `.cache`
and `__pycache__`; supplied static assets are copied and then verified. No private runner or
second Compose YAML is needed. Every project gets a random name, including its network and
containers. Ports bind only to loopback; override both with `--seafile-port`,
`--bridge-port` if needed. Browser IPC is private with 1 GiB shared memory.

The launcher starts the disposable stack, appends the managed Seahub configuration through
that project's Seafile service only, restarts it, runs slice then browser, and always attempts
project-scoped `down --remove-orphans` after startup, including on failure. Subprocess waits
are bounded (startup 15 minutes, each slice 60 minutes, cleanup 3 minutes). It never removes
volumes or data. Interrupted/failed runs are retained and cannot be reused by the launcher.
After an uncatchable kill, use the recorded `project.txt` and the copied Compose file for
manual project-scoped cleanup; never use global Podman prune commands.

Optional browser selection: `--editor wordcraft --wordcraft-fixture fidelity-layout.docx` (the fixture
name is passed unchanged to `BROWSER_WORDCRAFT_FIXTURE`; use a name supported by
`run_browser.py`). These options affect browser only; the HTTP slice remains complete.
Raw logs, generated config, credentials and results remain inside the private run directory.
Review and redact evidence before copying anything into Git; this launcher does not publish it.
Offline check: `python3 tests/lab/test_local.py`. The parent must run the real lab and obtain
independent review before treating this candidate as final evidence.

### Optional external HTTPS origins (offline candidate; runtime NOT VERIFIED)

For the upcoming WordCraft replay, add both flags to the rootless command above:

```bash
  --seafile-public-url https://seafile.example.ts.net \
  --bridge-public-url https://craft.example.ts.net \
  --editor wordcraft --wordcraft-fixture fidelity-layout.docx
```

These must be HTTPS origins with distinct DNS hostnames, even when ports differ.
Credentials, paths (including a trailing slash), query strings and fragments are rejected
before creating the run directory or invoking Podman. Omit both for the unchanged internal
HTTP lab. The launcher clears inherited public URL variables in that default mode.
Compose falls back to `http://seafile.lab` and `http://bridge:8778`; with the flags it uses
`SEAFILE_PUBLIC_URL` / `BRIDGE_PUBLIC_URL` for bridge origin checks and discovery URLs,
and the slice/browser target URLs.

Only the fresh project's generated Seahub settings gain public `SERVICE_URL`,
`FILE_SERVER_ROOT` (`/seafhttp`), bridge discovery URL (`/wopi/discovery.xml`),
`CSRF_TRUSTED_ORIGINS` (Seahub origin), and
`SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')`.
The Seafile and bridge published ports still bind to loopback; this adds no TLS listener,
proxy, Tailscale configuration, daemon, SSH setup or hold mode. Existing production
configuration and ONLYOFFICE routing are untouched. HTTP failure diagnostics and final
project cleanup still apply, so the endpoints must already route to this fresh run's ports
while the launcher is running.

Remaining runtime prerequisites: independently provisioned authenticated desktop/PVE
Tailscale HTTPS endpoints with separate DNS names and trusted certificates; routes to the
launcher host's loopback Seafile/bridge ports; DNS, TLS trust and authenticated access from
both lab containers and the desktop browser. The Seahub proxy must forward the original
Host, strip untrusted forwarded-protocol headers and set `X-Forwarded-Proto: https`.
Both bridge-to-Seahub and Seahub-to-bridge requests must pass endpoint authentication.
Verified upstream WordCraft assets/manifest, rootless resources and the existing image/pip
prerequisites are still required. None of these endpoints or runtime conditions have been
verified by the offline tests. The pending evidence is a WordCraft browser open → typed edit
→ save → Seafile version → close/reopen replay over HTTPS, plus independent review;
no runtime PASS is claimed and no additional ONLYOFFICE replay is requested here.

## Run with Lima (existing workflow)


```bash
limactl start --name=seafile-lab --cpus=4 --memory=6 --disk=30 --tty=false template:docker
```

```bash
lab/real-seafile/up.sh up          # sync files into the VM, pull images, start db/redis/seafile/onlyoffice/bridge
```

```bash
lab/real-seafile/up.sh configure   # append the managed Seahub settings block, restart Seafile
```

```bash
lab/real-seafile/up.sh slice       # HTTP slice (run_slice.py) → results/slice.json
```

```bash
lab/real-seafile/up.sh browser     # headless Chromium slice (run_browser.py) → results/browser.json + screenshots
```

`up.sh down` stops the stack; `limactl delete seafile-lab` removes the VM. Secrets are generated
into `.env` inside the VM on first `up` and never leave it.

Editor bundles live under `static/<editor-id>/` (gitignored) with a `static/<editor-id>-PROVENANCE.txt`
(tag, SHA-256, and whether the lab changed anything). `editors.json` maps extensions to editors;
`seahub_settings.extra.py` is the managed block `configure` writes.

The VM has a Rust/wasm toolchain (`rustup`, `trunk`) for building patched bundles under `~/build/`
(`docs/upstream-drafts/<app>-host-bridge/apply.py` applies a port to a shallow clone, then
`cd apps/<app>-web && CARGO_BUILD_JOBS=2 trunk build --release`). Give the VM 6 GiB and stop the
whole stack during builds (`docker compose stop`): a single rustc on PhotoCraft's engine crate
passes 2 GB and wasm-bindgen on a 50 MB wasm needs ~1.2 GB; both were OOM-killed at 4 GiB next to
the containers. `~/build/build-all.sh` is the sequential queue used in the lab. `wire-built-bundle.sh <app>` then copies
`dist/web` into the lab, records provenance, saves the diff under `docs/upstream-drafts/` and
deletes the build's `target/` (each is several GB on a 30 GB disk).

## Human checklist (HTTPS, desktop browser) — not yet run

The slices run headless over plain HTTP, so they cannot see these. Run against a deployment from
`deploy/bridge/` behind TLS, in Chrome/Edge and Firefox:

1. Open a `.docx` from Seafile Web: WordCraft appears inside the Seafile page, the host bar shows
   the file name and `ready`; no `frame-ancestors` or CSP error in the console.
2. Renderer: the console says WebGPU (not the WebGL2 fallback) on HTTPS.
3. Type, see the host bar say `unsaved changes`; press Ctrl/Cmd+S; the bar says `saved to Seafile`
   and Seafile's history shows a new version by you.
4. Close the tab with unsaved changes: the browser's leave-page prompt appears.
5. Clipboard: copy/paste text within the editor and from another app.
6. Open the same file in a second tab, save there, then save in the first: the first gets
   `the file changed in Seafile since it was opened` and nothing is overwritten.
7. Share the library read-only with another user; for them the bar says `read-only` and Ctrl+S
   is refused.
8. Wait past `WOPI_ACCESS_TOKEN_EXPIRATION`; a save then says the token expired; reopen works.
9. `.pdf` opens Seafile's viewer; the `?edit_pdf=true` URL opens PdfCraft.
10. `.pptx` still opens in ONLYOFFICE.
