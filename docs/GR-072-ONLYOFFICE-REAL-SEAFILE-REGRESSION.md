# GR-072 — post-change ONLYOFFICE edit/save regression

## Result

On 2026-10-26, the existing Seafile-to-ONLYOFFICE route opened the synthetic
`OnlyOffice/artcraft-lab/synthetic.docx` document after the ArtCraft route work.
The operator-recorded sequence is open → visible edit → Ctrl+S and `All changes
saved` → new Seafile history version → navigate away → load the file route again
with the final marker visible. The retained screenshots directly show the
ONLYOFFICE document, final GR-072 marker, and save-status display; they do not
independently establish navigation chronology or Seafile history creation.

This closes the previously open **post-change ONLYOFFICE edit/save/version
smoke** for this synthetic DOCX and this deployment. It is evidence that the
existing editor path still works for this tested file. It does not establish
broader production readiness or byte-for-byte editor-to-storage identity.

## Observed sequence

1. Opened the existing synthetic DOCX from the non-ArtCraft
   `OnlyOffice/artcraft-lab` folder in the real Seafile browser UI. The file
   opened in the existing ONLYOFFICE editor. Representative ONLYOFFICE assets
   loaded successfully.
2. Switched the editor's UI from its mobile layout to desktop layout using its
   own restart prompt. This was an editor UI preference; no server configuration
   or ONLYOFFICE settings were changed.
3. Initially appended `GR-071 ONLYOFFICE regression save 2026-10-26.` to the
   synthetic document. Ctrl+S resulted in the visible `All changes saved`
   indicator.
4. Seafile's file history showed a new current version at `2026-10-26 06:13:23`
   (25.3 KB), above the earlier 5.3 KB version. I then corrected the marker's
   work-item label from GR-071 to GR-072 and saved again. History showed the
   final current version at `2026-10-26 06:16:13` (25.4 KB), with the 5.3 KB
   version still present. The two versions are both retained in the history;
   this report does not collapse them into one save.
5. Navigated away from the editor to Seafile, inspected the file history, then
   loaded the file route again. The newly loaded ONLYOFFICE editor displayed the
   final GR-072 marker. The original editor was exited by navigation; an
   explicit in-app close was not performed.

No edited-output download, manual upload, route change, allowlist change, or
server-side ONLYOFFICE configuration change was performed during this test.

## Evidence

- [Sanitized browser observations](reviews/GR-072/runtime/browser-observations.txt)
- [Save confirmation screenshot](reviews/GR-072/runtime/onlyoffice-save-confirmation.png)
- [Fresh editor reopen screenshot](reviews/GR-072/runtime/onlyoffice-fresh-reopen.png)
- [Evidence index and checksum command](reviews/GR-072/README.md)

Screenshots omit the Seafile history view because it displayed an account name.
The sanitized observation record retains only the version timestamps and sizes.

## Scope and limitations

- **Operator-recorded runtime sequence:** the existing real Seafile →
  ONLYOFFICE route opened the synthetic DOCX, accepted a visible edit, reported
  save completion, created Seafile history versions, and loaded the final saved
  edit in a later editor load. The screenshots corroborate the displayed final
  marker and `All changes saved` state, but not the history or sequence.
- **Not verified:** exact byte equality between ONLYOFFICE's submitted payload
  and Seafile readback; an explicit in-app close action; other file types,
  libraries, users, or ONLYOFFICE versions; concurrency and failure recovery;
  production security or deployment readiness.
- This was a browser/UI smoke using one synthetic file, not a full ONLYOFFICE
  compatibility matrix. The history page was inspected live but not captured
  because it exposed account identity.
- This result does not grant project GPT PASS or upstream publication approval.
  Project status remains **INCOMPLETE** and upstream publication remains
  **LOCKED**.
- Independent R3 returned **PROVISIONAL ACCEPT with no remaining findings**;
  the R1/R2 documentation minors are corrected. See
  `docs/reviews/GR-072/INDEPENDENT-REVIEW-R1.md` and
  `docs/reviews/GR-072/INDEPENDENT-REVIEW-R2.md` and
  `docs/reviews/GR-072/INDEPENDENT-REVIEW-R3.md`.
