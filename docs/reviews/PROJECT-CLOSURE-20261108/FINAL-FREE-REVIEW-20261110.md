# Final independent free review — 2026-11-10

**Candidate:** `265897f36739349f453d8519e6113ac43d3dbe51` (`main`, clean tree,
pushed to `origin`).
**Reviewer:** configured `artcraft-reviewer` role, fresh read-only session
(provider `nvidia`, model `nvidia/nvidia/nemotron-3-ultra-550b-a55b#high`,
edit permission denied). The reviewer did not write this candidate.
**Verdict:** **PROVISIONAL PASS** — no BLOCKER, no MAJOR.

This is a bounded free review, not the project GPT gate and not a global PASS.
The project remains INCOMPLETE and upstream publication remains LOCKED.

## Findings

| Severity | Finding | State |
| --- | --- | --- |
| MINOR | `scripts/validate-candidate.py` reported a per-test failure when Playwright was absent instead of naming the missing dependency. | Remediated: explicit Playwright precheck with exit 2 and a usage message, plus the dependency documented in the docstring. |
| MINOR | `scripts/probe-legacy-import.py` did not state the Playwright/Chromium requirement in its docstring. | Remediated: requirement now stated in the docstring; the usage example already passed `--with playwright`. |

## Evidence the reviewer reported

* `tests/bridge/test_bridge.py`: **33 tests OK**.
* `tests/test_legacy_fixtures.py`: **9 tests OK** (1 skipped because the
  reviewer's environment had no Playwright).
* `tests/lab/test_local.py`: **13 tests OK**.
* Every retained `verify.py` under `lab/real-seafile/results/` passed, and every
  `SHA256SUMS` matched, including the legacy/OpenDocument fixtures.
* The status documents agree on INCOMPLETE, the frozen evidence commit, the
  seven unrouted formats and ONLYOFFICE retirement; no secrets or credentials
  were found in the committed evidence.
* The bundle import probe's **5/5** result was accepted from the retained
  `summary.json` outside the repository (it cannot run without Playwright).
* Bridge source checks: same-origin `postMessage` validation, `targetOrigin`
  confinement, CSP nonces, iframe sandbox, token kept out of URLs, read-only
  enforced on the bridge save path.

## Limits

* Runtime was not replayed. The `--viewing` browser 140/140 and the bundle probe
  5/5 remain parent-run evidence.
* The reviewer's environment lacked Playwright, so its offline run was 19/20;
  that is the origin of the first MINOR and is not a repository failure.
* No CI workflows exist in the repository (`actions/workflows` total count 0);
  the green gate is the local suite described in `docs/VALIDATION-STATE.md`.
* `artcraft-gpt-auditor` (GPT-5.6 Luna) returned “The usage limit has been
  reached”; the Sol final gate was not attempted. GPT REVIEW remains PENDING.
* Human HTTPS/hardware acceptance (WebGPU, clipboard, fonts, unload guard) and
  rendered legacy content in a combined session remain NOT VERIFIED.

The raw reviewer transcript is private and not retained; this summary is
sanitized.
