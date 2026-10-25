# GR-049 evidence

Base: `7238bc85b3816a6acfc1230c3cb1fb3172e1b696`.
Artifact: `docs/GR-049-IDEMPOTENT-SAVE-RETRY.md`.

- `retry-tests.txt`: six synthetic regression tests; direct save calls simulate
  loss of the already committed result. No real network-loss reproduction.
- `gateway-tests.txt`: existing gateway unit checks, including separate-session
  CAS race and HTTP origin/session security checks.
- `checks.txt`: syntax and whitespace validation.

Independent R1 review returned **PROVISIONAL PASS**, with no blocker, major,
minor, or actionable P3 finding; see `INDEPENDENT-REVIEW-R1.md`. The reviewer
did not run tests or services. GR-050 adds an independently reviewed loopback
HTTP response-loss regression. Browser retry and real Seafile
version/readback/reopen remain **NOT VERIFIED**. The work item is
GPT REVIEW PENDING; this does not change the project verdict or authorize
upstream publication.

Follow-up: GR-050 adds deterministic real-route loopback socket response-loss
coverage; see `../GR-050/README.md`. Original GR-049 runs remain direct-call
evidence; this follow-up does not extend the scope of its independent review.
