#!/usr/bin/env bash
# Can the five unimportable legacy formats be covered by normalizing them to
# OOXML first? Converts each fixture with the pinned LibreOffice tool image,
# then probes both the converted copy (matching extension) and the same bytes
# under the original extension. The second set is expected to fail: the pinned
# bundles select their import filter by extension, so a bridge would have to
# present a converted name/extension, not just converted bytes.
#
# No Seafile, bridge or network access. Requires the pinned LibreOffice image
# and Playwright (run through uv).
#
# usage: scripts/probe-legacy-conversion.sh <libreoffice-image> <new-private-dir> <static-dir>
set -euo pipefail

IMAGE=${1:?usage: probe-legacy-conversion.sh <libreoffice-image> <new-private-dir> <static-dir>}
OUT=${2:?usage: probe-legacy-conversion.sh <libreoffice-image> <new-private-dir> <static-dir>}
STATIC=${3:?usage: probe-legacy-conversion.sh <libreoffice-image> <new-private-dir> <static-dir>}
ROOT=$(cd "$(dirname "$0")/.." && pwd)
FIXTURES="$ROOT/lab/real-seafile/fixtures/legacy"

OUT=$(cd "$(dirname "$OUT")" && pwd)/$(basename "$OUT")
rm -rf "$OUT"
mkdir -p "$OUT/in" "$OUT/out"
cp "$FIXTURES/slide.ppt" "$FIXTURES/slide.pps" "$FIXTURES/slide.odp" \
   "$FIXTURES/slide.fodp" "$FIXTURES/doc.fodt" "$OUT/in/"

podman --remote=false run --rm -v "$OUT:/w:Z" "$IMAGE" bash -lc '
set -e; cd /w/in
soffice --headless --convert-to pptx --outdir /w/out slide.ppt slide.pps slide.odp slide.fodp >/dev/null 2>&1
soffice --headless --convert-to docx --outdir /w/out doc.fodt >/dev/null 2>&1
'

cd "$OUT/out"
for name in slide.ppt slide.pps slide.odp slide.fodp; do
  cp slide.pptx "converted_${name%.*}_${name##*.}.pptx"
  cp slide.pptx "as_${name}"
done
cp doc.docx converted_doc_fodt.docx
cp doc.docx as_doc.fodt

uv run --with playwright --with pillow python "$ROOT/scripts/probe-legacy-import.py" \
  --static "$STATIC" --fixtures "$OUT/out" --output "$OUT/probe" \
  --cases converted_slide_ppt.pptx=deckcraft \
  --cases converted_slide_pps.pptx=deckcraft \
  --cases converted_slide_odp.pptx=deckcraft \
  --cases converted_slide_fodp.pptx=deckcraft \
  --cases converted_doc_fodt.docx=wordcraft \
  --cases as_slide.ppt=deckcraft \
  --cases as_slide.pps=deckcraft \
  --cases as_slide.odp=deckcraft \
  --cases as_slide.fodp=deckcraft \
  --cases as_doc.fodt=wordcraft || true

python3 - "$OUT/probe/summary.json" <<'PY'
import json
import sys

summary = json.load(open(sys.argv[1]))
results = {case["fixture"]: case for case in summary["cases"]}
converted = [name for name in results if name.startswith("converted_")]
original = [name for name in results if name.startswith("as_")]
assert len(converted) == 5 and len(original) == 5, summary
assert all(results[name]["ok"] for name in converted), {
    name: results[name].get("error") or results[name].get("kinds") for name in converted
}
assert not any(results[name]["ok"] for name in original), {
    name: results[name].get("kind") for name in original
}
print("PASS: 5 converted OOXML copies import; 5 original-extension copies are "
      "rejected, so a conversion path must also present a converted extension")
PY
