# GR-052 evidence

Base: `a7804a23183c3bc5680028b0a88ac24e4eeb3a86`.
Scope and source references: `docs/GR-052-UPSTREAM-SAVE-RECONCILIATION.md`.

- `gr052-tests.txt`: native synthetic commit-then-status=None reconciliation and failure cases.
- `gr049-tests.txt`: existing receipt behavior.
- `gr050-tests.txt`: existing loopback HTTP retry behavior.
- `gateway-tests.txt`: existing gateway checks.
- `checks.txt`: syntax and whitespace validation.

Independent reviews R1–R3: bounded PROVISIONAL PASS, no blocker/major. R2
requested a deterministic contention signal and correction of stale test counts;
both were fixed and R3 re-reviewed them. GPT REVIEW PENDING; this is not a
project-level PASS. Real Seafile/browser behavior remains NOT VERIFIED.
