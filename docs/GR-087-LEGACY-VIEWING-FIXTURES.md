# GR-087 — legacy / OpenDocument viewing fixtures and routing

**State: GPT REVIEW PENDING. Project INCOMPLETE. Upstream LOCKED.**

Candidate reviewed by the free pass: `2c112fc` (branch
`work/project-closure-20261108`). The source that produced the retained runtime
evidence is `4f4b2dc`; `0dd3d25` and `2c112fc` add documentation, fixtures, a
bridge signature extension and tests only. This claim is verifiable with
`git diff 4f4b2dc 2c112fc -- bridge/ lab/`.

## What this work item produces

The ONLYOFFICE replacement matrix still listed twelve *viewing* formats with no
deterministic test input and no candidate route. This item supplies the missing
test input and a bounded, honest routing candidate. It does **not** claim any
format is replaced.

| Element | Path |
| --- | --- |
| One synthetic fixture per format | `lab/real-seafile/fixtures/legacy/` |
| Provenance and limits | `lab/real-seafile/fixtures/legacy/PROVENANCE.txt` |
| Pinned bytes | `lab/real-seafile/fixtures/legacy/SHA256SUMS` |
| Regeneration recipe | `scripts/make-legacy-fixtures.sh` |
| Opt-in routing candidate | `lab/real-seafile/editors.viewing.json` |
| Offline check | `tests/test_legacy_fixtures.py` |
| Signature guard additions | `bridge/app.py` (`content_matches_extension`, `SIGNATURE_KNOWN`) |
| Signature tests | `tests/bridge/test_bridge.py` (`test_signature_covers_legacy_office_and_opendocument`) |

Formats covered: DOC, ODT, FODT, XLS, ODS, FODS, CSV, PPT, ODP, FODP, PPS,
PPSX. Each fixture carries `GR-LEGACY-MARKER-20261108` in its real content
(UTF-16LE in the OLE binaries, `content.xml` in the ODF ZIPs, plain XML/text in
FODT/FODS/FODP/CSV).

The bridge name-to-bytes guard now recognises DOC/XLS/PPT/PPS (OLE compound
file), PPSX (OPC package with a `ppt/` part) and FODT/FODS/FODP (flat
OpenDocument `office:document`). CSV stays deliberately unguarded — it has no
strong signature — and remains listed as unguarded in `SIGNATURE_KNOWN`.

The routing candidate maps only formats with a documented upstream import:
DOC/ODT to WordCraft, ODS/CSV to GridCraft. The other eight formats have no
documented Craft import and stay unrouted.

## Evidence

* Offline validation at `2c112fc`: **20/20 command groups PASS**
  (`scripts/validate-candidate.py`), which now includes
  `tests/test_legacy_fixtures.py`.
* `tests/bridge/test_bridge.py`: **33 tests OK** (was 32).
* Fixture bytes and their SHA-256 are committed; `PROVENANCE.txt` records the
  exact container image id (`72717717d6ce…`) and the disclosed limit that
  `slide.pps` and `slide.ppt` are byte-identical under this LibreOffice.

## Independent review

* `artcraft-gpt-auditor` (GPT-5.6 Luna) — **not run**: the provider returned
  "The usage limit has been reached". Recorded in `docs/AI-ROUTING.md`.
* `artcraft-reviewer` (Nemotron 3 Ultra 550B, `#high`) — **PROVISIONAL PASS**,
  no blocker and no major. It independently ran the bridge suite (33 OK) and the
  legacy fixture test (6 OK) and inspected the bridge, host page and security
  docs. Its minors are test-gap and deployment-gate observations, several of
  which are already covered by existing tests (revoked token 401, expired
  session GR-043). All free verdicts are PROVISIONAL.

## Explicit limits (NOT VERIFIED)

* No runtime import of any legacy/OpenDocument format in a real Seafile +
  browser session. The fixtures and routing are offline-only evidence.
* No format is declared replaced; the eight formats with no documented Craft
  import remain without a candidate route.
* Human HTTPS desktop acceptance remains pending.
* The project-level GPT gate cannot run while the `openai` provider quota is
  exhausted (the Sol final reviewer uses the same provider).

## Next steps

1. Add a bounded lab viewing probe: run the four documented-import routes
   (DOC/ODT via WordCraft ≥ 0.16.0, ODS/CSV via GridCraft ≥ 0.17.0) through a
   real Seafile click and assert the marker is rendered, not downloaded.
2. Keep the eight import-less formats unrouted and disclosed.
3. Run the GPT final gate once the provider quota resets.

Project INCOMPLETE; upstream publication LOCKED.
