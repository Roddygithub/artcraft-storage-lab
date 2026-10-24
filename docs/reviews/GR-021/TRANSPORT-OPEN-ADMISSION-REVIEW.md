# GR-021 — Shared Open admission review

**Scope:** shared `craft-platform` receive-side Open buffer admission only.
This is not a project-level GPT verdict, app review, Seafile runtime test, or
deployment approval.

## Finding and remediation

The initial pre-copy hardening rejected oversized buffers and strings before
conversion. A subsequent EffectCraft review found that the app rejected repeat
Open events only after the transport had copied their bytes. A one-Open gate
was added before copying, but independent review found that it broke
in-session `openRequest` flows and that state local to `listen()` could be
bypassed by registering another listener.

The final implementation permits multiple Opens while enforcing a cumulative
256 MiB byte budget and 64-message budget per app/origin runtime. Admission
state is held in a thread-local registry and shared by transports and listeners
for the same origin and app. Type, bounded name, byte representation, and
per-message size are checked before admission; admission is consumed before
either ArrayBuffer or Uint8Array is copied. Oversized/cumulative-overflow
messages and messages after the count cap are rejected before copying.

## Independent review

- Luna high round 1 accepted the pre-copy size/string caps, with browser tests
  compile-checked but not browser-executed.
- Luna high round 2 rejected a one-Open gate because it broke the existing
  same-session GridCraft OpenRequest harness.
- A follow-up review found admission state was scoped to each listener call;
  the final implementation moved it to shared app/origin runtime state.
- Luna high round 4 found no functional issue in cumulative accounting,
  repeated Open compatibility, sharing across transport instances, or bounded
  arithmetic. It noted one “per-listener” doc comment; that wording was changed
  to “per-app runtime” before recording this report.

## Verification

- `./scripts/check-craft-platform.sh`: 7 native tests pass; browser-feature
  WASM `cargo check --tests` passes.
- `sha256sum -c integration/rust/craft-platform/SHA256SUMS`: all 19 entries
  pass.
- `rustfmt --edition 2024 --check` on the changed Rust files and `git diff
  --check`: pass.
- Browser tests were compiled but not run; no browser runner was available.

This package-level change does not prove an app's Seafile save/version/reopen
flow. App patches must pin the resulting immutable transport revision and be
reviewed against it.
