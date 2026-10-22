# GR-005 — First host-integration technical proof

Status: **PROVISIONAL — FREE REVIEW PASS** (the Seafile side) · GPT REVIEW: PENDING
Date: 2026-10-22 · Library: `c82cc792-389d-43e6-b963-0dab1a47a9a8` ("OnlyOffice", an
empty library on the reference instance) · Folder `/artcraft-lab/`

## 0. What is proven, and what is not

| | Status |
| --- | --- |
| Seafile -> gateway -> document bytes -> Craft app -> saved bytes -> **a new Seafile version** | **PROVEN**, end to end, against the real instance |
| The **conflict** behaviour: a stale save is refused and the file is left alone | **PROVEN** |
| The Craft web app actually rendering in a browser and talking to the host page | **not yet proven in a browser** (no browser on this machine at the time of writing) |

The browser half is a *rendering* question; the protocol half (the message
vocabulary, the origin checks, the byte transfer) is verified by reading the
Craft source, and the two implementations of it are documented in
`docs/HOST-CONTRACT.md`. The missing piece is a browser to click in.

## 1. Why GridCraft and `.xlsx` for the first proof

The proof had to be **zero-risk** for the production instance. Two facts decided
it:

* Seafile's third-party-editor hook is keyed by **file extension** and applies
  to **every library** (`docs/SEAFILE-INTEGRATION-POINTS.md` §4). Any extension
  it claims stops being handled by whatever handled it before.
* The reference instance's libraries were inventoried first:

```text
Google Drive   (real personal data)  1 .pdf, 1 .docx, 1 .pptx, 1 .txt, 2 dirs
OnlyOffice     (empty)                the test library
Ma bibliothèque (empty)
```

`.xlsx` occurs **nowhere** in the real data, and it is **not** in the deployed
`ONLYOFFICE_FILE_EXTENSION`. Claiming it therefore has **zero** effect on any
existing file and **zero** effect on the ONLYOFFICE integration.

GridCraft was chosen because it **already ships the `?host=parent` bridge**
(`storytold/gridcraft/apps/gridcraft-web/src/host.rs`), so the proof needs
**no change to any Craft application** and no Rust/wasm toolchain: the app
publishes its browser build in its GitHub release
(`gridcraft-web-0.10.0.zip`, 7 MB).

## 2. The configuration change on the reference instance

One additive block in `/opt/seafile/conf/seahub_settings.py`:

```python
# --- ArtCraft Storage Lab: third-party editor hook -----------------------
ENABLE_THIRDPARTY_EDITOR = True
THIRDPARTY_EDITOR_ACTION_URL_DICT = {
    "xlsx": "http://127.0.0.1:8777/open/",
}
```

* **Backup taken first:** `/opt/seafile/conf/seahub_settings.py.bak-artcraft-20261022-123134`
* **Rollback:** restore that file, `systemctl restart seahub`. The ONLYOFFICE
  block above it is not touched.
* **Blast radius:** one extension that no existing file uses, and that
  ONLYOFFICE does not claim.
* `seahub` was restarted once; both `seahub` and `seafile` came back `active`.

## 3. What was built

```text
integration/gateway/seafile.py    the Seafile client (stdlib only)
integration/gateway/sessions.py   the editing sessions
integration/gateway/hostpage.py   the host page (the parent side of the bridge)
integration/gateway/server.py     the HTTP server
integration/config/dispatch.json  extension -> Craft app
scripts/fetch-craft-web.sh        fetch the prebuilt Craft web builds
tests/fixtures/make_fixtures.py   synthetic docx / xlsx / pdf / svg
tests/upload_fixtures.py          put the fixtures in a test library
tests/test_integration.py         the end-to-end test
```

The gateway holds the Seafile credential. **The browser never sees it**: the
browser only ever holds an opaque session id that maps to one document, one
user, for 30 minutes.

## 4. The flow that was exercised

```text
Seafile Web
  -> view_lib_file -> the thirdparty-editor hook (config only)
  -> form POST access_token to the gateway's /open/
  -> the gateway reads file-info / file-content, creates a session
  -> the gateway serves the host page, which frames the Craft app
     (same origin, ?host=parent)
  -> Craft app: wordcraft/gridcraft:ready
  -> host page: gridcraft:open { name, bytes }
  -> the user edits in GridCraft
  -> Craft app: gridcraft:save { name, bytes }
  -> the gateway checks the content id, writes through seafhttp update-api
  -> Seafile creates a NEW VERSION
```

