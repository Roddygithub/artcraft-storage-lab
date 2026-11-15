# Independent review — candidate `123d2a0` (docs at `2dd571f`)

**Verdict: PROVISIONAL PASS for the claimed lab scope.** This is a free-model
review. It is **not** a GPT gate, not a project-wide PASS, and not production
approval. Upstream remains LOCKED.

The reviewing context's own headline verdict was **FAIL on one BLOCKER**
(`/relay/save` buffering before token validation). That BLOCKER was re-checked
against the source and reduced to a documented deployment limitation; the
reasons are in "Why finding 1 is a limitation, not a blocker" below. The PASS
above is this record's conclusion, not the reviewer's.

| Field | Value |
| --- | --- |
| Technical candidate | `123d2a0ca8435e93e37b6d2f31fb73ac016fc5fb` |
| Reviewed head | `fc795a6` (no change under `bridge/` since `123d2a0`) |
| Findings resolved at | `2dd571f` (documentation only) |
| Reviewer independence | Separate agent context; authored none of `bridge/`, `lab/` or the retained evidence |
| Model class | Free model — verdict is PROVISIONAL by construction |

## Checks run first-hand

| Check | Result |
| --- | --- |
| `python3 tests/bridge/test_bridge.py` | 33/33 OK |
| `.../2026-11-15-seafile12-replay/verify.py` | PASS: 66/66 browser assertions, DOCX/PPTX relay readback equality, artifact hashes |
| `.../2026-11-15-seafile-render-readonly/verify.py` | PASS: HTTP 56/56, browser 58/58, 4 read-only legacy formats, 8 unrouted |
| `.../2026-11-15-offline-validation-123d2a0/verify.py` | PASS: 21/21 groups, exact logs, complete manifest |
| `sha256sum -c SHA256SUMS` (replay) | All entries OK |
| `python3 scripts/forensic-audit.py` | PASS: 24 directories, 21 verifiers, 19 provenance, 307 hashes, 87 JSON + 2 loose JSON, no secrets |
| `git diff --stat 123d2a0 2dd571f` | Documentation and evidence only; no `bridge/` change |

## Confirmed findings

| # | Severity | Finding | Evidence | State |
| --- | --- | --- | --- | --- |
| 1 | LIMITATION | `/relay/save` buffers the whole body before validating the token | `bridge/app.py:573` (`_read_body`) precedes `:577` (`check_file_info`) | Documented in `bridge/README.md` Serving section |
| 2 | MINOR | Extensions outside `SIGNATURE_KNOWN` are not byte-checked, and the README security table did not say so | `bridge/app.py:318`; `tests/bridge/test_bridge.py:546` | Fixed |
| 3 | MINOR | `bridge/README.md` status line claimed "45 HTTP + 21 browser" from the 2026-11-08 generation | Retained evidence is 56/56 + 58/58 and 66/66 | Fixed |
| 4 | MINOR | `bridge/README.md` Layout block said "32 offline checks" while the status line said 33 | `grep -c "def test_"` = 33 | Fixed |
| 5 | MINOR | Review packet `Current evidence` described `be51c3b`: 20/20 groups, 20 directories, 17 verifiers, 16 provenance; the CE12 three-editor replay was absent | Current audit: 21/21, 24, 21, 19 | Fixed |

### Why finding 1 is a limitation, not a blocker

An initial report raised the body-buffering order as a `BLOCKER`. It is not,
for two reasons that are verifiable in the code:

1. The relay requires `X-Bridge-Request: 1`, an `Origin` equal to the bridge's
   own origin, and a same-origin `Sec-Fetch-Site` (`bridge/app.py:679-687`).
   The bridge serves no `OPTIONS` handler and sends no CORS headers
   (`grep -n "OPTIONS\|Access-Control" bridge/app.py` → no match), so a browser
   on another site cannot send that preflighted request at all. The remaining
   actor is a direct HTTP client, which is an ordinary unauthenticated upload.
2. Reading the body first is what lets the bridge answer with a clean JSON
   error instead of resetting the connection on an unread body — the same
   reason `_read_body` drains moderately oversized bodies before returning 413
   (`bridge/app.py:695-705`).

The real mitigation is a reverse-proxy body and rate limit, which the README
now states. Changing the order would create a new technical candidate and
invalidate the retained evidence at `123d2a0` for no security gain.

## Claims examined and rejected

| Claim | Why it does not hold |
| --- | --- |
| The host-page CSP lacks `frame-ancestors` | It is present at `bridge/app.py:520`. The report retracted this itself mid-review. |
| `bridge/README.md` cites a non-existent report `§2.1` | `§2.1` exists at `docs/REFOUNDATION-REPORT.md:70`. |
| `host.js` should send `Sec-Fetch-Dest` on relay calls | `Sec-Fetch-*` are forbidden header names; only the browser sets them. The bridge reads `Sec-Fetch-Site` correctly (`bridge/app.py:685`). |
| `PROJECT-CLOSURE.md:304` must say 21/21, not 20/20 | That row is explicitly dated "re-run 2026-11-10 at `864fc77`". 20/20 is correct for that entry; `VALIDATION-STATE.md` carries the current 21/21. |
| No rate limiting, no `pyproject.toml`/pytest | Deployment and tooling choices. The bridge is deliberately stdlib-only and the suite is `unittest`; both are stated in the README. |
| `_HASHED_ASSET_RE` is fragile | The report itself concludes "no bug"; the regex matches both top-level and `fonts/<hash>/` forms. |

The report also retracted one of its own `BLOCKER` findings inside the same
document and promoted a documentation-date difference to `MAJOR`. Its verdict
was therefore not adopted at face value; each claim above was re-checked
against the code and the retained files.

## Scope honesty — verified as correctly labelled

These are stated as `NOT VERIFIED` and are not presented as passing:

* Human HTTPS/hardware acceptance: WebGPU, clipboard, fonts, popups, dirty
  close, refused saves, network recovery.
* The owner's live Seafile 12.0.14: WOPI currently disabled; authenticated
  current-bridge edit/save not demonstrated; supplied credentials rejected.
* Concurrent-writer atomicity: the non-atomic save window is documented and
  tested, and is owner-accepted for the zero-patch MVP.
* Broad Office fidelity: only one synthetic fixture per format.
* Eight unrouted legacy formats: DOC, XLS, FODS, FODT, FODP, PPT, ODP, PPS.
* The global GPT gate: not run on this candidate.

## Answers

* **Is the lab MVP subset ready at the scope it claims?** Yes, for synthetic
  fixtures in an isolated lab under headless Chromium: open, edit, save, new
  Seafile version, fresh-session reopen for DOCX/XLSX/PPTX, plus four
  read-only legacy routes. It is not production-ready.
* **Is full ONLYOFFICE replacement complete?** No. Three editing formats and
  four read-only viewing formats are covered; eight viewing formats are
  unrouted, and replacement completeness remains PARTIAL.
* **Can a global GPT review gate pass on this evidence?** No. No GPT gate has
  run on `123d2a0`; every verdict in this repository is PROVISIONAL.
* **What would most increase confidence next?** Run the GPT gate on
  `123d2a0`/`2dd571f` when the provider quota resets, then execute the human
  hardware checklist. Neither is a code change.

## What this review does not establish

Runtime behaviour on any real deployment, HTTPS with a human in a real browser,
the owner's live server, broad format fidelity, host-enforced authorization, or
atomic saves. It reviews source, retained evidence and the honesty of the
scope wording.
