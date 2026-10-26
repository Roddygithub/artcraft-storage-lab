# GR-062 independent review R1

**Verdict:** bounded **PROVISIONAL PASS** with one MINOR documentation finding.
No blocker or major finding. This is not a project GPT verdict or publication
authorization.

## Finding and remediation

- **MINOR — verifier scope overstated.** The evidence README and test matrix
  described the GR-057 candidate verifier as checking provenance. It actually
  checks exact served-file membership, sizes, SHA-256 hashes, and index
  references. The README and matrix now state those checks precisely and point
  to the separate GR-057 source/build provenance record.

## Independently verified

- All three GR-062 evidence checksums pass; `git diff --check` passes.
- The save screenshot shows the edited field and PdfCraft's new-version
  confirmation. The fresh-reopen screenshot shows the same field value and the
  editor's open status. Neither screenshot exposes a private hostname, account,
  library ID, or session capability; the PNGs contain no textual metadata.
- The exact three GR-057 candidate assets are present in the recorded local
  deployment static root. The GR-057 verifier passes against both the live
  static directory and the original candidate. The local service definition
  points to that deployment.
- The current dispatcher differs from its retained pre-change copy only by the
  PDF route; DOCX/WordCraft and XLSX/GridCraft entries are unchanged. The
  WordCraft and GridCraft candidate verifiers pass, and their deployed files
  match the pre-change rollback archive.
- The private rollback archive is outside Git and readable. The pinned local
  AcroForm fixture is 1,744 bytes and matches the GR-057 fixture digest.
- The report, screenshots, and sanitized transcript are consistent with the
  supplied browser observations. Fixture uploads are clearly separated from
  editor persistence; the 655-byte PDF is correctly described as unedited.

## Remaining limits

- HTTP results, the Seafile history `Modified` event, and distinct gateway
  sessions are retained as implementer observations, not independently
  inspectable raw captures.
- The reviewer did not access Seafile, Proxmox, or services. Current remote
  allowlist contents, post-restart `ENABLE_ONLYOFFICE=True`, remote ONLYOFFICE
  state, and service/LXC state were not independently verified.
- Actual served bytes, editor-message/readback hash identity, optimized output,
  and post-change ONLYOFFICE edit/save remain **NOT VERIFIED**.

No files or services were changed by the reviewer. R2 confirmed the wording
correction and found no remaining actionable minor; see
`INDEPENDENT-REVIEW-R2.md`.
