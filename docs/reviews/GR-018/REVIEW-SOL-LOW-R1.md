# GPT-6.1 Sol low — GR-018 bounded review, round 1

**Verdict:** BLOCKED / changes required. This was an independent code review of
the bounded prototype, not a project-level GPT verdict. No files were edited.

## Findings

- **BLOCKER — wasm host mode could panic:** engine save lifecycle called
  `std::time::Instant::now()` on wasm. Replaced by a browser clock.
- **MAJOR — stale SaveAs ACK lost its destination:** if the editor changed while
  the save was pending, successful ACK returned before recording path/title and
  format metadata. The current engine records the committed destination while
  retaining newer edits as dirty.
- **MAJOR — expiry was not enforced at result receipt and no timeout repaint was
  scheduled:** late success could clean the document. The bridge now rejects late
  results and schedules repaint for pending deadlines.
- **MAJOR — exports could produce untracked tickets and TABLEEXPORT discarded
  Pending:** exports now retain ticketed completion and do not clear the drawing.
- **MAJOR — result queue allowed unknown/duplicate messages to crowd out valid
  acknowledgements:** only known outstanding tickets enter the bounded queue,
  and receipt consumes each once.
- **MAJOR — absolute `/tmp/.../platform` dependency is not portable:** remains
  an explicit reproducibility/publication gate; accepted only for a local scratch
  prototype.
- **MINOR — startup failure notification:** restored use of `cadcraft:failed`.

## Verification limits

The original review ran focused tests, a wasm check and `git diff --check`, but
found no CADCraft browser runtime or Seafile persistence proof. Later rounds and
the final bounded disposition are recorded in `REVIEW-SOL-LOW-R2.md` through
`REVIEW-SOL-LOW-R4.md`.
