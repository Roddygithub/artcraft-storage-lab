# GR-021 shared transport pre-copy bounds

**Bounded independent review: PASS** — no findings on this package remediation.

The GR-021 DesignCraft review found that its 64 MiB application limit ran only
after `craft-platform` had copied an incoming `ArrayBuffer` or `Uint8Array` into
a Rust `Vec`. It also found unbounded JavaScript string conversion for message
metadata. The shared parser now checks the typed-array or buffer length before
copying, with a 256 MiB transport ceiling, and checks UTF-16 code-unit limits
before converting `type` (128), `name` (1,024), `ticket` (256), and `error`
(4,096) fields to Rust strings.

## Verification

| Check | Result |
|---|---|
| `./scripts/check-craft-platform.sh` | PASS: six native tests; WASM browser-feature `cargo check --tests` passes |
| `rustfmt --check --edition 2024 integration/rust/craft-platform/src/browser/host.rs` | PASS |
| `sh -n scripts/check-craft-platform.sh` | PASS |
| `(cd integration/rust/craft-platform && sha256sum -c SHA256SUMS)` | PASS, all 19 entries |
| `git diff --check` | PASS |

The new browser tests for over-limit byte buffers and metadata strings compile
for WASM but were **not executed**: this environment has no
`wasm-bindgen-test-runner` or browser executable. This change does not establish
browser runtime behavior, Seafile persistence, or public deployment readiness.

The independent reviewer verified the exact source diff, found no alternate
inbound message parser in `integration/rust`, confirmed the byte and metadata
checks precede copies/conversion, and verified the package checksums. No source
outside the host transport parser and its check/provenance artifacts changed.

## Prior finding

`HostEventBuffer::enqueue` in the DesignCraft adapter rejects payloads larger
than 64 MiB after transport delivery. This package fix adds a prior 256 MiB
transport cap before allocation; app-level caps still apply after that. The
DesignCraft patch must be repinned to this new package revision and receive an
exact-patch re-review before it can be accepted.
