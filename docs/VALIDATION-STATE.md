# Validation checkpoint — candidate `123d2a0` (2026-11-17 remediated)

## Evidence correction — 2026-11-20

The 2026-11-18 `37/37` fidelity row below is retained as a historical report,
but its producer scripts and exact fixture bytes are not recoverable from the
packet. It is **not** a reproducible fidelity pass. The current comparators
reconcile the saved DOCX/PPTX artifacts as preserved when the recorded edit
marker is excluded; their second readback binaries are absent, so reopened
fidelity remains **NOT_VERIFIED**. The saved XLSX artifact contains an invalid
`Data!C2` formula (`Sheet2!B1`) and `#REF!`; its archived formula/value pass is
not supported. The source fixture has been corrected for future campaigns,
without altering historical evidence. See
[`FIDELITY-EVIDENCE-RECONCILIATION-20261120.md`](reviews/FIDELITY-EVIDENCE-RECONCILIATION-20261120.md).

The probe now requires the fresh editor to receive the saved bytes through its
own `/relay/file` request and requires OCR confirmation of the edited marker
in the reopened screenshot. An API download is storage-integrity evidence
only. No new tri-format Seafile replay has been performed: this checkout has no
Lima executable or editor bundles, and the isolated CE12 stack is not running.

**Technical candidate SHA:** `23de889181bd1b002019da89f824877d123d81b3` (bridge: `123d2a0ca8435e93e37b6d2f31fb73ac016fc5fb`).
This candidate adds a reproducible Seafile CE12 runner and retains a corrected
66/66 browser replay. The offline runner passed 21/21 command groups at this
exact SHA. An independent free-model review of `123d2a0` returned PROVISIONAL
PASS for the bridge source and the consistency of the retained evidence; its
one limitation and four documentation minors are resolved. See
`reviews/PROJECT-CLOSURE-20261115/INDEPENDENT-REVIEW-2DD571F.md`.
That review did **not** cover the CE12 launcher or the replay evidence chain in
depth; a separate targeted review of those ran at `5fe30c6` in an isolated
worktree: PROVISIONAL PASS, no BLOCKER/MAJOR, two MINOR evidence-quality
findings (version and fresh-session claims retained as bare booleans), both
remediated and re-proven in `../lab/real-seafile/results/2026-11-15-seafile12-detail/`.
See `reviews/PROJECT-CLOSURE-20261115/CE12-REVIEW-5FE30C6.md`.
The prior GPT-6 Sol PROVISIONAL PASS at `98c6bba` covered
an earlier evidence-only delta, not this candidate. **No GPT gate has run on
`123d2a0`**, so the global gate remains open.

This short checkpoint is the continuation entry point. Do not re-read the
historical GR corpus to resume routine validation.

