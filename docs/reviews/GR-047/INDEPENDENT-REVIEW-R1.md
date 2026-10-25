# GR-047 independent review R1

**Bounded result: PROVISIONAL PASS, no blocker or major finding; one minor
evidence gap.** The reviewer found that the report listed build and packaged
WASM/JS/HTML hashes but retained neither those outputs nor a browser network
snapshot, so the hashes and exact assets loaded by Chromium could not be
independently verified from the bundle. The runtime payload, fixture, host and
screenshot hashes did match; the screenshot showed the synthetic save ticket,
clean state and fresh-instance render. Seafile persistence remains unverified.

## Follow-up

The owner replayed the exact cached build in Chromium on loopback and retained
the browser's successful asset request list, response-body hashes, fixture
hash, edit/save/ACK/reopen result, and a fresh-iframe screenshot in
[`runtime/replay-20261025.txt`](runtime/replay-20261025.txt) and
[`runtime/filmcraft-review-replay.png`](runtime/filmcraft-review-replay.png).
This supplements the original worker run; it does not claim durable storage.

The R2 review confirmed the browser-served assets and flow, with a remaining
minor for the separate pre-packaging WASM hash. That cache artifact has since
been checked and is documented in
[`INDEPENDENT-REVIEW-R2.md`](INDEPENDENT-REVIEW-R2.md). R3 subsequently
returned bounded PROVISIONAL PASS with no findings; no project-level GPT PASS
is implied.

## Checks performed by reviewer

- Verified the GR-023 stored patch SHA, local regenerated diff SHA, source pin,
  transport pin and retained fixture/host/screenshot hashes.
- Inspected the report, evidence bundle, harness and project tracking files.
- Ran `git diff --check`; no browser replay or build was performed in this
  review round.

The separate owner replay is recorded above and in its own supplemental
transcript.
