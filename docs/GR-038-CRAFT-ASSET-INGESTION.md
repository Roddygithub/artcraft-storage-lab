# GR-038 — Safe Craft Web asset ingestion

The fetcher no longer selects a mutable latest release or writes downloaded
assets into the active app directory. It requires an exact release tag and
SHA-256, verifies the archive, rejects unsafe ZIP contents, and stages it outside
the dispatch-selected path. Staging is **not** host-protocol or deployment
approval; a candidate must pass the app-specific protocol smoke before manual
promotion.

## Verification

| Check | Result |
|---|---|
| `bash -n scripts/fetch-craft-web.sh` | PASS |
| `git diff --check` | PASS |
| Exact asset stage | WordCraft v0.10.0 asset SHA-256 `46e32c024cac86d644874e7120ee9e42a6c0ccc76bd020ba9c741706b5b77b05` passed archive verification and staged under `integration/static/candidates/wordcraft/`; no active path is written by the script. |
| Existing-candidate refusal | PASS; repeated staging refused the existing path and the provenance-file hash remained unchanged. |
| Candidate-path symlinks | Guard added to reject symlinked root/app directories and resolved paths outside the candidate root; negative symlink case not executed. |
| Independent review | Luna High bounded re-review: provisional ACCEPT; no material finding remains. Symlink and malformed-ZIP rejection cases are code-inspected, not executed. |
| Negative ZIP cases | NOT RUN; archive traversal/symlink/ambiguous-root rejection is code-inspected only. |
| Host protocol compatibility of staged release | NOT VERIFIED; stage remains a candidate only. |

The command and staging rules are in [`docs/ASSET-INGESTION.md`](ASSET-INGESTION.md).
The staged release is generated and gitignored; it is not part of this evidence
bundle or a deployable artifact.

## Remaining distribution gate

The repository does not yet have a reviewed immutable app-build manifest or an
automated protocol-compatibility check. This change makes fetching explicit and
non-destructive; it does not close the broader distribution/readiness finding.
