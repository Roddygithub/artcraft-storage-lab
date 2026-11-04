# GR-083 independent review R1

**Reviewed commit:** `075a8621caaad025c2437ae071378ac2d18207d9`

**Base:** `824dafddfb844159298ad18c1873ffce9d2dfa50`
**Verdict:** changes requested; no blocker.

## Findings

- **P2 — generated OOXML property order.** Paragraph styles emitted `w:rPr` before `w:pPr`; table cells emitted shading before width; table properties emitted borders before width. Both editors opened the documents, but acceptance does not establish schema-valid ordering. Correct the order and add focused regression checks. Full schema validation was not run.
- **P3 — ambiguous status sentence.** `docs/REFOUNDATION-REPORT.md` described the comparison as having “full page-layout fidelity and two … 502s unresolved,” which could read as a positive fidelity claim. Say that full page-layout fidelity remains unverified and the two 502 responses remain unresolved.

## Remediation and remaining work

The corpus generator now emits paragraph-style properties as `pPr` then `rPr`, table-cell width before shading, and table width before borders. A focused test checks these three used child-order constraints in generated fixtures; this is not a complete ECMA-376 schema validator. The report wording is clarified.

The retained browser run and screenshots predate this source correction. They are historical only and do not validate the corrected corpus. A fresh synthetic browser replay remains pending after independent source re-review. The ONLYOFFICE manifest 502 cause also remains **NOT VERIFIED**.

Review checks before remediation: five committed tests passed, 14 evidence checksums passed, screenshots had valid PNG framing and no metadata/trailing payload, and no private identifiers or credentials were observed. The reviewer did not access services, run browsers/builds, or edit files.
