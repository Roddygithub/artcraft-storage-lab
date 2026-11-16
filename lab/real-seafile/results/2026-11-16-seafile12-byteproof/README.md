# Seafile CE12 replay with byte-level proof for all three formats

Third run of the CE12 chain on the pinned Seafile CE 12.0.14 image
(`sha256:7bbe7043…`), synthetic accounts and synthetic files, isolated
rootless Podman, loopback only. The owner server and its data/configuration
were not used. It supersedes
[`2026-11-15-seafile12-detail`](../2026-11-15-seafile12-detail/), which is the
superseded replay documented in
[`CE12-REVIEW-5FE30C6.md`](../../../../docs/reviews/PROJECT-CLOSURE-20261115/CE12-REVIEW-5FE30C6.md).

## What this run adds over the previous one

1. **GridCraft XLSX bytes are now retained** — `gridcraft-original.xlsx`,
   `gridcraft-first-relay.xlsx`, `gridcraft-first-readback.xlsx` and
   `gridcraft-second-readback.xlsx`. The byte-level claim that was previously
   assertion-only for XLSX is now mechanically checkable: the verifier proves
   `first-relay == first-readback` and `original != first-readback`, exactly
   as DOCX and PPTX already were.
2. **Fresh sessions prove the new context.** Every fresh-session assertion
   records `new_browser_context=True url_has_login_redirect=False`; the
   runner creates a real `browser.new_context(...)` and logs in again before
   reopening from the Seafile file list.

## Browser results

| Editor / format | Assertions | Result |
| --- | ---: | --- |
| WordCraft / DOCX | 24/24 | PASS |
| GridCraft / XLSX | 27/27 | PASS |
| DeckCraft / PPTX | 15/15 | PASS |
| **Total** | **66/66** | **PASS** |

## The proof, as retained

[`verify.py`](verify.py) rejects bare booleans and requires:

| Claim | Retained detail (all three editors) |
| --- | --- |
| Save creates a new Seafile version, attributed to the opener | `history 1->2 grew=True creator_is_opener=True` (second saves: `history 2->3 …`) |
| Reopen in a fresh session | `new_browser_context=True url_has_login_redirect=False` |
| Reopen / open from the Seafile file list | `url_has_login_redirect=False` |
| Readback equals the saved bytes | byte equality for DOCX, XLSX and PPTX; `len` details in the JSON |

The full observed chain per editor: open from the file list → real typed
edit → dirty state visible → save through the bridge → Seafile version
incremented with the opener as creator → readback byte-identical → new
browser context, new login, reopen from the file list → saved bytes loaded →
both edits visible → second save → second version. Screenshots retain the
opened/typed/saved/reopened states.

`SHA256SUMS` pins all 31 retained files; `static-sha256.json` is the exact
extracted editor tree manifest (167 entries: WordCraft v0.13.2, GridCraft
v0.14.2, DeckCraft v0.16.0). The run used the launcher
(`launcher_sha256` in `provenance.json`) and the runner as pinned below.

Run the check from this directory:

```sh
python3 verify.py
sha256sum -c SHA256SUMS
```

## Limits

Synthetic sequential flows on the pinned isolated CE12 image only. It does
not establish broad Office fidelity, legacy-format support, hardware
acceptance, owner-server access, host-enforced read-only permissions (see
[`docs/security/HOST_PERMISSION_BOUNDARY.md`](../../../../docs/security/HOST_PERMISSION_BOUNDARY.md)),
or concurrent-writer safety. The known non-atomic WOPI save window remains.
Six DeckCraft assertions still record no detail; their substance is retained
elsewhere (byte equality, screenshots).
