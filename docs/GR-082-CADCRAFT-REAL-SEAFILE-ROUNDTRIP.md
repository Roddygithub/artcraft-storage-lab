# GR-082 — CADCraft real edit on synthetic Seafile

**Runtime result: PASS, bounded to this isolated synthetic run.** Independent
evidence review is pending. This is neither project GPT approval nor upstream
authorization. Project status remains **INCOMPLETE**; upstream remains
**LOCKED**.

## Result

On 2026-11-03, the direct parent run used a fresh, rootless Podman lab with
Seafile CE 13.0.28 and the released, unpatched CADCraft Web v0.15.1 bundle.
The candidate typed `CIRCLE`, center `5,5`, radius `3` into the editor after
opening `test.dxf` from the Seafile file list. The initial fixture had no
circle. The drawing showed the new circle and the host reported unsaved
changes before save. Save produced a user-attributed Seafile version and the
host displayed “saved to Seafile”. The saved DXF readback contained the circle;
the relay save bytes and Seafile readback were byte-identical. A new browser
context reopened the file from the Seafile list, read the same saved bytes, and
rendered the circle. The editor save did not trigger a browser download.

The same browser slice continued into DeckCraft after the CADCraft flow and
completed its existing native-document save/reopen assertions. The full
sequential browser harness passed **95/95** assertions, including **18/18**
CADCraft checks. The HTTP slice passed **48/48** checks.

## Candidate and review history

The changed browser harness and new focused regression are
`lab/real-seafile/run_browser.py` and `tests/test_cadcraft_real_edit.py`.
The first isolated browser attempt passed 89/95 checks; six CADCraft assertions
failed. Its diagnostics exposed DXF group-code padding and geometry outside the
initial fixture's view. The parser now handles the editor's padded DXF, and
the typed circle is placed within the original drawing extents. The passing
result is from a separate fresh synthetic stack and database (`runtime-r3`);
the failed attempt remains private and is not represented as passing evidence.

The independent source review initially requested changes. R2 passed for
proceeding to a synthetic run while noting a low-severity gap between some
test descriptions and committed unit coverage. R3 and R4 passed the source
remediations; R4 checked the exact source hash used by the successful run. The
Independent evidence R1 found no P1/P2 issue and one P3 count error. R2 found a
remaining stale count in HISTORY.md. Both have been corrected. R3 confirmed
the counts and evidence bundle with no current P1–P3 findings; its review did
not replay the runtime.

This was work performed directly by the parent agent, not an autonomous
Aptarchy completion. Aptarchy's earlier task state remains separate.

## Limits

- This proves one synthetic DXF circle edit on the isolated Seafile 13.0.28
  lab and the tested released bundle. It does not establish broad CADCraft DXF
  fidelity, other drawings, fonts, browsers, human HTTPS use, or production
  readiness.
- The run used a new synthetic data volume and temporary lab configuration.
  Production Seafile, production ONLYOFFICE configuration, and upstream were
  not accessed or changed. A post-change ONLYOFFICE UI edit/save regression was
  not run.
- Browser assertions and screenshots are retained in sanitized form. The raw
  runtime JSON and console log remain outside Git; hashes are recorded, but
  those hashes alone are not independent observation of the run.
- The browser was Chromium in the isolated lab. No manual file upload or
  download was used as the editor save.

Evidence: [`docs/reviews/GR-082/`](reviews/GR-082/).
