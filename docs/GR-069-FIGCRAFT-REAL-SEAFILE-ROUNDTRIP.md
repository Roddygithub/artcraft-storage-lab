# GR-069 — FigCraft real synthetic Seafile roundtrip

## Result

The exact optimized GR-048 FigCraft Web candidate opened a native `.figcraft`
document from the existing synthetic Seafile library. A visible rectangle was
created through FigCraft’s UI, the editor submitted a host save, Seafile
returned a new head/version identifier, and a fresh Seafile file-list open
rendered the rectangle again.

This is a bounded real-Seafile result for one synthetic file and one candidate.
It does not establish general FigCraft compatibility, production readiness, or
the project-level GPT verdict. The project remains **INCOMPLETE** and upstream
publication remains **LOCKED**.

## Candidate and scope

| Item | Value |
|---|---|
| Source | `storytold/figcraft`, commit `8d790607ff1ad40e32343ca2116d8fdcf3244c8d` |
| Host-save patch | GR-019 exact patch, SHA-256 `954850ba5aff7362e776b2331a5a5ff54bf9d71374d7b29bc856c2b7a47c4798` |
| Shared transport | `craft-platform` revision `56c5e16d79b77751106173c13111ef4fe0a2c0ec` |
| Candidate | Existing optimized GR-048 WASM build; no rebuild for this run |
| Served files | `index.html`, hashed JavaScript, hashed WASM; 23,650,333 bytes total |
| Fixture | `GR-069-synthetic.figcraft`, 268 bytes; SHA-256 `899204d7ab596e9efd9d86df7935474ef15df0bc2cbb80a8798ad8ce102b3d8a` |
| Target | The existing `ArtCraft GPT Review Synthetic` library only |

Candidate paths, file sizes and hashes are recorded in
[`candidate-inventory.json`](reviews/GR-069/candidate-inventory.json). Run
`python3 docs/reviews/GR-069/verify_candidate.py` to compare the build cache,
staged candidate and active static-root files.

## Runtime observations

1. The 268-byte fixture was uploaded through Seafile’s file picker as test
   setup. This was not an upload of edited output.
2. The fixture was opened by clicking it in the Seafile library. The T3 preview
   did not retain Seahub’s popup, so a test-only `window.open` shim redirected
   only this fixture’s popup into the same tab. The file route then submitted
   the normal `/open/` request; the FigCraft index, JS and WASM each returned
   HTTP 200.
3. The first editing session reached a 502 because the local gateway process
   had exited. Its editor save was not acknowledged. That unsaved rectangle was
   discarded after navigating away; it is not counted as a save.
4. After restarting the gateway and reopening the fixture from the library,
   the rectangle tool created a visible 100×100 rectangle. FigCraft reported
   unsaved changes. Ctrl+S submitted one save; the gateway returned HTTP 200,
   the host displayed `Saved to Seafile` and `Saved — new version`, and the
   editor returned to a clean state. The returned Seafile head identifier is
   `492a142d2afc76458f2d68eb0d9710cdf72413b4`.
5. The successful editor was exited by navigating to the Seafile library, not
   by an observed in-app close. Clicking the file again created a distinct
   open/document session. The fresh editor showed the rectangle and the
   `GR-069-synthetic.figcraft opened` status.

The retained [save screenshot](reviews/GR-069/runtime/save-confirmation.png)
shows the rectangle, Seafile save confirmation, new-version identifier and
clean status. The [fresh-reopen screenshot](reviews/GR-069/runtime/fresh-reopen.png)
shows the rectangle in the reopened editor. A sanitized chronology is in
[`browser-observations.txt`](reviews/GR-069/runtime/browser-observations.txt).

## Cleanup and remaining limits

- The temporary `.figcraft` Seahub allowlist entry was removed. The restored
  `seahub_settings.py` bytes match the private pre-test backup SHA-256
  `38162e03aef79c048e5a9334e2fd70ae04ca145b62703027f9caddacb0f69741`;
  `ENABLE_ONLYOFFICE=True` was verified. Seahub is active. The restored file is
  owned by `seafile:seafile` with mode `0600` so the service can read it.
- The local test-gateway dispatch was restored byte-for-byte to its private
  pre-test backup SHA-256 `af3c4cbbb76f3583b0bb70118c48ebd7445bc2841e577658918edd7c43f83c2d`;
  no FigCraft dispatch entry remains. The local gateway process was stopped.
- Candidate files remain in the local static root but have no dispatcher route.
- No edited output was downloaded or manually uploaded. The setup fixture upload
  is explicitly excluded from the save claim.
- No separate export of the save message or Seafile readback bytes was hashed;
  exact editor-to-Seafile byte identity is **NOT VERIFIED**.
- A separate Seafile history-page capture was not retained; version evidence is
  the successful host/gateway response with the returned head identifier and
  the subsequent fresh file-list reopen.
- Explicit in-app close, a post-change ONLYOFFICE edit/save regression, other
  browsers, cross-origin deployment and production security are **NOT VERIFIED**.
- The Seafile library’s PDF thumbnail requests returned HTTP 500 during the
  library view. This unrelated thumbnail issue was not investigated.

Independent R1 returned a bounded **PROVISIONAL PASS** with no findings. The
review verified the candidate inventory and retained artifacts read-only; it
did not replay the browser or independently verify live HTTP chronology,
service state, or cleanup. This evidence does not authorize an upstream issue,
PR or RFC.
