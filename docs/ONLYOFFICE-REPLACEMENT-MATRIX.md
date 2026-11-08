# ONLYOFFICE replacement target

On 2026-11-08 the owner requested replacement coverage for **all formats**.
A read-only AST inspection of the current Seafile configuration found the
following declared routes. No settings were executed or changed, and no
credentials or private origins are retained. Configuration membership is not
proof that every current ONLYOFFICE path works in practice.

| Required format | Current configured mode | Craft replacement evidence |
| --- | --- | --- |
| DOCX | View + edit | WordCraft: three synthetic corpus edit/save/version/fresh-reopen cases, 28 checks each; bounded reviews PASS |
| XLSX | View + edit | GridCraft: synthetic typed-cell edit/save/version/fresh-reopen evidence; broader workbook fidelity NOT VERIFIED |
| PPTX | View + edit | NOT VERIFIED; historical DeckCraft foreign import exported native format rather than saving PPTX in place |
| DOC | View | NOT VERIFIED |
| PPT | View | NOT VERIFIED |
| XLS | View | NOT VERIFIED |
| ODT | View | NOT VERIFIED |
| FODT | View | NOT VERIFIED |
| ODP | View | NOT VERIFIED |
| FODP | View | NOT VERIFIED |
| ODS | View | NOT VERIFIED |
| FODS | View | NOT VERIFIED |
| CSV | View | NOT VERIFIED |
| PPSX | View | NOT VERIFIED |
| PPS | View | NOT VERIFIED |

The initial replacement baseline is **15 viewing formats and 3 editing
formats**. Adding editing support for the currently view-only formats would be
an additional capability, not something established by the existing settings.
Changing an extension, exporting another format or downloading a file cannot
satisfy same-file edit/save/new-version validation for the three editing routes.

The shipped zero-patch candidate currently validates only DOCX/XLSX among the
required office formats. PDF/DXF/SVG/FIGCRAFT are additional Craft routes, not
substitutes for the missing office coverage. Experimental DeckCraft Rust ports
remain outside the zero-patch default. No ONLYOFFICE removal is justified yet.

Next: establish pinned upstream import/export capabilities without assuming
support, prioritize PPTX same-format persistence, then validate the remaining
viewing formats with deterministic synthetic files and observed browser output.
Preserve DOCX/XLSX successes while broadening fidelity and HTTPS acceptance.
Production stays unchanged; upstream LOCKED; project INCOMPLETE.
