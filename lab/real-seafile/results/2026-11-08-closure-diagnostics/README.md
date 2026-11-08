# Historical closure diagnostics — local candidate

These are **historical-source private harness assertions**, not final candidate
or independent runtime proof. No runtime was rerun for this inventory. No
forensic or project PASS is claimed. Parent independent review remains required.

| Private run suffix (under `closure-`) | Slice assertions true/false | Browser assertions true/false |
| --- | --- | --- |
| wordcraft-final-20261108-run1 | 46/0 | 28/0 |
| gridcraft-20261108-run1 | 46/0 | 27/0 |
| pdfcraft-20261108-run1 | 46/0 | 18/0 |
| cadcraft-20261108-run1 | 46/0 | 20/0 |
| vector-20261108-run4 | 46/0 | 20/0 |
| fig-20261108-run1 | 46/0 | 21/0 |
| onlyoffice-final-20261108-run2 | not included | 11/0 (limited diagnostic) |

ONLYOFFICE final-run2 ran without WOPI and has no final fresh reopen. Its 11
assertions are a limited diagnostic, **not regression/coexistence PASS**.
The repeated Craft slice checks, including ONLYOFFICE-related check names,
are not six independent ONLYOFFICE regressions or evidence of full coexistence.
Check names are retained verbatim assertions, not endorsements of their meaning.

`inventory.json` includes only allowlisted check names/booleans and totals from
six pairs of `results/slice.json` and `results/browser.json`, plus the selected
ONLYOFFICE `results/onlyoffice-browser.json`. `raw_private_sha256` hashes the
original complete private JSON bytes, not a sanitized reconstruction. ONLYOFFICE
totals are derived from its checks; Craft totals were also checked against the
original declared totals. No other private result artifact is included or hashed.
Details, URLs, repository/account/version/session identifiers, secrets, logs,
screenshots and document payloads are omitted.

For each run, `source_snapshot` records SHA-256 of every non-editor-static file
actually present in its private `app/` snapshot (29 files, including the bridge
host assets). `static_manifest` hashes every file actually present under that
snapshot's `app/lab/real-seafile/static/` (154 files, all bundled editors, including
PROVENANCE files). These are byte inventories, not claims about served bytes,
upstream identities, build provenance accuracy, or correspondence to a Git tree.
No source/static contents are copied. Relative filenames are artifact locators.

Source comparisons use local Git blob bytes at the two full commits recorded in
`comparison_commits`; each source record retains the reference SHA-256 and exact
byte-equality boolean. Missing Git paths would be represented by null SHA-256.
Only captured source paths are compared, not entire repository trees. Static
assets have an actual-byte manifest rather than an inferred upstream identity.

| Captured source comparison | Differences from reference |
| --- | --- |
| All six Craft snapshots vs `32ce907` | `bridge/README.md`, `bridge/__main__.py`, `lab/real-seafile/local.py`, `lab/real-seafile/run_onlyoffice_browser.py` |
| All six Craft snapshots vs `4e7d637` | None among the 29 captured source paths |
| ONLYOFFICE snapshot vs `32ce907` | Same four paths listed above |
| ONLYOFFICE snapshot vs `4e7d637` | `lab/real-seafile/local.py`, `lab/real-seafile/run_onlyoffice_browser.py` |

This does not identify a run's Git commit: matching selected captured bytes is
insufficient to establish checkout identity. Final-candidate applicability and
independent runtime correctness are **NOT VERIFIED**.

Run the offline stdlib verifier from any directory:

```sh
python3 lab/real-seafile/results/2026-11-08-closure-diagnostics/verify.py
```

To additionally rehash original private result JSON, re-extract its allowlisted
checks, verify the complete private app file inventory, and recheck local Git
comparisons (no network or services):

```sh
python3 lab/real-seafile/results/2026-11-08-closure-diagnostics/verify.py --private-root /home/roddy/.cache/artcraft-storage-lab
```

Exact included artifact inventory: `README.md`, `inventory.json`, `verify.py`,
`SHA256SUMS`. SHA256SUMS covers the other three files; it cannot self-authenticate.
Without private inputs the verifier checks packaged consistency only. Checksums
are integrity references, not an independent attestation or proof of execution.
