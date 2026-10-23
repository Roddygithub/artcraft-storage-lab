# GR-015 isolated Seafile runtime evidence

Date: 2026-10-23
Repository tip when exercised: `7f828a4c58f49de247ac71bc66e58d2f41bfa230`
Scope: synthetic Seafile Server 12.0.14 + Seahub 12.0.14 + WordCraft Web

## Result

The mandatory DOCX workflow was reproduced in an isolated local stack:

```text
Seahub file list click
→ patched per-library dispatch
→ real WordCraft Web/WASM
→ real text edit
→ editor Save
→ patched Seahub conditional save
→ patched Seafile C fileserver commit
→ fresh Seafile file-list open
→ WordCraft renders the saved edit
```

This is evidence for the synthetic local prototype only. It does not change the
GPT-6.1 Sol **FAIL** on `0edbe524b4fa321b0f73f8601afef390e7f785e6`, approve a
new candidate, establish production deployment readiness, or unlock upstream
publication.

## Isolated environment

| Component | Evidence |
| --- | --- |
| Seafile source | `haiwen/seafile-server` `32ed9c69594c9faa5cea28024403fcde362589ec`, GR-015 patch applied, configured, compiled, and run in a rootless Podman container |
| Seahub source | `haiwen/seahub` `1e9bde801b4360c14d784d9681d4261abc233a8b`, GR-015 patch applied, Django checks and migrations completed, then run in the same isolated container |
| Editor | WordCraft Web/WASM, built from the local GR-014 patched tree; the running editor showed the WordCraft UI and loaded the DOCX in Chromium |
| Data | Synthetic user, synthetic library `6862763d-721f-498a-bbf0-d666cee97496`, synthetic `synthetic.docx`; no personal or production documents |
| Network | The first browser run used a same-origin test proxy. A follow-up on the same isolated stack used Seahub at `http://127.0.0.1:18000` and the gateway/Craft at `http://127.0.0.1:18777`; both were loopback-only. This checks cross-origin handoff in Chromium, not production TLS, proxy headers, CSP, or CSRF. |
| Live services | No production Seafile, ONLYOFFICE, Proxmox guest, DNS, or upstream repository was changed during this test. |

The test account password, access capabilities, session identifiers, and tokens
are intentionally omitted. The temporary container is not a public or
production service.

## DOCX click, edit, durable save, and reopen

The browser opened `synthetic.docx` by clicking it in the synthetic Seahub
library. The patched dispatcher sent the file to `/open/`; the gateway then
served `/artcraft/wordcraft/?host=parent`, and the browser loaded the WordCraft
JavaScript and WASM assets. WordCraft visibly rendered the synthetic starting
text. No download or manual upload was used.

The user typed `Edited in the isolated Seafile test.` in WordCraft and pressed
Ctrl+S. The editor showed its dirty state before saving. The browser sent the
save request through the host bridge; Seahub returned HTTP 200 only after the
patched fileserver returned the new file ID and Seahub read the committed
repository head. WordCraft then displayed `Saved — new version` and returned to
clean state.

Independent Seafile metadata and content readback for that save:

| | Before | After save |
| --- | --- | --- |
| Repository head | `04e4f66c22324c967d94a95590b793d098bcbee7` | `c1b214fe592de93d762430f6ae2679d7a5b54843` |
| File ID | `7fdeab927b4bc73119ea9f5c046dd8a79438a7fc` | `4f50fb196a82a499244f5693a9707c3a87bc245f` |
| Byte length | 1,632 | 5,298 |
| SHA-256 | `93a69349a6e4e620113e82456dc84ccb4f161a8aeaed702ceb03daf469208940` | `ce75265e95ffb077b41670f4e2a4b49717d637a66f7b3f74939e23b316d5e5cd` |
| DOCX validation | valid ZIP package; phrase absent | valid ZIP package; phrase present in document XML |

The editor was navigated away from, then `synthetic.docx` was opened again from
the Seahub file list. A fresh WordCraft session fetched the saved document and
rendered `Edited in the isolated Seafile test.` in the editor. This verifies
semantic reopen, not only byte equality.

## Stale session and simultaneous conditional saves

Two WordCraft sessions opened the same version. Session A saved its edit first
and received HTTP 200. The older session B then attempted to save and received
HTTP 409; it remained dirty and did not report success. Seafile retained A's
change and did not contain B's stale edit.

