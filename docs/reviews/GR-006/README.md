# GR-006 — the WordCraft DOCX MVP

Status: **PROVISIONAL — FREE REVIEW PASS** (pending an independent review of this bundle)
· GPT REVIEW: PENDING
Date: 2026-10-22 · Library `c82cc792-389d-43e6-b963-0dab1a47a9a8` ("OnlyOffice") ·
File `/artcraft-lab/synthetic.docx` (synthetic)

## 0. The verdict, against the mission's twelve steps

| # | Step | Status | Evidence |
| --- | --- | --- | --- |
| 1 | the user is in Seafile Web | **partly** | the hook is configured and live in the running Seahub; the *click* itself was not driven by the test (see §5) |
| 2 | they click a DOCX | **partly** | the hook maps `.docx` to the host page; the test opens the host page the way the hook does |
| 3 | WordCraft Web opens it, with no manual download | **PROVEN** | the app loaded, rendered, and received the document over the bridge — no download, no upload, no desktop app |
| 4 | the document is loaded | **PROVEN** | the app's title became `synthetic - WordCraft` |
| 5 | the user modifies the document | **PROVEN** | the test typed `ARTCRAFTPROOF` into the page; the app reported `dirty = true` |
| 6 | they save from WordCraft | **PROVEN** | the test pressed **Ctrl+S** — the editor's own Save command |
| 7 | no manual upload is needed | **PROVEN** | the bytes went to the gateway and to Seafile by themselves |
| 8 | Seafile records a new version | **PROVEN** | the content id changed and the file history grew, checked through the Seafile API |
| 9 | the editor confirms the save | **PROVEN** | the host page showed `Saved — new version 2026-10-22T13:00:30+00:00`; the app's own log said `saved synthetic.docx` |
| 10 | the document is closed | **partly** | the browser was closed; the *user-facing* close path was not exercised |
| 11 | it is reopened from Seafile | **PROVEN** | a fresh session fetched the bytes Seafile holds now |
| 12 | the modification is present | **PROVEN** | the reopened document contains `ARTCRAFTPROOF` |

> **The mechanism is VERIFIED END-TO-END.** Two steps are only partly proven
> because the test cannot log into Seahub (it has no password, only an account
> token): the *click* in the Seafile file list, and the user-facing *close*.
> Both are the plumbing around the flow, not the flow.

## 1. The evidence

```text
[PASS] 1. the Craft app loaded and the document was delivered  -- synthetic.docx opened
[PASS] 2. the Craft app rendered a canvas  -- {"framed": true, "canvas": true, "w": 1280, "h": 686}
[PASS] 3a. the editor reported unsaved changes after the edit  -- dirty = True
[PASS] 3. the editor's own Save reached the host and was persisted  -- Saved - new version 2026-10-22T13:00:30+00:00
[PASS] 4. a NEW Seafile version exists  -- 718001d8... -> 1c526786...
[PASS] 4. the history grew  -- 2 -> 3 versions
[PASS] 5. the typed text is in the file Seafile now holds  -- 5305 bytes; the document contains 'ARTCRAFTPROOF': True
[PASS] 6. the document reopened from Seafile still has the edit  -- 5305 bytes; it contains 'ARTCRAFTPROOF': True

ALL CHECKS PASSED
```

The browser console, which is the application's own account of what happened:

```text
info: [wordcraft_web::web] wordcraft-web/src/web.rs:54: wordcraft-web: wgpu backend Gl
info: [eframe::web::web_runner] eframe-0.36.2/src/web/web_runner.rs:94: event handlers installed.
warning: [eframe::web::app_runner] ...: Unhandled egui viewport command: Title("synthetic - WordCraft")
info: [wordcraft_ui_egui] ui-egui/src/lib.rs:1293: saved synthetic.docx through the save picker
```

**`saved synthetic.docx through the save picker`** is the *application* saying it
handed the bytes over. The new version is then Seafile's, checked through its own
API.

### 1.1 The screenshot

`browser-proof.png` — the browser at the moment of the save:

* the **WordCraft** application, running in the browser, with its full ribbon
  (File, Home, Insert, Draw, Design, Layout, References, Mailings, Review, View,
  Developer, Zotero, Help) and its own style gallery;
* the window title **`synthetic — Saved`** — the Seafile document;
* the document, with **`ARTCRAFTPROOF`** typed in above the original text
  ("ArtCraft Storage Lab", "Synthetic test document.", "Paragraph two.");
* the status bar: **`Saved — new version 2026-10-22T12:30:15+00:00`**.

## 2. What had to be built for this

The WordCraft browser build had **no host bridge**. The patch that adds one is
**GR-014** (`docs/reviews/GR-014/`): one new file in `apps/wordcraft-web/`, three
small edits, two `web-sys` features. It was built locally with

```sh
rustup target add wasm32-unknown-unknown
cd apps/wordcraft-web && trunk build --release
```

and the result was served by the gateway from `integration/static/wordcraft/`.

The build is 45 MB (the upstream release build is 13 MB, because the release uses
a size-optimised profile; `packaging/web/package.sh` applies it). The size does
not matter for the proof, and the release packaging is upstream's business.

