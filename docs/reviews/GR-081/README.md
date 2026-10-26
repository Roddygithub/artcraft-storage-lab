# GR-081 evidence — project GPT review remediation

The project review of candidate `70fa192ed5d414daf28087315f0f77f8312e98b5`
returned **FAIL**. The retained finding-by-finding record is
[`PROJECT-GPT-REVIEW-70FA192.md`](PROJECT-GPT-REVIEW-70FA192.md). The remediation
report is [`../../GR-081-PROJECT-GPT-REVIEW-REMEDIATION.md`](../../GR-081-PROJECT-GPT-REVIEW-REMEDIATION.md).
The bounded ONLYOFFICE diagnosis is
[`ONLYOFFICE-BOUNDED-DIAGNOSIS-R1.md`](ONLYOFFICE-BOUNDED-DIAGNOSIS-R1.md);
it is hypothesis-only and leaves preservation **INCONCLUSIVE / NOT VERIFIED**.
The editor identity design is recorded in
[`IDENTITY-BINDING-DESIGN-R1.md`](IDENTITY-BINDING-DESIGN-R1.md). A source-only
implementation is retained in [`patches/`](patches/), with its independent
R1/R2 review at [`INDEPENDENT-CODE-SECURITY-REVIEW-R2.md`](INDEPENDENT-CODE-SECURITY-REVIEW-R2.md)
and response at [`RESPONSE-R2-CODE.md`](RESPONSE-R2-CODE.md). It is not built;
same-name replacement safety in the running editors remains **NOT VERIFIED**.

## Scope

GR-081 changes the ArtCraft gateway, its dispatcher verifier, and
documentation/evidence descriptions. The protocol-test file is unchanged in
the current candidate.
It does not access Seafile or ONLYOFFICE services, change settings, build an
editor, run tests, or publish upstream.

The gateway now rejects WordCraft/GridCraft saves without the negotiated
identity, matching open/document IDs, `intent:"save"`, and a fresh ticket;
filename and format checks remain additional constraints. The source patches
bind the native editor document after parsing, guard replacement/Save As before
serialization, and use a typed ordinary-Save route. They also correct pending
save dirty reporting for an exact snapshot/revision. Both identity-patched apps
now pass locked Rust 1.95 WASM checks, and their existing UI unit suites pass;
exact results and limits are recorded in
[`VALIDATION-R3.md`](VALIDATION-R3.md). Same-name replacement refusal before
serialization, browser save/ACK behavior, and the Seafile version/reopen gate
remain **NOT VERIFIED**. The dependency commit is local and fresh public-remote
resolution is **NOT VERIFIED**.

The directory index is resolved and confined before serving. The tracked route
verifier now expects all five routes, while noting that only four
GR-055–058 candidates are checked by its asset-verification loop. PhotoCraft
has separate GR-076 evidence.

Screenshot attribution and missing-link claims were corrected in the cited
reports. R3 identified stale checksum and screenshot qualifications; those
were corrected, and docs/evidence R4 verified them. R3/R4 findings and responses
are retained in the review records. Code/security R4 confirmed source fixes for
missing names and the dirty-state latch, but found save identity unresolved.
Its report/response are retained. The reused
GR-078 PhotoCraft PNGs and duplicated GR-015 concurrency PNG are preserved
unchanged and explicitly not treated as evidence for the later workflow they
were attributed to.

## Validation state

`git diff --check`, Python and shell syntax checks, modified JSON parsing, and
local Markdown target checks were recorded before the app builds. Both app
WASM checks and both existing UI suites subsequently passed; see
[`VALIDATION-R3.md`](VALIDATION-R3.md). The gateway browser protocol test was
not run because Python Playwright is unavailable. Browser workflows, runtime
symlink exercise, dispatcher verifier execution and service checks were not
performed. ONLYOFFICE's current-route UI remains INCONCLUSIVE / NOT
VERIFIED. Code/security R3/R4 and docs/evidence R3 returned PROVISIONAL FAIL;
docs/evidence R4/R5/R6 returned PROVISIONAL PASS with their MINOR findings
addressed in [`RESPONSE-R4-DOCS.md`](RESPONSE-R4-DOCS.md),
[`RESPONSE-R5.md`](RESPONSE-R5.md), and [`RESPONSE-R6.md`](RESPONSE-R6.md).
R6's absent GR-076 log reference is corrected. Docs/evidence R7 returned
PROVISIONAL PASS with no new findings; see
[`INDEPENDENT-DOCS-EVIDENCE-REVIEW-R7.md`](INDEPENDENT-DOCS-EVIDENCE-REVIEW-R7.md)
and [`RESPONSE-R7.md`](RESPONSE-R7.md). Current-route ONLYOFFICE UI remains
INCONCLUSIVE / NOT VERIFIED. Bounded diagnosis is in
[`ONLYOFFICE-BOUNDED-DIAGNOSIS-R1.md`](ONLYOFFICE-BOUNDED-DIAGNOSIS-R1.md).
Project GPT review remains FAIL for 70fa192; a fresh review is required for a
later candidate.
