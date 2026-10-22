# Seafile integration points

Status: **GPT review failed on candidate `c76a7594`; remediation is in progress.**
GR-002 · Architecture: `artcraft-architect` (original research; current facts below were rechecked on 2026-10-22)

## Current deployment facts

- The live instance is Seafile Pro 12.0.14 on LXC 108, reached through the Tailscale HTTPS hostname.
- `ENABLE_ONLYOFFICE = True`; its 15 configured file extensions were left unchanged.
- `THIRDPARTY_EDITOR_ACTION_URL_DICT = {}`. The former global `.xlsx` route to `127.0.0.1:8777` was removed because it shadowed ONLYOFFICE and browser loopback would point at the client machine.
- Seahub and nginx are active. No ArtCraft gateway listens on LXC 108, and no new Nginx route was installed.
- The original config is backed up on LXC 108 at `/root/seahub_settings.py.artcraft-rollback-20261022`.
- The synthetic test library is `c82cc792-389d-43e6-b963-0dab1a47a9a8` (`OnlyOffice`), folder `/artcraft-lab/`. No real document has been written by this remediation.

## What Seafile's built-in hook does

Seahub includes `seahub/thirdparty_editor/`. The stock hook maps file extensions globally, creates a short-lived token bound to a user/repository/path, and exposes file info and content. The stock view code sets `can_edit` to false and provides no safe write endpoint. Its branch is evaluated before ONLYOFFICE, so a globally registered extension takes precedence over ONLYOFFICE for that extension.

Sources: deployed Seahub 12.0.14 `seahub/views/file.py` and `seahub/thirdparty_editor/{settings,urls,views}.py`; local exact-source checkout and the initial read-only inspection are recorded in `docs/reviews/GR-001/` and `docs/reviews/GR-015/README.md`.

## Current architecture decision

The stock global extension map is not sufficient for this project. The candidate remediation prepares an additive Seahub/Seafile Server change that:

1. Routes configured file extensions only for an explicit repository allowlist, preserving ONLYOFFICE behavior in other libraries.
2. Binds editor reads and saves to the user, repository, path, original filename, current file ID, and repository head recorded when the file opens.
3. Rechecks the user's current web-edit permission at save time.
4. Requires an atomic server-side compare-and-swap before commit; a stale file or library head must return conflict instead of overwriting newer data.
5. Reports success only after Seafile returns a committed file ID and repository head.

The patch is only a draft against the exact deployed sources. It has not been compiled, installed, or exercised against Seafile. The gateway is also not installed on the server. See [`GR-015`](reviews/GR-015/README.md).

## Required end-to-end proof

The representative workflow remains:

```text
Seafile Web file-list click
→ WordCraft Web opens the actual synthetic DOCX
→ edit and serialize in WordCraft
→ user-bound conditional Seafile save
→ new Seafile version
→ close and reopen from Seafile Web
→ semantic edit is still present
```

This has **not** been verified. The browser preview currently shows the Seafile login page, and no authenticated file-list click was performed. Unit tests use a fake Seafile/CAS implementation; they do not prove Seafile persistence or ONLYOFFICE preservation.

## Scope for the full suite

A single Seafile connector and file-type dispatcher should route only apps whose web build implements the shared host/save bridge. The current app capability inventory is in `docs/ARTCRAFT-GLOBAL-INTEGRATION.md` and `docs/ARTCRAFT-WEB-CAPABILITIES.md`. WordCraft is the representative office MVP. GridCraft needs a real workbook semantic round-trip. VectorCraft/SVG can prove a non-Office format only after its editor-generated output is persisted and reopened. Apps without a working bridge remain unsupported; DeckCraft is blocked by its upstream bridge gap. Do not claim “all ArtCraft apps” until each supported route has an editor-specific proof.

## Readiness boundaries

| Target | Current status |
| --- | --- |
| Local prototype code and fake-CAS unit checks | available; tests pass locally |
| Local self-hosted Seafile test | not ready: source patch unbuilt and gateway not installed |
| LAN/Tailscale use | not approved: save, CSRF/CSP, rate limiting, and browser origin behavior need verification |
| Public internet | not ready; see `docs/SECURITY.md` |
| Upstream RFC/patch publication | locked until a final independent GPT review PASS and later explicit user approval |
