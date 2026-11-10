# Independent free review of the payload-evidence delta — 2026-11-10

**Candidate:** `7d18afb` (`main`, `265897f..7d18afb`), clean tree, pushed.
**Reviewer:** configured `artcraft-reviewer` role in a fresh read-only session
(provider `nvidia`, model `nvidia/nemotron-3-ultra-550b-a55b#high`, edit
permission denied). The reviewer did not write this delta.
**Verdict:** **PROVISIONAL PASS** — three MINOR, no BLOCKER or MAJOR.

This is a bounded free review of a delta, not the project GPT gate and not a
global PASS. The project remains INCOMPLETE and upstream remains LOCKED.

## Findings

| Severity | Finding | State |
| --- | --- | --- |
| MINOR | `results/2026-11-08-legacy-viewing/slice.json:146` used a differently named placeholder (`<synthetic-admin>`) than the newer evidence (`<run-admin>`), and its verifier only rejected the email form. | Remediated: both placeholders unified to `<run-admin>`; the verifier now rejects any `synthetic-` token and sums were recomputed. |
| MINOR | `scripts/forensic-audit.py` skipped an 8-character token merely for starting with `20`, so a real commit id of that shape would have been ignored. | Remediated: only a token matching a real `YYYYMMDD` date is skipped. |
| MINOR | `scripts/probe-legacy-import.py` carried synthetic account defaults in source. | Remediated with an explicit comment that they are lab-only offline defaults overridden by the environment on real runs. |

## Evidence the reviewer reported

* Ran every retained `verify.py`: the relay-bytes directory (**59/59**, **67/67**,
  43 viewing checks, 7 fixtures with exact bytes), the FODS/PPSX run (**59/59**,
  **173/173**, 29 viewing checks), both re-redacted older summaries
  (**57/57**; **57/57**, **140/140**, 21 viewing checks) — all PASS.
* Confirmed the byte counts and marker kinds in the new README table against the
  retained `detail` fields, including the OLE UTF-16LE/UTF-8 branch.
* Confirmed sanitization: no `@auth.local`, `repo_id`, `access_token`, plain
  `WOPISrc=http`, or unredacted `wopi/files/<hex>`; only `reader@lab.test`
  remains as a static fixture name.
* Confirmed provenance SHAs are ancestors of HEAD and that the self-audit report
  itself states it is not independent review.
* Re-ran `scripts/forensic-audit.py`: PASS over 17 evidence directories.
* Found no security, data-integrity or licensing problem in the probe/audit code.

## Limits

* Runtime was not replayed by the reviewer; the browser totals remain
  parent-run evidence.
* Event-sourced UI state after a reload of these legacy fixtures is not covered:
  fresh-reopen capture of the marker for a *saved* legacy format is still
  NOT VERIFIED, as are rendered legacy pixels, hardware acceptance and the
  project GPT gate.
* `artcraft-gpt-auditor` (GPT-5.6 Luna) remained unavailable (provider usage
  limit); there are no CI workflows in the repository.

The raw reviewer transcript is private and not retained; this summary is
sanitized.
