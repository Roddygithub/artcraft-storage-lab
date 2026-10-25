# Independent review — GR-027 null-codec track fix (round 4)

**Verdict:** PROVISIONAL PASS with one MAJOR.

The reviewer verified patch identity, source/base blobs, and the previous R1–R3
fixes. It found that zero-padded MP4 could skip its bounded preflight because
leading zero bytes were stripped into the middle of the first atom header. R5
now tries possible starts within the leading zero prefix and preserves the
atom offset. Exact review of R5 is recorded in
[`REVIEW-INDEPENDENT-R5.md`](REVIEW-INDEPENDENT-R5.md). No tests were rerun in
R4. Browser and Seafile behavior remain NOT VERIFIED.
