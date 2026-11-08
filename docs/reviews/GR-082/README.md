# GR-082 evidence bundle

This bundle records the successful isolated CADCraft runtime attempt on
2026-11-03. The lab used a fresh rootless Podman project and synthetic Seafile
data. The source candidate was checked against the prepared runtime source
manifest before launch. Runtime cleanup removed the project's containers and
network; bind data and raw run records remain outside Git.

## Results

- `runtime/slice-summary.json`: sanitized HTTP result, **48 passed / 0 failed**.
- `runtime/browser-summary.json`: sanitized Chromium result, **95 passed / 0
  failed**; all 18 CADCraft-specific assertions passed. The checks include the
  real Seafile list open, visible user edit, host save confirmation,
  user-attributed new version, exact relay/readback byte equality, no edited
  output download, and a fresh Seafile-list reopen rendering the saved circle.
- `runtime/cadcraft-typed.png`, `cadcraft-saved.png`, and
  `cadcraft-reopened.png`: editor canvas before save, after host confirmation,
  and after fresh-session reopen.
- `runtime/deckcraft-reopened-saved.png`: confirms the later DeckCraft flow
  continued after CADCraft in the same browser run.
- `runtime/private-artifact-hashes.json`: SHA-256 digests of the private raw
  slice, browser, and console records. Raw records are not included because
  they contain synthetic repository/session details and request data.
- `runtime/candidate-provenance.json`: base revision, hashes of the changed
  source and regression test, lab compose hash, and source bundle archive
  hashes.

The first browser attempt failed six CADCraft assertions and is not included as
passing evidence. Its diagnosis led to the parser and fixture-coordinate fixes;
the recorded successful run used a new data volume and separate Compose
project. See [the report](../../GR-082-CADCRAFT-REAL-SEAFILE-ROUNDTRIP.md).

## Limits and review state

The runtime used synthetic data and headless Chromium. It does not verify
production, human HTTPS behavior, broad CADCraft DXF fidelity, other browsers,
or a post-change ONLYOFFICE UI regression. R1/R2 found P3 count errors in
current summaries; both are corrected. R3 returned a bounded provisional pass
with no current P1–P3 findings; the runtime was not replayed by the reviewer.
Project GPT remains **INCOMPLETE** and upstream publication **LOCKED**. This
was direct parent work, not successful completion by Aptarchy.

The sanitized summaries omit repository IDs, URLs, account names, session
details, tokens, cookies, and raw per-check detail. SHA-256 checksums for every
file in this bundle are in `SHA256SUMS`.
