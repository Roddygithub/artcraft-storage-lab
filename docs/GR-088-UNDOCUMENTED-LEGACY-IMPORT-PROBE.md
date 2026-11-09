# GR-088 — undocumented legacy/OpenDocument import probe

**State: GPT REVIEW PENDING. Independent free review NOT PERFORMED for this item.
Project INCOMPLETE. Upstream LOCKED.**

GR-087 left seven formats unrouted because no upstream README documents a Craft
import for them. This item tests the actual pinned bundles instead of inferring
from documentation: the same `scripts/probe-legacy-import.py` harness that
proved the five documented imports now receives explicit `--cases` pairs and
short waits.

Bundles: WordCraft v0.16.0, GridCraft v0.17.0 and official unpatched DeckCraft
v0.16.0 (archive SHA-256
`8795d58ab02c30ad25f38525a79ee0e69c40b3d122e223dc04d2703827621f55`). Each case
opens the committed synthetic fixture through the upstream `?host=parent`
protocol, then saves; success means the marker
`GR-LEGACY-MARKER-20261108` is present in what the editor itself serialized.

## Result — 2 of 7 import, 5 do not

| Fixture | Editor | Import | Evidence |
| --- | --- | --- | --- |
| `slide.ppsx` | DeckCraft | **YES** | marker in `ppt/slides/slide1.xml`; saved PPTX 23,786 bytes |
| `sheet.fods` | GridCraft | **YES** | marker in `xl/sharedStrings.xml`; 196 XLSX cells, 8,327 bytes |
| `slide.ppt` | DeckCraft | no | saved a blank deck (5,048 bytes, no marker, no OPC parts) |
| `slide.pps` | DeckCraft | no | identical blank deck (same SHA-256 as `.ppt`) |
| `slide.odp` | DeckCraft | no | identical blank deck |
| `slide.fodp` | DeckCraft | no | identical blank deck |
| `doc.fodt` | WordCraft | no | no save payload at all, even with 60/45/30 s waits |

The four presentation formats that fail all produce the *same* 5,048-byte blank
deck (`sha256:7dbd50543d54e795…`), which is the signature of "opened as a new,
empty presentation" rather than a partial import. `doc.fodt` never becomes
dirty and never emits a payload, i.e. WordCraft rejects the flat ODF text file.

## Change made

`scripts/probe-legacy-import.py` gained `--cases FIXTURE=EDITOR` and explicit
`--open-timeout/--dirty-timeout/--save-timeout`; it now retains the first saved
payload per case for inspection. `run_slice.viewing_payload_has_marker` now also
scans generic OPC XML parts, so a PPTX slide is detected instead of being
reported as a missing marker; `tests/test_legacy_fixtures.py` covers that case.

Routing: only `fods` was added to the opt-in candidate
(`lab/real-seafile/editors.viewing.json`) because GridCraft is already part of
it. `ppsx` stays unrouted: DeckCraft is not part of the viewing candidate, and
adding an editor without a real-Seafile replay would be an unverified change.

## Limits

* Bundle-level only: no host page, bridge, Seafile route or new version. The
  `fods` route is configured and offline-checked, but its real-Seafile routing
  is **NOT VERIFIED** until the next `--viewing` replay.
* One synthetic fixture per format; no fidelity claim.
* Six formats remain unrouted: FODT, FODP, PPT, ODP, PPS and PPSX (PPSX is
  import-proven but has no viewing-candidate editor).
* No independent review of GR-088 yet. Project INCOMPLETE; upstream LOCKED.
