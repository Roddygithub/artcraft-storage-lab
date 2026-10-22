# GPT Luna Independent Audit

Candidate: `c76a7594cc43ba2a6cf56de2232836f008a97863`
Branch: `main`
Date: 2026-10-22

The candidate commit was clean and equal to `origin/main` at freeze. No freeze
tag exists. Review-only role definitions and this report are uncommitted and do
not change the candidate SHA. The candidate implementation was not remediated.

The audit was performed by GPT-5.6 Luna (`openai/gpt-5.6-luna`) and checked by
the primary reviewer against the frozen source. OpenCode 2.1.0 exposes that ID
and `openai/gpt-6.1-sol`; both read-only roles are installed in
`config/opencode/agents/` and `~/.config/opencode/agents/`. The independent Sol
review remains required.

## Reproduction

Environment: Linux, Python 3.14, Rust 1.97.0, Cargo 1.97.0, OpenCode 2.1.0.
`ARTCRAFT_SEAFILE_URL`, `ARTCRAFT_SEAFILE_TOKEN`, and `ARTCRAFT_GATEWAY` were
unset. No production Seafile endpoint or personal document was accessed.

| Command | Result |
| --- | --- |
| `python3 tests/test_gateway_unit.py` | exit 0; all printed unit checks passed |
| `python3 -m compileall -q integration/gateway tests` | exit 0 |
| `git diff --check` | exit 0 |
| `python3 -m pytest --version` | unavailable: `No module named pytest` |
| `python3 tests/test_integration.py` | not run against Seafile; requires credentials and a synthetic library |
| `python3 tests/test_browser.py <repo> <path>` | not run; requires Seafile, gateway, browser, and synthetic fixture |
| `python3 tests/test_gr012_svg.py <repo> <path>` | not run; requires Seafile, gateway, browser, and synthetic fixture |
| `~/.cargo/bin/cargo build --target wasm32-unknown-unknown -p wordcraft-web --release --offline` in `.work/wordcraft-patch` | exit 0; five existing `dead_code` warnings; patch checkout `8707047`, parent `00bc6a4b028013b2dfb0e85e8b326aeed3ecff6d` |

Concurrency reproduction used an in-memory fake Seafile client and two threads
barriered after the same content-ID read. Both `Gateway.save` calls returned
HTTP 200/`ok: true`; final storage held only one editor's bytes. This reproduces
the read-then-write race without touching Seafile.

## Verified claims

* `main` and `origin/main` both pointed to the frozen candidate SHA; the initial
  worktree was clean. No freeze tag was present.
* The gateway unit tests cover sequential stale-save refusal, read-only values
  supplied by a fake backend, session expiry/cap, and static path escape.
* The WordCraft bridge patch exists in `docs/reviews/GR-014/DIFF.patch`; its
  checkout is based on `00bc6a4…`, and the WASM release build succeeds locally.
