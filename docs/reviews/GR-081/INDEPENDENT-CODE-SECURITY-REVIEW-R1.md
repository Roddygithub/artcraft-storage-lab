# GR-081 — identity-binding implementation review R1

**Verdict: PROVISIONAL FAIL.** The identity checks materially improve source
protection, but R1 found unresolved integration and save-confirmation defects.
This review was read-only. It did not run tests/builds or access a browser,
network, or service.

## Findings

| Severity | Finding | R1 evidence |
|---|---|---|
| MAJOR | The app patches did not reproduce the reviewed transport dependency. | Both app manifests and locks still pinned transport `90c261de…`; identity APIs existed only in the working-tree transport. Their absolute `.cargo/config.toml` path overrides were excluded from the app patches, with no lock resolution. Compilation was NOT VERIFIED. |
| MAJOR | GridCraft could store bytes but fail to confirm a clean save. | A dirty signal for the exact just-serialized snapshot could arrive while the host save was pending, increment host dirty state after `saveRevision` was captured, and prevent the matching clean ACK. |
| MODERATE | WordCraft retry could leave a successful retry dirty. | After refusal/failure, a retry could send dirty=true for the same serialized revision while pending. The host then rejected the clean ACK as newer dirty state. |

R1 also confirmed by source inspection that trusted opens bypass picker/drop,
replacement/Save As command gates precede the guarded serialization routes, and
ordinary Save has a typed host route. Those observations did not prove every
path or zero serialization/uploads in actual editor builds.

## R1 disposition

R2 updates Cargo manifests and locks to local transport commit
`d572f2d550278a7f4aad91a1bac650105c19812b` and removes local absolute overrides.
Fresh remote resolution still requires that commit to be made available at the
configured Git URL. GridCraft now suppresses dirty reporting only for the
pending native UID and exact `Arc` snapshot; WordCraft suppresses only for the
matching bound identity and pending revision. R2's independent source review
found no new MAJOR regression. These changes remain uncompiled and untested.

See [`INDEPENDENT-CODE-SECURITY-REVIEW-R2.md`](INDEPENDENT-CODE-SECURITY-REVIEW-R2.md)
and [`RESPONSE-R2-CODE.md`](RESPONSE-R2-CODE.md). The save-identity and
ONLYOFFICE preservation gates remain open.
