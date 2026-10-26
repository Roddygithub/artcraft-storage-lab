# GR-081 response to independent R3 reviews

Both independent R3 reviews returned **PROVISIONAL FAIL**. Findings and
responses are preserved in:

- `INDEPENDENT-CODE-SECURITY-REVIEW-R3.md`
- `INDEPENDENT-DOCS-EVIDENCE-REVIEW-R3.md`

The docs/evidence findings were corrected in the overview, GR-069 checksum
manifest, and test matrix. The code/security dirty-state finding was addressed
with a rejection revision latch; missing names are now rejected instead of
falling back to the selected filename. A proposed protocol-test edit was later
reverted; no test files are changed and no tests were run in the current
candidate.

The code/security identity MAJOR is **not closed**. WordCraft/GridCraft can
still emit the selected filename with `saveAs=false` for a replacement, and the
host receives bytes only after serialization. Same-name replacement detection
and editor-side pre-serialization refusal remain **NOT VERIFIED**. ONLYOFFICE
current-route preservation also remains **INCONCLUSIVE / NOT VERIFIED**.

Independent R4 reviews are requested for the current code and documentation.
The project GPT FAIL on `70fa192ed5d414daf28087315f0f77f8312e98b5` remains in
force; upstream publication remains locked.
