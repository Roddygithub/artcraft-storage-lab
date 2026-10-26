# GR-067 evidence — EffectCraft on synthetic Seafile

This bundle records the GR-046 EffectCraft Web candidate opening a native
project from the Seafile file list, saving a visible edit through the host
protocol, and reopening it from the file list in a fresh editor session.

## Evidence

- [`runtime/save-confirmation.png`](runtime/save-confirmation.png) — visible
  canvas edit and Seafile's new-version confirmation. The history page
  screenshot is omitted because it exposed the account display name.
- [`runtime/fresh-reopen.png`](runtime/fresh-reopen.png) — the saved composition
  after the new file-list open. The long centered label is cropped at the
  composition edges, but the `GR-067` text is visible.
- [`runtime/browser-observations.txt`](runtime/browser-observations.txt) —
  sanitized event sequence and HTTP statuses. Private origin, repository ID,
  session capability, and account identity are omitted.
- [`candidate-inventory.json`](candidate-inventory.json) and
  [`verify_candidate.py`](verify_candidate.py) — exact candidate file
  membership, sizes, and hashes across build, staged, and active roots.
- [`SHA256SUMS`](SHA256SUMS) — retained screenshot and transcript hashes.

The existing GR-046 candidate was reused without rebuilding. One initial page
load found a missing runtime snippet in the copied static roots; it was restored
from the exact build output, verified by SHA-256, and the successful retry
returned HTTP 200 for all app assets. The successful run used only the existing
synthetic Seafile library. The temporary `.ecproj` route and Seahub extension
allowlist entry were restored after the test; ONLYOFFICE remained enabled.

No save-message or readback bytes were retained for hashing. The browser save,
Seafile Versions page, and fresh session support durable persistence but do not
prove byte identity. The complete scope and limits are in the
[GR-067 report](../../GR-067-EFFECTCRAFT-REAL-SEAFILE-ROUNDTRIP.md). This is
not a project-level GPT PASS or upstream authorization.

R1 returned a bounded PROVISIONAL PASS with no findings. The exact review
record is in [`INDEPENDENT-REVIEW-R1.md`](INDEPENDENT-REVIEW-R1.md).
