# GR-079 — read-only Seafile history verification after GR-078

## Result

After the GR-078 combined replay, Seafile Web's History view showed a current
version for each of the five synthetic files. The displayed current-row times
and sizes are recorded in the sanitized JSON. The version counts were 5 DOCX,
3 XLSX, 4 PDF, 3 SVG and 4 Pcraft. No file was edited or downloaded during
this read-only check. The retained record does not compare these sizes with a
separate file-list observation.

The sanitized record includes only filename, displayed version time, size and
count. Seafile displayed a modifier name in each history row; it was excluded
from the retained evidence. No screenshot was retained to avoid copying that
personal display name. The check confirms history entries exist for the current
synthetic files; it does not compare saved editor payloads byte-for-byte with
Seafile readback or establish production behavior.

## Scope

- Existing synthetic `ArtCraft GPT Review Synthetic` library only.
- Read-only navigation through each file's Seafile Web History menu.
- No config, dispatcher, allow-list, service or ONLYOFFICE change.
- No history download, restore, rename, delete or edit action.
- Runtime observations are recorded in
  [`reviews/GR-079/history-observations.json`](reviews/GR-079/history-observations.json).

R1 returned **PROVISIONAL MINOR**; both findings are recorded in
[`reviews/GR-079/INDEPENDENT-REVIEW-R1.md`](reviews/GR-079/INDEPENDENT-REVIEW-R1.md)
and addressed in [`reviews/GR-079/RESPONSE-R1.md`](reviews/GR-079/RESPONSE-R1.md).
R2 verified the remediations and returned **PROVISIONAL PASS** with no new
findings. Project GPT review remains PENDING and upstream publication remains
LOCKED.
