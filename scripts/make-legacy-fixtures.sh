#!/usr/bin/env bash
# Regenerate the deterministic synthetic legacy/OpenDocument viewing fixtures.
#
# The committed bytes under lab/real-seafile/fixtures/legacy/ are the reviewed
# artifact; this script documents how an equivalent set was produced. LibreOffice
# embeds creation timestamps, so a rerun is equivalent, not byte-identical.
#
# Requires a pinned LibreOffice tool image (see the fixtures' PROVENANCE.txt).
# Nothing here touches Seafile, the network or a production system.
#
# usage: scripts/make-legacy-fixtures.sh <libreoffice-image> <output-dir>
set -euo pipefail

IMAGE=${1:?usage: make-legacy-fixtures.sh <libreoffice-image> <output-dir>}
OUT=${2:?usage: make-legacy-fixtures.sh <libreoffice-image> <output-dir>}
MARKER='GR-LEGACY-MARKER-20261108'

OUT=$(cd "$(dirname "$OUT")" && pwd)/$(basename "$OUT")
rm -rf "$OUT"
mkdir -p "$OUT/in" "$OUT/out"

printf '%s\nSynthetic legacy/OpenDocument viewing fixture.\n' "$MARKER" > "$OUT/in/doc.txt"
printf 'marker,%s\nvalue,42\n' "$MARKER" > "$OUT/in/sheet.csv"
cat > "$OUT/in/slide.fodp" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" xmlns:presentation="urn:oasis:names:tc:opendocument:xmlns:presentation:1.0" xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0" xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0" office:version="1.3" office:mimetype="application/vnd.oasis.opendocument.presentation">
 <office:body><office:presentation>
  <draw:page draw:name="page1">
   <draw:frame draw:name="title" presentation:class="title" svg:width="24cm" svg:height="4cm" svg:x="2cm" svg:y="2cm">
    <draw:text-box><text:p>$MARKER</text:p></draw:text-box>
   </draw:frame>
  </draw:page>
 </office:presentation></office:body>
</office:document>
EOF

podman --remote=false run --rm -v "$OUT:/w:Z" "$IMAGE" bash -lc '
set -e; mkdir -p /w/out; cd /w/in
c(){ soffice --headless --convert-to "$1" --outdir /w/out "$2" >/dev/null 2>&1; }
c doc doc.txt;   c odt doc.txt;   c fodt doc.txt
c xls sheet.csv; c ods sheet.csv; c fods sheet.csv; c csv sheet.csv
c odp slide.fodp; c fodp slide.fodp; c ppt slide.fodp; c pps slide.fodp; c ppsx slide.fodp
'

echo "generated in $OUT/out:"
ls -l "$OUT/out"
