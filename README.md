# ArtCraft Storage Lab

> ArtCraft Storage Lab is an independent open-source research and prototyping project
> exploring direct browser-based editing integration between self-hosted file platforms
> and ArtCraft Web editors.

Seafile is the primary real-world reference integration. The target experience is
comparable to Seafile's integrated online editing workflow with office document servers:
open, edit and save directly from Seafile Web without local filesystem mounts.

```text
Seafile Web
   |
   | click rapport.docx
   v
WordCraft Web  (iframe)
   |
   | edit in the browser
   v
Save
   |
   v
Seafile
   |
   v
new version of the file
```

No SeaDrive. No manual download. No manual upload. No desktop application required.

---

## What this project is

* A **research and prototyping** space, not a production product (yet).
* A place to answer one question rigorously: **what is the contract between a
  self-hosted file platform and a browser-based editor, and how do ArtCraft's
  editors satisfy it?**
* A source of **implementation-grade documentation** (contract, save protocol,
  conflict handling, authentication, security) that a future implementation —
  here or upstream — can be built from without redoing the research.

## What this project is not

* Not an official **ArtCraft** project.
* Not an official **Seafile** project.
* Not a replacement for **DriveCraft**.
* Not a **SeaDrive** client, and not a **WebDAV** client.
* Not a re-implementation of Seafile.

## Scope

| In scope | Out of scope |
| --- | --- |
| Seafile/Seahub online-editor integration contract | Mounting Seafile as a local filesystem |
| ArtCraft Web/WASM capability audit | SeaDrive-based workflows |
| A reusable Craft **host contract** | 13 independent per-app Seafile plugins |
| Save protocol, conflicts, auth, security | Replacing the existing ONLYOFFICE integration |
| Self-hosted deployment design | Aptarchy / MCP-driven editing workflows |

## Repository layout

```text
docs/          research, contracts, protocols, review evidence
integration/   the Seafile-side integration layer (one connector, not N plugins)
prototypes/    technical proofs of concept
scripts/       helper and validation scripts
tests/         test matrix, fixtures and automated checks
config/        OpenCode agent definitions used for automatic model routing
```

## Review status

Every result produced here is **provisional** until an independent GPT review
passes. The free-model review pass is a quality gate, not a final verdict.

```text
FREE REVIEW : PROVISIONAL
GPT REVIEW  : PENDING
```

See [`STATUS.md`](STATUS.md), [`docs/GPT-REVIEW-QUEUE.md`](docs/GPT-REVIEW-QUEUE.md)
and [`docs/GPT-HANDOFF.md`](docs/GPT-HANDOFF.md).

## How work is routed

The project uses OpenCode sub-agents with **automatic model routing** — the owner
agent never asks the human which model to use. See
[`docs/AI-ROUTING.md`](docs/AI-ROUTING.md) for the exact model IDs and the
agent definitions (in [`config/opencode/agents/`](config/opencode/agents/)).

## License

Dual licensed: [MIT](LICENSE-MIT) or [Apache-2.0](LICENSE-APACHE), at your option.

Third-party components retain their own licenses; see
[`docs/LICENSING.md`](docs/LICENSING.md) once written.

## Status

Alpha research. See [`ROADMAP.md`](ROADMAP.md) for phases and
[`HISTORY.md`](HISTORY.md) for the running log.
