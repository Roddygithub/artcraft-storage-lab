# Task evidence — WordCraft DOCX typed edit before Save (browser slice)

Task: first bounded slice of `ROADMAP.md` step 3 (WordCraft DOCX only; other editors stay on
their existing paths). Branch `aptarchy/artcraft-wordcraft-real-edit-20261102`, based on
`5b576de`. Candidate = the last commit of this task (exact SHA recorded by the task lane).
No push; upstream LOCKED; project GPT REVIEW: INCOMPLETE.

## What changed

| File | Change |
| --- | --- |
| `lab/real-seafile/run_slice.py` | `docx_text(data)` helper: all `w:t` runs of `word/document.xml` (stdlib only, tolerant of bad zips) |
| `lab/real-seafile/run_browser.py` | WordCraft branch: real typed change before Save, then close the old editor, reopen from Seafile in a fresh browser session; new checks `wordcraft_typed_edit_before_save_is_visible_as_unsaved_changes`, `wordcraft_save_confirmed_by_host_page`, `wordcraft_save_creates_seafile_version_by_user`, `wordcraft_saved_docx_contains_the_typed_marker`, `wordcraft_save_is_not_identical_bytes`, `wordcraft_saved_docx_bytes_look_right`, `wordcraft_reopen_fresh_seafile_session`, `wordcraft_reopen_host_frame_from_seahub`, `wordcraft_reopen_editor_ready_and_document_opened`, `wordcraft_reopen_shows_the_typed_marker`, `wordcraft_reopen_bytes_identical_to_the_saved_version` |
| `ROADMAP.md` | step 3 row updated to "coded, NOT RUN" (nothing runtime-level is claimed) |

The bridge, Seahub, and the ONLYOFFICE integration are untouched. No bytes are injected and no
helper uploads anything: the change is typed into the editor (Playwright trusted keys, with a
single IME-style `insert_text` fallback typed into the same focused editor), Save is Ctrl+S
inside the editor, and assertions read Seafile history/API plus the reopened editor's own
`/relay/file` fetch. All other editors keep the previous generic flow.

## Scope guard

WordCraft DOCX only, per the bounded task. Reusable piece: `docx_text()` is stdlib-only and
environment-free (plain helper over bytes), so later editor slices can reuse it.

## Checks run on this machine now

| Check | Result |
| --- | --- |
| `python3 -m py_compile lab/real-seafile/run_slice.py lab/real-seafile/run_browser.py` | OK |
| Focused helper check: `docx_text(minimal_docx('hello world'))` contains `hello world`; not-a-zip and broken-zip return `''` | OK (output in commit history) |
| `python3 tests/bridge/test_bridge.py` | OK, 30/30 (bridge untouched) |

## NOT RUN — real-Seafile / browser runtime

| Check | Prerequisite missing |
| --- | --- |
| `lab/real-seafile/up.sh browser` (the new WordCraft typed-edit + reopen checks; also re-proves `up.sh slice`, including the ONLYOFFICE checks) | Lima (`limactl`) is not installed and Docker permission is denied on this machine; the compose stack (Seafile, bridge, Chromium) cannot start. Run on the usual lab VM: `up.sh up`, `up.sh configure`, `up.sh slice`, `up.sh browser` (`lab/real-seafile/README.md`). |

Historical `lab/real-seafile/results/{slice,browser}.json` (2026-10-31) predate this change and
are NOT evidence for this candidate; nothing was fabricated or reused.

## Gate status unchanged

Project GPT REVIEW: INCOMPLETE. `UPSTREAM_STATUS=LOCKED`. This task review is not the project
gate; production untouched.
