# Independent Nemotron review — `36c0bc0`

Date: 2026-10-23  
Reviewed SHA: `36c0bc0f2b534b34c52193519fbb422ac5c22948`  
Scope: diff from `e513c6ae8f076f5abc07bb5f9634a7c6975cba5b`, GR-015 isolated
runtime report, source/tests, and earlier review findings.  
Verdict: **FAIL for candidate readiness**.

## Verified by reviewer

- The synthetic Seahub and gateway used distinct loopback origins (`:18000`
  and `:18777`); Chromium enforced the cross-origin boundary.
- The patched C server accepted the `op=update` route token and rejected an
  `op=view` token.
- The isolated run recorded a real WordCraft edit, conditional save, new
  Seafile file ID/head/history, and subsequent content readback.
- Exact pinned patches applied and the C fileserver build/runtime checks passed.
- The evidence report explicitly acknowledged that the separate-origin run
  had not captured editor save confirmation.

## Blockers

1. **ONLYOFFICE regression not run.** The scratch stack had no ONLYOFFICE.
   The existing Seafile document route is a compatibility constraint; a source
   branch check does not demonstrate that the prior edit/save/version/reopen
   workflow remains intact.
2. **Authorization edge cases not runtime-tested.** Permission revocation,
   read-only bypass, expiry/replay, cross-user access, and external-writer races
   remain unverified against the running stack.
3. **Production security topology not verified.** Loopback testing does not
   exercise TLS termination, reverse-proxy trust, CSP, CSRF, rate limits,
   cookie isolation, or adversarial editor frames.

## Major findings

- GridCraft and VectorCraft still lack demonstrated Seafile durable-save
  acknowledgement and semantic reopen; their adapters are not proven to meet
  the WordCraft save contract.
- Stock/Go fileserver rejection was inferred from route absence, not exercised
  against a running unsupported server.
- Same-editor overlapping tickets, stale same-content saves, response loss,
  retries, duplicate commits, and crash windows remain untested.
- Licensing and redistribution notices for the patched multi-repository
  artifacts need resolution before publication.

## Minor findings

- The matrix and older GR-012 labels still mix prototype evidence and verified
  E2E wording in places.
- The recorded server patch has trailing whitespace in context lines.
- Rollback was not exercised.

## Assessment

The isolated synthetic prototype is **functional for the demonstrated DOCX
path**. It is not a GPT-reviewed candidate, production deployment, or upstream
release. Nemotron recommended testing ONLYOFFICE dispatch/preservation,
authorization revocation and expiry, unsupported fileserver rejection, a
production-shaped origin topology, and remaining Craft workflows before
freezing a candidate.

### Follow-up after this review

The same synthetic browser session later completed another WordCraft save and
exposed `Saved — new version`, `dirty=false`, and `confirmedSave=true`. A fresh
Seafile file-view session then fetched a valid DOCX containing the new marker
and the winning concurrent edit, with the losing edit absent. This strengthens
the local DOCX evidence; it does not test ONLYOFFICE or close the other findings.

No GPT-6.1 Sol review was requested. The current SHA remains an unreviewed local
remediation tip; upstream publication remains locked.
