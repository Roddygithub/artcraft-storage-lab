# GR-084 exact-candidate GPT review — R5

**Reviewed candidate:** `5e6bf106cc2d29b1c8ea01b41b9ba470fe147b0e`.

**Verdict:** changes required. One P3 tracking finding; no P1/P2.

## Finding

The opening status paragraph said the exact-commit R4 review was pending even
though the body and closing paragraph recorded R4's finding and said R5 was
pending. The opening status now records R1–R5 outcomes and R6 as pending.

## Verified in R5

- R1's active-xref selection and superseded-value regression pass.
- R2's truncated-xref EOF regression passes.
- All 23 archive checksums, retained JSON parsing, and source-provenance hashes
  passed. The retained PDF is 2,386 bytes with SHA-256
  `d1bb31792966cf0b5551029e56224074629e2590c9a6865be92ce70d6599dad2`; the
  active `name` field contains the marker.
- R3 corrected the current GR-084 HISTORY byte count; the remaining old count
  is explicitly historical GR-057.

The HTTP 48/48 and browser 18/18 results remain retained evidence, not a
reproduced runtime. The post-run EOF helper change is disclosed. Exact-commit
GPT R6 review is pending. No project-level PASS or upstream authorization is
implied.
