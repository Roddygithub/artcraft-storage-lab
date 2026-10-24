# GR-017 bounded review — GPT-6.1 Sol low, round 3

**Result:** FAIL for this bounded prototype only. No project-level verdict.

## Findings

- **BLOCKER:** none found in this round.
- **MAJOR:** none found in this round.
- **MINOR — callback cap could be bypassed across follow-up saves.**
  `retry_host_save` wrapped a vector of retained callbacks in one closure. The
  next save counted that wrapper as one callback, allowing repeated
  edit/save/ack cycles to exceed the intended per-document limit.
- **MINOR — lifecycle test coverage remained incomplete.** Tests constructed
  pending records directly and did not test timeout execution, Save As,
  response-loss/capacity recovery, or actual browser submission.

## Prior findings disposition

- Form and paragraph UI drafts are committed before acknowledgement settlement;
  their close callbacks cannot discard newer typing.
- Same-generation coalesced saves preserve close callbacks.
- Tickets expire after 120 seconds and closed tabs release app snapshots.
- Browser timeout closures are now owned by ticket and released on ACK, send
  failure, or processed timeout.
- Independent reviewer confirmed patch/source consistency at SHA-256
  `6e46d56bb6a3aa045d2e242739516449a3d69b7cb83c6646a1ca4f1c8e577507` and
  origin/source checks. Sol independently ran `git diff --check`; native,
  WASM, Trunk and browser claims were not independently reproduced in round 3.

## Remediation in current patch

- Replace raw callbacks with `HostSaveAfter`, which carries the retained
  callback count through aggregation and follow-up saves.
- Enforce the 64-callback cap by the retained count, not wrapper-vector length.
- Extend the cap test to create a 64-callback aggregate, then prove another
  callback is rejected.

The current source passes 7 focused native tests and Rust 1.95 WASM `cargo
check`. Release/browser smoke evidence exists for the earlier timer-and-ACK
version; the latest callback-count-only change was not run through Trunk or
Chromium. The synthetic browser smoke used `sessionStorage`, not Seafile.
The follow-up patch archived at `patches/pdfcraft-durable-host-ack.patch` has
SHA-256 `de30f47e823536c8b99d4d718a0731f8afdc1f56537deceec3d77f9ffda7fbf5`.
Round 4 must review this exact patch. Upstream publication and overall project
GPT status are unchanged.
