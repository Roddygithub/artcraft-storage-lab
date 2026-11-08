# Unpublished draft: mixed WOPI / ONLYOFFICE error propagation

**Not submitted. Upstream LOCKED. No host patch applied.**

## Observed scope

Packaged Seafile CE / Seahub 13.0.28, with WOPI enabled for Craft formats and
ONLYOFFICE enabled for ODT/PPTX outside those WOPI extension tuples.

The normal authenticated file-list route prepares WOPI even when the extension
has no WOPI action. WOPI returns no configuration; the view sets a shared error.
ONLYOFFICE preparation can then succeed, but its rendered page still receives
that error. Its React view displays the error instead of mounting the editor.
APIJS appearing in the HTML therefore does not establish a working editor.

## Source locations in the packaged version

| Location | Behavior |
| --- | --- |
| `seahub/views/file.py:824–845` | WOPI preparation guarded only by enable flag, not extension; sets shared error |
| `seahub/views/file.py:847–878` | Successful ONLYOFFICE configuration merged with shared error |
| `seahub/wopi/utils.py:73–74` | Missing/invalid action returns no WOPI config before network access |
| `frontend/src/view-file-onlyoffice.js:49–50` | Nonempty error renders error view |

Parent observed blocking errors in both ODT and PPTX HTML from the new
synthetic combined run. The independent review verified the local packaged
source path; it did not replay the browser. Production was not accessed.

## Reproduction outline

1. Fresh disposable CE 13.0.28 lab with synthetic documents only.
2. Configure the standard WOPI and ONLYOFFICE settings with disjoint formats.
3. Click an ONLYOFFICE ODT/PPTX file in the normal authenticated library list.
4. Inspect the visible error and the generated page's nonempty `err` field.
5. Compare an isolated ONLYOFFICE-only disposable lab; that comparison is not
   proof that the combined deployment preserves ONLYOFFICE.

Private logs/pages contain tokens and must not accompany a future report.
`run_slice.py` now rejects an APIJS-bearing page with nonempty/missing error
metadata. The dedicated ONLYOFFICE browser test additionally requires genuine
edits, new attributed revisions, current-body readback and final fresh-editor
searches. No direct edited-byte upload or forced-save API is accepted.

## Resolution requirement

A compatible unmodified host or a verified native configuration is required
by this project's zero-patch and never-break-ONLYOFFICE rules. Guarding WOPI
preparation by extension and avoiding inherited errors on a successful fallback
are possible upstream investigation directions, not an applied local patch.
Multiple-suite selection is per-library and its normal selection API is
Pro-gated; it is not a verified CE per-extension workaround.

Any future submission requires project GPT PASS and separate owner approval.
