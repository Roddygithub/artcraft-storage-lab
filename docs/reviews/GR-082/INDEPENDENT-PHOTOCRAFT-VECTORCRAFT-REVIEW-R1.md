# GR-082 PhotoCraft and VectorCraft release-smoke review R1

**Verdict: bounded PROVISIONAL PASS with two LOW documentation findings.** No
high or medium issue was identified in this read-only evidence review. This
does not accept either release for Seafile or production.

## Findings

1. **LOW — PhotoCraft report retained stale current-tense wording.** The
   packaging-stage text at `ports/photocraft-v0.16.0.md` said the Web/UI tests
   were still unverified, although the later follow-up recorded 6/6 Web and
   8/8 UI focused tests passing. It also described all three suites as
   unverified without distinguishing the engine snapshot suite that remains
   open. Remediation: label the earlier result as a historical checkpoint and
   point to the later Web/UI results; keep the engine snapshot limitation.
2. **LOW — broken browser-test link.** The PhotoCraft report used
   `../../../tests/test_photocraft_gr082_release.py`, which resolved under
   `docs/tests/`. Remediation: use the repository-root-relative depth
   `../../../../tests/test_photocraft_gr082_release.py`.

## Evidence checks

- PhotoCraft's saved `.pcraft` hash and the hashes of its edited, saved and
  reopened screenshots match the retained artifacts. The images visibly show
  the black stroke before and after the memory-host save. The test asserts the
  created layer, native identity and clean fresh-iframe reopen; it does not
  programmatically compare stroke pixels.
- The optional `fonts/manifest.txt` 404 matches the v0.16.0 source comment that
  absence of the custom-font manifest is the normal case. Custom-font behavior
  is not covered.
- VectorCraft's saved SVG, reopened geometry JSON and capture agree. Its R2
  test checks memory-host save/reopen through the page API; it does not prove
  native host ACK, Ctrl+S/menu-export dirty-state behavior, or Seafile storage.
- The summaries preserve the in-memory boundary. Seafile persistence and
  history, PhotoCraft gateway identity-mode enablement, ONLYOFFICE, deployment
  and project GPT approval remain open.
- No credentials or production document content were identified in the
  inspected artifacts.

## Scope

Read-only inspection of the current `upstream-refresh/wave-1` worktree. No
files edited, tests/builds run, browser sessions opened, network or service
access, commits or pushes.
