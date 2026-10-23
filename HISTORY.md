# HISTORY

## 2026-10-23 — Sol re-review of 0edbe52 and route-token remediation

* GPT-6.1 Sol reviewed exact SHA
  `0edbe524b4fa321b0f73f8601afef390e7f785e6` at medium effort/default tier and
  returned **FAIL**. Full report: `docs/reviews/GPT-SOL-REREVIEW-0EDBE52.md`.
* Sol independently found the dedicated C path `conditional-update-api` did not
  begin with `update`, while the existing `upload_headers_cb` passes the first
  path component to `check_access_token`, which enforces the `op=update` prefix.
  Thus the proposed save route would reject the minted update token before the
  conditional handler. The route is now named `update-conditional-api`, keeping
  the route distinct while preserving the existing operation check. The GR-015
  source harness passes against pinned Seahub/Seafile sources with both patches
  applied, and both patches pass applicability checks. The harness confirms the
  route begins with `update` and the existing hook still enforces the token
  operation; it is source-level evidence, not actual hook execution. C/Django
  runtime behavior remains **NOT VERIFIED**.
* The GR-006 historical free-model “VERIFIED END-TO-END” claim is explicitly
  marked superseded, and the RFC now documents the browser-mediated capability
  handoff to the gateway. These changes correct claims; they do not add Seafile
  E2E evidence.
* System Python has no Playwright module and the prior temporary Playwright
  environment is gone, so the host/WordCraft/VectorCraft Chromium suites could
  not be rerun during this pass. Gateway unit, SVG assertion, XLSX fixture,
  Python compilation, patch applicability and GR-015 source checks were rerun;
  no production files were altered.
* Blockers remain: real Seafile DOCX version/reopen and ONLYOFFICE regression are
  unverified. Public deployment and upstream publication remain locked.

* A bounded, independent Nemotron review returned **PASS for the route-prefix
  finding only**. It confirmed that `update-conditional-api` preserves the
  existing token-operation check. The reviewer classified the evidence as
  static/source-only; no C/Django/runtime behavior was tested. See
  `docs/reviews/GR-015/ROUTE-TOKEN-REVIEW.md`.
* The exact patched Seafile Server 12.0.14 source was subsequently configured
  and built in an isolated `/tmp` tree. `server/upload-file.o` compiled and
  `make -C server -j2` linked the complete fileserver subproject successfully.
  An earlier apparent build PASS was discarded after a source-tree check showed
  it had built the clean upstream base without the patch; both exact GR-015
  patches were then applied and the build repeated successfully.
  The workstation's `libjwt` 3.2.3 API is incompatible with this Seafile source,
  so `libjwt` 1.18.4 was built from its upstream tag into `/tmp`; Seafile's other
  missing build dependencies were staged under `/tmp` as well. GNU C11 flags
  were needed for this older source's callback signatures with the current GCC.
  This establishes compile/link only: the binary was not installed or run, and
  no HTTP route, token hook, Django flow, race, or save was exercised. The
  earlier “configure stopped/no C compilation” row below is superseded by this
  result.

### Reproduction record for the local route remediation

Reviewed base SHA: `0edbe524b4fa321b0f73f8601afef390e7f785e6`. The commands below
ran on 2026-10-23 against the working tree after that SHA; the source clones
were pinned to the Seahub and Seafile SHAs listed in `docs/reviews/GR-015/README.md`.

| Command | Exit | What it establishes |
| --- | ---: | --- |
| `env ARTCRAFT_SEAHUB_SOURCE=/tmp/artcraft-seahub-sol-next ARTCRAFT_SEAFILE_SERVER_SOURCE=/tmp/artcraft-seafile-server-sol-next python3 tests/test_gr015_authorization.py` | 0 | Synthetic helper checks plus source assertions for the update token, route, callback, path operation extraction and existing prefix check; no C/Django runtime |
| `python3 tests/test_gateway_unit.py` | 0 | Gateway tests against fake upstream/CAS; not real Seafile |
| `python3 tests/test_gr012_svg_assertions.py` | 0 | Offline SVG assertion unit checks; not an editor/Seafile round trip |
| `python3 tests/test_xlsx_fixture.py` | 0 | Fixture has a formula element and cached value; no GridCraft recalculation/reopen |
| `python3 -m py_compile integration/gateway/*.py tests/*.py tests/fixtures/make_fixtures.py` | 0 | Python syntax only |
| `git diff --check` plus pinned-source `git apply --check` for each GR-015 patch | 0 | Whitespace and applicability against clean source trees; no build/runtime |
| `python3 tests/test_gr012_svg.py` without its required Seafile URL/token, gateway, repository and path | 2 | Not run; the script printed its invocation and stopped |
| `python3 tests/test_gr010_xlsx.py` | 2 | Not run; no such test file exists (`tests/test_xlsx_fixture.py` is the fixture check) |
| `./autogen.sh && ./configure --disable-fuse --disable-python --enable-httpserver` in the pinned patched Seafile Server clone, after staging its build dependencies under `/tmp` | 0 | Configure passed; `intltoolize` was unavailable but `autogen.sh` continued and generated the configure script |
| `make -C lib libseafile_common.la` and `make -C common/cdc libcdc.la` with temporary dependency paths | 0 | Built required local static dependencies in the pinned source clone |
| `git apply --check` then `git apply` for both GR-015 patches on the pinned Seahub and Seafile Server clones | 0 | Confirms both exact patch artifacts apply to the recorded upstream source commits; the Seafile Server worktree contains the patch during the build below |
| `make -C server -j2` with `CPPFLAGS` for staged libjwt/libsearpc/evhtp headers, `CFLAGS='-std=gnu11 -g -O2'`, and temporary `LDFLAGS`/runtime library paths | 0 | Rebuilt and linked the complete fileserver subproject, including patched `upload-file.c`, against the pinned patched source; not runtime or integration evidence |

