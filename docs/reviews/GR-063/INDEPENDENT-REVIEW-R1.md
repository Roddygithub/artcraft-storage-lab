# GR-063 independent evidence review — R1

Date: 2026-10-26
Verdict: **PROVISIONAL PASS**, bounded to the GR-063 evidence. No BLOCKER or
MAJOR finding. This is not a project GPT verdict or publication authorization.

## Finding

- **MINOR — wording overstated closure.** The test matrix initially described
  “Close/reopen,” but the retained browser observations establish opening a
  second session and do not record closing the first. The matrix and report
  now say a second fresh-session open from the Seafile file list and explicitly
  state that the first editor was not closed. This resolves the finding without
  changing the reported storage-backed reopen result.

## Review observations

- The reviewer verified the three manifest hashes, screenshot PNG structure
  and absence of metadata chunks, and inspected both images. They show the
  edited rectangle; the save image also shows the host's version confirmation
  and the native dirty asterisk, while the fresh-session image shows the
  rectangle in the newly opened editor.
- Source inspection confirms VectorCraft uses the in-page API/export polling
  adapter in `integration/gateway/hostpage.py`: captured export bytes are
  submitted to the gateway, and the host page displays success after an
  HTTP-success response with `ok:true`. That path does not send a save ACK to
  VectorCraft. The app's native dirty marker remaining after export is
  therefore not evidence against persistence, but native dirty-state clearance
  must not be claimed.
- The repository dispatcher maps SVG to VectorCraft without `?host=parent` and
  retains DOCX/XLSX/PDF routes. The report accurately preserves byte-identity
  and post-change ONLYOFFICE regression as unverified.
- The retained screenshots/transcript do not independently prove the live
  Seafile HTTP outcomes, active deployed candidate identity, history event,
  fresh storage read, synthetic-library-only scope, rollback state, or live
  ONLYOFFICE configuration. Those remain implementer-reported observations.
  The candidate verifier can verify a supplied static root; R1 verified the
  default staged candidate, not the live static deployment.

No files or services were changed or accessed by the reviewer. No browser
workflow was replayed and no project verdict was issued.