A separate simultaneous request test then submitted two different synthetic
DOCX payloads through the actual patched Seahub `file-save` view, with the same
expected repository head and file ID. The requests were launched concurrently
from Chromium using one fresh synthetic capability:

| Request | Result |
| --- | --- |
| Writer A | HTTP 200; file ID `300ef732afd98164eb13d6fc4a6c07fd45c13b41`; new head `e9374207099bfc512e66bd7d2f2bb0889a29686a` |
| Writer B | HTTP 409; `file changed; reopen it` |
| Current file history | four entries; newest head is Writer A's head |

After the race, the file was opened again through the Seahub route in a fresh
WordCraft page. WordCraft rendered `Concurrent writer A`; the competing
`Concurrent writer B` paragraph was absent. The screenshot is
[`concurrent-save-reopen.png`](concurrent-save-reopen.png).

This first race is a real concurrent HTTP save race against the patched local
Seahub and C fileserver. The race's two writes were direct synthetic calls to
the same Seahub save endpoint.

### Concurrent saves from two real WordCraft sessions

After the direct request test, two separate Chromium tabs opened the same
current DOCX through the synthetic Seahub file route. Each real WordCraft editor
received a different text edit and showed its dirty state. Ctrl+S was sent to
both tabs concurrently.

| Session | Result |
| --- | --- |
| Editor A | Host showed `Saved — new version f540086f76da398bea7fbdaefadb861eafc515dd`; file ID changed to `0deaba676f0e4f30df28dbb7708c2264f9864cbb`; editor became clean |
| Editor B | Host showed `Unsaved changes`; save returned HTTP 409 conflict; editor remained dirty |

A new click from the Seahub file list opened a fresh WordCraft session. After
the WASM editor finished rendering, it showed `Concurrent editor session A`.
The current Seafile file-info and file-content endpoints reported the same new
head and file ID; the retrieved DOCX was 5,340 bytes, its `word/document.xml`
contained session A and the earlier committed content, and it did not contain
session B. The screenshot is
[`concurrent-editor-save-reopen.png`](concurrent-editor-save-reopen.png).

This reproduces two real editor saves competing through the host bridge and
patched local Seahub/C fileserver; one committed, the other stayed dirty, and a
fresh editor reopen rendered the winning change. It does not test the Go
fileserver, stock fileserver rejection, crash/network windows, permission
revocation, or external writers.

### Separate Seahub and gateway origins

After the two-editor race, the synthetic Seahub setting was temporarily changed
to `ARTCRAFT_ACTION_URL = "http://127.0.0.1:18777/open/"`; the gateway was
already configured to accept `/open/` only from Seahub's `http://127.0.0.1:18000`
origin. Only the synthetic Seahub process/configuration was changed, then the
original setting `/open/` was restored and Seahub restarted. No repository file,
production service, or upstream artifact was changed.

Opening the synthetic DOCX through Seahub loaded the handoff form with the
gateway's `:18777/open/` action and targeted Seahub's `office_frame`. The frame
was cross-origin from Seahub (`:18000` vs `:18777`); Chromium blocked direct
document access across that boundary. The gateway served the real
WordCraft Web/WASM app and its document-read endpoint returned HTTP 200. A
keyboard edit added `OriginCheck`; Ctrl+S reached the patched
`thirdparty-editor/file-save` path and returned HTTP 200. Readback from
Seafile's user-bound file-content endpoint showed a new file ID
`c5e9d4e4651ac4bbd4afb8c75962ff462bf5c251`, repository head
`ce2bcd90b3684448251d1ef7145a9c356bc9b6d3`, and a six-entry file history.

The file-view route was reloaded to mint a fresh handoff and reopen the saved
DOCX. The subsequent Seafile readback returned HTTP 200 and 5,351 bytes; the
DOCX `word/document.xml` contained `OriginCheck` and the earlier committed
`Concurrent editor session A`, while `Concurrent editor session B` remained
absent. This verifies separate-origin handoff, durable save, and persisted
content after a fresh route load. The editor's visible clean/save-confirmation
indicator was **not captured in this follow-up** because the preview snapshot
timed out on the canvas-heavy tab; the earlier same-origin run did observe it.
This test does not establish production origin isolation through a reverse
proxy, TLS, CSP, CSRF, or credential non-access from an adversarial Craft build.