Environment: Python 3 on the local workstation; Playwright is unavailable in the
system Python and the old temporary browser-test environment is absent. No
production service or upstream artifact was changed. These checks do not resolve
Sol's real-Seafile E2E blocker.

## 2026-10-23 — Sol final re-review and focused remediation (local only)

* GPT-6.1 Sol reviewed exact candidate
  `afec19e63a6a4faec8a94f93651363dbe007e526` and returned **FAIL**. The full
  findings are preserved in `docs/reviews/GPT-SOL-REREVIEW-AFEC19E.md`; the
  previous `d9ef476e` FAIL remains unchanged.
* The confirmed overlapping-save defect now rejects a second host save while
  another is in flight. The Chromium protocol test proves the first save's
  acknowledgement cannot clear the later dirty revision; retry succeeds after
  the first save completes.
* Gateway save errors no longer expose arbitrary upstream bodies, and document
  downloads are bounded while reading. Unit tests cover a malformed HTTP-200
  page echoing the capability URL and an oversized content response.
* `POST /open/` now accepts a foreign Origin only when it matches configured
  `ARTCRAFT_SEAFILE_ORIGIN`; session mutations remain gateway-origin-only. The
  deployment docs now require Seahub and ArtCraft to be separate origins.
* GR-015 draft patches now scope save capabilities to the ArtCraft audience,
  original edit grant, repo allowlist and extension. Seahub uses a distinct
  `conditional-update-api` route exposed only by the proposed C patch; stock/Go
  route absence and source patches are checked, but binaries are not built or
  runtime-tested.
* SVG/XLSX evidence was corrected. The old GR-010/GR-012 PASS claims are marked
  superseded; the XLSX fixture now has a real `<f>` formula element. The local
  VectorCraft web bundle edited and reopened the expected pencil stroke in a
  browser (270 → 609 bytes); this is local editor evidence, not Seafile E2E.
* Reproduced local checks: `tests/test_gateway_unit.py`,
  `tests/test_hostpage_protocol.py`, `tests/test_gr015_authorization.py`,
  `tests/test_wordcraft_host_roundtrip.py`, `tests/test_gr012_svg_assertions.py`,
  `tests/test_vectorcraft_svg_local.py`, `tests/test_xlsx_fixture.py`, Python
  compilation, and both patch-application checks pass. `git diff --check` exits 2
  because the generated server patch contains one unified-diff context line
  flagged as trailing whitespace; patch applicability passes.
  `tests/test_integration.py` was not run because no Seafile URL/token, editor
  capability, or isolated patched Seafile deployment is available in the shell.
* No production Seafile, Proxmox service, ONLYOFFICE, or upstream repository was
  modified. Public deployment and upstream publication remain locked. A fresh
  Sol review is required on the new exact candidate SHA.

## 2026-10-22 — GPT-6.1 Sol remediation (local only)

The unauthenticated direct `/open` route was closed. Token sessions are writable
only with an explicit user-bound authorization hook, and saves require an
atomic upstream CAS hook; the stock Seafile client therefore fails closed.
WordCraft saves now carry and validate the original filename/type, with Save As
and PDF export rejected. Deterministic unit coverage was added for the CAS race
and refusal paths. The real Seafile Web DOCX and ONLYOFFICE checks remain
**NOT VERIFIED**. Evidence: `docs/reviews/GPT-LUNA-REMEDIATION.md`.

Running log. Newest first.

## 2026-10-22 — the fourth review, and the GR-012 proof hardened

* **REVIEW-04 (Nemotron) on GR-012: FAIL, remediated.** Four blockers, all right:
  the "document really changed" assertion compared the *length* of a
  `document.inspect` snapshot instead of the content; the save poll compared
  *sizes*, so an identical re-save was invisible; there was no `beforeunload`
  guard and no dirty state for VectorCraft; and `dispatch.json` claimed
  `?host=parent` for an application that does not speak it.
* The fixes: the test now reads the **bytes the editor produced** and asserts
  they differ from the original and form a valid SVG with a path element; the
  poll compares a **content fingerprint** and only a *stored* save becomes the
  new baseline; the host page warns on unload while a save is in flight; the
  dispatch entry no longer claims a contract VectorCraft does not implement; the
  adapter verifies the frame's **origin** before it drives it.
* Two bugs the remediation itself found: `api.readFile` is **synchronous** (it
  throws, it does not return a promise), and VectorCraft's SVG export writes a
  rectangle as a `<path>`, so an assertion looking for `<rect>` failed on a
  correct file.
* Final GR-012 run: **12/12 PASS**, including the strongest check — the bytes
  Seafile holds are **byte-identical** to what the editor produced.
* **GR-010** bundle written: the `.xlsx` round-trip, distinct from GR-005 (the
  mechanism) by being about the format and its conflict behaviour.
* The unit check on the dispatch table was corrected to match the truth: only
  the applications that speak the bridge name `?host=parent` in their URL.
* The architect sub-agent timed out a **second** time (GR-003), after cloning and
  reading all fourteen repositories for hours. Both GR-001 and GR-003 had already
  been completed independently by the owner, so nothing was lost. The lesson is
  recorded in `docs/AI-ROUTING.md`: a very long research brief is a bad fit for a
  single sub-agent call; research is now split into bounded questions, and the
  owner's own verification is the primary path.

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
