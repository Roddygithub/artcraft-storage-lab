# Legacy conversion feasibility — the five unimportable formats

**State: offline probe evidence. Project INCOMPLETE; upstream LOCKED.** This is
not an independent review and does not add a route, dependency or deployment.

GR-088 proved the pinned bundles cannot import PPT, PPS, ODP, FODP or FODT. This
probe asks the next question: if a converter normalized them to OOXML first,
would the bundles import the result? It also tests whether the same bytes are
accepted under the original extension.

## Method

`scripts/probe-legacy-conversion.sh` converts each committed fixture with the
pinned `artcraft-fixture-tools` image (LibreOffice 7.4.7.2) and runs the same
bundle-level probe used by GR-088, once per converted copy:

| Case | Bytes | Name/extension | Editor |
| --- | --- | --- | --- |
| `converted_slide_ppt.pptx` | PPTX (from PPT) | `.pptx` | DeckCraft |
| `converted_slide_pps.pptx` | PPTX (from PPS) | `.pptx` | DeckCraft |
| `converted_slide_odp.pptx` | PPTX (from ODP) | `.pptx` | DeckCraft |
| `converted_slide_fodp.pptx` | PPTX (from FODP) | `.pptx` | DeckCraft |
| `converted_doc_fodt.docx` | DOCX (from FODT) | `.docx` | WordCraft |
| `as_slide.ppt`, `as_slide.pps`, `as_slide.odp`, `as_slide.fodp` | same PPTX bytes | original deck extension | DeckCraft |
| `as_doc.fodt` | same DOCX bytes | `.fodt` | WordCraft |

The probe opens each pair in a same-origin `?host=parent` wrapper, sends
`<app>:open`, presses Ctrl+S and requires the fixture marker in the document the
editor serializes.

## Result

| Case | Result |
| --- | --- |
| 5 converted copies with matching OOXML extension | **PASS**: marker found (DOCX text for FODT; `ppt/slides/slide1.xml` for all four deck formats) |
| 5 original-extension copies carrying those bytes | **FAIL**: no save payload with the marker |

So the editor accepts the converted bytes only when the name/extension also
matches the format it is being asked to import. Conversion alone, under
`slide.ppt` or `doc.fodt`, is not enough.

## What this means

A bridge-side conversion path is technically possible, but it is an
architectural change, not a routing flag:

1. It needs a converter runtime (LibreOffice or equivalent) in the bridge
   image, plus conversion time, cache/memory limits and failure handling.
2. It must present the editor a converted name/extension, not the original one.
   That changes the host title and the WOPI `BaseFileName` contract.
3. These five formats are view-only in the current Seafile configuration, but
   the WOPI token still carries write permission for an owner. A safe view-only
   path must force `UserCanWrite=false`; otherwise an editor could save OOXML
   bytes into the original `.ppt`/`.fodt` file. The existing routed legacy
   formats share that risk and are not save-tested.
4. Saving back to the original format would need a reverse conversion and a
   fidelity policy; this probe does not test that.

No converter is added here: it would add a heavyweight dependency and change
the deployment and save contract, which the project's zero-patch, MVP-first
rules reserve for an explicit owner decision. The alternatives are upstream
import support (upstream is LOCKED) or accepting the five formats as uncovered.

## Reproduce

```sh
scripts/probe-legacy-conversion.sh \
  localhost/artcraft-fixture-tools:20261108 \
  /absolute/new/private-dir \
  /absolute/verified-static
```

Expected: `5 converted OOXML copies import; 5 original-extension copies are
rejected`. Conversion output embeds timestamps, so it is equivalent, not
byte-identical, across runs.

## Limits

* Bundle-level only: no Seafile, bridge, route, version or rendered-pixel claim.
* One synthetic fixture per format; not broad fidelity.
* Wire-format conversion is not tested for save-back, concurrency or locking.
* Independent review: NOT PERFORMED.
