# Independent review — `d2379f04602b67c6bdd6456337fe4aa178feb59f`

**Reviewer:** OpenAI GPT-6 Sol, delegated T3 review task
`artcraft-sol-final-d2379f0-20261115-r1`
**Verdict:** **PROVISIONAL PASS for the isolated MVP subset only**

The reviewer inspected the exact candidate worktree, found it clean, and reran
the three retained evidence verifiers. They passed. The reviewer did not rerun
the live lab or the 20 offline groups; those totals are supported by retained
summaries, not this review's own execution.

## Findings

* **ACCEPTED — bounded subset:** synthetic DOCX typed saves create versions and
  survive a fresh-session reopen. Four opt-in legacy routes have exact bytes,
  visible markers, read-only UI, and no version change on open. These claims do
  not establish broad format fidelity.
* **MAJOR — production permission boundary:** CE 13.0.28 accepted direct
  `PutFile` with a read-only WOPI token. The bridge refuses its own relay, but
  cannot enforce Seahub's direct endpoint. `read-only` is accurate for the
  bridge/UI route, not a host-side security guarantee. The reproduced host
  bypass used a read-only SVG token.
* **ACCEPTED / LIMITATION — concurrency:** version preflight plus unconditional
  `PutFile` retains a TOCTOU race. Readback cannot make the write atomic. The
  owner accepted this limit for the zero-patch MVP.
* **MINOR — wording:** viewing-config labels claimed DOC/XLS host failures not
  retained as exact-source evidence; a historical matrix paragraph did not mark
  its FODS route as superseded. Both are corrected in the follow-up candidate.
* **LIMITATION — audit scope:** the 20-directory inventory has checksums for 20
  directories, 17 available verifiers, 16 provenance files and two loose JSON
  files. It is a pattern-based mechanical self-audit, not 20 complete evidence
  chains or independent review.
* **NOT VERIFIED:** DOC/XLS host rendering, legacy saves, arbitrary-file
  fidelity, authenticated owner-server edit/save, and physical hardware/browser
  acceptance. Eight legacy formats are unrouted. Earlier free-review source
  transcripts are unavailable.

## Readiness conclusion

The isolated MVP subset is ready for its narrowly stated lab scope. Full
ONLYOFFICE replacement is **not complete**. The review grants no production
approval, atomic-save guarantee, or project-wide GPT PASS.

The underlying delegated review result is retained in the T3 conversation; this
file is a concise report, not a verbatim transcript.
