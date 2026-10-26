# GR-080 — security status and post-change ONLYOFFICE evidence reconciliation

## Result

This documentation-only work reconciles `docs/SECURITY.md` with the later
GR-015 isolated runtime evidence and records a fresh read-only ONLYOFFICE route
check in Seafile's synthetic `OnlyOffice` library. The historical GPT REVIEW
FAIL remains attached to candidate `0edbe524b4fa321b0f73f8601afef390e7f785e6`;
GR-080 does not replace that verdict or claim a new project-level GPT review.

The GR-015 patches were built and exercised in an isolated synthetic Seafile
stack after that candidate was reviewed. The retained evidence includes a
patched C-fileserver token-hook check, synthetic DOCX save/version/reopen,
concurrent conditional saves (one 200, one 409), and a Django save check that
rejects read-only and revoked cached edit grants before token minting or
fileserver calls. The current inspected Seafile host still has no ArtCraft
gateway installed; the unpatched gateway fails closed against stock Seafile.
Production deployment, live permission revocation, external-writer races and
stock/Go fileserver rejection remain **NOT VERIFIED**.

The fresh browser check opened the existing synthetic `synthetic.docx` from the
non-allow-listed `OnlyOffice` library without editing or saving it. Seafile's
configured `/onlyoffice/web-apps/apps/api/documents/api.js` request returned
HTTP 404 with an HTML response, and `window.DocsAPI` was undefined. No editor
instance (`window.docEditor`) or editor frame was created. This confirms the ONLYOFFICE UI regression is
still **INCONCLUSIVE / NOT VERIFIED** in the current lab routing. ONLYOFFICE
settings and service configuration were not changed. Sanitized observation:
[`runtime/onlyoffice-route-check.json`](reviews/GR-080/runtime/onlyoffice-route-check.json).

## Scope and limits

- Documentation reconciliation only; no source patch, Seafile setting, proxy,
  gateway, Document Server, or ONLYOFFICE configuration was changed.
- The browser step was read-only and used only a synthetic DOCX.
- No credentials, cookies, server hostname, user identity, session ID, file
  bytes, or screenshot were retained.
- The isolated GR-015 runtime is separate from the current Seafile lab route
  check; neither establishes production readiness.

Independent review is recorded in
[`reviews/GR-080/README.md`](reviews/GR-080/README.md). Project GPT review
remains PENDING and upstream publication remains LOCKED.