### Follow-up: host confirmation and another Seafile readback

After the separate-origin save, a fresh gateway `/open/` session loaded the
current DOCX. A second synthetic edit (`AckConfirmed`) followed by Ctrl+S
changed the host status to `Saved — new version dd23f47ae94d0f74657b9eeda0e9b7924c8b8d52`;
the host exposed `dirty=false`, `confirmedSave=true`, and
`saveConfirmationPending=false`. The editor canvas was not captured, so this is
the host's protocol acknowledgement, not a visual screenshot. A fresh Seafile
file-view request then loaded WordCraft and its document endpoint returned a
valid DOCX whose `word/document.xml` contained `AckConfirmed`, `OriginCheck`,
and the winning concurrent edit, and omitted the losing edit. This closes the
earlier gap for a visible host confirmation and a subsequent Seafile content
readback, but it does **not** capture that confirmation inside the cross-origin
Seahub iframe itself; production-proxy behavior remains unverified.

The UI readback used the host document endpoint after the gateway returned
success. The XML check establishes persisted semantic content. The follow-up
fresh WordCraft route loaded that same response, but the canvas-heavy editor did
not provide a capturable visual proof in this session.

## Conditional-route token check

Using the patched fileserver's actual HTTP listener and tokens minted by its
Seafile RPC service:

* an `op=update` token on `update-conditional-api` passed the existing
  `upload_headers_cb` / `check_access_token` operation-prefix check and reached
  the conditional handler; a deliberately incomplete upload then received the
  handler's HTTP 400 `No target file.` response;
* an `op=view` token on the same route was rejected by the existing hook with
  HTTP 403 `Operation does not match access token.`

This verifies the narrow route-name/header-hook correction at runtime without
weakening token operation checks. The incomplete-request 400 is not a document
save; the successful DOCX save above is the evidence for that.

## ONLYOFFICE dispatch guard

The synthetic stack has no ONLYOFFICE Document Server. To test the routing
boundary without configuring the live service, `tests/test_gr015_dispatch.py`
executes the patched Seahub `view_lib_file` handler in its Django runtime. With
the storage API and ONLYOFFICE response builder replaced by synthetic doubles,
it asserts that an allow-listed DOCX selects the ArtCraft handoff template and
the same DOCX in a non-allow-listed library falls through to
`onlyoffice_file_view_react.html`. This verifies the new per-library branch
does not shadow Seahub's existing ONLYOFFICE route. It does **not** load
Document Server or test ONLYOFFICE edit/save/version/reopen; that compatibility
check remains open.

Reproduction in the pinned runtime container:

```sh
podman cp tests/test_gr015_dispatch.py artcraft-seafile-dev:/tmp/test_gr015_dispatch.py
podman exec artcraft-seafile-dev sh -lc 'PYTHONPATH=/usr/local/lib/python3.10/site-packages:/work/src/seafile-server/python:/work/src/seahub:/work/src/seahub/thirdpart SEAFILE_CENTRAL_CONF_DIR=/work/test-config SEAFILE_CONF_DIR=/work/test-data SEAFILE_DATA_DIR=/work/test-data CCNET_CONF_DIR=/work/test-config DJANGO_SETTINGS_MODULE=seahub.settings python3 /tmp/test_gr015_dispatch.py'
```

## Limits still open

| Area | Status |
| --- | --- |
| Mandatory synthetic DOCX open/edit/save/version/close/reopen | **REPRODUCED** in this isolated local stack |
| Stale session and overlapping save conflict | **REPRODUCED**; one writer commits and stale writer is refused |
| Permission revocation, read-only bypass, expired/replayed capability | **NOT VERIFIED** end to end |
| Unsupported stock C or Go fileserver fails closed | Source route absence is known; runtime deployment test **NOT RUN** |
| ONLYOFFICE edit/save/version/reopen regression | **NOT RUN**; ONLYOFFICE was not configured in the scratch stack |
| Separate Seahub/gateway origins and cross-origin handoff | **REPRODUCED** on distinct loopback ports; a fresh gateway session showed the host save acknowledgement and a following Seafile readback retained the edit. The acknowledgement was not captured inside the cross-origin Seahub iframe. Production TLS/proxy/CSP/CSRF and adversarial-frame testing remain **NOT VERIFIED** |
| Production Seafile / LAN / Tailscale | **NOT TESTED or changed** |
| GridCraft, VectorCraft, DeckCraft, PdfCraft | **NOT covered by this DOCX evidence** |
| Upstream RFC/patch or publication | **NOT READY; locked** |

