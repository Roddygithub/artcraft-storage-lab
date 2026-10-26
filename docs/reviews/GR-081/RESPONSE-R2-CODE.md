# GR-081 code review R2 response

The R2 report is
[`INDEPENDENT-CODE-SECURITY-REVIEW-R2.md`](INDEPENDENT-CODE-SECURITY-REVIEW-R2.md).

| Finding | Response |
|---|---|
| App dependency/lock did not resolve the identity transport | Updated both app patches and lockfiles to pin local transport commit `d572f2d550278a7f4aad91a1bac650105c19812b`; removed the absolute local Cargo override. The commit is not yet available from the configured remote, so fresh remote resolution remains **NOT VERIFIED**. |
| GridCraft clean confirmation could be lost after Save | The bridge now suppresses dirty reporting only for the exact active UID and `Arc` snapshot while its host save is pending. Newer snapshots continue to report dirty. Runtime behavior remains **NOT VERIFIED**. |
| WordCraft retry could report the same saved revision dirty while pending | The bridge now suppresses dirty reporting only for the matching bound identity and pending revision. Later revisions continue to report dirty. Runtime behavior remains **NOT VERIFIED**. |
| Patch checker did not verify that applied output matched the manifest | The checker now applies each patch in a temporary copy and compares the complete changed-file set and output hashes to the manifest. |
| GridCraft patch contained an unrelated Rust version change | Removed from the regenerated patch. |

The artifact checker and `git diff --check` pass. No test or build was run. The
save-identity MAJOR remains open pending compilation and runtime verification;
the separate ONLYOFFICE preservation gate also remains open. Candidate
`70fa192` remains GPT **FAIL**, and upstream publication remains **LOCKED**.
