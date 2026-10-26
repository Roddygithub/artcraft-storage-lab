# GR-081 — identity-binding implementation review R2

**Verdict: PROVISIONAL source review; no new MAJOR regression identified.**
This review does not close the save-identity gate or change candidate
`70fa192ed5d414daf28087315f0f77f8312e98b5` from its GPT **FAIL**. No project
PASS or upstream approval is claimed.

## Scope and limits

Read-only review of the identity-binding source patches, gateway host page,
transport and patch manifest. No tests, builds, browser, network or services
were used. The editor patch inputs are pinned WordCraft
`00bc6a4b028013b2dfb0e85e8b326aeed3ecff6d` and GridCraft
`06920de8da609c19de7446945cfc62b844691efd` checkouts with the existing GR-016
patch baseline. Remote availability of the new transport commit was not
checked.

## R1 findings and R2 verification

| R1 finding | R2 result | Evidence and remaining limit |
|---|---|---|
| MAJOR — app patches used an old transport revision and an excluded absolute source override | **Artifact remediation verified; remote resolution NOT VERIFIED** | Both Cargo manifests and locks now pin `d572f2d550278a7f4aad91a1bac650105c19812b`; the local override is removed. The commit contains the identity transport and `PendingSaves::any`. A fresh remote checkout needs that commit to be available at the configured Git URL. |
| MAJOR — GridCraft could report dirty for the exact snapshot being saved, preventing its clean ACK | **Source correction verified** | The bridge suppresses the dirty report only while the active native UID and `Arc` match a pending save snapshot. Later workbook edits use a different snapshot and remain dirty. Runtime ordering is NOT VERIFIED. |
| MODERATE — WordCraft retry could report dirty for the revision included in its pending save | **Source correction verified** | The bridge suppresses dirty reporting only when the bound identity and current revision match a pending save. Later revisions remain reportable. Runtime ordering is NOT VERIFIED. |

## Additional R2 findings

R2 found two MINOR artifact issues. Both are corrected in the retained R2
artifacts:

- The GridCraft patch no longer changes the workspace `rust-version`.
- `check-identity-artifacts.py` now applies each patch in a temporary copy and
  verifies that the resulting changed-file set and SHA-256 values exactly match
  the implementation manifest.

The checker reported exact pinned app bases, matching source hashes, and
successful applicability/output reproduction for all three patches. It does
not compile or execute the code.

## Remaining gates

Same-name replacement refusal before serialization, the real editor Save and
ACK lifecycle, GridCraft active-cell Save, edits during an outstanding save,
fresh dependency resolution, WASM bundle behavior, Seafile version/reopen, and
ONLYOFFICE post-change preservation remain **NOT VERIFIED**. ONLYOFFICE was not
changed; its current-route UI remains **INCONCLUSIVE / NOT VERIFIED**, with no
causal attribution to ArtCraft.
