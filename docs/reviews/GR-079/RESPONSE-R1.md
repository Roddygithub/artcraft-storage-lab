# GR-079 R1 remediation response

| R1 finding | Disposition | Change |
|---|---|---|
| MINOR: history-verification status lacked the GR-078 cutoff | Fixed | STATUS.md and HISTORY.md now say history checks had not been performed at GR-078; they reference GR-079's later current-row check. Byte identity and production limits remain NOT VERIFIED. |
| MINOR: size/timing comparisons exceeded retained observations | Fixed | The report and matrix now state only the displayed current-row timestamps/sizes and version counts. They explicitly say no separate file-list comparison was retained and make no comparison to GR-078 edit timestamps. |

R2 verified both remediations and returned PROVISIONAL PASS with no new
findings. Both free-review rounds remain PROVISIONAL; this response is not a
project GPT REVIEW PASS.
