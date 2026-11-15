# ArtCraft desktop acceptance checklist — NOT RUN

Run only against an HTTPS deployment of the current stateless WOPI bridge and
the synthetic Seafile library. The owner's live Seafile is 12.0.14; its current
WOPI bridge is disabled and a pre-existing legacy route is not this candidate.
This checklist does not authorize changing that server. Use Chrome or Edge and
Firefox where available. Do not use personal documents.

## Record before testing

- Date/time and tester:
- OS/device and display scale:
- Browser name/version:
- GPU and WebGPU availability:
- Editor bundle SHA-256:
- Synthetic file and expected markers/reference image:

## Checks

Mark each `PASS`, `FAIL` or `NOT RUN`. Attach screenshots or a short recording
for failures and visual comparisons; include the Seafile version history where
the check expects a save.

| Check | Expected result | Status / observation |
| --- | --- | --- |
| HTTPS open | Synthetic DOCX opens in WordCraft inside Seafile; filename and `ready` appear; no CSP/frame error | NOT RUN |
| GPU and stability | WebGPU is selected; no crash, blank canvas or editor reset during a 15-minute edit session | NOT RUN |
| Rendering and fonts | Known text, styles, lists and table match the reference; exact fonts or fallback are recorded; do not accept a merely non-empty canvas | NOT RUN |
| Clipboard | Copy/paste within the editor and between editor and another desktop app preserves text | NOT RUN |
| Popup/window behavior | Any expected new window opens; blocked/unexpected popups and focus loss are recorded | NOT RUN |
| Save and reopen | Type a unique marker; host shows dirty then saved; Seafile creates a version; a fresh session shows the marker | NOT RUN |
| Dirty close | With a new unsaved marker, close prompts; Stay preserves dirty state; Leave discards only that unsaved edit; reopen confirms persisted version | NOT RUN |
| Refused save | With the synthetic read-only route, Save is refused and dirty state remains; Seafile version count/content does not change | NOT RUN |
| Concurrent session | Save a change in a second tab; first tab reports version conflict and does not silently clear dirty state | NOT RUN |
| Network interruption | Disconnect network after editing; save failure keeps dirty state; after restore, retry succeeds once and fresh reopen preserves the marker | NOT RUN |
| Session expiry | After the WOPI token expires, save reports expiry; reopening starts a usable session | NOT RUN |

## Limits to keep with the results

- A refused save through the bridge does not prove Seafile host-side
  authorization. CE 13.0.28 accepted direct `PutFile` with a read-only token;
  keep this test isolated and synthetic.
- The save path has a documented non-atomic version-check/PutFile window.
  Sequential success does not prove concurrent-writer safety.
- Physical acceptance on one machine does not prove broad font or document
  fidelity. Keep the tested file, browser, GPU and bundle SHA with the result.
