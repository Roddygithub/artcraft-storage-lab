# GridCraft XLSX real-edit browser slice — code-stage evidence

> Code-stage candidate only. Real Seafile runtime for this slice is **NOT RUN** here: the parent
> owns the separately authorized isolated replay after independent exact-candidate review.
> Historical WordCraft runtime successes and the first pilot's failed/blocked states are preserved
> untouched; see [the first pilot](2026-11-02-first-pilot.md) for that manual-completion assessment.

Original Aptarchy implementation: `450d19abeb2d3f14bb2221eab07d543c10191890`, followed by
evidence candidate `9f1fd73d5842ce009e6cf5dfe63363be7c9a0edd` (base `4af729a`). Parent remediation
implementation: `9fe910fbd3ef8818b39fc9dcf29dccb4966c1f41`, on
`work/gridcraft-parent-remediation-20261103`. WordCraft's scenario remains intact; its download
instrumentation and loopback regression now also cover GridCraft's shared callbacks.
Aptarchy integration mode: none; push: false; project GPT:
**INCOMPLETE**; upstream: **LOCKED**. No paid/PAYG lane was used.

## Changes

| Location | Change |
| --- | --- |
| `lab/real-seafile/run_slice.py` | Stdlib `xlsx_cells`: first-worksheet cell values of an XLSX (`{"A1": "1", ...}`), resolving plain numerics, cached formula strings, inline strings and shared strings; raises `ValueError` on malformed archives/parts or invalid shared-string references, so a positive cell assertion can never pass on unreadable input. Placed next to `minimal_xlsx`/`docx_text`, which the GridCraft flow in `run_browser.py` calls (`rs.xlsx_cells`) — the format-helper home the WordCraft slice already used. |
| `lab/real-seafile/run_browser.py` | GridCraft-specific flow (WordCraft and generic other-editor paths untouched): the fixture stays `minimal_xlsx()` (A1=1); `test.xlsx` is opened by a real Seafile file-list click (`open_from_seafile_list`, download tracking registered from before navigation including popup pages); an actual editor cell is focused by trusted mouse click, a distinct random value is typed with `keyboard.type` (IME-style fallback insert into the same focused editor), committed with Enter; Save is the existing host/bridge Ctrl+S path with the editor's own `/relay/save` payload captured; assertions are semantic (`xlsx_cells` on the editor payload and on the Seafile readback), plus bytes-differ-from-input, fixture A1 still `1`, host `saved to seafile` confirmation, and a new version owned by the authenticated user. Then the old editor is closed, a fresh browser context logs in (response/request/download capture registered before login/navigation), reopens the same file via the file list, `wait_for_saved_response` observes the reopened host's successful `/relay/file` fetch (bytes identical to the saved version, parsed and containing the first value), and a second trusted edit in a different cell is saved there: the reopened editor's own save payload and the Seafile readback must carry both values, another user-attributed version must exist, bytes must differ from the first save, and downloads must stay empty the whole scenario. |
| `tests/test_gridcraft_real_edit.py` | Focused stdlib regression for `xlsx_cells`: the real lab fixture parses to A1=`1`; numeric/float/negative/cached-formula-string cells; inline string; shared strings incl. multi-run `<si>` joining; rejection (`ValueError`) of non-zip input, broken sheet XML, out-of-range and non-numeric shared-string indexes, and a missing index. Synthetic workbook bytes are local parser fixtures only. |

Reuses the proven WordCraft helpers (`open_from_seafile_list`, `wait_for_saved_response`,
`find_frame`, `check`, `rs.history`/`rs.download`/`rs.upload`) instead of copying the whole flow;
no new dependency, no editor framework, no mock editor.

## Initial local verification (Aptarchy implementation `450d19a`)

Full transcript: [local-checks.txt](evidence/2026-11-03-gridcraft/local-checks.txt).

| Command | Result |
| --- | --- |
| `python3 tests/bridge/test_bridge.py` | 30/30, `OK` |
| `python3 tests/test_gridcraft_real_edit.py` | 10/10 PASS, 0 failed, exit 0 |
| `uv run --offline --with playwright -- python tests/test_wordcraft_reopen_wait.py` | 8/8 PASS, 0 failed, exit 0 (cached Python 3.14.8 + Playwright, no installs) |
| `python3 -m py_compile lab/real-seafile/run_browser.py` | OK |

The WordCraft loopback regression proves the shared navigation/response-wait helpers under real
Chromium: delayed callback dispatch (the production wait sees it, the former sleep-only loop did
not), same-tab and popup file-list opening. It proves helper behavior only — it loads no editor and
no Seafile, so it does not prove GridCraft or Seafile runtime behavior.

