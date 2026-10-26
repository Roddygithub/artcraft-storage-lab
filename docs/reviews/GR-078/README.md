# GR-078 evidence — combined synthetic Seafile browser replay

This bundle records a sequential browser replay of the five currently tracked
dispatcher routes in the synthetic `ArtCraft GPT Review Synthetic` library.
Every route was opened from Seafile Web, edited, saved through its host-bound
save path, closed by closing the editor tab, and reopened from Seafile Web.
The reopened editor retained the edit.

## Runtime record

- [`runtime/README.md`](runtime/README.md): workflow chronology, scope and
  observed save responses.
- [`runtime/observations.json`](runtime/observations.json): sanitized,
  per-route summary. Session capability IDs, cookies, account names and server
  addresses are not retained.
- [`runtime/screenshots/`](runtime/screenshots/): retained screenshots for the
  synthetic editors. PhotoCraft's two PNGs are byte-identical to earlier GR-076
  captures and show Layer 1/2, not the later GR-078 added-layer state; they do
  not corroborate that GR-078 save/reopen observation. SHA-256 digests are
  listed in the runtime README.

## Independent review

R1 returned **MAJOR — remediation required**, with two MAJOR and two MINOR
findings. All four are addressed in [`RESPONSE-R1.md`](RESPONSE-R1.md). R2
verified the remediations and found no new issues: **PROVISIONAL PASS** in
[`INDEPENDENT-REVIEW-R2.md`](INDEPENDENT-REVIEW-R2.md). Both free-review rounds
remain PROVISIONAL and are not a project GPT REVIEW PASS.
