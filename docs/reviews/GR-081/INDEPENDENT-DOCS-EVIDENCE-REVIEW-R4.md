# GR-081 independent docs/evidence review R4

**Verdict: PROVISIONAL PASS for documentation/evidence, with three MINOR
corrections.** No edits, tests, builds, browser use, or service access were
performed.

## Findings and responses

1. **MINOR — Review provenance wording.** The GR-081 README said R3 confirmed
   checksum and screenshot corrections. It now distinguishes R3's findings,
   the subsequent corrections, and R4's verification.
2. **MINOR — Cookie-isolation claim.** The integration README implied different
   origins guarantee cookie isolation. It now requires a distinct gateway host
   and explicit cookie scope, notes origin splits do not isolate cookies by
   port or broadly scoped domain, and marks deployed isolation **NOT VERIFIED**.
3. **MINOR — Stale scope.** GR-081 README said a protocol-test edit was in scope,
   although the edit had been reverted. It now states the test file is unchanged.

R4 verified the cross-origin form POST topology; all seven GR-069 manifest
entries; PhotoCraft screenshot reuse and WordCraft's uncaptured save-version
confirmation qualifications; and `[~]` for PhotoCraft and the combined replay.
Same-name replacement/Save As identity and pre-serialization refusal remain
unresolved; ONLYOFFICE remains INCONCLUSIVE / NOT VERIFIED.

All 87 inspected local Markdown links resolved. All ten GR-078 screenshot
hashes matched their listing and the disclosed duplicate image was confirmed.
No new secrets or personal data were identified. The original project
candidate `70fa192ed5d414daf28087315f0f77f8312e98b5` remains FAIL, and upstream
publication remains locked.
