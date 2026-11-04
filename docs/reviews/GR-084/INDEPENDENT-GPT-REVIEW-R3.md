# GR-084 exact-candidate GPT review — R3

**Reviewed candidate:** `88742e82bc56467ff9c28ba7aaac989975b39dc8`.

**Verdict:** changes required. One P3 documentation finding; no remaining P1/P2.

## Finding

`HISTORY.md` still described the relay-save/readback PDF as 2,385 bytes, while
the corrected report and exact artifacts establish 2,386 bytes. The count is
corrected in the current GR-084 entry. A separate historical 2,385-byte
GR-057 entry is unchanged.

## Verified in R3

- R1's active-xref regression rejects the superseded field value.
- R2's truncated-xref EOF regression terminates and passes.
- The private run-7 relay payload, private Seafile readback, and retained PDF
  are byte-identical: 2,386 bytes, SHA-256
  `d1bb31792966cf0b5551029e56224074629e2590c9a6865be92ce70d6599dad2`.
- All 21 evidence checksums, source provenance hashes, and retained JSON parse.
- The private runtime source differs from the exact candidate only by the
  documented EOF/progress guard.

The review did not replay the browser or services. The HTTP 48/48 and browser
18/18 results remain bounded to the retained synthetic run. Exact-commit GPT
R4 is pending. No project-level PASS or upstream authorization is implied.
