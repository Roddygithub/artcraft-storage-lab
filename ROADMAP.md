# ROADMAP

Phases are sequential. A phase is not "done" until its artifact exists, its
independent free review passed, and its evidence bundle is committed.

| # | Phase | Artifact | Exit criterion |
| --- | --- | --- | --- |
| 0 | OpenCode routing & bootstrap | `docs/AI-ROUTING.md`, agent defs | all 5 agents smoke-tested with the exact expected model |
| 1 | Seafile / ONLYOFFICE integration research | `docs/SEAFILE-ONLYOFFICE-RESEARCH.md` | the editor contract Seafile expects is written down with code evidence |
| 2 | Seafile integration points | `docs/SEAFILE-INTEGRATION-POINTS.md` | the best insertion point is chosen and justified, incl. "can we avoid a permanent fork?" |
| 3 | ArtCraft Web capability matrix | `docs/ARTCRAFT-WEB-CAPABILITIES.md` | all 13 apps have a verified Web/WASM/host-bridge verdict |
| 4 | Common Craft Host Contract | `docs/HOST-CONTRACT.md` | a reusable host contract exists (or the decision to not have one is justified) |
| 5 | First technical Craft Web proof | `integration/`, `prototypes/` | a real Craft Web editor opens a Seafile file and saves it back |
| 6 | **WordCraft DOCX MVP** | `docs/reviews/GR-006/` | the 12-step MVP checklist is **VERIFIED END-TO-END** on synthetic files |
| 7 | Save / conflicts / security | `docs/SAVE-PROTOCOL.md`, `docs/CONFLICTS.md`, `docs/SECURITY.md` | save never lies, concurrent edits never silently overwrite, security reviewed |
| 8 | GridCraft | `docs/reviews/GR-010/` | `.xlsx` round-trips through GridCraft Web into a Seafile version |
| 9 | DeckCraft | `docs/reviews/GR-011/` | `.pptx` round-trips through DeckCraft Web into a Seafile version |
| 10 | PdfCraft / VectorCraft | `docs/reviews/GR-012/` | the integration is proven **not** reserved to Office formats |
| 11 | Packaging / deployment | `docs/DEPLOYMENT.md` | a 100 % self-hosted, free/OSS deployment path is designed |
| 12 | ArtCraft RFC / patches | `docs/RFC-DRAFT.md` | an upstream-ready RFC and the smallest justified patch are prepared (not published) |
| 13 | GPT review | `docs/GPT-HANDOFF.md` | the project is fully handed over to GPT for an independent review |
| 14 | Upstream contribution | — | **only after `GPT REVIEW PASS`** |

## Explicitly excluded phases

* SeaDrive-based workflow. Not a phase, not a milestone.
* WebDAV client. Only studied if the research proves it is a useful brick.
* DriveCraft.
* Re-implementing Seafile.
* 13 independent per-app Seafile plugins.

## MVP definition (the only definition that counts)

1. The user is in Seafile Web.
2. They click a synthetic DOCX.
3. WordCraft Web opens it — no manual download.
4. The document is loaded.
5. The user modifies the document.
6. They save from WordCraft.
7. No manual upload is needed.
8. Seafile records a new version.
9. The editor genuinely confirms the save.
10. The document is closed.
11. It is reopened from Seafile.
12. The modification is present.

**VERIFIED END-TO-END.** Not a mock, not a download, not a manual upload.

## Phase dependency notes

* Phase 6 depends on Phase 5 choosing a Craft whose web/host bridge is mature
  enough. If no Craft qualifies, Phase 5's conclusion is "we must build the web
  host ourselves" — that is a valid, documented outcome.
* Phase 4 must not block Phase 6: a single-Craft, single-file contract is
  acceptable for the MVP as long as the shape is compatible with a common one.
