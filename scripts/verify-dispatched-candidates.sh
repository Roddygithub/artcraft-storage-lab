#!/bin/sh
set -eu

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <static-root>" >&2
  exit 2
fi

repo=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
static_root=$1

python3 - "$repo/integration/config/dispatch.json" <<'PY'
import json
import sys

expected = {
    "docx": {"app": "wordcraft", "url": "/artcraft/wordcraft/?host=parent"},
    "xlsx": {"app": "gridcraft", "url": "/artcraft/gridcraft/?host=parent"},
    "pdf": {"app": "pdfcraft", "url": "/artcraft/pdfcraft/?host=parent"},
    "svg": {"app": "vectorcraft", "url": "/artcraft/vectorcraft/"},
    "pcraft": {"app": "photocraft", "url": "/artcraft/photocraft/?host=parent"},
}
with open(sys.argv[1], encoding="utf-8") as dispatch_file:
    observed = json.load(dispatch_file)
if observed != expected:
    raise SystemExit(f"FAIL: dispatch mapping changed: {observed!r}")
print("PASS: dispatch maps all five tracked extensions to their expected apps")
PY

for gr in 055 056 057 058; do
  python3 "$repo/docs/reviews/GR-$gr/verify_candidate.py" --static-root "$static_root"
done
echo "NOTE: candidate checks above cover the four GR-055–058 candidates; PhotoCraft's GR-076 bundle has separate source and runtime evidence."
