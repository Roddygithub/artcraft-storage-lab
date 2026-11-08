# GR-084 exact-candidate GPT review — R4

**Reviewed candidate:** `c5a7c3eeee35d222333f377df2f23090ce491850`.

**Verdict:** changes required. One P3 tracking finding; no P1/P2.

## Finding

The closing sentence of the GR-084 report still said exact-commit R3 was
pending, while the report body correctly said R4 was pending and retained the
R3 review record. The closing sentence now links the R3 record, notes the
correction, and says exact-commit R5 is pending.

## Verified in R4

R1's active-xref check and superseded-value regression are correct. R2's
truncated-xref guard terminates and its regression passes. The retained PDF is
2,386 bytes and matches the recorded private relay/readback digest. All 22
bundle checksums, source provenance hashes and retained JSON parse passed.

The runtime review did not reproduce the HTTP or browser run. Its recorded
48/48 HTTP and 18/18 Chromium result remains bounded to one synthetic PDF.
No project-level PASS or upstream authorization is implied.

Exact-commit GPT R5 review was pending when this record was written. R5 later
found a stale opening status in the main report; its correction is recorded in
`INDEPENDENT-GPT-REVIEW-R5.md`.
