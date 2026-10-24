# GR-024 — Ignore malformed host save acknowledgements

**Status:** bounded shared-transport fix; app consumers must pin the new immutable revision.
This is not a project-level GPT verdict or upstream authorization.

| Field | Value |
|---|---|
| Base | `ee140f37be49517e2e35a542fec0fa9453cba27b` |
| Transport patch SHA-256 (source, package docs, checksums) | `1ed8ef74ee5d0d37653de74d6d7644be1767cf45cd79d32c8fc824fa63f89669` |
| `host.rs` SHA-256 | `c45c37c7267e25328b4ae6d21db195b70476065df295b520d86dbf7734c3b404` |
| Independent review | [`REVIEW-INDEPENDENT.md`](REVIEW-INDEPENDENT.md) |

The browser parser previously converted a missing or non-boolean `ok` field in
`saveResult` to `false`. Apps could consume the save ticket as a known failed
write and permit a retry even though the host's commit outcome was ambiguous.
The parser now ignores malformed results before invoking the app callback.
Valid `ok: true` and `ok: false` messages retain their existing behavior, so
the app leaves malformed outcomes pending for its timeout/unknown-outcome path.

## Checks

- `./scripts/check-craft-platform.sh`: 7 native tests passed; browser-feature
  WASM test targets compile.
- `sha256sum -c SHA256SUMS`: all 19 entries passed.
- Rust formatting on the changed file and `git diff --check` passed.
- Independent read-only review confirmed the exact diff and source hashes,
  parser behavior, compatibility and checksum manifest.

The browser WASM tests were compiled but not executed in a browser. This change
does not establish editor or Seafile runtime behavior.

## Required follow-up

The immutable transport revision changes only after this patch is committed.
Active app patches using earlier pins must be regenerated and rechecked against
the new revision before they are treated as current. No app is added to Seafile
dispatch by this work.
