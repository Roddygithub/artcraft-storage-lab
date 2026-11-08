# Current project closure ledger

## Candidate scope

The candidate follows AGENTS.md rule 6: no Seafile patch and no editor patch.
It includes the released WordCraft, GridCraft, PdfCraft and CADCraft bundles,
plus VectorCraft/FigCraft with the explicitly declared lab JavaScript shim.
The default lab advertises only DOCX, XLSX, PDF, DXF, SVG and FIGCRAFT.
PPTX remains on ONLYOFFICE. Deployment defaults to DXF; office extensions
remain explicit operator opt-ins as documented in `deploy/bridge/README.md`.

DeckCraft, SoundCraft, PhotoCraft and DesignCraft require local Rust shell
ports. They remain experimental drafts and retained evidence, outside this
zero-patch candidate. Their former lab configuration is preserved in
`lab/real-seafile/editors.experimental.json` and
`seahub_settings.experimental.py`; it is not selected by the default launcher.
Media applications and the draw.io stub are also outside the candidate.
This is a scope correction required by rule 6, not validation of those ports.

## Evidence still required before freeze

| Requirement | Current evidence/state |
| --- | --- |
| WordCraft real edits and semantic fresh reopen | GR-085; safety replay GR-086, HTTP 48/48 + browser 28/28 |
| GridCraft real edits and semantic fresh reopen | 2026-11-08 closure run, HTTP 46/46 + browser 27/27 |
| PdfCraft field edit/save/reopen | 2026-11-08 closure run, HTTP 46/46 + browser 18/18 |
| CADCraft circle edit/save/reopen | 2026-11-08 closure run, HTTP 46/46 + browser 20/20 |
| VectorCraft and FigCraft semantic edits/reopen | 2026-11-08 closure runs, HTTP 46/46 + browser 20/20 (VC), 21/21 (FC) |
| ONLYOFFICE browser edit/save/version regression | 2026-11-08 closure run, 2 rounds, 12/12 checks |
| Reproducible rootless launcher with exact asset identity | Implemented, five offline tests, bounded source review PASS; successful WordCraft real run retained in GR-086 |
| Human HTTPS desktop acceptance | Pending: `lab/real-seafile/README.md` checklist |
| Frozen clean candidate, exact SHA, forensic review | Pending |
| Fresh independent project GPT gate after forensic review | Pending |

GR-078 belongs to the retired `integration/` deployment and is not current
bridge runtime evidence. The historical results remain retained. Bounded
source/evidence reviews do not replace the final project gate.

## Accepted host limit and trust model

On 2026-11-08 the owner selected: **“Accepter cette limite documentée dans le
MVP zéro patch”** in response to the reproduced CheckFileInfo/PutFile race.
A version already changed at preflight is rejected, but a different writer
can commit after that check and before the unconditional host write. Readback
verification cannot reconstruct or prevent that intervening write. Atomic
protection requires a host-enforced conditional write; it is not guaranteed.
The regression in `tests/bridge/test_bridge.py` retains this counterexample.

Seahub also accepts writes with a directly extracted read-only WOPI token.
The bridge checks permissions on its own save path; it cannot fix the host's
direct endpoint. Same-origin editor bundles are trusted code with access to
the host frame, not a sandbox protecting that frame's token. These limits
must remain visible in the final verdict and deployment documentation.

Production upgrades/rollback, live ONLYOFFICE diagnosis and deployment are
separate owner-controlled work, not actions required to close the isolated
lab MVP. Upstream remains LOCKED until a project GPT PASS and separate owner
publication approval. Direct parent work is not Aptarchy completion.
