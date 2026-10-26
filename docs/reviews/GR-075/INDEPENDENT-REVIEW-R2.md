# GR-075 independent review R2 — test synchronization and cleanup

**Verdict:** bounded PROVISIONAL review with two MINOR test findings. No
production-code major defect was identified. This is not project GPT approval.

## Findings

1. The first remediation signaled from a wrapper before the original reader
   created its deadline. The reviewer inserted a 70 ms delay after that signal;
   the valid request then completed within the 250 ms budget, clearing dirty
   state and invalidating the test's expected 408. Synchronizing with wrapper
   entry therefore did not prove deadline start.
2. The class override was installed before socket creation, which was outside
   `try/finally`. A simulated connection failure left both class attributes
   patched.

## Remediation in the current working tree

The test now wraps only the target handler's `rfile` with a tiny delegating
reader that signals immediately before the first `read1`. Production code has
already created the absolute deadline and set the socket timeout by this point.
The client begins sending only after this signal; subsequent bytes arrive every
90 ms, four intervals (360 ms) after the deadline begins, while each interval
remains below the 250 ms inactivity timeout. Overrides are installed and the
socket acquired inside `try`; `finally` restores both class attributes, closes
any acquired socket, and joins the sender if started.

R2 also verified the production reader with local socket-pair probes, including
buffered/pipelined boundaries, a 150,000-byte multi-chunk body, truncated EOF,
stalled-body timeout, and restoration of a prior socket timeout. Those probes
are reviewer-reported and were not retained as repository tests.

Independent R3 verification is pending. The 120-second policy, header-read
deadline, reverse-proxy behavior, and other Python versions remain unverified.
