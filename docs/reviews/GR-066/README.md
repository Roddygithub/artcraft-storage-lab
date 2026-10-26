# GR-066 evidence — FilmCraft on synthetic Seafile

This bundle records the exact GR-047 FilmCraft Web candidate opening a native
project from the Seafile file list, saving a visible edit through the host
protocol, and reopening it from the file list in a fresh editor session.

## Evidence

- [`runtime/save-confirmation.png`](runtime/save-confirmation.png) — Program
  monitor edit and Seafile's new-version confirmation. The transient
  `Saved to host` editor status is recorded in
  [`runtime/browser-observations.txt`](runtime/browser-observations.txt).
- [`runtime/fresh-session-reopen.png`](runtime/fresh-session-reopen.png) —
  `GR-066 Film` visible in the Program monitor after reopening from Seafile.
- [`runtime/seafile-file-list.png`](runtime/seafile-file-list.png) —
  synthetic library listing the setup fixture after the saved version.
- [`runtime/browser-observations.txt`](runtime/browser-observations.txt) —
  sanitized event sequence and HTTP statuses. Session capabilities, private
  origin, repository identifier, and account identity are omitted.
- [`hash-inventory.json`](hash-inventory.json) and
  [`verify_candidate.py`](verify_candidate.py) — exact candidate membership,
  sizes, hashes, and HTML/runtime asset references.
- [`SHA256SUMS`](SHA256SUMS) — digests for the retained screenshots and
  sanitized transcript.

The package was reused without rebuilding from
`/home/roddy/.cache/artcraft-filmcraft-gr021/target/web/dist`; the staged
candidate and active local static-root files matched all five hashes. The
Seafile History panel was inspected but its screenshot is omitted because it
displayed the account name. No screenshot, request-body hash, or readback hash
is claimed for the history/payload boundary.

The scoped `.fcproj` route, same-tab popup shim, single synthetic library, and
ONLYOFFICE limits are described in the
[GR-066 report](../../GR-066-FILMCRAFT-REAL-SEAFILE-ROUNDTRIP.md). This is not
a project-level GPT PASS or upstream authorization.
