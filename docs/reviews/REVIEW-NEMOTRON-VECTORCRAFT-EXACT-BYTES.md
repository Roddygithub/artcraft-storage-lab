# Independent review — VectorCraft exact-byte polling fix

Date: 2026-10-23  
Reviewed base: `56e1cd6e89bb9743796ab9a959edcd31632d46cf`  
Scope: exact-byte polling remediation only; not an overall project verdict.

## Verdict

**PASS for this bounded remediation.** Nemotron found no blocker or major issue.

## Verified evidence

* The test collision pair `46e9bb16c707a921` and `33d4b4702b82e0e2` contains
  distinct equal-length bytes and collides under the former FNV-1a 32-bit
  fingerprint (`0x4d10285d`).
* The synthetic Chromium test verifies unchanged output causes no write, changed
  colliding output is persisted exactly once, and another identical poll causes
  no duplicate write.
* The post-fix isolated Seafile/VectorCraft run saved 695 bytes, obtained a new
  Seafile version/file ID, read back bytes with matching SHA-256
  `e5cd9d2e39f80ef3194d5c2ae08b45cd7180046f35604c9035b41fa827c2ef23`, and
  reopened the SVG with the path at `{x:300,y:100,width:100,height:50}`.

## Minor findings and remaining limits

1. VectorCraft has no dirty signal, so `beforeunload` only warns during an
   in-flight save, not for every unsaved edit.
2. VectorCraft save-failure retry and concurrent saves are not tested.
3. The iframe has no `sandbox` attribute and the host page has no CSP.
4. This remains a VectorCraft-specific private page API, not proof of the common
   host contract or all-app support.

This narrow PASS does not change the GPT-6.1 Sol FAIL on candidate
`0edbe524b4fa321b0f73f8601afef390e7f785e6`, establish production readiness, or
unlock upstream publication.
