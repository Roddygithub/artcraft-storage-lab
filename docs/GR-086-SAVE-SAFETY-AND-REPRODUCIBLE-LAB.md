# GR-086 — verified saves and a reproducible rootless lab

The host now requires JSON with `verified: true` and a nonblank version before
acknowledging storage success. Refused saves retain their unload warning despite
editor clean notifications. An older successful request cannot erase a newer
rejected save. Offline Node behavior tests cover those orderings and valid retry
recovery. The fake-host suite also retains the counterexample showing Seahub's
non-atomic version-check/write window; the owner accepted that documented limit.

`lab/real-seafile/local.py` creates a fresh private workspace, snapshots source
and exact-manifest assets, generates synthetic credentials, checks rootless
Podman and runs HTTP then Chromium. Native podman-compose is supported; the
Docker Compose fallback owns a private API process/socket and cleans it up.
Containers and networks are uniquely project-scoped. Shared systemd services,
other projects and data volumes are not removed. Tests cover exact membership,
rootful rejection, private credentials, failure cleanup and plugin discovery.

Independent GPT source R2 passed exact candidate
`7380e4629e0815e2088fae486cbedaa25d27782d`, closing R1's retry and plugin-location
findings. A fresh run of that candidate passed **HTTP 48/48 and WordCraft
Chromium 28/28**, including two typed edits, versions, preserved original body
text, old-page closure and fresh-session semantic reopen. Ten prepared
source/config hashes match that candidate. The runner exited 0; the parent
observed no remaining project containers/network, free test ports, and an
inactive shared user Podman socket.

This run predates the narrowed six-editor configuration and the later shim
corrections. It is a safety/launcher regression, not the final combined replay.
Its HTTP inputs included the historical DeckCraft lab-port ZIP, accurately
identified in provenance. Four other ZIPs were unmodified upstream releases.
Raw logs and identifiers remain private; sanitized checks, three original PNGs
and hashes are in the [bundle](../lab/real-seafile/results/2026-11-08-save-safety/README.md).

Runtime and cleanup remain parent observations, not independently replayed.
Subsequent VectorCraft/FigCraft code, HTTPS acceptance, ONLYOFFICE edit/save and
the frozen-candidate forensic/final GPT gates still require validation.
Project **INCOMPLETE**, upstream **LOCKED**; direct parent work, not Aptarchy.
