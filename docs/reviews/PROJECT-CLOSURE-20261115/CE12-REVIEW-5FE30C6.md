# Targeted CE12 review — runner, replay evidence and their limits

**Verdict: PASS with limitations.** No `BLOCKER`, no `MAJOR`, two `MINOR`
evidence-quality findings. Free-model review; PROVISIONAL; not a GPT gate.

| Field | Value |
| --- | --- |
| Reviewed head | `5fe30c67235371974dd5bbd9400a89d471db501d` |
| Isolation | Dedicated worktree `/home/roddy/.cache/artcraft-storage-lab/review-ce12`, detached, clean; main checkout off limits to the reviewer |
| CE12 equivalence | `git diff --name-only a1984d5 5fe30c6 -- local_ce12.py compose.ce12.yml test_local_ce12.py results/2026-11-15-seafile12-*` → empty, so the runner and both replay directories are byte-identical to the `a1984d5` review head |
| Scope | `local_ce12.py`, `compose.ce12.yml`, `tests/lab/test_local_ce12.py`, both CE12 replay directories, and the claims made about them |

## Verified from retained files

| Claim | Evidence |
| --- | --- |
| Seafile image pinned by digest | `local_ce12.py:18`, `compose.ce12.yml:31`, `test_local_ce12.py:24` |
| Stack bound to loopback | `compose.ce12.yml:35` |
| Per-run synthetic accounts and passwords | `local_ce12.py:117-122` |
| Teardown in `finally` | `local_ce12.py:151-155` |
| 66/66 (24 + 27 + 15) | three `*-browser.json`, both verifiers |
| DOCX relay == readback, byte-identical | `sha256sum` on `wordcraft-first-relay.docx` / `wordcraft-first-readback.docx` |
| PPTX relay == readback, byte-identical | `sha256sum` on `pptx-first-relay.pptx` / `pptx-readback.pptx` |
| XLSX bytes not retained, disclosed | no `.xlsx` in either directory; `README.md:21-22` |
| Bridge-start ordering fix is in the launcher | `local_ce12.py:134-140` |
| Summaries sanitized | grep scan: only `[redacted]` / `<synthetic-repo>` |

## Fault injection — the verifier is not a rubber stamp

Both verifiers rejected all six mutations:

| Mutation | Result |
| --- | --- |
| `passed` count edited | rejected |
| one `"ok": true` flipped to `false` | rejected |
| file listed in `SHA256SUMS` deleted | rejected |
| one byte of a retained `.docx` corrupted | rejected |
| fake account string injected into a JSON | rejected |
| `source_commit` set to a non-existent SHA | rejected |

## MINOR findings

| # | Finding | Evidence |
| --- | --- | --- |
| 1 | "each produced a new Seafile version" is carried only by a boolean in the retained summary; no history length, creator or version id is retained | `wordcraft-browser.json` → `{"name": "...creates_seafile_version_by_user", "ok": true}` |
| 2 | "reopened in a fresh session" is likewise assertion-only; no storage state or context evidence is retained | `wordcraft-browser.json` → `{"name": "...reopen_fresh_seafile_session", "ok": true}` |

### Root cause

The runner does observe these facts and does record them:
`run_browser.py:1289` built
`f"history {len(before)}->{len(after)} top={after[0]}"`, and the check compares
`after[0]["creator"] == admin_username`. The evidence drop then stripped
`detail` (along with `repo_id` and `ran_at`) during sanitization, and no
sanitizer was committed. The proof existed at run time and was discarded.

This is a sanitization defect, not a defect in the observation logic. It is
being remediated by keeping `detail`, emitting redaction-safe facts from the
runner, and committing the sanitizer that performs the redaction.

## Additional finding found during remediation (not raised by the reviewer)

Nine assertions were written `check(name, True)`: they append `"ok": true`
unconditionally and can never fail. Four of them are inside this replay —
`wordcraft_reopened_from_seafile_file_list`, `gridcraft_reopened_from_seafile_file_list`,
`deckcraft_reopened_from_seafile_file_list`, `pptx_fresh_session_file_list_reopen`
— so the advertised 66/66 includes assertions that carry no check.

| Severity | Assessment |
| --- | --- |
| `MINOR` | The adjacent assertions (host frame present, readback bytes equal, marker visible) carry the substance, so the core claim is not resting on these. But a count that includes unfalsifiable assertions overstates coverage. |

Remediated: each now asserts that the navigation did not land on
`/accounts/login`, and records `url_has_login_redirect=False` in its detail.
The remaining five occurrences are in flows outside this replay and are left
for a later pass rather than changed without a re-run.

## Weakest link

The retained summary is the last step of the chain, and for the two claims
above it records a verdict without its evidence. The underlying check is
auditable in committed code (`run_browser.py`), so the claim is not
unfalsifiable — but it is not re-verifiable from the retained files alone,
which is the standard the rest of this evidence meets.

## Contradiction with the scope wording

None found. `VALIDATION-STATE.md` already qualifies broad fidelity, hardware,
owner-server, concurrent writers, the XLSX byte gap and the absent GPT gate.

## Answers

* **Is 66/66 supported by the retained files?** Yes.
* **Is "new version + fresh-session reopen" proven by the retained files?** No — it is asserted by the runner and recorded as a boolean. Remediation in progress.
* **Is the verifier trustworthy under mutation?** Yes, 6/6 mutations rejected on both verifiers.
* **Weakest link?** The sanitized summary dropped the observed detail for the two central claims.
