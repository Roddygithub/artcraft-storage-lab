# Bounded recovery reviews, 2026-11-08

These are retained summaries of independent GPT 6.1 Sol low child reviews.
They are not the forensic or project gate. Runtime was not independently replayed.

| Reviewed exact candidate | Independent outcome | Parent response |
| --- | --- | --- |
| `2825f4cff73135c136eb33290b0bf22a5b393969` | Closure unsupported: private-only evidence; source mismatch; 11 ONLYOFFICE assertions, not 12; no final reopen; invented HTTP categories; no independent forensic completion | Withdrew completion/freeze claims, corrected inventory and tracking; retained sanitized diagnostics |
| `32ce907cc17695407fd02612ffd26bcbdcb41288` | Host/shim bounded source PASS. P2: multiple final Find queries could reuse stale positive counts. Tracked-deletion filter accepted | One new authenticated editor per final query; empty input and initial no-results required; absent/stale-positive regression |
| `664898fc6f30ce2d27aaa47a7fccd342e536ac0e` | ONLYOFFICE runner/tests bounded source PASS; no concrete findings | New runtime still required; no coexistence claim |

The separate read-only packaged-source audit found CE 13.0.28's mixed-suite
error propagation at `seahub/views/file.py:824–878`, with frontend rejection
at `frontend/src/view-file-onlyoffice.js:49–50`. It found no standard
per-extension configuration-only fix. The multiple-suite selection API is
Pro-gated and operates per library. This is a source finding, not a live
production observation or permission to modify production/upstream.

The new HTTP predicate was also applied locally to the newly generated private
combined-run ODT and PPTX pages: both contain the blocking error. Only the
boolean conclusion is retained here; raw pages contain capabilities and remain
private. This is a parent observation, not independent runtime certification.

The subsequent bounded review of `664898f..5ff302e` returned PASS with no
findings for the HTTP error predicate, explicit diagnostic isolation,
deployment log/frame safeguards and sanitized historical inventory. Its offline
candidate-scope, seven launcher and private-byte inventory checks passed.
It explicitly leaves coexistence blocked and grants no project gate approval.

The bounded review of `727fc37..ecea1a9` returned PASS with no actionable
findings. Eight offline launcher tests passed; diagnostic browser continuation
preserves the HTTP failure after cleanup. Private synthetic DOCX capture does
not alter edits or assertions. The reviewer also verified four combined-run
checksums, 33 source hashes against `664898f`, and 119 browser assertions.
No runtime or document-fidelity verdict was granted.

The independent evidence review of `e49da48` returned bounded PASS with no
material findings. It verified all 33 source hashes against `c909252`, raw JSON
and static-manifest hashes, structural invariants and first relay/readback byte
equality, and inspected all three screenshots and four DOCX packages. It found
no visible secrets, external relationships or credential matches. No independent
rendering/runtime replay, full-fidelity verdict or removal approval was granted.

The independent source review of `04ac568` against `e49da48` returned bounded
PASS with no findings. The explicit three-document allowlist, pre-edit waits,
body-text retention and fail-closed fixture selection passed the offline test.
Runtime for the added prose and structure cases follows separately.

The independent evidence review of `aec6c937bb6e266237e25ff136deaa3607cc19cf`
returned bounded PASS with no actionable findings. It verified both 33-file
source inventories against `9a71dff`, private-result/static-manifest hashes,
retained asset equality and the verifier. Four screenshots and all package
parts of eight DOCX files support the bounded formatting/list/structure claims.
Browser 28/0 and HTTP 44/2 per run remain explicit. No independent rendering,
runtime replay, project gate or ONLYOFFICE removal approval was granted.
The reviewer could not reproduce the credential-value scan from the inspected
inputs; that scan remains a parent observation, not independently established.
