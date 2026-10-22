# HISTORY

Running log. Newest first.

## 2026-10-22 — GR-012, and the owner model retired mid-flight

* **GR-012** — proved a **non-Office** round-trip: an SVG opened from Seafile in
  **VectorCraft Web**, modified with the editor's own pencil tool in the browser,
  saved, and Seafile recorded a **new version**; the document reopened with the
  edit. `docs/reviews/GR-012/`.
* The first attempt (PdfCraft/PDF) **failed**, and the failure was the finding:
  the application was never dirty, so the Save handed the gateway unchanged bytes
  and the file server correctly created no new version. The lesson is that the
  modification must be driven deterministically, not by guessing where to click.
* VectorCraft was chosen because it exposes its own page API
  (`window.vectorcraft`), which is deterministic end to end. The host page gained
  a **second transport adapter** for it, documented as a gap in the common
  contract (VectorCraft has no `?host=parent` bridge).
* **The owner model was retired mid-flight**: MiniMax M3.1 Flash (free,
  OpenRouter) lost its endpoint during GR-012. The owner role moved to
  **GLM-5.3-Flash (thinking)**; no work was redone and no file rewritten — the
  state was reconstituted from `STATUS.md`, `HISTORY.md`, the GR queue,
  `docs/reviews/` and `git log`. `docs/AI-ROUTING.md` has the incident entry.
* `scripts/install-agents.sh` had a real bug, found while reinstalling: with
  `XDG_CONFIG_HOME` set it installed the agents to `~/.config/agents/` instead of
  `~/.config/opencode/agents/`. Fixed; the routing was verified through
  `/api/agent` afterwards.

## 2026-10-22 — Phases 1-6: research, the contract, and a working proof

* **GR-001** — read the *deployed* Seafile 12.0.14 Professional instance (read-only
  over SSH) and mapped the ONLYOFFICE contract exactly: the doc key, the token
  set, the callback statuses, the update call, the lock, and the fact that
  **the save is unconditional**. `docs/reviews/GR-001/DEPLOYED-INSTANCE-CONTRACT.md`.
* **GR-002** — found that Seafile already ships a **generic, configuration-only**
  third-party-editor hook (`seahub/thirdparty_editor/`), in the open-source upstream
  *and* in the Professional build. Established the shadowing problem (it wins over
  ONLYOFFICE per extension) and the read-only nature of the hook.
  `docs/SEAFILE-INTEGRATION-POINTS.md`.
* **GR-003** — **all 13 ArtCraft apps have a browser build**, and **3 of them
  already ship a `?host=parent` postMessage bridge** (GridCraft, PdfCraft,
  CADCraft) with a consistent vocabulary and a correct security model. The
  baseline audit was about the desktop packages and was silent about this.
  `docs/ARTCRAFT-WEB-CAPABILITIES.md`.
* **GR-004** — the host contract is the *existing* bridge, generalised, with one
  addition: the host must be able to tell the app how a save ended.
  `docs/HOST-CONTRACT.md`.
* **GR-008** — Seafile's file server has **no** compare-and-swap (`last_modify`
  only stamps the mtime; `head` is not a guard), so the conflict check is ours:
  compare the content id at save time. `docs/reviews/GR-008/`.
* **GR-005** — built the gateway (`integration/gateway/`), enabled the hook for
  **one extension that ONLYOFFICE does not claim and no real file uses** (`.xlsx`),
  and proved the whole flow **in a real browser**: GridCraft opened the Seafile
  workbook, the test edited a cell, the editor's own Ctrl+S produced the bytes, and
  Seafile created a **new version** containing the edit. Screenshot in
  `docs/reviews/GR-005/browser-proof.png`.
* **Two independent free reviews** (Nemotron), both **FAIL**, both remediated:
  `docs/reviews/REVIEW-01.md`, `docs/reviews/REVIEW-02.md`. The first caught a wrong
  generalisation about the save confirmation; the second caught a symlink escape, a
  TOCTOU window, a missing save answer, an account token leaking to the file
  server, and a dead dispatch entry.
* **GR-014** — wrote the **WordCraft `?host=parent` bridge** (the patch that
  unblocks the DOCX MVP) and it compiles. `docs/reviews/GR-014/DIFF.patch`.

### Decisions

| # | Decision | Rationale |
| --- | --- | --- |
| D-005 | The first proof uses **GridCraft + `.xlsx`** | `.xlsx` is in no other library and is not claimed by the deployed ONLYOFFICE configuration, so claiming it has **zero** blast radius; and GridCraft already ships the bridge, so no application had to be changed |
| D-006 | The first proof runs against the **existing instance**, not a new one | the change is one extension in one dict, backed up, with a documented rollback, and it touches nothing else |
| D-007 | The gateway **writes with its own credential** (option B) for the MVP | it needs no Seafile code change at all; the price — the version is attributed to the service account — is stated prominently, and the upstream patch (option A) is the production answer |
| D-008 | The host contract is the **existing `?host=parent` bridge**, not VectorCraft's `window.vectorcraft` API | the bridge is the shape a host platform needs; the page API is an automation surface with a much larger security cost |
| D-009 | The upstream patch is **one new file in `apps/wordcraft-web/`** | the smallest change that unblocks the MVP, and an alignment with the three apps that already have the bridge — not a new idea and not a multi-repo PR |
| D-010 | The browser test is part of the test suite, not a nicety | it found three real bugs the HTTP test could not see, including a JavaScript `ReferenceError` that left the page dead |

## 2026-10-22 — Phase 0: bootstrap

* Inspected the OpenCode installation (v2.1.0, V2 agent format: Markdown with
  YAML frontmatter under `~/.config/opencode/agents/<name>.md`, `mode:
  primary|subagent|all`, `model: provider/model#variant`).
* Discovered the **exact** model IDs available in this environment and recorded
  them in `docs/AI-ROUTING.md`.
* Created the five project agents and smoke-tested every one of them. All mapped
  to their expected model. `artcraft-deepseek-worker` timed out on the first
  attempt and succeeded on the second — recorded as a flakiness warning.
* Created the public repository skeleton, dual license, `AGENTS.md`, `README.md`,
  `STATUS.md`, `ROADMAP.md`.
* Read `~/ArtCraft-Audit.md` as baseline input evidence. It reports the 13 apps
  are **Rust-only, native egui/eframe + wgpu, explicitly not Tauri/Electron/webview**,
  and that the CI gate includes a `wasm` check. The Web/WASM story must be
  re-verified specifically for this project (GR-003).
* Located the Seafile reference host: `svc-seafile-host.tailb64fb1.ts.net`.
  No local Seafile/Docker runtime on this workstation. No production change made.

### Decisions

| # | Decision | Rationale |
| --- | --- | --- |
| D-001 | Agents are installed **globally** in `~/.config/opencode/agents/`, with the canonical copies versioned in `config/opencode/agents/` | Routing must work in every session, including ones started outside the project directory. `scripts/install-agents.sh` keeps the two in sync. |
| D-002 | Project-local `.opencode/agents/` is **not** used | It would shadow the global definitions and create two sources of truth. |
| D-003 | A reviewer's verdict is only `PROVISIONAL` until GPT passes | Hard gate required by the mission; free-model verdicts are not final. |
| D-004 | The Seafile test bed is the remote server, with a synthetic library | Production data and personal files must not be cloned into the project. |
