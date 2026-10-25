# GR-059 evidence bundle

Bounded evidence for the real synthetic Seafile deployment documented in
[`docs/GR-059-REAL-SEAFILE-WORDCRAFT-DEPLOYMENT.md`](../../GR-059-REAL-SEAFILE-WORDCRAFT-DEPLOYMENT.md).

## What was exercised

- Authenticated Seafile file-list click for the single synthetic `synthetic.docx`.
- The exact GR-055 staged WordCraft WASM, host open, UI edit, Ctrl+S, gateway
  save response, and WordCraft's new-version confirmation.
- Seafile history page showing a new current version above two earlier versions.
- A second file-list click opening a fresh iframe/session and rendering the edit.
- Post-deployment open-only check for ONLYOFFICE on another synthetic DOCX
  outside the ArtCraft allowlist. No edit/save was made in that check.

## Retained artifacts

- `runtime/browser-observations.txt` — sanitized statuses, history sizes, and
  flow facts. No hostnames, library identifiers, capabilities, auth headers,
  or user identity are retained.
- `runtime/wordcraft-save-confirmed.png` — saved status and edited text.
- `runtime/wordcraft-fresh-reopen.png` — the text visible after a fresh
  Seafile file-list reopen.
- `runtime/onlyoffice-post-deploy-open.png` — ONLYOFFICE opened the synthetic
  out-of-allowlist document after deployment.
- `SHA256SUMS` — hashes for all retained screenshots.

Verify screenshot integrity from this directory:

```sh
sha256sum -c SHA256SUMS
```

The candidate source/bundle and its four-file verifier are retained under
GR-055. The route patches are under GR-015. No live host, repository UUID,
session capability, account token, or other credential is recorded here.

## Scope and verdict

Real synthetic Seafile version creation and fresh-session reopen are evidenced
for this one WordCraft DOCX route. This bundle does not prove the post-deploy
ONLYOFFICE save/version path, permission revocation, external writers,
response-loss recovery, other Craft apps, or production/deployment security.
Independent review is pending. The project verdict remains **INCOMPLETE**;
upstream publication remains **LOCKED**.
