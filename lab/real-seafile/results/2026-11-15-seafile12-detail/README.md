# Seafile CE12 replay with retained proof details

Re-run of [`2026-11-15-seafile12-replay`](../2026-11-15-seafile12-replay) after
remediating the findings of the targeted CE12 review
([`CE12-REVIEW-5FE30C6.md`](../../../../docs/reviews/PROJECT-CLOSURE-20261115/CE12-REVIEW-5FE30C6.md)).
Same pinned Seafile CE 12.0.14 image (`sha256:7bbe7043…`), same synthetic
accounts and synthetic files, same launcher (`local_ce12.py`,
`launcher_sha256` unchanged), isolated rootless Podman, loopback only. The
owner server and its data/configuration were not used.

## What changed since the replay

1. **The proof is retained, not just the verdict.** The earlier sanitization
   step stripped the `detail` field from every assertion, reducing "Seafile
   created a new version attributed to the opening account" to a bare
   `"ok": true`. The runner always observed those facts; the committed
   sanitizer ([`scripts/sanitize-browser-evidence.py`](../../../../scripts/sanitize-browser-evidence.py))
   now keeps `detail` and redacts only identifiers (synthetic accounts, UUID
   and hex ids, tokens, URL queries), failing closed if a forbidden pattern
   survives.
2. **No unfalsifiable assertions.** Nine assertions were written
   `check(name, True)` and could never fail; three of them ran inside the
   replay and counted toward its 66/66. All nine now assert that the
   navigation did not land on `/accounts/login` and record
   `url_has_login_redirect=False`.
3. **Version assertions emit redaction-safe facts**
   (`version_detail()` in the runner): `history N->M grew=True
   creator_is_opener=True` instead of the raw version record.

## Browser results

| Editor / format | Assertions | Result |
| --- | ---: | --- |
| WordCraft / DOCX | 24/24 | PASS |
| GridCraft / XLSX | 27/27 | PASS |
| DeckCraft / PPTX | 15/15 | PASS |
| **Total** | **66/66** | **PASS** |

## The proof, as retained

The verifier ([`verify.py`](verify.py)) rejects a bare boolean for the central
claims; it requires this content in the retained details:

| Claim | Retained detail (all three editors) |
| --- | --- |
| Save creates a new Seafile version, attributed to the opener | `history 1->2 grew=True creator_is_opener=True` (second saves: `history 2->3 grew=True creator_is_opener=True`) |
| Reopen in a fresh session / from the file list | `url_has_login_redirect=False` |
| Readback equals the saved bytes | `len=6598 vs saved 6598` (WordCraft), `len=4085 vs saved 4085` (GridCraft); DOCX and PPTX also byte-compared |

`SHA256SUMS` pins all 27 retained files; `static-sha256.json` is the exact
extracted editor tree manifest (167 entries) used by the launcher, matching
the WordCraft v0.13.2 / GridCraft v0.14.2 / DeckCraft v0.16.0 bundles.

Run the check from this directory:

```sh
python3 verify.py
sha256sum -c SHA256SUMS
```

## Limits

Same limits as the replay this supersedes: synthetic sequential flows on the
pinned isolated CE12 image only. It does not establish broad Office fidelity,
legacy-format support, hardware acceptance, owner-server access, host-enforced
read-only permissions, or concurrent-writer safety. The known non-atomic WOPI
save window remains. Six DeckCraft assertions still record no detail; they are
boolean results for checks whose substance is retained elsewhere (byte
equality, screenshots).
