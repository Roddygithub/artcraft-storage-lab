# GR-081 — project GPT review remediation

## Result

This work item records remediation of findings from the project GPT review of
candidate `70fa192ed5d414daf28087315f0f77f8312e98b5`. That review returned
**FAIL**. GR-081 does not change that verdict; the new candidate requires a
fresh project review after implementation and independent review. Upstream
publication remains **LOCKED**.

## Changes made

| Finding | Change | Status |
|---|---|---|
| WordCraft/GridCraft native document identity | The gateway requires negotiated native identity and the editor patches bind the parsed document, guard replacement/Save As before serialization, and route ordinary Save with identity and a ticket. | Source-only. R1/R2 corrected dependency pinning and pending-save dirty ordering; independent R2 found no new MAJOR source regression. Compilation, zero serialization/upload on refusal, runtime Save/ACK and Seafile version/reopen remain **NOT VERIFIED**; save-identity MAJOR remains open. |
| ONLYOFFICE post-change preservation | No settings or services were changed. | **INCONCLUSIVE / NOT VERIFIED**. The configured client API script returned 404 and the editor did not initialize in GR-080. A successful current-route edit/save/version/reopen is still required. |
| Screenshot attribution | GR-015's duplicated concurrent screenshot and GR-078's reused PhotoCraft screenshots are explicitly identified. Unsupported visual corroboration claims are narrowed to operator-recorded observations. | Documentation corrected; original image files and hashes retained. |
| Deployment topology | `integration/README.md` now separates the Seahub origin from the gateway/Craft origin and includes `ARTCRAFT_SEAFILE_ORIGIN` in the quickstart and environment table. | Corrected against `docs/SECURITY.md` and `docs/DEPLOYMENT.md`. |
| Directory index symlink confinement | `_serve_static` resolves and confines the final `index.html` target before serving it. | Source corrected; runtime symlink exploitability was **NOT VERIFIED**. |
| Dispatcher verifier | Expected mapping now includes all five tracked extensions, including `pcraft`; output distinguishes the four per-candidate checks from PhotoCraft's separate GR-076 evidence. | Corrected; verifier was not run. |
| Stale claims and missing links | GR-015/GR-076/GR-078 claims were bounded to retained artifacts; GR-030 and GR-048 references were corrected to existing files. | R3/R4/R5 corrections recorded; docs R4/R5/R6/R7 PROVISIONAL PASS; R7 found no new findings. |

## Identity implementation follow-up

GR-081 now carries source patches for native identity binding in WordCraft and
GridCraft, together with the identity-aware host transport. They bind the
native document after parsing, route ordinary Save through an identity-bearing
message, and refuse replacement/Save As commands before the guarded
serialization path. The app patches and lockfiles pin transport commit
`d572f2d550278a7f4aad91a1bac650105c19812b`; that commit is local and remote
availability is **NOT VERIFIED**.

Independent code/security R1 returned PROVISIONAL FAIL for dependency
reproducibility and pending-save dirty ordering. The R2 response updates the
app pins, fixes the WordCraft/GridCraft source ordering, removes an unrelated
GridCraft MSRV change, and makes the artifact checker compare applied output
hashes with its manifest. Code/security R2 found no new MAJOR source regression
and two MINOR artifact findings, which are corrected in the retained artifacts.
See [`reviews/GR-081/INDEPENDENT-CODE-SECURITY-REVIEW-R2.md`](reviews/GR-081/INDEPENDENT-CODE-SECURITY-REVIEW-R2.md)
and [`reviews/GR-081/RESPONSE-R2-CODE.md`](reviews/GR-081/RESPONSE-R2-CODE.md).
This remains a source-only result: no build, tests, browser, services, or
Seafile version/reopen verification were performed. The save-identity MAJOR
and ONLYOFFICE preservation gate remain open.

## Validation and limits

No tests were added. Since the initial source-only review, both identity-patched
apps passed locked Rust 1.95 WASM checks and their existing UI suites (WordCraft
824 passed/2 ignored; GridCraft 151 passed). The gateway browser protocol test
was not run because Python Playwright is unavailable. No Seafile workflow or
service check was performed. Full results and limits are in
[`reviews/GR-081/VALIDATION-R3.md`](reviews/GR-081/VALIDATION-R3.md). Current
local checks include Python AST parsing, selected
JSON parsing, shell syntax, `git diff --check`, GR-069 manifest verification,
and local Markdown target checks. The identity artifact checker confirms patch
applicability and exact output hashes. The dispatcher verifier itself,
same-name Save As/replacement rejection inside WordCraft/GridCraft,
the ONLYOFFICE regression, production behavior and a fresh project GPT review
remain **NOT VERIFIED**.

The bounded ONLYOFFICE diagnosis and current inconclusive disposition are
recorded in
[`reviews/GR-081/ONLYOFFICE-BOUNDED-DIAGNOSIS-R1.md`](reviews/GR-081/ONLYOFFICE-BOUNDED-DIAGNOSIS-R1.md).
The project GPT review record is
[`reviews/GR-081/PROJECT-GPT-REVIEW-70FA192.md`](reviews/GR-081/PROJECT-GPT-REVIEW-70FA192.md).
R3 code/security and docs/evidence reviews returned PROVISIONAL FAIL; their
findings and responses are recorded in the evidence bundle. R4 code/security
returned PROVISIONAL FAIL; response is recorded. R4/R5 docs/evidence returned
PROVISIONAL PASS with their MINOR findings addressed; responses are recorded.
Bounded ONLYOFFICE research remains inconclusive. Document-identity design
research is recorded in
[`reviews/GR-081/IDENTITY-BINDING-DESIGN-R1.md`](reviews/GR-081/IDENTITY-BINDING-DESIGN-R1.md);
the save-identity finding remains open. Docs R6 returned PROVISIONAL PASS with
its MINOR reference correction applied. R7 returned PROVISIONAL PASS with no
new documentation findings; its report and response are in the evidence bundle.
