# Forensic audit — retained evidence at `d2ed680` (2026-11-10)

**State: mechanical self-audit by the implementer. This is NOT an independent
forensic review and does not grant a project PASS.** Project INCOMPLETE; upstream
LOCKED.

`scripts/forensic-audit.py` re-checks what is committed, not what a lab run
claims while it is private:

* every `SHA256SUMS` entry in `lab/real-seafile/results/` (hash, membership,
  unsafe paths);
* every retained `verify.py`, executed in its directory;
* every commit SHA found in `provenance.json`, required to exist and to be an
  ancestor of `HEAD`;
* retained `*.json` for per-run Seafile accounts (`@auth.local`), synthetic ids,
  plain `WOPISrc`, unredacted WOPI file ids, token fields and `repo_id` keys.

## Result at `d2ed680dc255`

```text
PASS: 17 evidence directories, hashes, verifiers, provenance and secret scan at d2ed680dc255
```

| Check | Result |
| --- | --- |
| Evidence directories | 17 |
| `SHA256SUMS` integrity / coverage | PASS |
| `verify.py` present and passing | 14 of 14 present |
| Provenance commits exist and are ancestors | PASS |
| Secret/identifier scan of retained JSON | PASS |

Directories without `verify.py` (`2026-11-08-combined-core-recovery`,
`2026-11-08-save-safety`, `2026-11-08-wordcraft-fidelity-edit`) are reported as
`verifier=False`; their hashes and provenance still pass. They are not upgraded
to verified evidence by this audit.

## Findings repaired by this audit

| Finding | Action |
| --- | --- |
| `2026-11-08-legacy-viewing/slice.json` retained four `@auth.local` account values | Replaced with `<run-admin>`; its `verify.py` now rejects `@auth.local`; sums recomputed and verifier PASS |
| Retained relay-bytes summaries carried `repo_id`, `WOPISrc` values, a WOPI file id and synthetic accounts | Sanitized before retention; `results/2026-11-10-viewing-relay-bytes/verify.py` rejects them |
| Generated `__pycache__/verify.cpython-314.pyc` inside an evidence directory | Removed; audit ignores generated `*.pyc` |
| Date tokens (`20261108`, `20261109`, `20261110`) treated as commit SHAs | Audit no longer treats 8-digit `20…` tokens as commits |

## What this establishes and what it does not

It establishes that the committed evidence is internally consistent, that its
recorded source commits belong to this history, and that the retained summaries
no longer carry per-run account identifiers or WOPI secrets.

It does **not** re-run Seafile or a browser, authenticate chronology, prove that
a run happened as described, review implementation quality, or replace the
independent forensic/project review. The implementer wrote both the changes and
this audit; AGENTS.md requires a different context for review.

## Reproduce

```sh
python3 scripts/forensic-audit.py --output /absolute/new/private-dir
```

Expected: `PASS: 17 evidence directories …` at the audited `HEAD`.
