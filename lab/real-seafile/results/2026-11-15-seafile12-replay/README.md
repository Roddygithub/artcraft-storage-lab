# Reproducible Seafile CE12 edit/save replay

Replayed on 2026-11-15 in an isolated rootless Podman stack, using the pinned
Seafile CE 12.0.14 image (`sha256:7bbe7043facbc639a8e6144f32d50dc4d771191ecaa68002efb2b0237fb90358`), synthetic accounts and synthetic files. The owner server and its data/configuration were not used.

## Browser results

| Editor / format | Assertions | Result |
| --- | ---: | --- |
| WordCraft / DOCX | 24/24 | PASS |
| GridCraft / XLSX | 27/27 | PASS |
| DeckCraft / PPTX | 15/15 | PASS |
| **Total** | **66/66** | **PASS** |

Each editor opened its synthetic file from Seafile Web, sent edits through the
WOPI bridge, produced a new Seafile version and reopened the persisted edit in
a fresh session. WordCraft and GridCraft each made two saves; DeckCraft made
one. The retained screenshots show the opened, edited, saved and reopened
states. Visual inspection confirmed the typed markers were visible after
reopening. DOCX and PPTX originals, first relays and readbacks are retained;
GridCraft's runner does not retain XLSX relay bytes, so its byte-level claim is
limited to the recorded browser assertions. Assertions are sanitized to names
and pass/fail values; account, repository IDs, tokens and raw browser logs are
omitted.

The run used the unmodified WordCraft v0.13.2, GridCraft v0.14.2 and DeckCraft
v0.16.0 bundles. `static-sha256.json` records the exact extracted static tree
used by the launcher. The bundle release digests are recorded in the adjacent
`lab/real-seafile/static/*-PROVENANCE.txt` files.

## Reproduction

Use [`local_ce12.py`](../../local_ce12.py), the adapted official CE12 Compose
file [`compose.ce12.yml`](../../compose.ce12.yml), and the exact static-tree
manifest here. The launcher copies a verified static tree into a new private
run directory, creates synthetic credentials, binds Seafile to loopback,
applies WOPI settings only to that disposable stack, runs the browser flows,
and tears the stack down.

The first replay exposed a launcher ordering bug: DeckCraft was added to the
editor map after the bridge had started. The bridge therefore advertised no
PPTX action and Seahub showed “Online view is not applicable.” The launcher now
configures `editors.json` before starting the bridge; this corrected replay
passed all three workflows.

Run the retained-evidence check from this directory:

```sh
python3 verify.py
sha256sum -c SHA256SUMS
```

## Limits

This proves only the synthetic sequential flows on the pinned isolated CE12
image. It does not establish broad Office fidelity, legacy-format support,
hardware acceptance, owner-server access, host-enforced read-only permissions,
or concurrent-writer safety. The known non-atomic WOPI save window remains.
Older free-review transcripts that were never retained remain unavailable;
this new replay does not reconstruct them. No production or upstream action
was performed.
