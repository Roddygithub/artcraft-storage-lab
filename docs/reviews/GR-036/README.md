# GR-036 evidence bundle

This directory records a PhotoCraft host Open/edit/save/ACK/version/reopen
reproduction on the isolated synthetic Seafile stack.

| Artifact | Purpose | SHA-256 |
|---|---|---|
| `photocraft-host-repaint.patch` | Incremental repaint request after host-message queueing, based on the GR-032 adapter | `e3af083933f035ddb557f67a1d3d148a9056780dc46c135e93f1722e5acf584e` |
| `runtime/photocraft-seafile-reopen-20261025.png` | Fresh Seahub reopen showing the saved layer | `70d28c90f7ece27782863fbb15d98be74ac81ac89d9535782fe0aae13f0aecab` |
| `runtime/seafile-readback.json` | Redacted result of a later read-only Seafile history/detail/content GET | `00e132139eb4f694de8ef3f22d5bbb4b2d41e5310709eacf81e1c777bba510ba` |
| `runtime/verify_seafile_readback.py` | Reproducible GET-only history, hash and ZIP manifest verification | `564540c2706a3b3336b66ea283df4b0dfaf8edb04ade9810a1d9833557c93a4f` |

The Web build was a release-profile functional reproduction with `wasm-opt=0`.
It loaded WASM SHA-256
`d4f339df6312429fa15de653a37b3ef156cee84a3c58eee1358caee34523324c`
(35,820,040 bytes). Seafile history and object readback are recorded in
[`docs/GR-036-PHOTOCRAFT-SEAFILE-E2E.md`](../../GR-036-PHOTOCRAFT-SEAFILE-E2E.md).

The fixture, browser profile, session capability, API token and service state
are not included. The dispatcher was temporary to the synthetic test and is
not changed in the repository.

Independent bounded review: **PROVISIONAL ACCEPT**, no blocker/major. R1's
history/readback evidence qualification was addressed with the retained JSON
and GET-only verifier; the R2 stale duplicate README entry was removed. Review
details: [`INDEPENDENT-REVIEW.md`](INDEPENDENT-REVIEW.md).

Independent bounded review: **PROVISIONAL ACCEPT**, no blocker/major. The
reviewer noted that history and readback metrics were initially report-only;
the retained JSON and GET-only verifier were added after a separate read-only
API check. The reviewer did not run services or access Seafile.
