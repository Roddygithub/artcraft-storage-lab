# GR-038 / GR-041 — Safe Craft Web asset ingestion and size limits

The fetcher requires an exact release tag and SHA-256, downloads at most 256 MiB
with a 30-second socket timeout and a 15-minute total deadline, and stages the
verified asset outside the dispatch-selected path. Before `zipfile` builds its
in-memory entry table, the helper checks the end-of-central-directory record
and rejects more than 10,000 entries, multi-disk ZIPs, and ZIP64. Extraction
rejects unsafe paths, duplicate normalized names and special file types; it
caps total extracted bytes at 1 GiB using both declared sizes and actual
streamed bytes. These limits apply to candidate staging only; no active app tree
is modified. Staging is **not** host-protocol or deployment approval; a
candidate must pass an app-specific protocol smoke before manual promotion.

## Verification

| Check | Result |
|---|---|
| `bash -n scripts/fetch-craft-web.sh` | PASS |
| `python3 tests/test_gr041_craft_zip_limits.py` | PASS; eight tests cover byte limits/deadline, entry-count preflight, ZIP64/multi-disk rejection, duplicate/traversal/absolute/backslash/symlink rejection, missing assets, and malformed ZIP rejection |
| `git diff --check` | PASS |
| Exact asset stage | WordCraft v0.10.0 asset SHA-256 `46e32c024cac86d644874e7120ee9e42a6c0ccc76bd020ba9c741706b5b77b05` passed archive verification and staged under `integration/static/candidates/wordcraft/`; no active path is written by the script. |
| Existing-candidate refusal | PASS; repeated staging refused the existing path and the provenance-file hash remained unchanged. |
| Candidate-path symlinks | Guard added to reject symlinked root/app directories and resolved paths outside the candidate root; negative symlink case not executed. |
| Independent review | Luna High bounded GR-038 re-review: provisional ACCEPT; it predates GR-041. GR-041 exact round 3: PROVISIONAL PASS, no blocker/major (`docs/reviews/GR-041/INDEPENDENT-REVIEW-R3.md`). |
| Unsafe ZIP path/symlink cases | Traversal, absolute/backslash paths, duplicate normalized names, Unix symlink, multi-root, and missing index/WASM negative tests pass. |
| Host protocol compatibility of staged release | NOT VERIFIED; stage remains a candidate only. |

GR-041 tests use small synthetic in-memory/local data and reduced limits; they
verify boundary behavior without allocating files near the production caps. A
live release download was not repeated. ZIP64 and multi-disk archives are
intentionally unsupported. The 15-minute total deadline is checked between
reads; a read already in progress can last up to the 30-second socket timeout.

The command and staging rules are in [`docs/ASSET-INGESTION.md`](ASSET-INGESTION.md).
The staged release is generated and gitignored; it is not part of this evidence
bundle or a deployable artifact.

## Remaining distribution gate

The repository does not yet have a reviewed immutable app-build manifest or an
automated protocol-compatibility check. This change makes fetching explicit and
non-destructive; it does not close the broader distribution/readiness finding.
