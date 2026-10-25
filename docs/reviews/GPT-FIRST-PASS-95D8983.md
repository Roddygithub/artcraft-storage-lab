# GPT-6.1 Sol first-pass review — 2026-10-25

Candidate reviewed: `95d89835b2b1d06fd098c586469ed03b8fd0549e`  
Working tree at review: clean  
Mode: read-only source and retained-evidence review; no services started and no
production or upstream systems accessed.

## Verdict: INCOMPLETE — GPT REVIEW PASS not granted

The synthetic DOCX workflow is now credibly demonstrated. This review does not
find that workflow broken. The project-wide acceptance and publication gates
remain open, so the previous “no Seafile E2E” finding is closed but the overall
project FAIL/NOT READY conclusion is not replaced by PASS.

## Findings

| Severity | Finding | Closure evidence required |
|---|---|---|
| BLOCKER | ONLYOFFICE preservation is not verified. The routing double proves fallback selection, not a real Document Server edit/save/version/reopen. | Complete the regression on a safe synthetic setup with ONLYOFFICE enabled. |
| MAJOR | Authorization and concurrency coverage is partial: revocation, expired/replayed capabilities, external writers, and interrupted writes remain unverified. | Exercise these failures against the patched stack; show no data loss or false save acknowledgement. |
| MAJOR | Writable support depends on custom Seahub and C-fileserver patches. Stock/Go-server rejection has not been verified at runtime. | Define supported server versions and verify unsupported versions fail closed without unconditional writes. |
| MAJOR | Production security topology is unverified. Loopback-origin tests do not establish TLS, proxy, CSP, CSRF, or adversarial-frame safety. | Test a representative isolated deployment and its negative security cases. |
| MAJOR | `scripts/fetch-craft-web.sh` fetches mutable latest releases and replaces static app assets without a pinned digest or host-protocol compatibility check. | Pin reviewed artifacts and verify their hashes and required host protocol before installation. |
| MAJOR | The intended combined distribution and licensing treatment is undecided. This is an unresolved review gate, not a finding of infringement. | Record the distribution model, notices/source obligations, and owner acceptance. |
| MINOR | The test matrix understates the later GridCraft formula-recalculation evidence. | Reconcile the matrix with the GR-016 follow-up evidence. |

## Verified progress

- GR-015 records the synthetic Seahub file-list click → real WordCraft Web/WASM
  edit → committed Seafile version → editor confirmation → fresh file-list
  reopen with the edit visible.
- Two real WordCraft sessions saving concurrently produced one committed winner
  and one dirty conflict loser; a fresh open rendered only the winner.
- Later work records Seafile version/reopen flows for GridCraft, PdfCraft,
  VectorCraft, CADCraft, and SoundCraft. GR-037 additionally records matching
  editor-message, gateway-body, and Seafile-readback hashes for PhotoCraft.
- This evidence describes isolated synthetic environments. It does not establish
  production readiness or broad support for all ArtCraft applications.

## Readiness boundary

The defensible claim is a demonstrated synthetic integration on a patched
Seafile C-fileserver stack. Production readiness and project acceptance remain
incomplete. Upstream publication remains locked. SoundCraft and PhotoCraft stay
excluded from the committed dispatcher; the current dispatcher lists DOCX,
XLSX, PDF, and SVG only.

Evidence reviewed: `docs/reviews/GR-015/ISOLATED-RUNTIME-E2E-20261023.md`,
`docs/reviews/GR-016/`, `docs/reviews/GR-017/`, `docs/reviews/GR-018/`,
`docs/reviews/GR-031/`, `docs/reviews/GR-036/`, `docs/reviews/GR-037/`,
`docs/SECURITY.md`, `docs/LICENSING.md`, `docs/TEST-MATRIX.md`,
`integration/config/dispatch.json`, and `scripts/fetch-craft-web.sh`.
