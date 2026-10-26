# GR-078 R1 remediation response

| R1 finding | Disposition | Change |
|---|---|---|
| MAJOR: PdfCraft ID transcribed incorrectly | Fixed | Report, runtime README and sanitized observations now use screenshot ID `9e9a8b9a7e2fa90df924cab8d6da9798676e7630`. |
| MAJOR: WordCraft new-version claim unsupported by retained screenshot | Qualified | Removed the unsubstantiated exact ID. The retained screenshot is described as showing saved state and marker; the new-version confirmation is marked operator-observed but not captured, and its exact ID is NOT VERIFIED from retained evidence. |
| MINOR: Missing R1 artifact / conflicting pending wording | Fixed | Added `INDEPENDENT-REVIEW-R1.md`; the GR-078 report and evidence README now link/describe the R1 result and pending R2. |
| MINOR: Historical combined-replay gaps lack cutoff | Fixed | GR-071/GR-077 matrix rows and the GR-071 queue entry now date the NOT VERIFIED result and point to the later GR-078 replay. The checkout static-root and production limitations remain explicit. |

R2 verified all four remediations and found no new issues, returning
PROVISIONAL PASS. All free-review results remain PROVISIONAL; this response is
not a project GPT REVIEW PASS.
