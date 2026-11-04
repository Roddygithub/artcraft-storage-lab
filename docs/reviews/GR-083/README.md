# GR-083 evidence bundle

This bundle retains the sanitized result of the 2026-11-04 synthetic DOCX comparison. Its JSON
omits Seafile library IDs, URLs, tokens, cookies, and raw DOM. Screenshots are unaltered captures
from the disposable synthetic lab; private logs and DOCX bytes are not included.

## Contents

- `runtime/observations.json` — six bounded file-open/readback outcomes and fixture hashes.
- `runtime/environment.json` — disposable image tags/config IDs and isolation scope.
- `runtime/cleanup.json` — dedicated API service and test-container cleanup status.
- `runtime/private-artifact-hashes.json` — hashes only for private raw records retained in the
  local cache, not the records themselves.
- `runtime/wordcraft/` — prose/runs, lists/table, first-page layout and page-2 screenshots.
- `runtime/onlyoffice/` — prose/runs, lists/table, first-page and corrected page-2 screenshots.

Every retained PNG has valid chunk framing and only image/color chunks; no textual, EXIF, or
trailing data was found. Corrected page-2 screenshots show text in both editors; the ONLYOFFICE
table is partly obscured by a first-use tip and viewport crop. The initial wheel-only captures
are not included. The corrected ONLYOFFICE run logged two 502 responses on plugin/theme
manifest endpoints; their cause is not established.

The runtime result is limited to opening and reading the same synthetic fixtures. No editor
save, new version, or edit fidelity was tested. Earlier disposable attempts that failed before
both editor routes completed are not counted as passing runs; the retained result is the
corrected completed replay.

Project GPT remains **INCOMPLETE**; upstream publication remains **LOCKED**. This run was direct
parent work and is not Aptarchy task completion.