* GR-011 is not implemented. The current DeckCraft `apps/deckcraft-web/src/web.rs`
  still uses file-picker input and browser-download output, and has no `host.rs`
  bridge ([upstream source](https://raw.githubusercontent.com/storytold/deckcraft/main/apps/deckcraft-web/src/web.rs)).
* GR-012 does not use the common `?host=parent` contract. It uses
  `window.vectorcraft` and a polling adapter, as stated in
  `integration/gateway/hostpage.py:67-77`.
* The existing screenshot `docs/reviews/GR-012/browser-proof-svg.png` visibly
  shows a newly drawn stroke. This is supporting historical evidence, not a
  fresh E2E reproduction.
* The `.work/seahub` checkout is exactly `c01d46bcaa0b2ce24c71561c6c61d15fea808d1a`.
  Its root `LICENSE.txt` is Apache-2.0, while `.work/seafile-server/LICENSE.txt`
  declares AGPLv3 with an OpenSSL linking exception. This contradicts
  `docs/LICENSING.md:14-15` (“GPLv2” / “LGPL-ish”). The Seahub license text is
  also available at [haiwen/seahub/LICENSE.txt](https://raw.githubusercontent.com/haiwen/seahub/master/LICENSE.txt).
* A public ArtCraft issue already discusses suite-wide Host Mode and shared
  session infrastructure ([issue #2420](https://github.com/storytold/artcraft/issues/2420),
  opened 2026-10-16). Its stated scope is remote authoritative sessions and
  multi-surface UI, not the Seafile byte-in/byte-out contract here; the RFC must
  distinguish the two and account for this existing discussion.
* No upstream issue, PR, or RFC was published during this review.

## Claims not reproduced

* No real Seafile request, Seafile Web click-through, WordCraft DOCX save/reopen,
  GridCraft XLSX save/reopen, or VectorCraft SVG save/reopen was rerun. The E2E
  artifacts in `docs/reviews/GR-*` are historical claims/evidence only.
* `tests/test_browser.py` opens via direct gateway `POST /open/` with `repo_id`
  and `path`; it does not automate the file click in Seafile Web
  (`tests/test_browser.py:85-94`). GR-006 itself marks the click partly proven
  and says DOCX was not routed through the live hook because that would conflict
  with ONLYOFFICE (`docs/reviews/GR-006/README.md:12-27, 134-159`).
* The current code was not tested against real read-only, expired-share,
  permission-revoked, rename/delete, network-loss, or concurrent-user cases.
* ONLYOFFICE behavior was not tested. No committed candidate changes target it.
* The Seafile save patch was not executed against a test Seahub instance.

## Test-quality findings

* The unit tests use `FakeSeafile`; they establish gateway branch behavior, not
  Seafile authorization semantics, atomicity, or persistence.
* `tests/test_gr012_svg.py:202-211` calls the output a document “that holds the
  drawn stroke” but only checks for `<svg` and `<path`. It does not compare the
  serialized path geometry to the requested gesture. The source fixture starts
  with `<rect>` and `<text>` (`tests/fixtures/synthetic.svg`), while VectorCraft
  export may convert the rectangle to a path; changed bytes plus any path could
  pass without proving the intended stroke. The screenshot supports the old run,
  but the assertion is weaker than the claim.
* `tests/test_gr012_svg.py:217-222` treats both “Saved” and “Save failed” as the
  same `saved = True` event. Later revision/history and byte equality checks help
  reject a failed save in normal circumstances, but the status assertion itself
  is not a persistence assertion.
* SVG rows 5.5–5.8 remain unchecked in `docs/TEST-MATRIX.md:72-83`, despite the
  GR-012 bundle's reported proof.
* The repository has no pytest installation/config; its test scripts are
  standalone Python programs. No formatter/linter command is declared.

## Architecture findings

* The gateway uses one dispatcher and one service, which fits the requested
  connector shape. WordCraft/GridCraft use `postMessage`; VectorCraft is a
  separately documented page-API adapter.
* The host contract's save response correctly waits for the gateway's HTTP result
  before replying to an editor ticket. The gateway's `ok: true` may still carry
  `version: null` when the post-write `file_detail` call fails
  (`integration/gateway/server.py:179-190`), which is weaker than
  `docs/SECURITY.md:152`.
* The proof is not the exact target workflow: the DOCX test bypasses Seafile Web
  and the live hook. Under the repository's non-negotiable MVP definition, this
  remains a blocker.
* The current DeckCraft Web source has no bridge, so GR-011 is correctly
  `NOT IMPLEMENTED` / capability-gap deferred; it is not an integration failure.

## Security findings

* `POST /open/` accepts `repo_id/path` without authenticating a user
  (`integration/gateway/server.py:281-297`) and creates a session through the
  gateway account (`server.py:80-95`). A caller who can reach the service and
  knows a repository/path can obtain a session SID; the document and save routes
  then trust that bearer SID (`server.py:252-268`). This contradicts the
  documented user-bound model and enables access to files available to the
  service account.
* For token-based opens, the username comes from Seafile's third-party token,
  but `can_edit` is derived from `file_detail()` called with the gateway's
  account token (`server.py:68-78, 102-117`; `seafile.py:95-99`). Save repeats
  the permission check against that same service account
  (`server.py:165-167`). A user's read-only permission is therefore not proven
  to be enforced; the code can substitute the gateway account's write right.
* CSP, Origin/Referer validation, and rate limiting are absent in the gateway;
  the repository itself says these block exposure beyond the operator
  (`docs/SECURITY.md:169-194`).
* No evidence was found that browser cookies or Seafile account tokens are
  embedded in the frontend. The session ID is a bearer capability and relies on
  correct issuance and containment.

## Data-integrity findings

* `Gateway.save` reads the content ID, compares it, then issues an unconditional
  update (`integration/gateway/server.py:145-170`). The source admits this is
  not compare-and-swap (`server.py:132-138`). Two simultaneous saves can both
  pass the comparison, both report success, and silently overwrite one another;
  this was reproduced with a barriered fake backend. Per the mission's explicit
  rule, that is a BLOCKER.
* The tests exercise stale saves sequentially, so they do not catch the race.
* Save acknowledgement is based on the file server update response; a later
  metadata read is best-effort and can fail while the gateway still returns
  success (`server.py:179-190`). This should be reviewed against the claimed
  “confirmed version” contract.

## Licensing findings

* The repository contains no apparent copied Seahub or proprietary code; the
  connector uses an HTTP boundary. The inspected Seahub root license is
  Apache-2.0, and the inspected Seafile server license is AGPLv3 with exception.
  `docs/LICENSING.md:14-35, 89-90` misstates these as GPLv2/LGPL-ish and derives
  an incompatibility rationale from the wrong license facts. Correct the
  provenance analysis before upstream publication.
* ArtCraft repos inspected in the recorded GR-003 survey are described as MIT OR
  Apache-2.0; the WordCraft checkout's workspace declares the same. This audit
  does not establish maintainer acceptance of a contribution.
* The Seafile patch lives outside this repository and its runtime behavior is
  unverified. Its license and patch provenance need Sol's review.

## Upstream findings

* The upstream artifacts remain unpublished, as required.
* GR-014's WordCraft patch is based on `00bc6a4…`; that commit is its local
  parent. The build passed, but application behavior was not freshly exercised.
  Current upstream WordCraft's page still documents file-picker open and browser
  download save ([source](https://raw.githubusercontent.com/storytold/wordcraft/main/apps/wordcraft-web/src/main.rs)).
* `docs/RFC-DRAFT.md` proposes shared host infrastructure in `craft-libs`. The
  recent public ArtCraft issue #2420 proposes broader shared remote-session
  infrastructure. It is not an equivalent byte-storage integration, but the RFC
  should explicitly position itself alongside it and confirm the appropriate
  upstream home before publication.
* The Seafile patch targets a generic hook, but is only a draft and was not
  executed. Its references to GPLv2 and the claimed licensing incompatibility
  require correction based on the actual target tree.

## Candidate findings

BLOCKER:
- Unauthenticated direct open can mint a session against the gateway's broad
  Seafile account (`integration/gateway/server.py:80-95, 281-313`).
- User write permission is inferred from the service account, not the editing
  user (`server.py:68-78, 102-117, 165-167`; `seafile.py:95-99`).
- Concurrent saves silently overwrite: read-then-write is non-atomic and two
  concurrent calls can both succeed (`server.py:132-170`); reproduced with a
  controlled fake backend.
- The hard-gated Seafile Web → DOCX → WordCraft MVP is not proven by the actual
  browser test, which opens directly through the gateway. No fresh E2E could be
  run because the Seafile environment is unavailable.

MAJOR:
- GR-012's assertion does not verify the expected SVG stroke geometry; its save
  status check accepts “Save failed” (`tests/test_gr012_svg.py:202-222`).
- The licensing analysis misidentifies Seahub and Seafile Server licenses
  (`docs/LICENSING.md:14-35`).
- CSP, CSRF origin checks, and rate limits are absent. The project documents
  these as blockers before non-operator exposure (`docs/SECURITY.md:169-194`).
- The RFC does not discuss the adjacent current upstream Host Mode proposal
  (#2420); its contribution boundary and shared-crate home need reconsideration.

MINOR:
- Gateway can return save success with `version: null` after the post-write
  metadata read fails (`integration/gateway/server.py:179-190`).
- `docs/TEST-MATRIX.md:72-83` does not record the reported SVG coverage.
- The Seafile write patch was not executed against a test Seahub instance; no
  claim of runtime validation is supported.

## Recommendation to Sol

**NOT READY FOR PASS; perform the independent final review, expected result
FAIL.** The current candidate has multiple blockers. Do not remediate before
Sol's first verdict.
