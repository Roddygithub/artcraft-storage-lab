# GR-017 bounded evidence review — Nemotron Free, round 1

**Review scope:** PdfCraft synthetic Seafile save/version/readback/reopen evidence only

**Candidate project verdict:** none; this is not a GPT final review

**Result:** **ACCEPT WITH MINOR QUALIFICATIONS**

## Findings

**BLOCKER:** None.

**MAJOR:** None.

**MINOR:** The previously recorded PdfCraft lifecycle test coverage gap remains:
the browser timeout, response-loss, Save As, send-failure, and capacity-recovery
paths have not been exercised end-to-end. The GR-017 README and Sol low round 4
report already disclose this limitation.

## Evidence checked

The reviewer inspected the E2E report, both screenshots, GR-017 README, test
matrix rows 5.1–5.4 and 9.8, `STATUS.md`, and `HISTORY.md`.

- The saved screenshot shows PdfCraft's `Saved — new version` state; the fresh
  reopen screenshot displays `PdfCraftSeafileRoundTrip` on the PDF and in the
  Comments inspector.
- Recorded Seafile IDs, history count, commit parent, size and readback hash are
  consistent with the documented synthetic run.
- The report explicitly says the file-list click was not observed, the file was
  opened by direct Seahub route navigation, and the outgoing editor payload was
  not separately hashed.
- The reports do not claim production readiness, project GPT PASS, all-PDF
  compatibility, or permission/security coverage.

## Bounded conclusion

The evidence supports one real PdfCraft annotation → host acknowledgement →
synthetic Seafile new revision → API readback → fresh PdfCraft reopen flow. It
does not establish file-list click behavior, byte identity across the browser
message boundary, broad PDF semantics, production deployment, or support for
other ArtCraft apps. Keep overall GPT status **FAIL** on
`0edbe524b4fa321b0f73f8601afef390e7f785e6`; upstream publication remains locked.
