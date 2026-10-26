# GR-071 — Recheck dispatched app candidates against the shared test static root

Date: 2026-10-26. Status: **GPT REVIEW PENDING**.
Project verdict remains **INCOMPLETE**; upstream publication remains **LOCKED**.

## Result

The four source-pinned candidates used by the recent WordCraft, GridCraft,
PdfCraft, and VectorCraft Seafile runs are present together under the same local
test static root. A new read-only wrapper checked the tracked dispatch mapping
and invoked each existing candidate verifier against that root. All checks
passed for **20 files totaling 207,970,569 bytes**:

| Route | Candidate and prior Seafile run | Verified input |
|---|---|---|
| DOCX → WordCraft | GR-055 candidate; GR-059 synthetic Seafile edit/version/fresh reopen | GR-055 source `00bc6a4b028013b2dfb0e85e8b326aeed3ecff6d`, GR-016 patch, transport `90c261de` |
| XLSX → GridCraft | GR-056 candidate; GR-061 synthetic Seafile edit/version/fresh reopen | Source `06920de8da609c19de7446945cfc62b844691efd`, pinned GR-016 patch, transport `90c261de` |
| PDF → PdfCraft | GR-057 candidate; GR-062 synthetic Seafile edit/version/fresh reopen | Source `57e531ccca0047597809748b5cb4276336d6051a`, GR-017 patch, transport `90c261de` |
| SVG → VectorCraft | GR-058 candidate; GR-063 synthetic Seafile export/version/fresh reopen | `v0.14.0`, commit `ad0566943ab9741e6356bbc9b53c3cc09895068d`, pinned `craft-fonts` commit `a71c20e30af613287c504f7e685ca8fad77752bc` |

The command is:

```sh
scripts/verify-dispatched-candidates.sh \
  /home/roddy/.cache/artcraft-storage-lab/gr059-deployment/integration/static
```

It fails if the checked-in dispatch mapping differs from the expected four
routes, if any app candidate's file set/size/hash/index linkage differs, if
GridCraft's source/patch/transport/overlay checks fail, or if VectorCraft's
index integrity values fail. The full command output and dispatch hash are in
[`checks.txt`](reviews/GR-071/checks.txt).

## How this updates GR-054

GR-054 is a dated inventory of the clean source base and parent-local
`integration/static` tree observed on 2026-10-25. Its finding that those
captured default bundles lacked matched exact provenance remains true for that
snapshot. GR-055–058 later produced separate source-pinned candidates, and
GR-059 plus GR-061–063 exercised those candidates against Seafile. GR-071 now
proves that the four per-app candidate file sets coexist and match their
recorded manifests in the GR-059 local test static root. It does **not** replace
the GR-054 `integration/static` inventory, promote the candidates there, or
prove that a currently running service serves this root.

## Boundaries

- The check is local and read-only. It does not contact Seafile, start a service,
  modify dispatch, copy assets, or promote a candidate.
- GR-059 and GR-061–063 are per-app Seafile browser runs. GR-071 does not claim
  one atomic end-to-end run of the four-route dispatcher or simultaneous
  Seafile/ONLYOFFICE compatibility.
- The repository's `integration/static` snapshot from GR-054 remains separate;
  the GR-059 test static root is a cache directory. Production deployment,
  TLS/proxy/security controls, permission revocation, external writers,
  response-loss handling, exact editor-message/readback byte identity, and a
  post-change ONLYOFFICE edit/save regression remain **NOT VERIFIED**.
- The PhotoCraft tree is still outside the four-route dispatch and its GR-054
  index-to-WASM mismatch is not addressed by this work.

See [`docs/reviews/GR-071/`](reviews/GR-071/) for the command transcript and
independent review. No upstream issue, PR, or RFC is authorized by this result.