## Local checks reproduced on 2026-10-23

Repository SHA during the two-editor race: `a4ecc8e1d0da44a12f7bd9c4e529ed4accdb4a0e`. The separate-origin follow-up was exercised against the same committed application at local tip `e513c6ae8f076f5abc07bb5f9634a7c6975cba5b`; its only temporary change was the mounted synthetic Seahub setting described above.
The patched Seafile runtime was the rootless `artcraft-seafile-dev` container;
the exact patch artifacts passed reverse-application checks against its source
trees. The system Python is 3.14.8; browser checks used an ephemeral Python
3.13.16 environment at `/tmp/artcraft-review-pw` with Playwright 1.64.1 and the
already installed Chromium build. No dependency was added to the repository.

| Command | Exit | What it establishes |
| --- | ---: | --- |
| `python3 tests/test_gateway_unit.py` | 0 | Gateway unit checks, including fake CAS, permission handling and error redaction; upstream is simulated |
| `/tmp/artcraft-review-pw/bin/python tests/test_hostpage_protocol.py` | 0 | Synthetic save acknowledgement, dirty state, overlapping-ticket refusal and retry protocol |
| `/tmp/artcraft-review-pw/bin/python tests/test_wordcraft_host_roundtrip.py` | 0 | Real WordCraft Web edit/serialize/ack/reopen against in-memory storage; not Seafile persistence |
| `/tmp/artcraft-review-pw/bin/python tests/test_vectorcraft_svg_local.py` | 0 | Local VectorCraft editor semantics; not gateway or Seafile persistence |
| `tests/test_gr015_dispatch.py` in `artcraft-seafile-dev` | 0 | Patched Django view selects ArtCraft for allow-listed DOCX and preserves the ONLYOFFICE template fallback elsewhere; test doubles do not exercise Document Server |
| `python3 tests/test_gr012_svg_assertions.py` | 0 | SVG false-positive guards |
| `python3 tests/test_xlsx_fixture.py` | 0 | Formula fixture includes an OOXML `<f>` element and cached value |
| `ARTCRAFT_SEAHUB_SOURCE=/tmp/artcraft-seafile-dev/src/seahub ARTCRAFT_SEAFILE_SERVER_SOURCE=/tmp/artcraft-seafile-dev/src/seafile-server python3 tests/test_gr015_authorization.py` | 0 | Exact patched helper/decorator checks with synthetic dependencies; not Django authorization runtime |
| `python3 -m compileall -q integration tests` | 0 | Python syntax compilation |
| `git -C /tmp/artcraft-seafile-dev/src/seahub apply --reverse --check /home/roddy/Projects/artcraft-storage-lab/docs/reviews/GR-015/seahub-12.0.14.patch` | 0 | The recorded Seahub patch is present in the running source tree |
| `git -C /tmp/artcraft-seafile-dev/src/seafile-server apply --reverse --check /home/roddy/Projects/artcraft-storage-lab/docs/reviews/GR-015/seafile-server-12.0.14.patch` | 0 | The recorded fileserver patch is present in the running source tree |
| `/tmp/artcraft-review-pw/bin/python tests/test_gr012_svg.py` | 2 | Not run: requires a Seafile API token, gateway URL, repo ID and file path |
| `python3 tests/test_integration.py` | 2 | Not run: requires a synthetic Seafile API token, repo ID and file path |
| Manual Chromium test on separate loopback origins, 2026-10-23 | — | Seahub file route → gateway `/open/` on `:18777` → real WordCraft edit/Ctrl+S → Seafile file ID/head/history/content readback → route reload and content readback; no production data |

## Verdict boundary

This evidence removes “no real Seafile DOCX E2E” as an accurate description of
the local GR-015 remediation. It does not resolve the remaining Sol findings,
retroactively change the verdict on `0edbe52`, or qualify the current tip as a
GPT candidate. The current tip remains unreviewed; keep the overall GPT state
at **FAIL** until a new exact candidate receives an independent final review.
