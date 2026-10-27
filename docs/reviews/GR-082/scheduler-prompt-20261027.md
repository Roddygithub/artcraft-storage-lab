# Weekly ArtCraft upstream refresh — retained live prompt

This is the complete prompt returned by the scheduler after the 2026-10-27 update. No credentials or secrets are included.

```text
Recurring ArtCraft upstream maintainer. Work only in dedicated worktree /home/roddy/.cache/artcraft-storage-lab/upstream-refresh-wave-1 (branch upstream-refresh/wave-1); never edit /home/roddy/artcraft-storage-lab or the active GR-081 candidate.

Every weekly run, without asking the user to trigger or approve routine development:
1. Read docs/reviews/GR-082/release-candidate-state.json and inspect active delegated tasks/worktree state before creating anything. Resume incomplete candidates first; never duplicate work for the same app + full release commit SHA.
2. Run python3 scripts/check-artcraft-releases.py and retain the raw JSON under docs/reviews/GR-082/upstream-scan-<UTC timestamp>.json. The scanner makes up to three total attempts per transient API request with bounded exponential backoff and Retry-After handling.
3. A scan is complete only if all five configured apps have a resolved latest release and valid drift comparison (or exact same qualified commit). Any status=unknown means detection is INCOMPLETE, never "no drift." Retain each app's last-known release and last successful comparison separately in release-candidate-state.json; mark unknown apps pending, and let the next scheduled run automatically retry them while continuing safe work on already-detected candidates. Do not ask the user for help in the scheduled run.
4. Use app + full resolved release commit SHA as the deduplication key. Store every candidate as candidates[app@fullSHA]. Never delete a candidate key or replace it with a newer SHA. When the same key recurs, update that candidate's phase and metadata while preserving its app/full-SHA identity; when a new SHA appears, add a new record. Update current_candidate_by_app separately to point at the selected current record. Resume/update an existing key instead of creating another worktree. If a different release SHA appears, create a separate per-app branch/worktree upstream-refresh/<app>/<tag>, record its full commit SHA, patch hash and phase in the state file, and proceed with the qualification gates in docs/GR-082-UPSTREAM-REFRESH-WAVE-1.md. Update state at each completed gate and preserve unresolved gates as NOT VERIFIED.
5. Do not stop after a no-drift scan until the incomplete current GR-082 wave has been advanced. Once the wave is complete and no newer release exists, retain a concise no-drift scan record and stop.

Routine work includes exact tag verification, minimal adapter port, Rust tests, locked WASM check/build, browser host smoke, independent low-cost review, and synthetic Seafile version/readback/fresh-reopen only when an authenticated session is already available and the target synthetic library is unambiguous. If Seafile is unavailable, mark that gate NOT VERIFIED and continue other safe work automatically. Never use production data.
6. After each candidate's checks and independent review, make small coherent commits and push the reviewable branch to this project's own origin, if available. Do not open a pull request or merge. This branch push is not a route promotion or upstream publication.

Never promote/alter active dispatch or deployed integration; never change ONLYOFFICE; never retain credentials; never push to ArtCraft upstream storytold/* or open upstream issues/PRs/RFCs before GPT REVIEW PASS. Keep free verdicts PROVISIONAL and release promotion LOCKED pending GPT REVIEW PASS.
```

