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
| Network | Test-only Nginx proxy; browser-facing endpoints were bound to host loopback. Seahub, gateway, and Craft were merged onto one local origin because the collaborative browser could not reach a second loopback port. This does **not** verify the intended separate-origin production topology or its security properties. |
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

This is a real concurrent HTTP save race against the patched local Seahub and C
fileserver. The race's two writes were direct synthetic calls to the same
Seahub save endpoint, not two simultaneous keystroke-driven WordCraft saves.
It does not test the Go fileserver, stock fileserver rejection, all crash/network
windows, permission revocation, or external writers.

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

## Limits still open

| Area | Status |
| --- | --- |
| Mandatory synthetic DOCX open/edit/save/version/close/reopen | **REPRODUCED** in this isolated local stack |
| Stale session and overlapping save conflict | **REPRODUCED**; one writer commits and stale writer is refused |
| Permission revocation, read-only bypass, expired/replayed capability | **NOT VERIFIED** end to end |
| Unsupported stock C or Go fileserver fails closed | Source route absence is known; runtime deployment test **NOT RUN** |
| ONLYOFFICE edit/save/version/reopen regression | **NOT RUN**; ONLYOFFICE was not configured in the scratch stack |
| Separate Seahub/gateway/Craft origins, TLS, CSP, CSRF, rate limits, proxy trust | **NOT VERIFIED**; the browser test used a same-origin local proxy |
| Production Seafile / LAN / Tailscale | **NOT TESTED or changed** |
| GridCraft, VectorCraft, DeckCraft, PdfCraft | **NOT covered by this DOCX evidence** |
| Upstream RFC/patch or publication | **NOT READY; locked** |

## Verdict boundary

This evidence removes “no real Seafile DOCX E2E” as an accurate description of
the local GR-015 remediation. It does not resolve the remaining Sol findings,
retroactively change the verdict on `0edbe52`, or qualify the current tip as a
GPT candidate. The current tip remains unreviewed; keep the overall GPT state
at **FAIL** until a new exact candidate receives an independent final review.
