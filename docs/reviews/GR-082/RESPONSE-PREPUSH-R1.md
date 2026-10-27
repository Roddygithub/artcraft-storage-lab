# Response to GR-082 pre-push review R1

**Disposition: one MEDIUM and two LOW findings addressed locally; independent
recheck pending. No commit or push has occurred yet.**

1. **Reopen assertion (MEDIUM):** the WordCraft actual-WASM smoke now selects
   and copies text from the freshly reopened editor canvas, then asserts the
   copied text contains the synthetic edit marker after clearing the clipboard. The run log binds the exact test-source SHA-256 and all four asset hashes before and after execution. This supplements the
   persisted-byte check. Final result and exact command are retained in
   `checks/wordcraft-browser-smoke-r8.txt`.
2. **Stale STATUS wording (LOW):** changed “No browser or Seafile result” to
   “No Seafile browser acceptance,” preserving the bounded WordCraft memory
   host result.
3. **Publication wording (LOW):** clarified that a reviewed branch can be
   pushed to this repository, while route promotion, merge, and upstream
   issues/PRs/RFCs remain gated. The live weekly prompt now permits a small
   commit and push to this project's origin only after candidate checks and
   independent review; it forbids pull requests, merges, active route changes,
   ONLYOFFICE changes, and pushes to ArtCraft upstream repositories.

The final browser smoke passed. Seafile persistence, release promotion and
project GPT REVIEW PASS remain outstanding.
