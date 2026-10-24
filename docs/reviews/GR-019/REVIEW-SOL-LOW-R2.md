# GR-019 — independent review round 2

**Reviewer:** GPT-6.1 Sol, low

**Verdict:** FAIL — bounded patch review
**Reviewed:** FigCraft base `8d790607ff1ad40e32343ca2116d8fdcf3244c8d`; patch SHA-256 `1bd98b5ec70042ea19cb2f0df42c26b3b0bad59a43590a6d000e73021e30cf83`.

## Finding

### MAJOR — document-creation UI still had three normal bypasses

Host mode did not reject `file.duplicate`, `version.duplicate`, or
`collab.join`. The first two create a second document; the latter can join a
live session and change the document set. These violate the explicit
one-document-per-iframe limit even though host save itself fails closed when
multiple documents exist.

## Previous findings disposition

- Wrong-tab save and dirty-state omission: closed by document-count/active-UID
  checks and dirty reporting across all open tabs.
- Branch creation/open: closed for the inspected command and menu paths.
- Failed `post_ready` leaving transport available: closed; transport and
  listener are dropped on failure.
- ACK snapshot safety: no additional issue found in the inspected lifecycle.

## Remediation planned for round 3

- Reject file and version duplication and all `collab.*` commands through
  `FigApp::run`.
- Reject the direct menu dispatch for branch and collaboration actions.
- Extend the synthetic UI test to invoke the real menu join path and exercise
  file/version duplication commands.

The review inspected the source and tests but did not rerun them. Browser and
Seafile save/version/reopen, timeout runtime, negative ACK, and transport
failure behavior remain **NOT VERIFIED**. This result is not a project GPT
verdict or upstream approval.
