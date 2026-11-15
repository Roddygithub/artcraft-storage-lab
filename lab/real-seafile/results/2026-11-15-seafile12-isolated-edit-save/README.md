# Isolated Seafile 12 browser edit/save replay

Run on 2026-11-15 against a private, rootless Podman stack using the official
Seafile CE 12.0.14 image (`sha256:7bbe7043facbc639a8e6144f32d50dc4d771191ecaa68002efb2b0237fb90358`).
The code and bridge were copied from repository HEAD `11b75a23be5e263f9bb7b4b9cb332caa2158bd6d`.
No owner server, production account, document or configuration was used.

## Browser results

| Editor / fixture | Browser assertions | Result |
| --- | ---: | --- |
| WordCraft / synthetic DOCX | 24 | PASS |
| GridCraft / synthetic XLSX | 27 | PASS |
| DeckCraft / synthetic PPTX | 15 | PASS |
| **Total** | **66** | **PASS** |

Each test opened the file from Seafile's browser UI, typed synthetic edits,
observed the WOPI save, verified a new version attributed to the synthetic
account, opened a fresh browser session and observed the saved edits. No browser
downloads occurred. WordCraft and GridCraft each made two saves and created
versions 1→2→3. DeckCraft created a new version and reopened the edited title.
The JSON files retain assertion names and sanitized details; screenshots show
key edited/reopened states. DOCX and PPTX source/readback bytes are retained.
The GridCraft runner did not retain source/relay XLSX bytes, so its content
comparison is limited to the recorded assertions and screenshots.

Bundle SHA-256 values match the unmodified candidate bundles in
`lab/real-seafile/static/` and the DeckCraft v0.16.0 pin:

- WordCraft v0.13.2: `b6c9c8d3a730495189ba0c213fe64313f317be8fc0611ac1ff8cdd6a4b20880c`
- GridCraft v0.14.2: `f6675cfe26f89f07cb9d9ff23a5ae0a946088eef6e22c93ac1141f0279f741f8`
- DeckCraft v0.16.0: `8795d58ab02c30ad25f38525a79ee0e69c40b3d122e223dc04d2703827621f55`

## Bounds and incomplete checks

The browser result is a real, synthetic Seafile 12.0.14 workflow, but this
one-off CE12 Compose setup was not the repository's standard CE13 launcher and
its setup script was not retained. The run is therefore retained evidence, not
a reproducible project runner. The standard launcher cannot be switched to CE12
by changing only its image: the CE12 image did not start Seahub under the CE13
environment contract. That failed experiment was stopped and its containers
were removed.

A broad exploratory HTTP slice reported 11/17 assertions; six failed: SVG
routing, PDF/DXF routing/open, and a GridCraft bundle fetch in that slice.
This was not the three-editor browser suite and is not counted as a pass. See
`slice.json`. It does not invalidate the separately passing browser workflows.

This test does not cover the owner's Seafile, HTTPS, physical hardware, legacy
formats, host-enforced read-only permissions, concurrent writers, or general
fidelity. Those remain separate checks. Hashes for retained files are in
`SHA256SUMS`.
