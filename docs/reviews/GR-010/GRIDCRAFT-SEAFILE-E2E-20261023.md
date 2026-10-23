# GR-010 — GridCraft ↔ Seafile synthetic runtime E2E

Date: 2026-10-23
Gateway/repository revision: `e6c559e7d7ea6e207f9d539f996eade4f1dc6334`
Editor: patched GridCraft Web built from the pinned GR-010 source patch targeting
`06920de8da609c19de7446945cfc62b844691efd`
Environment: isolated local synthetic Seafile/Seahub + gateway stack; not the
user's production Seafile.

## Result

**The GridCraft `.xlsx` open → edit → save → new Seafile version → reopen path
was reproduced in a real browser against the isolated Seafile stack.** This is
runtime evidence for this GridCraft path only. It does not complete GR-010 or
the broader all-ArtCraft / multi-platform project, and does not change the
existing GPT-6.1 Sol FAIL or upstream lock.

## Reproduced flow

1. Opened the synthetic library's Seahub file list and clicked `synthetic.xlsx`.
   The configured dispatcher opened `/artcraft/gridcraft/?host=parent`; the
   GridCraft Web JavaScript and WASM assets loaded and fetched the document via
   the host session.
2. Edited cell A3 in the real GridCraft Web app to
   `GridCraftSeafileRoundTrip`. The app reported unsaved changes.
3. Pressed Ctrl+S in GridCraft. The host sent the serialized bytes through its
   Seafile save route. Seahub returned success only after the patched fileserver
   save response supplied `file_id` and `head_commit_id`; the host displayed
   `Stored — new version …` and GridCraft returned to a clean workbook state.
4. Read the file back through the host session's document endpoint. The bytes
   formed an intact XLSX ZIP package. `xl/worksheets/sheet1.xml` contained an
   A3 shared-string reference resolving to `GridCraftSeafileRoundTrip`, and B3
   retained `<f>SUM(B2:B2)</f>` with cached value `42`.
5. Navigated away, clicked `synthetic.xlsx` again in Seahub, and opened a fresh
   GridCraft session. The reloaded editor displayed the edited cell; selecting
   A3 showed the complete marker in the formula bar. Screenshot:
   `gridcraft-seafile-reopen.png`.

## Captured evidence

| Evidence | Result |
| --- | --- |
| Initial fixture SHA-256 used for this run | `0235e662d1bd05fc46742ba5d7dbb368e9d209a3168199c5634a4ccb7bea1614` |
| Seafile readback size | 4,165 bytes |
| Seafile readback SHA-256 | `c12da8825f28e04ae7fddc8120b52cf3d28e1c9fc43634d9598d7583c26e15a2` |
| Saved file content ID from detail response | `f8722c5500121624c87c37e1e47d84ce2ac7e3da` |
| Host's committed revision acknowledgement | `bf8fbe332be22934a99da4d4f1028484d417c6ae` |
| XLSX integrity | ZIP CRC check passed; A3 marker and B3 formula/cached value parsed from readback |
| Fresh editor open | New Seahub click created a fresh GridCraft session; edited cell rendered |

The before/after byte hashes differ. The save response contained a committed
head revision and file ID, and the fetched content was the serialized workbook.
The Seafile history API was not independently verified in this run: the direct
browser request returned HTTP 403 because that route did not accept the current
browser session credentials. No claim of a queried history-list count is made.

## Limits

- Synthetic local stack only. Production Seafile, Tailscale/LAN deployment,
  external proxy/TLS, CSP, CSRF and rate limits were not exercised here.
- No permission revocation/read-only, expired-session, network-loss, retry, or
  external-writer race test was part of this GridCraft run.
- The fixture's formula XML and cached result survived serialization and
  appeared in the reopened sheet. Formula recalculation after changing an input
  was not tested.
- Concurrent editor conflict behavior and per-ticket overlapping saves were
  not tested for GridCraft in this run.
- This path does not validate WordCraft, VectorCraft, DeckCraft, PdfCraft,
  other Craft apps, or Nextcloud/ownCloud adapters.

## Follow-up found during runtime

The original synthetic XLSX fixture omitted `xl/styles.xml`; GridCraft displayed
a missing-styles warning on first open. The fixture generator and its check now
include a minimal OOXML styles part and workbook relationship. The E2E run above
used the original fixture (hash recorded above). After that correction, the
regenerated fixture was uploaded as `synthetic-styled.xlsx` to the synthetic
library and opened from the Seahub list in a new GridCraft session. It loaded
without a missing-styles warning; screenshot: `gridcraft-styled-fixture-open.png`.
The corrected fixture has not yet repeated the edit/save/reopen sequence.
After the browser checks, the isolated Seahub settings and Nginx proxy config
were restored from their pre-test backups; the synthetic Seahub login endpoint
returned HTTP 200 afterward. Production Seafile was not touched.
