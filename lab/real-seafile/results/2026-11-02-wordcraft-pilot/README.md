# WordCraft genuine-edit lab replay — 2026-11-02

**48/48 HTTP; 23/23 Chromium browser checks.** This is a fresh isolated Seafile CE
13.0.28 / ONLYOFFICE 9.4 lab run, not production and not a project GPT PASS.
Browser source: `e21c0b30e2d9b001bca5da17f561649de8114afd`; unchanged bridge source:
`e53fe097c7a3d1d8f854e4f74fc0fdca707ca66a`. Source review: bounded GPT PASS,
30 bridge tests and eight offline Chromium checks independently passed.

| Observed by the real browser/API scenario | Result |
| --- | --- |
| Actual Seafile file-list click opens released WordCraft 0.13.2 | PASS |
| Trusted keyboard input changes DOCX before Save; request contains marker | PASS |
| Bridge confirms save; user-attributed Seafile version contains marker and changed bytes | PASS |
| Old editor page closed; new browser context logs in and clicks the file-list link | PASS |
| Fresh host reads exactly the saved bytes; reopened editor accepts a second typed marker | PASS |
| Second editor save creates another version; storage and editor output contain both markers | PASS |
| Neither save triggers a browser download | PASS |

The retained JSON preserves check names, booleans, totals, timestamps and private-raw-file
SHA-256. Synthetic repository IDs and all free-form detail strings are omitted to avoid
publishing WOPI capabilities or incidental identities. Raw logs/results remain private.
Screenshots are unmodified browser captures, visually checked for secrets: first save,
fresh reopen, and second save. They corroborate visible states, not by themselves the full
chronology. Runtime execution is parent-operated; the source reviewer did not replay it.

## Exact runtime boundary

Rootless Podman with the repository Compose workflow: HTTP `slice`, then `browser`,
using the same scripts and images. Docker socket access was unavailable. Runtime-only
Compose overrides: unique project/container/network names; loopback ports 18800/18810/18878;
restart disabled; bounded CPU/memory; private browser IPC and 256 MiB shared memory.
`runtime-compose.yml`, `runtime-runner.py` and `runtime-editors.json` retain the exact
nonsecret runtime configuration/runner (copy under the private lab root as `compose.yml`,
`run-lab.py`, and `app/lab/real-seafile/editors.json`; supply a new private `.env` per the lab
README, never the original credentials). `runtime-source-hashes.json` fingerprints loaded
scripts/bridge files. `SOURCE.json` records limits; `image-digests.json` records pulled image identities.
Only WordCraft is visible in the browser service's static-directory mount, so the existing
bundle-selection logic skips other apps. The bridge serves five approved release bundles
for the HTTP route/asset checks; the four additional apps have **no new browser claim**.
DeckCraft's runtime label describes its unpatched release rather than the historical port.
Bundles were imported through `scripts/craft_web_zip.py download` and `extract`, with ZIP
hashes retained in `bundle-provenance.json`. No editor source/build modification occurred.
Lab Seahub settings were configured by the existing lab extra-settings block only.
Production Seafile/ONLYOFFICE were not changed. Runtime cleanup removed this project's
containers/network and stopped its temporary Podman API socket; lab data remains private.

Earlier attempts are not counted as passing: an API-socket prerequisite failure; omitted
bridge static files; missing four HTTP bundles; then an unconditional absent-FigCraft
fixture failure despite passing WordCraft checks. Those prompted environment correction
and the reviewed source change. This fifth attempt alone supplies these results.

## Recheck and reproduce

```
cd lab/real-seafile/results/2026-11-02-wordcraft-pilot
sha256sum -c SHA256SUMS
python3 verify.py
```

To replay on a prepared isolated Docker lab, follow `lab/real-seafile/README.md`, import
these pinned bundles, then run `lab/real-seafile/up.sh slice` followed by `browser`.
The recorded run used rootless Podman Compose with the overrides above; it is not evidence
that the unmodified Docker launcher ran here. Other editors' genuine-edit scenarios,
ONLYOFFICE browser edit/save fidelity, HTTPS/manual UX, and production readiness remain
**NOT VERIFIED by this run**. HTTP checks cover ONLYOFFICE api.js, authenticated command,
and fetch/conversion only. Project remains **INCOMPLETE**, upstream **LOCKED**.
