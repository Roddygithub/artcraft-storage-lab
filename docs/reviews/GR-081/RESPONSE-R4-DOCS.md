# GR-081 response to independent R4 documentation/evidence review

R4 returned **PROVISIONAL PASS for documentation/evidence**, with three MINOR
findings. All three were addressed:

1. The GR-081 README now distinguishes R3's findings from the subsequent
   corrections and R4 verification.
2. The integration README now describes cookie scoping as a separate deployment
   requirement, warns that origin splits do not isolate cookies by port or
   broad domain scope, and marks deployed cookie isolation **NOT VERIFIED**.
3. The GR-081 README now states the protocol-test file is unchanged in the
   current candidate; the proposed test edit was reverted.

R4 also verified the cross-origin topology, all seven GR-069 checksum entries,
PhotoCraft/WordCraft screenshot qualifications, and `[~]` matrix status for
PhotoCraft and combined replay. Its full review is retained in
`INDEPENDENT-DOCS-EVIDENCE-REVIEW-R4.md`.
