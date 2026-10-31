# Upstream drafts — prepared locally, NOT published

`UPSTREAM_STATUS=LOCKED` (CLAUDE.md §28): nothing in this directory has been sent anywhere. Each
item is ready to become an issue, RFC or PR *after* the project-level review gate passes and the
owner explicitly approves it. Until then it is documentation of what we would propose.

| Draft | Target | What it is | State |
| --- | --- | --- | --- |
| `deckcraft-host-bridge/` | storytold/deckcraft | `apps/deckcraft-web/src/host.rs` + shell changes: the same `?host=parent` bridge WordCraft, GridCraft, PdfCraft and CADCraft already ship | compiles? see README there |
| `soundcraft-host-bridge/` | storytold/soundcraft | same bridge for SoundCraft, through the engine's delivery hook | compiles? see README there |
| `photocraft-host-bridge/` | storytold/photocraft | same bridge for PhotoCraft, with a dirty signal | compiles? see README there |
| `seahub-wopi-putfile-note.md` | haiwen/seahub | measured on Seahub 13.0.28: `PutFile` ignores `can_edit`; no version precondition | note, no code |
| `artcraft-save-result-rfc.md` | storytold (craft-libs / each app) | optional `<app>:saveResult` acknowledgement so an editor can show a failed save as unsaved | RFC text |
| `host-bridge-ports.md` | storytold/{photocraft,designcraft,soundcraft,filmcraft,lightcraft,effectcraft,vectorcraft,figcraft} | per-app notes for porting the bridge; where the lab's older GR patches still apply | notes |

How a draft gets out of this directory: project-level GPT PASS on the candidate → owner says yes →
open it upstream under the owner's name, referencing the lab evidence (`lab/real-seafile/results/`).