| Scope | State | Evidence |
| --- | --- | --- |
| Active offline checks | 21/21 command groups PASS at exact candidate `123d2a0ca8435e93e37b6d2f31fb73ac016fc5fb`; all logs are retained and manifest-verified | `../lab/real-seafile/results/2026-11-15-offline-validation-123d2a0/` |
| Core Seafile DOCX edit/save/reopen | HTTP slice 56/56; browser 58/58; two typed saves create versions and fresh-session reopen preserves edits | `../lab/real-seafile/results/2026-11-15-seafile-render-readonly/` |
| Legacy read-only Seafile routes | 34/34 route assertions; exact fixture bytes, OCR marker/value, no download, no version write, host reports `read-only` | `../lab/real-seafile/results/2026-11-15-seafile-render-readonly/` |
| Legacy format status | `VIEW_SUPPORTED`: ODT, ODS, CSV, PPSX. `UNSUPPORTED`: DOC, XLS, FODS, FODT, FODP, PPT, ODP, PPS | `ONLYOFFICE-REPLACEMENT-MATRIX.md` |
| Seafile 12.0.14 isolated browser workflows | Reproduced through the checked-in CE12 launcher: WordCraft DOCX 24/24, GridCraft XLSX 27/27, DeckCraft PPTX 15/15; each saved a new version and reopened edits in a fresh session. Synthetic data only. Initial bridge-start ordering defect was fixed before this passing replay. Targeted review found the retained summaries assertion-only for the version and fresh-session claims; superseded by the re-run below | `../lab/real-seafile/results/2026-11-15-seafile12-replay/` |
| Seafile 12.0.14 replay with retained proof | Re-runs after the targeted review remediation: 66/66 and the verifier rejects bare booleans. Current run adds byte-level XLSX proof (relay==readback, original≠readback) and `new_browser_context=True` in fresh-session details; every version check retains `history N->M grew=True creator_is_opener=True`; the nine `check(name, True)` tautologies are gone; sanitizer committed and unit-tested (5 tests) | `../lab/real-seafile/results/2026-11-16-seafile12-byteproof/` (current), `../lab/real-seafile/results/2026-11-15-seafile12-detail/` (previous), `reviews/PROJECT-CLOSURE-20261115/CE12-REVIEW-5FE30C6.md` |
| Bundle render diagnosis | DOC/XLS/ODT/ODS/CSV/PPSX markers verified in standalone bundles; FODS shows flat XML. DOC/XLS host failure was observed in exploratory runs, not retained as an exact-source screenshot | `../lab/real-seafile/results/2026-11-15-legacy-render-probe/` |
| Default ArtCraft edit/save workflows | DOCX, XLSX, PPTX have isolated CE 12.0.14 save/version/fresh-reopen checks (24/24, 27/27, 15/15) with retained proof details and byte-level relay/readback artifacts for all three formats. Broad document/workbook/deck fidelity NOT VERIFIED | `../lab/real-seafile/results/2026-11-16-seafile12-byteproof/`; prior multi-app runs: `../lab/real-seafile/results/2026-11-08-seven-craft-validation/` |
| HTTPS automated WordCraft replay | HTTP 40/40, browser 28/28 at source `7961db5`; does not cover physical-device acceptance | `../lab/real-seafile/results/2026-11-08-wordcraft-https-current/` |
| Direct read-only WOPI PutFile | Seafile CE 13.0.28 accepts direct `PutFile` with read-only token; bridge relay refuses it, but token is browser-visible | `../bridge/README.md`, `../lab/real-seafile/results/2026-11-15-seafile-render-readonly/` |
| **Proxmox isolated deployment (LXC 115)** | **66/66 browser E2E PASS** (WordCraft 24, GridCraft 27, DeckCraft 15) on real HTTPS via Tailscale; byte-level proof (relay==readback); synthetic accounts only | `../lab/real-seafile/results/2026-11-17-proxmox-isolated/` |
| **Hardware acceptance (Omarchy/GTX 1060)** | 17/22 PASS; GPU/WebGPU confirmed; dirty close PASS; network outage/recovery PASS; session expiry TTL enforced. **Corrected 2026-11-18:** paste OS→editor **persists** in the saved DOCX and across reopen — the earlier "NOT persisted" was a probe defect (raw byte search on a DEFLATE ZIP, `clipboard_probe.py:289` in the old runner); copy editor→OS **FAILS** with a proven cause (Seahub's WOPI iframe does not delegate clipboard permissions — not a bridge defect, not fixable from the bridge); read-only access under the edit-only config is **CONDITIONAL PASS** | `../lab/real-seafile/results/2026-11-17-proxmox-isolated/hardware.json`, `../lab/real-seafile/results/2026-11-18-clipboard-and-fidelity/clipboard/` |
| **Session expiry (TTL 120s)** | 7/7 PASS; expired save REJECTED (**token TTL is enforced**, not a limitation); download fallback works; reopen save creates version; marker persistence NOT_VERIFIED (XML search imperfect) | `../lab/real-seafile/results/2026-11-17-proxmox-isolated/session-expiry.json` |
| **WOPI edit-only routing (2026-11-18)** | **8/8 PASS**: with `OFFICE_WEB_APP_FILE_EXTENSION = ()` and `OFFICE_WEB_APP_EDIT_FILE_EXTENSION = ('pptx',)` the owner still gets the bridge edit route, while a real read-only share recipient gets **no WOPI route and no token** and a clean "Online view is not applicable to this file format" page. All five `get_wopi_dict()` call sites are gated on `OFFICE_WEB_APP_FILE_EXTENSION` (`views/file.py:964,1089,1410,1653`; `api2/views.py:2890`), so the empty tuple closes every view-token path. Lab config restored after the test | `../lab/real-seafile/results/2026-11-18-clipboard-and-fidelity/wopi-edit-only-routing/`, `../lab/real-seafile/wopi_routing_probe.py` |
| **Document fidelity (2026-11-18, historical only)** | Archived report asserts 37/37, but exact producer scripts/source fixture bytes are not established. Current comparison confirms saved DOCX/PPTX features with the intentional marker; XLSX saved bytes have an invalid cross-sheet formula and `#REF!`. Second readback binaries are absent. **Overall historical verdict: NOT_VERIFIED**; do not cite the 37/37 as a reproducible pass. The tri-format fresh-editor probe correction is source-only until a new isolated lab run. | `../lab/real-seafile/results/2026-11-18-clipboard-and-fidelity/fidelity/`, `reviews/FIDELITY-EVIDENCE-RECONCILIATION-20261120.md` |
| **Clipboard copy/paste (2026-11-18)** | Paste system→editor→saved DOCX **PASS** (marker in the decompressed saved DOCX and after a fresh-context reopen). Copy editor→OS **FAIL, cause proven**: WordCraft's copy path uses the async Clipboard API; `clipboard-write` is denied by Permissions Policy; the blocking delegation is **Seahub's own WOPI iframe** (`frontend/src/view-file-collabora-online.js`, no `allow`). A plain `allow` is insufficient — that iframe is form-POST-targeted with no `src`, so `'src'` resolves to the wrong origin; an origin-qualified `allow` moves the error to "Write permission denied". Not fixable from the bridge; the bridge iframe `allow` attribute is contract-correct but insufficient on its own | `../lab/real-seafile/results/2026-11-18-clipboard-and-fidelity/clipboard/`, `../bridge/static/host.html` |
| **Backup/restore test** | LXC 115 snapshot → clone → restore verified; all services healthy; HTTPS connectivity confirmed | `deploy/bridge/CUTOVER-pve01.md` |
| **Backup verified** | `vzdump-lxc-108-2026_11_17-03_12_13.tar.zst` (12G), `zstd -t` → INTEGRITY_OK | read-only check 2026-11-17 |
| **LXC 115 isolated deployment** | Running, all 4 services healthy; HTTPS via Tailscale (8443/8444); pve01 socat relay | `deploy/bridge/CUTOVER-pve01.md` |
| Direct read-only WOPI PutFile | Seafile CE 13.0.28 accepts direct `PutFile` with read-only token; bridge relay refuses it, but token is browser-visible | `../bridge/README.md`, `../lab/real-seafile/results/2026-11-15-seafile-render-readonly/` |
| Hardware WebGPU/clipboard/fonts/unload acceptance | **PARTIAL** — GPU/WebGPU PASS; dirty close PASS (beforeunload dialog captured, history unchanged, dirty marker discarded); network recovery PASS; clipboard OS→editor NOT VERIFIED (canvas limitation); clipboard editor→OS NOT VERIFIED (canvas limitation); read-only access NOT VERIFIED (Seafile CE 12.0.14 share propagation limitation) | `../lab/real-seafile/results/2026-11-17-proxmox-isolated/hardware.json` |
| Independent and final review | Free-model independent review of `123d2a0` at docs `2dd571f`: PROVISIONAL PASS for the claimed lab scope; 1 limitation and 4 documentation minors, all resolved. GPT-6 Sol at `98c6bba` covered only the earlier evidence delta. **No GPT gate has run on this candidate.** | `reviews/PROJECT-CLOSURE-20261115/INDEPENDENT-REVIEW-2DD571F.md` |
| Mechanical evidence self-audit | PASS at exact candidate `123d2a0`: 24 result directories, 21 available verifiers run, 19 provenance commits checked, 307 files hashed and 87 JSON files scanned; two loose root JSON files scanned; pattern-based secret scan | `../scripts/forensic-audit.py`, `reviews/PROJECT-CLOSURE-20261115/MECHANICAL-AUDIT-123D2A0.json` |
| Owner's live Seafile server | HTTPS/TLS and ping PASS; synthetic library shared read-write. Seafile 12.0.14; current WOPI disabled. Patched Seahub route allowlists the synthetic library; a separate gateway service is active, but its relationship to the configured action URL is unverified. Supplied credentials were rejected at login; authenticated current-bridge edit/save NOT VERIFIED. No config/content changed | [`OWNER-SERVER-ACCESS-20261115.md`](reviews/PROJECT-CLOSURE-20261115/OWNER-SERVER-ACCESS-20261115.md), `GR-059-REAL-SEAFILE-WORDCRAFT-DEPLOYMENT.md` |
| WOPI host write boundary | Host gap: Seahub PutFile accepts any valid WOPI token and ignores the `can_edit` it stored in the token; verified on CE 13.0.28 in the lab and by source inspection on CE 12.0.14 and 2026-10-21 master. Zero-patch fix NOT possible; read-only view routes are not safe for untrusted viewers under this constraint | [`security/HOST_PERMISSION_BOUNDARY.md`](security/HOST_PERMISSION_BOUNDARY.md), `../lab/real-seafile/results/2026-11-15-seafile-render-readonly/` |
| Concurrent writers | Accepted, documented, non-atomic: version preflight + unconditional PutFile; an external write between the two can be overwritten. Refused saves keep the page dirty; reconciliation prevents duplicate versions; the race is reproduced by test, not hidden | `../bridge/README.md`, `../tests/bridge/test_bridge.py` (`test_save_overwrites_intervening_external_writer_despite_verified_readback`) |
| **Evidence verifier** | Strengthened with SHA256SUMS, artifact existence, counter consistency, provenance coherence. Earlier docs recorded contradictory mutation counts (10/10 and 8/8) and no harness was committed, so the count is **unproven**; an independent 9-probe check on 2026-11-18 rejected all 9 | `../lab/real-seafile/results/2026-11-17-proxmox-isolated/verify.py` |
| **Provenance** | Browser runner SHA256 documented (deployed copy with STATIC path sed-modified); sanitizer SHA256 matches repo; transformation documented | `../lab/real-seafile/results/2026-11-17-proxmox-isolated/provenance.json` |
| **CI evidence validation** | GitHub Actions workflow added for evidence integrity verification | `.github/workflows/evidence-validation.yml` |

ArtCraft is the intended suite. ONLYOFFICE retirement is authorized. Production
deployment remains outside these tests. Only the authorized synthetic-library
permission changed; server configuration and file contents were not changed.
Upstream remains LOCKED. An automated subset PASS is not full format coverage
or project approval.

The prior independent audit and follow-up fixes are recorded in repository
history. Its verdict remains PROVISIONAL; owner-server and hardware acceptance
and the GPT gate remain open.

## Repeat checks with compact output

```sh
# With Playwright, Pillow and its Chromium already installed in the Python environment:
python3 scripts/validate-candidate.py --output /absolute/new/private-check-dir
# Or use an isolated dependency environment (Chromium still required):
uv run --with playwright --with pillow python scripts/validate-candidate.py \
  --output /absolute/new/private-check-dir
# Real Seafile/browser run: no editor filter means all six default editors.
python3 lab/real-seafile/local.py --run-dir /absolute/new/private-lab-dir \
  --static /absolute/verified-static --manifest /absolute/verified-manifest.json
```

The compact runner uses four workers, captures full per-command private logs,
prints only totals and failing command names, returns nonzero on any failure,
and records command exits/source SHA in `summary.json`. It does not run legacy
integration tests, mutate production or confer independent review approval.

To save tokens: read this file and `git status --short`; run the compact runner;
inspect only failed logs; retain sanitized runtime totals and exact provenance.
Do not repeatedly dump successful logs, historical reports or bundle contents.

The HTTPS reopened-saved screenshot was inspected: both typed markers are
visible with the table and the saved-to-Seafile host status. This does not
prove full pagination or font fidelity.

## Remaining unresolved work (post-remediation)

1. **GPT_FINAL_GATE: PENDING** — No GPT-6 Sol review has run on candidate `123d2a0` (quota unavailable).
2. **PRODUCTION_CUTOVER: NOT EXECUTED** — Requires explicit owner authorization for LXC 116 bridge creation and Seahub WOPI config change.
3. **Clipboard copy editor→OS** — **FAIL, cause proven 2026-11-18**: WordCraft's copy path uses the async Clipboard API and the frame chain denies `clipboard-write` by Permissions Policy. The blocking delegation is **Seahub's own WOPI iframe** (`frontend/src/view-file-collabora-online.js`, no `allow` attribute); a plain `allow` is insufficient because that iframe is form-POST-targeted with no `src`, so the `'src'` allowlist resolves to the wrong origin. Paste is unaffected (it uses the synchronous `paste` event) and persists correctly. Fixing copy requires a Seahub front-end patch (forbidden by the project's no-patch rule) or same-origin bridge hosting (a security regression).
4. **Read-only share propagation** — Superseded by the 2026-11-18 routing probe: with `OFFICE_WEB_APP_FILE_EXTENSION = ()` a real read-only share recipient gets no WOPI route/token and a clean fallback page (8/8). The earlier "CE 12.0.14 limitation" attribution is withdrawn. Broad read-only *viewing* of every format is still NOT VERIFIED.
5. **Read-only viewer routes** — Not enabled; WOPI `can_edit` host boundary means view routes unsafe for untrusted viewers without host patch. The edit-only configuration (`OFFICE_WEB_APP_FILE_EXTENSION = ()`) is the verified mitigation.
6. **Document fidelity** — Bounded result only: DOCX 15/15, XLSX 9/9, PPTX 6/6 features PRESERVED on one representative fixture per format, with the typed edit present in every saved file. Broad arbitrary-document fidelity (tracked changes, comments, charts, animations, multi-sheet complexity) remains NOT VERIFIED.

## Next steps

1. Obtain owner authorization for production cutover (LXC 116 + Seahub config).
2. Schedule GPT-6 Sol review when quota available.
3. Consider upstream editor fix for clipboard persistence (WordCraft).
4. Consider upstream Seafile fix for share propagation and token TTL enforcement.

The default six-editor candidate remains unchanged. `--pptx` is opt-in and the
four legacy routes are also opt-in and read-only.
