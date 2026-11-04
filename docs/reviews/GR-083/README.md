# GR-083 evidence bundle

This bundle records a corrected-corpus synthetic DOCX comparison run on 2026-11-04. The public
JSON omits Seafile library IDs, URLs, tokens, cookies, raw DOM, and raw logs. Screenshots are
unaltered captures from the disposable synthetic lab; private logs and DOCX bytes are not
included.

**Current evidence:** the R2-reviewed corpus was opened three times in WordCraft and three times
in ONLYOFFICE. All six editor readiness checks and unchanged Seafile readback checks passed; no
browser downloads were observed. This run did not edit or save documents and did not create
Seafile versions. Independent evidence review R3 is pending. The OOXML ordering checks are
focused regression checks, not full ECMA-376 schema validation.

The initial pre-remediation run is archived under `runtime/pre-remediation/`; it is historical
and does not validate the corrected corpus. Its two ONLYOFFICE plugin/theme 502s did not recur in
the corrected run, but their cause remains **NOT VERIFIED**. The corrected run recorded two
WordCraft `net::ERR_ABORTED` request-failed events; targets and cause are omitted and
**NOT VERIFIED**.

## Contents

- `runtime/observations.json` — six corrected-corpus open/readback outcomes, fixture hashes,
  limited visual notes and sanitized request-failure counts.
- `runtime/environment.json` — disposable image tags/digests and isolation scope.
- `runtime/cleanup.json` — dedicated API service, project containers/networks and port cleanup.
- `runtime/private-artifact-hashes.json` — hashes only for private raw records retained in the
  local cache, not the records themselves.
- `runtime/candidate-provenance.json` — reviewed source hashes, runtime-copy match, and the
  served WordCraft asset inventory/hash.
- `runtime/pre-remediation/` — prior sanitized observations, provenance, cleanup record and
  screenshots retained as historical evidence.
- `INDEPENDENT-REVIEW-R1.md` — findings and remediation status from the first independent review.
- `INDEPENDENT-REVIEW-R2.md` — bounded source re-review; no full schema or runtime validation.
- `runtime/wordcraft/` — prose/runs, lists/table, first-page layout and page-2 screenshots.
- `runtime/onlyoffice/` — prose/runs, lists/table, first-page and corrected page-2 screenshots.

Every retained PNG was checked for valid chunk framing and absence of textual/EXIF metadata or
trailing bytes. The page-2 screenshots show the heading, paragraph and table in both editors. In
ONLYOFFICE, the first-use tip is in lower-right whitespace and the table is visible near the
viewport bottom. The initial wheel-only captures are not included.

The runtime result is limited to opening and reading the same corrected synthetic fixtures. No
editor save, new version, or edit fidelity was tested. WordCraft recorded two aborted network
requests (`net::ERR_ABORTED`); their request targets and cause are not in this bundle. The earlier
ONLYOFFICE 502s were not reproduced; the original cause remains unknown. Earlier disposable
attempts that failed before both editor routes completed are not counted as passing runs; the
retained current result is the corrected completed replay.

Project GPT remains **INCOMPLETE**; upstream publication remains **LOCKED**. This initial run was
direct parent work and is not Aptarchy task completion.