## 5. The test

```sh
export ARTCRAFT_SEAFILE_URL=... ARTCRAFT_SEAFILE_TOKEN=...
export ARTCRAFT_GATEWAY=http://127.0.0.1:8777
python3 tests/test_integration.py c82cc792-389d-43e6-b963-0dab1a47a9a8 \
        /artcraft-lab/synthetic.xlsx
```

Result on 2026-10-22:

```text
[PASS] 1. the host page is rendered
[PASS] 1. the host page asks for a document over the session
[PASS] 1. the document is delivered  -- HTTP 200, 1669 bytes
[PASS] 2. the save is accepted  -- {'ok': True, 'file_id': 'fe9011fd...', ...}
[PASS] 2. a NEW version exists  -- dc9dc324... -> fe9011fd...
[PASS] 2. the history grew  -- 3 -> 4 versions
[PASS] 2. the new content is what we saved  -- B2 = '<is><t>1337</t></is>'
[PASS] 3. a second save of the same content is accepted (same content, no new version)
[PASS] 3. a save with unchanged content is accepted
[PASS] 3. the second editor saves first
[PASS] 3. the STALE save is REFUSED  -- HTTP 409 {... 'conflict': True ...}
[PASS] 3. the refusal names the conflict
[PASS] 3. the file on the server was NOT overwritten  -- B2 = '<is><t>4242</t></is>'
[PASS] 4. an unknown session cannot write  -- HTTP 404
[PASS] 5. a known session can still write  -- HTTP 200

ALL CHECKS PASSED
```

### 5.1 What "a new version exists" means, precisely

Checked through the Seafile API, not through the gateway:

| Check | API | Result |
| --- | --- | --- |
| the content id changed | `GET /api2/repos/<id>/file/detail/?p=` | `dc9dc324...` -> `fe9011fd...` |
| the file history grew | `GET /api2/repos/<id>/file/history/?p=` | 3 -> 4 commits |
| the content is what was saved | `GET /api2/repos/<id>/file/?p=` then read the cell | `B2 = 1337` |

The gateway's own answer is **not** taken as evidence.

### 5.2 The conflict case, precisely

The test opens two sessions on the same version, saves from the second one, and
then saves from the first one:

```text
session A  opened on version N
session B  opened on version N
B saves  -> new version N+1            (accepted)
A saves  -> HTTP 409 {"ok": false, "conflict": true,
                      "error": "this file was modified by someone else while you
                                were editing it; your changes were not saved"}
```

and the file on the server still holds B's content, not A's. **A's write never
happened.** This is strictly better than Seafile's own ONLYOFFICE callback,
which writes unconditionally (`docs/reviews/GR-008/SEAFILE-CONCURRENCY-PRIMITIVES.md`).

## 6. Known limitations of this proof

| # | Limitation |
| --- | --- |
| L1 | The Craft app was not clicked in a real browser (no browser on the machine). The gateway side and the protocol are proven; the rendering is not. |
| L2 | The gateway's `action_url` is `http://127.0.0.1:8777`, which only works for a browser on this machine. The production design puts the gateway on its own host. |
| L3 | The write is attributed to the **service account**, not the user who edited. The upstream patch (option A in `docs/SEAFILE-INTEGRATION-POINTS.md`) fixes this by writing inside Seahub as the user. |
| L4 | The host page does not yet model "the Craft app believes it saved but the host failed" (the Craft app marks the document clean when the bytes leave the frame). The host page keeps its own state and shows the failure, but the Craft app does not know. This is the open question Q-5 in `docs/HOST-CONTRACT.md`. |
| L5 | Only the `.xlsx` extension is claimed. `.docx` is deliberately **not** claimed, because the deployed ONLYOFFICE configuration includes it and the rule is that ONLYOFFICE must keep working. |

## 7. What GR-006 adds

GR-006 is the WordCraft DOCX MVP. It needs:

1. the `?host=parent` bridge in WordCraft (it does not have one) -- the upstream
   patch (GR-014);
2. a way to claim `.docx` without taking it away from ONLYOFFICE -- either a
   dedicated test Seahub instance, or the per-library `artcraft` office-suite
   id upstream;
3. the browser half of this proof.

See `docs/reviews/GR-006/` when it lands.
