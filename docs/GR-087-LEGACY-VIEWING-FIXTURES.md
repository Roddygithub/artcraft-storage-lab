# GR-087 — legacy / OpenDocument viewing fixtures and routing

**State: GPT REVIEW PENDING. Project INCOMPLETE. Upstream LOCKED.**

Evidence freeze 2026-11-10 at `864fc77`: the `--viewing` browser replay, the
bundle-level import probe and the offline checks below were all re-run or
re-verified at that commit. Only documentation changed after the replay source
`53c7e22`.

Candidate reviewed by the free pass: `2c112fc`; the first retained real-Seafile
routing replay ran at `4fe3fc4`. The source that produced the earlier runtime
evidence is `4f4b2dc`; the later commits add documentation, fixtures, a bridge
signature extension, tests and the opt-in `--viewing` lab mode only. This claim
is verifiable with `git diff 4f4b2dc 4fe3fc4 -- bridge/ lab/`.

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
DOC/ODT to WordCraft and XLS/ODS/CSV to GridCraft. The other seven formats have
no documented Craft import and stay unrouted.

Documented-import evidence, cited from the pinned release bundles (hashes in
`docs/reviews/PROJECT-CLOSURE-20261108/upstream-release-pins.json`):

| Format | Upstream statement |
| --- | --- |
| DOC | WordCraft v0.16.0 `README.md:99` "opens legacy 97-2003 .doc"; `:128` "legacy 97-2003 .doc import" |
| ODT | WordCraft v0.16.0 `README.md:99` "and also .odt, .rtf, .html, .md, .tex (LaTeX), .txt" |
| XLS | GridCraft v0.17.0 `README.md:94` "Legacy 97-2003 .xls workbooks open with their values, formulas and number formats" |
| ODS | GridCraft v0.17.0 `README.md:96` "ODS worksheet data can be imported … using saved values instead of formulas" |
| CSV | GridCraft v0.17.0 `README.md:93` "CSV and TSV too" |
| PPT/PPS/PPSX/ODP/FODP | DeckCraft v0.16.0 `README.md:22` documents only "open and save .pptx" — no route |

## Evidence

* Offline validation at `4fe3fc4`: **20/20 command groups PASS**
  (`scripts/validate-candidate.py`), which now includes
  `tests/test_legacy_fixtures.py`.
* `tests/bridge/test_bridge.py`: **33 tests OK** (was 32).
* `tests/lab/test_local.py`: **13 tests OK**, including the `--viewing` flag and
  the opt-in map not replacing the default candidate.
* First Real Seafile routing replay at `4fe3fc4`: HTTP **57/57** (17 legacy
  viewing-route checks) and browser **119/119**, launcher exit 0, on stock
  synthetic Seafile CE 13.0.28. Sanitized evidence and verifier:
  `lab/real-seafile/results/2026-11-08-legacy-viewing/`.
* Browser routing replay at `53c7e22` (committed as `864fc77`): HTTP **57/57**
  and browser **140/140**, including **21** viewing checks. In one authenticated
  Seafile session each of DOC/ODT (WordCraft) and XLS/ODS/CSV (GridCraft) opens
  from the file-list click, routes to the documented editor, downloads nothing
  and writes no version; FODT/FODS/FODP/PPT/ODP/PPS/PPSX have no WOPI route.
  Launcher exit 0, containers removed; `verify.py` PASS. Sanitized evidence:
  `lab/real-seafile/results/2026-11-09-legacy-viewing-browser/`.
* Re-verified 2026-11-10 at `864fc77`: offline **20/20** command groups with
  `uv run --with playwright --with pillow python scripts/validate-candidate.py`,
  bridge **33** tests OK, legacy fixtures **9** tests OK (1 skipped), lab **13**
  tests OK, and the bundle import probe **5/5 PASS**.
* Bundle-level import probe: the pinned WordCraft v0.16.0 and GridCraft v0.17.0
  bundles import all five routed legacy fixtures (DOC, ODT, XLS, ODS, CSV) and
  serialize the marker in their native format (DOCX text, ODT content.xml,
  XLSX cells). Script `scripts/probe-legacy-import.py`, exit 0 with 5/5 passed.
  This is editor-bundle import evidence, independent of host/bridge/Seafile.
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

* No combined host+editor+Seafile run has captured the marker on fresh reopen or
  the rendered legacy document. The bundle-level probe
  (`scripts/probe-legacy-import.py`) proves editor-bundle import; the
  real-Seafile `--viewing` replay proves routing and safety only. The
  `/relay/file` capture inside the combined run is blocked by iframe load order:
  the nested same-origin request fires before any listener can attach. See
  `docs/VALIDATION-STATE.md`.
* No format is declared replaced; the seven formats with no documented Craft
  import (FODT, FODS, FODP, PPT, ODP, PPS, PPSX) remain without a route.
* Human HTTPS desktop acceptance remains pending.
* The project-level GPT gate cannot run while the `openai` provider quota is
  exhausted (the Sol final reviewer uses the same provider).

## Next steps

1. Optional: capture the rendered legacy content in one host+browser session by
   attaching the relay listener before the nested iframe load. Not required for
   the routing/import evidence above, which is already split across the
   real-Seafile replay and the bundle probe.
2. Keep the seven import-less formats unrouted and disclosed.
3. Obtain independent review of the 2026-11-09 browser routing run (NOT
   PERFORMED), then run the GPT final gate once the provider quota resets.

Project INCOMPLETE; upstream publication LOCKED.
