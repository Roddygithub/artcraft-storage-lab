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

Routing: both importable formats are now in the opt-in candidate
(`lab/real-seafile/editors.viewing.json`): `fods` to GridCraft and `ppsx` to
DeckCraft. The DeckCraft bundle is staged in the verified static, its native
`deckcraft` extension is included so its own workflow keeps a route, and
Seahub's `--viewing` WOPI tuples include `fods`, `ppsx` and `deckcraft`. Their
real-Seafile routes were verified by the replay below.

## Real-Seafile replay — 2026-11-10

A fresh rootless `--viewing` lab on Seafile CE 13.0.28 passed HTTP **59/59** and
browser **173/173**, including **29** viewing checks. FODS opens from the Seafile
file-list click, routes to GridCraft, downloads nothing and writes no version;
PPSX does the same through DeckCraft; the native `.deckcraft` workflow passes
again; the documented five still pass; and FODT/FODP/PPT/ODP/PPS still have no
route. Sanitized evidence and verifier:
`lab/real-seafile/results/2026-11-10-viewing-fods-ppsx/` (verifier PASS).

The launcher was interrupted after the browser container finished, so its final
exit code was not captured; the browser wrote a complete result and the project
containers were removed manually. No runtime/save of the legacy fixtures is
claimed, and rendered content remains NOT VERIFIED.

## Limits

* Bundle-level probe for the import claim; the replay above covers routing and
  safety only. Neither proves rendered content or a legacy save.
* One synthetic fixture per format; no fidelity claim.
* Five formats remain unrouted and unimportable: FODT, FODP, PPT, ODP and PPS.
* No independent review of GR-088 yet. Project INCOMPLETE; upstream LOCKED.