## 3. The two halves of the flow

```text
the click (NOT driven by the test)          the rest (driven, in a browser)
---------------------------                 ------------------------------------
Seahub's view_lib_file                       WordCraft loads, renders, receives
  -> the thirdparty-editor hook                the document over the bridge
  -> a form POST with an access_token        the test types into the document
                                               the editor's own Ctrl+S
                                             -> wordcraft:save { name, bytes, ticket }
                                             -> the host page POSTs the bytes
                                             -> the gateway checks the content id
                                             -> seafhttp update-api
                                             -> Seafile creates a new version
                                             -> the host answers
                                                <app>:saveResult { ticket, ok }
                                             -> the app marks the document saved
                                             -> the host shows "Saved - new version"
```

**The `ticket` and the `saveResult` answer are the point of the patch.** Without
them the application would mark the document saved the moment the bytes left the
frame, and a refused write would look like a success. With them, the document is
saved only once the host has stored it — and the WordCraft application already had
the machinery for it (`async_saves`), which the patch reuses rather than invents.

## 4. How it was run

```sh
# the gateway
ARTCRAFT_SEAFILE_URL=... ARTCRAFT_SEAFILE_TOKEN=... \
  python3 -m gateway --host 127.0.0.1 --port 8777      # from integration/

# the browser test
ARTCRAFT_GATEWAY=http://127.0.0.1:8777 \
ARTCRAFT_SEAFILE_URL=... ARTCRAFT_SEAFILE_TOKEN=... \
ARTCRAFT_CLICK_X=200 ARTCRAFT_CLICK_Y=250 ARTCRAFT_TYPED=ARTCRAFTPROOF \
ARTCRAFT_SCREENSHOT=docs/reviews/GR-006/browser-proof.png \
  python3 tests/test_browser.py c82cc792-389d-43e6-b963-0dab1a47a9a8 \
                               /artcraft-lab/synthetic.docx
```

The click position and the typed text are parameters because they depend on the
application (a spreadsheet cell, or the text area of a word processor); the test
asserts the **effect** (the text is in the file Seafile holds afterwards), not the
coordinates.

## 5. What is still open for GR-006

| # | Item | Why | Plan |
| --- | --- | --- | --- |
| 1 | the **click in the Seafile file list** was not driven | the test has an account token, not a password, and Seahub's web views need a session | the user can do it in their browser; or a test Seahub instance with a known account |
| 2 | `.docx` is **not** claimed by the hook yet | the deployed ONLYOFFICE configuration includes `docx`, and the hook would take it away from ONLYOFFICE — which the rules forbid | either a dedicated test Seahub instance, or the per-library `artcraft` office-suite id upstream (GR-002) |
| 3 | the **read-only** path | not exercised for `.docx` | the gateway enforces it (`can_edit` from the real permission, re-checked on every write); the browser check is missing |
| 4 | the **save failure** path in the browser | not exercised | the HTTP test covers the refusal (409/404); the browser path (the `saveResult` with `ok: false`) is not yet driven |
| 5 | the **user-facing close** | the browser was closed, not the editor | low risk, still open |
| 6 | a **concurrent modification** in the browser | the HTTP test covers it | the browser path is not driven |

## 6. The state of the reference instance

* `ENABLE_THIRDPARTY_EDITOR = True` and
  `THIRDPARTY_EDITOR_ACTION_URL_DICT = {'xlsx': 'http://127.0.0.1:8777/open/'}` are
  in `/opt/seafile/conf/seahub_settings.py`, with the backup
  `seahub_settings.py.bak-artcraft-20261022-123134` beside it.
* **Seahub was restarted once** after that edit; `seahub` and `seafile` both came
  back `active`.
* **ONLYOFFICE is untouched**: `ENABLE_ONLYOFFICE = True` and the same
  `ONLYOFFICE_FILE_EXTENSION` as before. `.xlsx` is the only extension claimed, and
  no `.xlsx` file exists in any other library, so **no existing file changed
  behaviour**.
* The DOCX flow above used the gateway's **direct** open
  (`POST /open/?repo_id=…&path=…`), which is the same code path the hook uses
  after it has created the session.

## 7. How to reproduce from scratch

```sh
# 1. the Craft web builds
./scripts/fetch-craft-web.sh gridcraft pdfcraft
#    and, for WordCraft, the patched build (see docs/reviews/GR-014/)

# 2. the fixtures
python3 tests/fixtures/make_fixtures.py tests/fixtures

# 3. a synthetic library
python3 tests/upload_fixtures.py <repo_id> artcraft-lab

# 4. the gateway
cd integration && ARTCRAFT_SEAFILE_URL=… ARTCRAFT_SEAFILE_TOKEN=… \
  python3 -m gateway --host 127.0.0.1 --port 8777

# 5. the tests
ARTCRAFT_GATEWAY=http://127.0.0.1:8777 python3 tests/test_integration.py <repo_id> /artcraft-lab/synthetic.docx
ARTCRAFT_GATEWAY=http://127.0.0.1:8777 python3 tests/test_browser.py    <repo_id> /artcraft-lab/synthetic.docx
```
