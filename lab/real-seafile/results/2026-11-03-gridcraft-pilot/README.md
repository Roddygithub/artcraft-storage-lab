# GridCraft and WordCraft genuine-edit replay — 2026-11-03

**HTTP 48/48; Chromium browser 48/48** against stock Seafile CE 13.0.28 in a fresh isolated
rootless Podman lab. Exact source candidate: `29484f65d5c09f3d819b87c1f64b0c41f0e6d567`,
implementation `a9eb3afc95ae5b92337f84a51f9e13e1fa75471d`. Its independent code-stage GPT R2
review passed without findings; the reviewer independently reran 23 offline Chromium checks.

| Observed by the real browser/API scenario | Result |
| --- | --- |
| Seafile file-list clicks launch released WordCraft 0.13.2 and GridCraft 0.14.2 | PASS |
| Trusted input changes each document before Save; editor request contains the new content | PASS |
| Host confirms save; user-attributed Seafile version contains the edit and differs from input | PASS |
| Old editor is closed; a fresh browser context logs in and opens the file from the file list | PASS |
| Reopened host reads exactly the saved bytes; editor accepts a second trusted edit | PASS |
| Second save creates another version, retaining both edits in editor output and storage | PASS |
| Neither editor save causes a browser download | PASS |

GridCraft also retains fixture A1=`1`. The captures visibly show the first value at J3, then
the second value at P16 with J3 retained. WordCraft's final capture shows both typed markers.
These images corroborate visible states; chronology, request/readback identity and version
attribution come from the parent-operated runner's assertions, not from screenshots alone.
The 48 browser checks comprise login (1), WordCraft (22), and GridCraft (25).

## Retained boundary and reproduction

`slice.json` and `browser.json` preserve names, booleans, counts, timestamps and SHA-256 of the
private raw JSON. Synthetic repository IDs and free-form details are omitted because they can
contain capabilities or incidental identity. Raw logs, HTML and secrets remain outside Git.
Four captures are unmodified browser PNGs, visually inspected and checked for textual/EXIF
metadata. Runtime replay was performed by the parent; the source reviewer did not replay it.

`runtime-compose.yml`, `runtime-runner.py`, and `runtime-editors.json` retain the nonsecret
configuration. Copy these to a private lab root as `compose.yml`, `run-lab.py`, and
`app/lab/real-seafile/editors.json`; provide a fresh private `.env` and the exact source/bundles.
The runner starts the synthetic stack and executes HTTP `slice`, then `browser`. It changes
only the fresh lab's managed Seahub settings block. It is the retained Podman adaptation of
the repository workflow; this is not a claim that the Lima/Docker `up.sh` launcher ran here.

`runtime-source-hashes.json` records 19 prepared files verified against the candidate before
execution; not every listed file is an entrypoint. `image-digests.json` records local image
identities. Five ZIPs were checked against recorded upstream SHA-256 and imported through
`scripts/craft_web_zip.py extract`; file sets and bytes match the previous verified release
inputs. `bundle-provenance.json` records those inputs. Only WordCraft/GridCraft are selected
for browser execution; the other three bundles have HTTP asset coverage only. No editor
source or bundle was modified. CPU/memory limits and loopback ports are in `SOURCE.json`.

The runner and its service cleanup removed this project's containers and network. The private
Podman API service was stopped; synthetic data remains private for reproduction. These cleanup
observations are parent-recorded, not historical state independently authenticated by this bundle.

```
cd lab/real-seafile/results/2026-11-03-gridcraft-pilot
sha256sum -c SHA256SUMS
python3 verify.py
```

## Aptarchy and remaining limits

Aptarchy generated the original code and its GPT reviewer rejected two defects. Both free
remediators then stopped; that task remains blocked, with the FAIL and failed dispatches
retained. The parent corrected the candidate, obtained independent review, and operated this
runtime replay. This is useful agent output followed by manual recovery, not autonomous
Aptarchy completion. See the [code/recovery report](../../../../docs/aptarchy/2026-11-03-gridcraft-browser-edit-slice.md).

This run covers one synthetic DOCX and one synthetic XLSX. It does not establish other-editor
genuine-edit workflows, ONLYOFFICE browser edit/save fidelity, HTTPS/manual UX, or production
readiness. HTTP checks include ONLYOFFICE api.js, authenticated command, and fetch/conversion
only. Production and upstream were untouched. Project GPT remains **INCOMPLETE**;
upstream remains **LOCKED**.
