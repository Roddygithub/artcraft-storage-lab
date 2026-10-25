# GR-058 evidence — VectorCraft reproducible candidate

Implementation base: `247ae75753d4d22c7567b53271b3bf0c0d119f99`.
Candidate: `/home/roddy/.cache/artcraft-storage-lab/gr058-vectorcraft-static/vectorcraft`.
Status: **candidate verification PASS; independent R1 PROVISIONAL PASS**.

## Evidence files

| File | Evidence |
|---|---|
| [inventory.json](inventory.json) | Exact source and font pins, release checksum and comparison hashes, every candidate file size/SHA-256, and index references |
| [verify_candidate.py](verify_candidate.py) | Stdlib-only candidate membership/hash/index verifier |
| [checks/build.txt](checks/build.txt) | Commands, exact source validation, release archive/checksum comparison, toolchain and build result |
| [checks/checks.txt](checks/checks.txt) | Final build, browser, inventory, syntax, whitespace and scope check summary |
| [checks/browser-smoke.txt](checks/browser-smoke.txt) | Actual candidate browser host roundtrip result and saved SVG hash |
| [checks/vectorcraft-path-edit.png](checks/vectorcraft-path-edit.png) | Browser screenshot showing the visible pencil path and host save acknowledgement |

## Reproduction

From the repository root, check candidate bytes and links:

```sh
python3 docs/reviews/GR-058/verify_candidate.py
```

Run the synthetic Chromium host harness against the staged candidate:

```sh
uv run --with playwright --python 3.14 -- python -u tests/test_vectorcraft_candidate_host.py \
  --static-root /home/roddy/.cache/artcraft-storage-lab/gr058-vectorcraft-static \
  --screenshot docs/reviews/GR-058/checks/vectorcraft-path-edit.png
```

The test serves the built candidate locally, renders the current
`integration.gateway.hostpage.render` VectorCraft adapter, and implements only
synthetic loopback document storage. The actual app page API opens the fixture,
draws and serializes a path, and the adapter polls and saves exact bytes. The
test reopens through a fresh host/editor session and checks the parsed path.
This is not real Seafile or a common-host-protocol result.

## Review handoff and limits

The official release ZIP checksum was verified against its release checksum
list. Its index/JS/WASM match GR-054's local VectorCraft bundle evidence. The
source build's principal files differ from the release archive; the difference
is captured, not masked. The exact source and release-pinned `craft-fonts`
inputs were used. That font checkout lacks several optional faces listed by
VectorCraft; details are in the report and build output. Release-binary
reproduction is **NOT VERIFIED**.

No Seafile service was contacted. The parent reports Seafile 12.0.14's
`/thirdparty-editor/file-save/` endpoint is 404; the exact-build Seafile
roundtrip was therefore not run. No dispatch change, credential, production
data, ONLYOFFICE change, upstream issue, PR, or RFC was used. Independent
review is pending; the task leaves the changes uncommitted.