## Parent remediation and fresh local checks

The original candidate received a GPT **FAIL**: missing focused save/download callback coverage
(major), and an empty shared-string index escaping as `TypeError` (minor). The GLM remediator
stopped after leaving an unfinished patch; that patch was retained privately, including its
syntax error, and its four files were restored to the committed candidate. The explicit failed
continuation reconciliation then tried DeepSeek, which produced no answer before its deadline.
The Aptarchy task remains **blocked**, with its failed dispatches and failed review retained.
It is not presented as an autonomous success or an Aptarchy-accepted candidate.

The parent wrote `9fe910f` on a separate branch. `save_and_capture` is now a directly testable
production helper with a bounded event-pumping wait and unconditional listener removal.
`track_downloads` covers existing pages and future popups in both editor contexts. The XLSX
parser turns an empty `<v/>` index into `ValueError`. The loopback fixture exercises delayed
successful saves, HTTP failure, missing-request timeout, status-reader error, listener cleanup,
and actual browser downloads on an existing page and popup. These are helper checks, not a
mock-editor replacement for the future Seafile replay.

| Command on `9fe910fbd3ef8818b39fc9dcf29dccb4966c1f41` | Result |
| --- | --- |
| `python3 tests/bridge/test_bridge.py` | 30/30 passed; exit 0; Python 3.14.8 |
| `python3 tests/test_gridcraft_real_edit.py` | 11/11 passed; exit 0; includes empty shared-string index |
| `uv run --offline --with playwright -- python tests/test_wordcraft_reopen_wait.py` | 20/20 passed; exit 0; cached Python 3.13.16, Playwright 1.64.1, real Chromium |
| AST parsing of both runners and both focused test files | Passed on Python 3.14.8 |
| `git diff --check` | Passed |

The first parent browser check exposed Playwright's inability to wrap the built-in
`list.append` method as a handler; the production helper uses a Python lambda instead, and the
fresh run above passed. The parent did not increase budgets again after the additional free
envelope was exhausted. Local policy changes (GLM 6→8, DeepSeek 4→5), plan
`plan-abf465650b11` (27 requirements, two ordered phases grouped into one task), recovery patch,
and temporary parent supervision are retained outside Git. The five-minute supervision detected
the second provider failure automatically and was disabled when this separate manual recovery
began. This supervision is external parent orchestration, not an Aptarchy feature.

Both original code and this correction use the completed Aptarchy fixes merged in PR21–23
(`fdeffa15b5aec46e3f4925092d120b74f200135e`). No PAYG was authorized. Independent review of the
final corrected candidate is required before the isolated runtime replay.

The independent review of `28bac12dfb0f03bbd6a34f47de2bd226d0d2757c` closed both original
findings and found one further minor: the save helper did not recognize the bridge's
`saved (reconciled after a lost response)` success message. Follow-up source
`a9eb3afc95ae5b92337f84a51f9e13e1fa75471d` accepts both exact bridge success statuses.
The same offline Chromium command then passed **23/23** checks, including the delayed
reconciled-save case; `git diff --check` also passed. The bridge and XLSX parser were unchanged
since their successful checks above. This remains local helper evidence; real Seafile is
still NOT RUN for this candidate.

## Honest runtime limits

A local, loopback-only check cannot prove that: the real GridCraft bundle accepts a mouse/keyboard
cell edit and commits it to its document; the typed value is serialized by GridCraft into the
save payload in a form `xlsx_cells` resolves (the value assertions require the value to appear as
a **cell**, not just bytes); the click points (35%/30% and 60%/55% of the editor frame) land on
distinct sheet cells; the host status wording (`unsaved` / `saved to seafile`) matches. All of
that is exactly what the runtime replay must demonstrate. If the editor's save lands failed, the
coded checks fail rather than falling back to any generic save/export path.

## Runtime commands — both NOT RUN for this candidate

| Command | Coverage / remaining prerequisite |
| --- | --- |
| `lab/real-seafile/up.sh slice` | HTTP/WOPI/storage in `run_slice.py`. NOT RUN for this slice implementation; requires the isolated Seafile lab. |
| `lab/real-seafile/up.sh browser` | Actual GridCraft open/edit/save/version/reopen in `run_browser.py`. NOT RUN for this slice implementation; requires the isolated stack and provenance-checked GridCraft bundle. It does not run `slice`. |

Historical result files (`lab/real-seafile/results/*`, the WordCraft pilot evidence) are unchanged;
no historical verdict has been overwritten or claimed as new proof. The parent will run a fresh
isolated replay for this exact candidate after review and record new results.
