# GR-012 — VectorCraft SVG Seafile runtime evidence

Date: 2026-10-23  
Scope: isolated synthetic Seafile only; no production service or user document.  
Result: **runtime round-trip reproduced for VectorCraft SVG**. This does not
prove the common `?host=parent` contract or support in every Craft app.

## Environment and input

| Item | Value |
| --- | --- |
| Seafile | isolated `artcraft-seafile-dev` container, Seahub at `127.0.0.1:18000` |
| Synthetic library ID | `6862763d-721f-498a-bbf0-d666cee97496` |
| Path | `/artcraft-vectorcraft-upload/synthetic.svg` |
| Editor | pinned VectorCraft Web v0.14.0 bundle; checksum verified against its release `SHA256SUMS.txt` |
| Initial bytes | 270 |
| Initial SHA-256 | `ff75662e35837299fe34eb26e9eaf03974b49edc1c836781b82a225e63d7c760` |
| Initial Seafile content ID | `b8f7677f8fd13be56db63537a6cd922abae1471b` |

The SVG was uploaded to a synthetic library through Seahub's browser UI. The
file was then opened by clicking its row in the Seahub file list; the browser
loaded the Seafile viewer and the dispatched VectorCraft editor. This was not a
direct gateway `/open/` test.

## Edit, durable save, and reopen

In the real VectorCraft Web editor, the deterministic `window.vectorcraft` page
API selected the pencil tool and sent pointer events in document coordinates
(60,60) → (120,90) → (180,120). The editor's own `app.save` serialized the
modified SVG. The editor snapshot showed the new path with bounds x=60, y=60,
w=120, h=60.

| Check | Observed evidence |
| --- | --- |
| Editor output | 609 bytes; SHA-256 `fad9b3e60c2e76e29214dccdd6edfeb00b5edc9be605aaefddaed8372d3497f2` |
| Host save result | `Saved — new version f73cd1dbd6b00b029f34ff27084a0d3e2fba0b93` |
| Seafile metadata | content ID changed to `fd8fd133431c39b4b248a9352f108854275171a9` |
| Readback | fresh gateway document read returned HTTP 200, 609 bytes, and the same SHA-256 as VectorCraft output |
| Seafile History UI | current version at 2026-10-23 17:10:14, 609 B; previous version at 17:07:02, 270 B |
| Reopen | clicked the file again from the Seahub list; a fresh VectorCraft session parsed the SVG and its inspect snapshot showed the new path at x=60, y=60, w=120, h=60 |

This is evidence of an editor-produced edit, changed bytes, a committed Seafile
version, exact byte readback, and a fresh editor reopen that parsed the saved
path. The Seafile History page, not the history API, supplied the two-version
listing; a separate history API request returned 403 and is not used as proof.

## Limits

- The run used VectorCraft's own page API because VectorCraft does not implement
  the shared `?host=parent` bridge. The file was opened and saved through the
  host adapter, but this does **not** demonstrate that the common host contract
  works for non-Office editors.
- This was a browser-driven manual reproduction using the editor API, not an
  execution of `tests/test_gr012_svg.py`; that harness requires access-token
  environment variables unavailable to this session.
- VectorCraft has no dirty signal or save event. The host polls the saved-file
  API; this run proves this successful save only, not unsaved-edit warnings,
  failure retry behavior, concurrent saves, or unload safety.
- A later source review found that the then-current poll used a 32-bit content
  fingerprint, which could collide. The current working-tree remediation uses
  exact byte comparison and has a synthetic Chromium regression test using a
  deterministic collision pair. The historical runtime run above predates that
  change; the actual VectorCraft/Seafile flow has not yet been rerun afterward.
- PDF/PdfCraft and all other Craft apps are outside this evidence.
- The temporary upload proxy and SVG dispatch settings were restored in the
  isolated container after the run. Seahub login returned HTTP 200 after
  restoration. Production Seafile and ONLYOFFICE were not changed.

## Reproduction record

The browser session was attached to `artcraft-seafile-dev`. The sequence was:

1. Upload `tests/fixtures/synthetic.svg` through the synthetic Seahub UI.
2. Click `synthetic.svg` in the Seafile file list and verify VectorCraft loaded.
3. Record the document and Seafile metadata before editing.
4. Use VectorCraft's documented page API to draw with the pencil tool and call
   the editor's SVG save API.
5. Verify the host's new-version acknowledgement, changed Seafile content ID,
   exact readback hash, and History UI entry.
6. Return to the folder, click the file again, and verify the path in a fresh
   VectorCraft inspect snapshot.

