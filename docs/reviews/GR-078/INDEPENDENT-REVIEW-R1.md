# GR-078 independent evidence review — R1

**Verdict: MAJOR — remediation required. PROVISIONAL.** No BLOCKER found.

Read-only review of the GR-078 report, runtime bundle, screenshots, status
documents, matrix and repository diff. No files were edited, tests run, services
accessed or browser tools used by the reviewer.

## Findings

| Severity | Finding | Evidence |
|---|---|---|
| MAJOR | PdfCraft version ID was transcribed incorrectly. The report and runtime records used `9e9a8b9a7e2fa90df924cab8d6da978676e7630`; the save screenshot shows `9e9a8b9a7e2fa90df924cab8d6da9798676e7630`. | `runtime/screenshots/pdfcraft-save.png`; prior `runtime/README.md`, `runtime/observations.json`, and GR-078 report |
| MAJOR | The retained WordCraft save screenshot shows the marker and saved-state UI but not the host's “Saved — new version” message or a version ID. The exact version claim was not substantiated by the screenshot. | `runtime/screenshots/wordcraft-save.png`; prior `runtime/README.md` and `runtime/observations.json` |
| MINOR | The report linked to a missing R1 artifact and stated that review was recorded, while the evidence README said R1 was pending. | Prior GR-078 report and `README.md` |
| MINOR | GR-071 and GR-077 matrix/queue entries described the combined replay as unverified without a clear historical cutoff, despite GR-078 being the later replay. | `docs/TEST-MATRIX.md` GR-071/GR-077 sections; `docs/GPT-REVIEW-QUEUE.md` GR-071 section |

The reviewer confirmed the tab-close boundary is disclosed, no in-app-close
success is claimed, history-page and byte-identity checks are marked
unverified, GridCraft and VectorCraft screenshot IDs match their records, and
all ten screenshot hashes match the manifest. The reviewer found no visible
secrets, server addresses, identifying usernames or personal content; PNGs had
no ancillary metadata chunks. PhotoCraft's screenshot shows “Saved to host” and
a clean state; HTTP 200 and chronology are narrative observations.

## Required remediation

1. Correct the PdfCraft ID everywhere to match its retained screenshot.
2. Qualify WordCraft's confirmation as operator-observed and mark the exact
   version ID/screenshot-backed confirmation NOT VERIFIED unless corroborating
   evidence is retained.
3. Add the R1 review artifact and align review-status wording.
4. Date GR-071/GR-077 unverified results and cross-reference GR-078.
