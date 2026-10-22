# Review 01 — independent free review of GR-001, GR-002, GR-004 and the GR-008 evidence

* Reviewer: `artcraft-reviewer` (Nemotron 3 Ultra 550B A55B, Nvidia) — **independent**,
  it did not write any of the reviewed material.
* Review date: 2026-10-22
* Reviewed: `docs/reviews/GR-001/DEPLOYED-INSTANCE-CONTRACT.md`,
  `docs/SEAFILE-INTEGRATION-POINTS.md`, `docs/HOST-CONTRACT.md`,
  `docs/reviews/GR-008/SEAFILE-CONCURRENCY-PRIMITIVES.md`, `docs/AUTHENTICATION.md`,
  `docs/reviews/GR-003/WEB-BUILD-SURVEY.md`, `docs/DEPLOYMENT.md`,
  `docs/LICENSING.md`, `docs/TEST-MATRIX.md`
* Verdict: **FAIL**

```text
REVIEW RESULT: FAIL
```

## 1. Findings and remediation

| # | Severity | Finding | Remediation | Status |
| --- | --- | --- | --- | --- |
| F1 | BLOCKER | `HOST-CONTRACT.md` claimed "the Craft app has already marked the document clean as soon as the bytes leave the frame". **False for WordCraft** (its `async_saves` defers the clean marking until `finish(Saved)`), **true for PdfCraft** (marks saved on `host_save` -> `Ok`), and **worse in GridCraft** (its `download` hook has no `Result`, so a failed save is only logged and the workbook is still marked saved). | §3.4-§3.7 of `HOST-CONTRACT.md` rewritten with a per-app table, the sources, the corrected statement, and the **proposed** `<app>:saveResult` extension. | **fixed** |
| F2 | MAJOR | Option B (the gateway writes with its own credential) attributes the new version to the **service account**, not the user; this was only a table cell. | A prominent callout in `SEAFILE-INTEGRATION-POINTS.md` §Q4, and L3 rewritten in the limitations table. | **fixed** |
| F3 | MAJOR | The `op=update` file-server token is **library-wide**, so the gateway is the only thing preventing a browser from getting a library-wide write capability. The consequence was under-stated. | A "the consequence, stated forcefully" block in `AUTHENTICATION.md` §1.2, including that the gateway's checks are the *only* defence, not defence-in-depth. | **fixed** |
| F4 | MAJOR | The 13 apps do **not** share a uniform `Services` struct; `HOST-CONTRACT.md` presented the generalised contract as if it already worked for all of them. | The gap table in §4 now carries each app's actual save hook and signature, with a "locate the seam first" verdict for the four apps with no `Services` in `ui-egui/src/lib.rs`. The summary in §0 now says the contract is "consistent for the open and dirty parts, and divergent for the save part". | **fixed** |
| F5 | MAJOR | Share-link editing is not covered by the hook, but this was not scoped out explicitly. | Limitation L7 now says **explicitly out of scope for the MVP**, explains that a read-only share link keeps working unchanged, and points at the upstream patch. | **fixed** |
| F6 | MINOR | The stable `doc_key` is a co-editing enabler for ONLYOFFICE, but our integration uses one session per user, so it is a session-isolation tool. | A note added to `DEPLOYED-INSTANCE-CONTRACT.md` §2.3. | **fixed** |
| F7 | MINOR | The extension key is the one after the **last** dot (`report.final.docx` -> `docx`). | A note added to `SEAFILE-INTEGRATION-POINTS.md` §2.1. | **fixed** |
| F8 | MINOR | The ONLYOFFICE `file_key` JWT carries no content id, so it cannot detect a concurrent modification. | Added to the token table in `DEPLOYED-INSTANCE-CONTRACT.md` §2.1. | **fixed** |

## 2. What the review confirmed as correct

The reviewer's own notes say so explicitly, and the confirmations are worth
recording because they are the parts a later reader will want to trust:

* the ONLYOFFICE contract as implemented in the deployed 12.0.14 Pro instance —
  verified line by line against the live files;
* the concurrency analysis: Seafile provides **no** native optimistic
  concurrency for an update (`last_modify` only stamps the mtime, `head` is not
  a guard, `441` on a deleted or renamed file, no new commit for identical
  content), so the obj_id-compare-at-save design is the right one;
* the branch order in `view_lib_file`: the third-party-editor branch really does
  come **before** the ONLYOFFICE branch, so it really does shadow it per
  extension;
* the `THIRDPARTY_EDITOR_ACTION_URL_DICT` key format and the hardcoded
  `can_edit: False`;
* the host contract's security model: origin **and** source checks, explicit
  `targetOrigin`, same-origin embedding — correct in both existing bridges, and
  it satisfies the mission's hard rules;
* the licensing analysis: the network boundary is the only way to keep this
  repository MIT/Apache while integrating with a GPLv2 Seahub.

## 3. Test gaps the review listed, and their current state

| Gap | State at the time of the review | State now |
| --- | --- | --- |
| "No tests have been run — all TEST-MATRIX.md rows are `[ ]`" | true for the docs under review | **changed**: `tests/test_integration.py` now runs the full open/save/conflict round trip against the real instance and passes. See `docs/reviews/GR-005/README.md`. The TEST-MATRIX rows are updated there. |
| the 8 apps with a reduced or absent `Services` need their seam located | open | **open** — tracked as GR-003's remaining work and in the §4 table |
| share-link editing end to end | open | **scoped out of the MVP** (F5) |
| cookie-forwarding vs service account | open | **open** — A-3 in `AUTHENTICATION.md` |
| `use_onetime=True` behaviour of the download token | open | **open** — A-1 in `AUTHENTICATION.md` |
| ArtCraft upstream acceptance | open | **open** — L-3 in `LICENSING.md` |
| Seafile upstream acceptance of the write patch | open | **open** — L-5 in `LICENSING.md` |

## 4. Status after remediation

```text
PROVISIONAL — FREE REVIEW PASS (remediated)
GPT REVIEW PENDING
```

The remediation was applied by the owner. A **second** independent review was
requested afterwards; its result is recorded in `docs/reviews/REVIEW-02.md`
when it lands. **Nothing here is final until `GPT REVIEW PASS`.**
