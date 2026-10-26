## GR-076 — bounded PhotoCraft host adapter

Isolated uncommitted candidate from local main `dc105220ae934f9779eb357a4cda901ee0aa0c0b`.
Reuses exact GR-026/GR-032 PhotoCraft base and transport; adds payload/decoded
bounds, nested-command and direct API guards, idle ACK/deadline repaint, and
focused lifecycle/standalone regressions. Retained patches omitted the engine
snapshot test module; repaired explicitly. Rust 1.95 locked snapshot/host/file-open/inbox tests (4/7/47/2), format, Web
WASM, clean-base patch application and whitespace checks PASS. Independent
R1/R2 source reviews returned PROVISIONAL PASS. **GPT REVIEW PENDING**; no GPT
PASS. Serialization peak memory and live browser/external persistence remain
NOT VERIFIED. No external services, deployment, dispatch, commit,
push or publication. See `docs/GR-076-PHOTOCRAFT-BOUNDED-HOST-ADAPTER.md` and
`docs/reviews/GR-076/`.

## GR-075 — gateway request-body deadline

Nonempty request bodies have a 120-second total deadline across bounded
`read1` calls. A loopback slow-drip test confirms 408/close and preservation of
`/dirty` state. R3 returned bounded PROVISIONAL PASS with one matrix minor,
corrected in the matrix. R4 returned bounded PROVISIONAL PASS and found stale
R3-pending text in this report and the GR-075 report; both are corrected.
Independent R1–R5 bounded reviews are PROVISIONAL PASS with no remaining
findings in scope. Header-read deadlines, proxy and
large slow-link behavior, production, and live Seafile/ONLYOFFICE remain NOT
VERIFIED. Project GPT remains INCOMPLETE and upstream publication LOCKED.
R1 found a timing race; R2 showed the first synchronization still preceded
deadline creation and socket creation was outside cleanup. The test now signals
at the first `read1` call after deadline creation and protects setup in
`finally`. R3's matrix-status minor and R4's stale R3-pending text were fixed;
R5 confirmed the current summaries agree. Evidence:
`docs/GR-075-HTTP-BODY-DEADLINE.md`, `docs/reviews/GR-075/`.

## GR-074 — gateway request-body framing

The shared POST body reader now rejects unsupported transfer encoding, duplicate
or invalid content lengths, truncated reads and over-limit bodies, closing the
connection on rejection. This also prevents an oversized `/dirty` body from
clearing unsaved state. Loopback tests use a synthetic Seafile double only.
R1's P2 Unicode-whitespace bypass and P3 false-positive test were fixed. R2
reproduced a parser-reported malformed-header bypass; header defects and the
unknown-route body path were addressed. R3's HTTP/0.9 and matrix-wording P3s
were corrected. R4 found malformed header residue in `get_payload()` without
parser defects; the reader now rejects it and raw tests cover both sequences.
Independent R1–R5 bounded reviews are PROVISIONAL PASS with no remaining
findings. Project GPT remains INCOMPLETE and upstream
publication LOCKED. Evidence: `docs/GR-074-HTTP-BODY-FRAMING.md`,
`docs/reviews/GR-074/`.

# GPT Review Queue

## GR-073 — gateway `/open/` rate limit

Bounded implementation adds a process-local 60-per-60-second fixed window per
observed TCP peer, capped at 1,024 entries. Rejected requests return 429 with
`Retry-After` before reaching Seafile. Forwarded headers are ignored. Behind a
reverse proxy clients may share the proxy's bucket; distributed rate limiting,
proxy identity, public deployment and broader security remain NOT VERIFIED.
Independent R1 requested two P2 and one P3 changes; connection closure, locked
clock sampling, and default-threshold regression coverage are now recorded.
R2 confirmed the code fixes and found one stale security-table entry, corrected
and verified in R3. Bounded R1–R3 reviews are PROVISIONAL PASS; project GPT
remains INCOMPLETE and upstream publication LOCKED. Evidence:
`docs/GR-073-OPEN-RATE-LIMIT.md`, `docs/reviews/GR-073/`.

## GR-072 — post-change ONLYOFFICE regression smoke

The operator-recorded run used Seafile's ONLYOFFICE route for a synthetic DOCX
outside the ArtCraft allowlist. The marker was initially GR-071 and then
corrected to GR-072. Screenshots show the final marker and `All changes saved`;
Seafile history and navigation chronology are operator-recorded, not
independently established by screenshots. The correction created a second
retained version and is disclosed. The editor was exited by navigation, not
explicit in-app close. Exact payload/readback identity and broader
compatibility/security remain NOT VERIFIED. No server route, allowlist or
ONLYOFFICE setting changed. Project remains INCOMPLETE; upstream publication
LOCKED. Bounded evidence only, not project GPT PASS.
Evidence: `docs/GR-072-ONLYOFFICE-REAL-SEAFILE-REGRESSION.md`,
`docs/reviews/GR-072/`. R1 returned PROVISIONAL ACCEPT with two documentation
minors; both are remediated. R2 returned PROVISIONAL ACCEPT with one
matrix-attribution minor, now corrected. R3 returned PROVISIONAL ACCEPT with no
remaining findings. Runtime claims remain operator-recorded, not independently
replayed.

## GR-071 — dispatched candidate provenance recheck

Independent R1–R3 bounded reviews returned PROVISIONAL PASS with no remaining
findings after the GridCraft source pin, GR-054 capture dates and historical
handoff wording were corrected. The read-only wrapper checks the shared-root
results, per-app verifier linkage and reconciliation with GR-054. The directory is
`/home/roddy/.cache/artcraft-storage-lab/gr059-deployment/integration/static`,
not a production or proven live service root. Do not contact services, promote
assets, or change dispatch. Per-app Seafile runs are evidence for their
respective candidates; one combined four-route replay, repository
`integration/static` promotion, save/readback byte identity, and production
security remain **NOT VERIFIED**. The post-change ONLYOFFICE smoke was
subsequently recorded in GR-072. Project must remain **INCOMPLETE** and upstream
publication **LOCKED**.
Evidence: `docs/GR-071-DISPATCHED-CANDIDATE-PROVENANCE.md`,
`docs/reviews/GR-071/`.

## GR-069 — FigCraft real synthetic Seafile roundtrip

Independent R1 returned a bounded PROVISIONAL PASS with no findings. The
reviewer verified candidate hashes, pins, checksums, screenshots, and scope
wording without replaying the browser or accessing services. Runtime chronology,
service state, and cleanup remain implementer-reported. Exact save/readback byte
identity, history-page evidence, explicit in-app close, and post-change
ONLYOFFICE edit/save remain NOT VERIFIED. The work item remains **GPT REVIEW
PENDING**; project verdict remains INCOMPLETE and upstream publication LOCKED.
Evidence and verifier: `docs/GR-069-FIGCRAFT-REAL-SEAFILE-ROUNDTRIP.md`,
`docs/reviews/GR-069/`.

## GR-068 — PdfCraft real synthetic Seafile roundtrip

Independent R1 returned a bounded PROVISIONAL PASS with no findings. Candidate
hashes, source/patch/transport pins, overlay, checksums, and screenshots were
verified read-only. Runtime chronology, history entries, cleanup, and ONLYOFFICE
state remain implementer-reported. Save/readback byte identity, explicit in-app
close, post-change ONLYOFFICE edit/save, and production readiness remain NOT
VERIFIED. The work item remains **GPT REVIEW PENDING**; project verdict remains
INCOMPLETE and upstream publication LOCKED. Evidence:
`docs/GR-068-PDFCRAFT-REAL-SEAFILE-ROUNDTRIP.md`, `docs/reviews/GR-068/`.

## GR-067 — EffectCraft real synthetic Seafile roundtrip

Independent R1–R3 returned bounded PROVISIONAL PASS results. R1's two evidence
minors, R2's tracking minor, and R3's two P3 documentation findings are
corrected; the R1 follow-up's old pending statement is explicitly historical,
and the README checksum is current. R4 returned bounded PROVISIONAL PASS with no
new findings. Reviewers verified all 11 assets, source and patch identity, transport pin,
screenshots, and retained checksums. Runtime chronology, fresh-session creation,
history timestamps, cleanup, and service state remain implementer-reported.
Save/readback byte identity, explicit in-app close, and post-change ONLYOFFICE
edit/save remain NOT VERIFIED. The work item remains **GPT REVIEW PENDING**;
project verdict remains INCOMPLETE and upstream publication LOCKED. Evidence:
`docs/GR-067-EFFECTCRAFT-REAL-SEAFILE-ROUNDTRIP.md`, `docs/reviews/GR-067/`.

## GR-066 — FilmCraft real synthetic Seafile roundtrip

Independently review the exact candidate inventory and recorded Seafile
open/edit/save/history/fresh-session reopen evidence. Validate that the staged
and active static roots match all five candidate files and that the source,
GR-023 patch, and craft-platform pins are recorded consistently. Review the
test-only same-tab popup shim, synthetic-library-only routing, rollback
disclosure, and ONLYOFFICE scope. Do not access services or replay the browser.
The editor was exited by navigation rather than explicit in-app close; exact
save-message/readback byte identity and a post-change ONLYOFFICE edit/save
regression are NOT VERIFIED. A thumbnail request returned HTTP 500 and was
not investigated. Project verdict must remain INCOMPLETE and upstream
publication LOCKED.

R1–R2 returned bounded PROVISIONAL PASS with no blocker/major; R1's screenshot
caption MINOR is closed. Runtime chronology/statuses remain implementer-
reported, not independently replayed. Evidence and reviews:
`docs/GR-066-FILMCRAFT-REAL-SEAFILE-ROUNDTRIP.md`, `docs/reviews/GR-066/`.

## GR-065 — DesignCraft real synthetic Seafile roundtrip

R1 returned a bounded PROVISIONAL PASS with no findings requiring remediation.
The reviewer verified candidate/source/artifact hashes and inspected the
sanitized evidence, but did not access services or replay the browser. HTTP
statuses, history events, fresh-session chronology, deployment changes,
rollback retention, and unchanged ONLYOFFICE configuration remain
implementer-reported. The T3 preview used a test-file-only `window.open`
same-tab shim. The history panel screenshot was omitted because it exposed the
account display name. The save payload was not hashed against Seafile
readback, and ONLYOFFICE edit/save was not rerun. Project verdict must remain
INCOMPLETE and upstream publication LOCKED.

Evidence: `docs/GR-065-DESIGNCRAFT-REAL-SEAFILE-ROUNDTRIP.md`,
`docs/reviews/GR-065/`. GR-065 remains GPT REVIEW PENDING; no project GPT PASS.

## GR-064 — DeckCraft real synthetic Seafile roundtrip

Review the exact GR-064 evidence, current local candidate inventory, and source
patch provenance. Check the Seafile file-list open/edit/host-ACK/new-version/
fresh-session reopen claim and the disclosed T3 same-tab popup adjustment.
Confirm the route and allowlist scope stays limited to the single synthetic
library, existing DOCX/XLSX/PDF/SVG routes remain, and ONLYOFFICE settings are
unchanged. Do not access services or repeat the browser flow. The post-change
ONLYOFFICE check was open-only; edit/save remains NOT VERIFIED. Project verdict
must remain INCOMPLETE and upstream publication LOCKED.

R1–R4 were bounded PROVISIONAL PASS reviews; all wording/verifier findings
were corrected. See `docs/reviews/GR-064/INDEPENDENT-REVIEW-R1.md` through
`R4.md`. Bounded review only, not project GPT PASS.
Evidence: `docs/GR-064-DECKCRAFT-REAL-SEAFILE-ROUNDTRIP.md`,
`docs/reviews/GR-064/`.

## GR-063 — VectorCraft real synthetic Seafile roundtrip

The exact GR-058 candidate opened the synthetic SVG through Seafile; an actual
VectorCraft edit was exported as SVG, captured by the in-page adapter and saved
through the gateway. Seafile history shows a modification and a fresh
file-list/editor session reopens the rectangle. This is the existing
VectorCraft page-API/export path, not the shared `?host=parent` protocol. Ctrl+S
opened Save As and was cancelled; the native dirty asterisk remains after the
export. Exact export-byte/readback identity and a post-change ONLYOFFICE
edit/save regression are **NOT VERIFIED**. ONLYOFFICE remained enabled and was
not reconfigured. Independent R1–R2 returned bounded PROVISIONAL PASS with no
remaining findings; R1's wording MINOR was corrected. R2 did not replay the
browser or verify live service state. Project remains INCOMPLETE; upstream
publication LOCKED. See `docs/GR-063-VECTORCRAFT-REAL-SEAFILE-ROUNDTRIP.md`
and `docs/reviews/GR-063/`.

## GR-062 — PdfCraft real synthetic Seafile roundtrip

The exact GR-057 candidate completed Seafile file-list open → AcroForm edit →
editor save acknowledgement → library-history modification → fresh list
reopen with the edited field intact. The fixture upload was setup only; the
editor save created the persisted edit. PDF was added to the same synthetic
library allowlist while preserving DOCX/WordCraft and XLSX/GridCraft.
`ENABLE_ONLYOFFICE=True` remained set; no ONLYOFFICE settings or routes changed.
Byte-level save-message/readback identity and a post-change ONLYOFFICE
edit/save regression remain **NOT VERIFIED**. Independent R1–R2 returned bounded
PROVISIONAL PASS with no blocker/major; R1's wording MINOR was corrected and
closed in R2. Project remains **INCOMPLETE**; upstream publication **LOCKED**.
See [report](GR-062-PDFCRAFT-REAL-SEAFILE-ROUNDTRIP.md) and
[evidence](reviews/GR-062/). GR-062 remains **GPT REVIEW PENDING**.

## GR-061 — GridCraft real synthetic Seafile roundtrip

**Bounded independent review: R1–R3 PROVISIONAL PASS**, no blocker/major; two
documentation minors corrected. Exact comparison against unavailable earlier
review snapshots remains NOT VERIFIED. The exact GR-056 GridCraft candidate
was staged on the existing gateway. In one synthetic library,
Seafile file-list open → visible B2 edit → save confirmation → library-history
modification → fresh Seafile-backed reopen completed; B2 and formula result B3
both display 1337. The fixture upload was setup only, not persistence of the
edit. DOCX/WordCraft routing remains; the extension addition is limited to the
same synthetic library; `ENABLE_ONLYOFFICE=True` remained set. The previous
GR-059 open-only ONLYOFFICE check was not repeated. Project GPT remains
**INCOMPLETE**; upstream publication **LOCKED**. See [report](GR-061-GRIDCRAFT-REAL-SEAFILE-ROUNDTRIP.md)
and [evidence](reviews/GR-061/). GR-061 remains **GPT REVIEW PENDING**.

## GR-060 — dedicated tailnet gateway LXC (paused)

The isolated non-privileged Debian LXC and loopback-only gateway were staged;
local health/static checks and the GR-055 candidate verifier passed before the
owner-requested shutdown. Tailscale reports `NeedsLogin`, HTTPS Serve and Seahub
migration are not configured, and the GR-059 route remains active. Independent
R1–R2 reviews returned bounded PROVISIONAL PASS after correcting STATUS wording.
Project remains **INCOMPLETE**, upstream publication **LOCKED**. See [report](GR-060-DEDICATED-TAILNET-GATEWAY-LXC.md)
and [evidence](reviews/GR-060/).

## GR-059 — real synthetic Seafile WordCraft deployment

**Review pending.** The exact GR-055 candidate now completed the real
synthetic Seafile open → visible edit → save acknowledgement → new history
version → fresh list reopen flow. Browser evidence includes a reopened screen
with the added text, the host save response, and Seafile history growth. A
post-deployment open-only ONLYOFFICE check loaded its assets from an
out-of-allowlist synthetic folder; ONLYOFFICE save/version behavior after this
deployment was not tested. Rollback archive SHA and deployment scope are
recorded. The project remains **INCOMPLETE**; this does not unlock upstream
publication. See [GR-059 report](GR-059-REAL-SEAFILE-WORDCRAFT-DEPLOYMENT.md)
and [evidence](reviews/GR-059/).

## GR-058 — reproducible VectorCraft candidate

The exact `v0.14.0` source candidate, built with the release-pinned font input,
passed the synthetic browser page-API edit/save/reopen flow against loopback
storage. Independent R1 review: bounded PROVISIONAL PASS, no findings. Seafile
version/reopen, release-binary reproducibility, and missing optional font
rendering remain **NOT VERIFIED**. Candidate remains outside dispatch; project
is **INCOMPLETE**, upstream publication **LOCKED**. See [report](GR-058-VECTORCRAFT-REPRODUCIBLE-CANDIDATE.md)
and [review evidence](reviews/GR-058/).

## GR-057 — reproducible PdfCraft candidate

The exact source/patch/transport candidate passed actual-WASM synthetic browser
form edit/save/ACK/fresh-reopen. R1–R2 bounded reviews are PROVISIONAL PASS;
R1's optimizer wording MINOR was corrected. Seafile persistence/version/reopen
remains **NOT RUN**; this build disabled `wasm-opt`. Candidate stays outside
dispatch; project remains **INCOMPLETE** and upstream publication **LOCKED**.
See [report](GR-057-PDFCRAFT-REPRODUCIBLE-CANDIDATE.md) and
[review evidence](reviews/GR-057/).

## GR-056 — reproducible GridCraft candidate

The exact source/patch/transport candidate passed actual-WASM synthetic browser
edit/save/ACK/reopen with B2/B3 recalculation. Independent R1–R5 bounded
reviews are PROVISIONAL PASS with no remaining findings. A read-only Seafile GET
preflight returned 404; no write was attempted and version/readback/reopen is
**NOT RUN**. Candidate remains outside dispatch; project **INCOMPLETE**,
upstream publication **LOCKED**. See [report](GR-056-GRIDCRAFT-REPRODUCIBLE-CANDIDATE.md)
and [review evidence](reviews/GR-056/).

## GR-055 — reproducible WordCraft candidate

Implementation produced an exact source/patch/transport Rust 1.95 release
WordCraft Web/WASM bundle in cache outside dispatch. The actual candidate passed
the synthetic in-memory browser edit/save-ack/fresh-reopen flow; exact asset
hashes and a runnable verifier are in [GR-055 evidence](reviews/GR-055/README.md).
At the time of GR-055, Seafile persistence/readback/reopen was **NOT RUN**;
GR-059 later records the live synthetic result. Independent R1–R2 bounded
reviews are PROVISIONAL PASS, no remaining findings. GR-055 is GPT REVIEW
PENDING; project remains **INCOMPLETE** and upstream publication remains locked. See
[candidate report](GR-055-WORDCRAFT-REPRODUCIBLE-CANDIDATE.md).

## GR-054 — Dated candidate manifest (bounded independent review passed)

Exact current **source** snapshot: `1c7914bf1e166ac4731a1c9b11dce649210eed70`.
R1–R2 bounded independent reviews are PROVISIONAL PASS. Project GPT review is
pending; project verdict remains **INCOMPLETE**, upstream publication **LOCKED**.

[Manifest](GR-054-CURRENT-CANDIDATE-MANIFEST.md) and
[evidence](reviews/GR-054/README.md) separate clean tracked source (no static
assets) from 82 ignored/untracked parent-local static files. Follow-up GR-071
verified later source-pinned candidates in a separate local test root; the
captured repository `integration/static` tree and live service remain
unverified for those candidates. GR-054 itself performed no build, promotion or
service access.

95d8983 and older candidate assertions below are historical. GR-040 closes
ONLYOFFICE preservation on the isolated synthetic patched stack (DOCX, actual
Document Server 8.0.1-31, two saves/versions/fresh file-list reopen). Earlier
per-run “ONLYOFFICE unverified” statements do not remain an unqualified current
blocker. Production/deployment, other file types/versions, security/authorization,
server compatibility, exact editor asset provenance/protocol and distribution
remain open; no current-source runtime replay or new GPT verdict is claimed.


## GR-053 — Credential redirect guard

**BOUNDED INDEPENDENT R1–R2: PROVISIONAL PASS, no blocker/major; GPT REVIEW
PENDING.** Local redirect/gateway checks pass. Real Seafile redirect behavior
NOT VERIFIED; canonical base/file-server URLs required. This is not a project
GPT PASS. Evidence:
`docs/GR-053-CREDENTIAL-REDIRECTS.md`, `docs/reviews/GR-053/`.


## GR-052 — Ambiguous upstream save response reconciliation

**BOUNDED INDEPENDENT R1–R3: PROVISIONAL PASS, no blocker/major; GPT REVIEW
PENDING.** Based on `a7804a23183c3bc5680028b0a88ac24e4eeb3a86`. Ten synthetic
tests, including a lock-contention retry after
reconciliation, plus GR-049/050 and gateway checks pass. Only
status=None save errors reconcile through bounded exact bytes and user-bound
identity/permission/current-head reads. No second write. Real Seafile/browser
NOT VERIFIED; no project GPT PASS claimed.
Evidence: `docs/GR-052-UPSTREAM-SAVE-RECONCILIATION.md`, `docs/reviews/GR-052/`.

## GR-051 — Browser committed-save response-loss retry

**BOUNDED INDEPENDENT REVIEW: PROVISIONAL PASS, no blocker/major; GPT REVIEW
PENDING.** Based on `5a1ceb66`; cached Playwright Chromium, actual Handler/Gateway/rendered
host, synthetic editor (not actual WASM), FakeSeafile (not real). First save
commits then browser response drops; ticket-1 fails/dirty; fresh user save
with identical bytes/ticket-2 succeeds, one fake write, clean/confirmed host.
Exact route statuses, connection failure, ticket results and cleanup asserted.
GR-049/050 and gateway regressions pass. Independent R1 P3 wording corrections
are closed. No production code edits or project PASS. Upstream response loss
before gateway receipt and real Seafile MVP remain NOT VERIFIED.
Evidence: `docs/GR-051-BROWSER-SAVE-RETRY.md`, `docs/reviews/GR-051/`.

## GR-050 — Loopback HTTP committed-save response-loss regression

**BOUNDED INDEPENDENT REVIEW: PROVISIONAL PASS, no blocker/major; GPT REVIEW
PENDING.** Slice based on `fd6ae99`; 1 real-route loopback HTTP test, 6 GR-049
receipt tests and existing gateway unit checks pass. Test-only response hook
closes the socket after fake commit, before sending any response; identical
HTTP retry returns success with one fake write/version. No production code
changes. Browser/real Seafile and upstream-response loss NOT VERIFIED. No
project GPT verdict claimed.
Evidence: `docs/GR-050-HTTP-SAVE-RETRY.md`, `docs/reviews/GR-050/`.

## GR-049 — Gateway committed-save retry

**BOUNDED INDEPENDENT REVIEW: PROVISIONAL PASS, no findings; GPT REVIEW
PENDING.** The receipt/locking change is based on `7238bc85`; 6 focused tests
and existing gateway unit checks pass. Direct-call discarded-result behavior is
now complemented by GR-050's independently reviewed loopback socket response-
loss proof. Browser and real Seafile behavior remain NOT VERIFIED.
No project GPT PASS or upstream publication authorization.
Evidence: `docs/GR-049-IDEMPOTENT-SAVE-RETRY.md`, `docs/reviews/GR-049/`.

## GR-048 — FigCraft host-save browser runtime smoke

**GPT REVIEW PENDING.** Exact GR-019 patch / base `8d790607` /
transport `56c5e16d`, optimized actual WASM build and bounded T3 Chromium
same-origin open → visible rectangle edit → 3,464 ticketed save bytes → matching
synthetic ACK → clean → fresh iframe reopen. Parent retained bytes only in
memory. Durable Seafile version/readback/reopen, dispatch and deployment remain
NOT VERIFIED. No project GPT PASS or upstream publication authorization.
Evidence: `docs/GR-048-FIGCRAFT-WASM-SMOKE.md`, `docs/reviews/GR-048/`.
Independent free R1 returned PROVISIONAL PASS, no blocker/major; warning/setup
MINOR observations and recorder clarifications are in that evidence directory.

## GR-047 — FilmCraft host-save browser runtime smoke

The exact GR-023 patched FilmCraft WASM opened a synthetic native `.fcproj`
in Chromium. An in-app visible text edit became dirty; Ctrl+S emitted 6,468
bytes (SHA-256 `891cc9648eab2496acbac908a3694f878dada101da3575673697e0faeb764e84`);
the same-origin parent ACKed matching ticket `filmcraft:1`, and the editor
reported clean. A fresh iframe reopened the captured bytes and rendered the
edit. The parent retained bytes in memory only; Seafile version/reopen, dispatch
and deployment remain NOT VERIFIED. Exact pins, hashes and commands are in
`docs/GR-047-FILMCRAFT-WASM-SMOKE.md` and `docs/reviews/GR-047/`. Independent
reviews R1, R2 and R3 returned bounded PROVISIONAL PASS with no remaining
findings. The R2 note about the separate pre-packaging WASM hash was resolved
with an independent cache hash check and clearer artifact distinction; the
review notes that historical continuity is not established. Seafile remains
NOT VERIFIED. Work-item state: **GPT REVIEW PENDING**; upstream publication
remains locked.

## GR-046 — EffectCraft host-save browser runtime smoke

The exact GR-022 patched EffectCraft WASM opened a native synthetic `.ecproj`
in Chromium. An in-app visible text edit became dirty; Ctrl+S emitted 62,136
serialized bytes, the same-origin synthetic parent captured them and ACKed
matching ticket `effectcraft:1`, and the editor became clean. A fresh iframe
reopened the captured bytes with the edit visible. Evidence, hashes, commands
and limitations: `docs/GR-046-EFFECTCRAFT-WASM-SMOKE.md` and
`docs/reviews/GR-046/`. This does not prove Seafile persistence, dispatch,
deployment or ONLYOFFICE behavior; those remain **NOT VERIFIED**. Independent
reviews R1 and R2 returned bounded **PROVISIONAL PASS** with no remaining
findings; see `docs/reviews/GR-046/INDEPENDENT-REVIEW-R1.md` and `R2.md`.
Work-item state: **GPT REVIEW PENDING**; upstream publication remains locked.

## GR-045 — DesignCraft host-save browser runtime smoke

The actual GR-021 patched DesignCraft WASM opened a synthetic native document
in Chromium; an in-editor visible text change became dirty, Ctrl+S emitted
3,184 serialized bytes, the same-origin synthetic parent ACKed matching ticket
`designcraft:1:1`, and the editor became clean. A fresh iframe reopened the
captured bytes with `GR045 runtime edit passed` visible. Evidence and exact
build pins/commands: `docs/GR-045-DESIGNCRAFT-WASM-SMOKE.md` and
`docs/reviews/GR-045/`. This does not prove Seafile persistence, dispatch,
production or ONLYOFFICE behavior; those remain **NOT VERIFIED**. Independent
reviews R1 and R2 returned bounded **PROVISIONAL PASS** with no remaining
findings; see `docs/reviews/GR-045/INDEPENDENT-REVIEW-R1.md` and `R2.md`.
Work-item state: **GPT REVIEW PENDING**; upstream publication remains locked.

Every work item in this project ends here. GPT performs an **independent** review
and does not trust the free-model verdicts.

Nothing may be published upstream (issue, PR, RFC in `storytold/*`, Seafile or
Seafile docs) before an entry reaches `GPT REVIEW PASS`.

## GR-044 — DeckCraft host-save browser runtime smoke

The actual GR-020 patched DeckCraft WASM opened a synthetic PPTX in Chromium;
a visible edit became dirty, Ctrl+S emitted 7,297 serialized bytes, the
synthetic same-origin parent echoed `deckcraft:1` in a positive ACK, and the
editor became clean. A fresh iframe reopened the captured bytes with the edit
intact. Evidence: `docs/GR-044-DECKCRAFT-WASM-SMOKE.md` and
`docs/reviews/GR-044/`. This is **NOT** Seafile persistence: version creation,
Seafile-backed reopen, dispatcher and production remain NOT VERIFIED. Independent reviews R1 and R2 recorded **PROVISIONAL PASS** with no blockers or
major findings: `docs/reviews/GR-044/REVIEW-NEMOTRON.md` and
`docs/reviews/GR-044/REVIEW-NEMOTRON-R2.md`. Final disposition remains GPT
REVIEW PENDING; upstream publication remains locked.

## GR-043 — expired editing session during browser save

The real gateway `/open/` and `/session/<sid>/save` routes are exercised in
Chromium with a synthetic editor and adapter. After TTL expiry, save returns
404 with reopen guidance, host dirty state stays true, the editor receives a
negative `saveResult`, and the fake Seafile writer receives no call. Evidence
and limits: `docs/GR-043-SESSION-EXPIRY.md` and `docs/reviews/GR-043/README.md`.
Independent bounded review: PROVISIONAL PASS, no findings (`docs/reviews/GR-043/INDEPENDENT-REVIEW-R1.md`). This does not verify Seafile capability expiry or revoke semantics, nor change the project-level INCOMPLETE verdict.

## GR-042 — browser enforcement of dynamic host-page CSP

`tests/test_gr042_hostpage_csp_browser.py` uses Chromium against the real
gateway `POST /open/` handler with loopback-only synthetic parent and Seafile
adapter. The configured Seafile ancestor framed the host response; a foreign
outer ancestor was refused; nonce inline script/style worked and no CSP
violation fired in the allowed case. Run and limits: `docs/GR-042-BROWSER-CSP.md`;
evidence: `docs/reviews/GR-042/README.md`. Independent bounded review returned
PROVISIONAL PASS with no findings (`docs/reviews/GR-042/INDEPENDENT-REVIEW-R1.md`).
The Craft bundle, static editor CSP,
proxy behavior, production deployment and other browsers remain NOT VERIFIED.
Work-item state: GPT REVIEW PENDING. This is a bounded browser test, not a
project-level GPT verdict; upstream publication remains locked.

## GR-041 — bounded Craft Web asset staging

The GR-038 fetcher now caps the release ZIP download at 256 MiB, socket timeout
at 30 seconds, total download deadline at 15 minutes, extracted bytes at 1 GiB,
and archive entries at 10,000. It preflights central-directory metadata,
rejects ZIP64/multi-disk, duplicate/path/special-file entries, and keeps
candidate-only staging. Eight focused standard-library tests are recorded in
`tests/test_gr041_craft_zip_limits.py` and `docs/GR-038-CRAFT-ASSET-INGESTION.md`.
Independent exact round 3 returned bounded PROVISIONAL PASS, no blocker/major;
see `docs/reviews/GR-041/INDEPENDENT-REVIEW-R3.md`. Round 2's cleanup finding
was a misread because `trap cleanup EXIT` was already present. Host-protocol
compatibility and live release retrieval remain NOT VERIFIED. No upstream or
service state changed.

## GR-039 — gateway host-page CSP

Implementation and unit evidence are recorded in
`docs/GR-039-HOSTPAGE-CSP.md`; `python3 tests/test_gateway_unit.py` passes.
The first independent round found a CSP-origin validation issue and a default
HTTPS port mismatch; both were fixed. Round 2 found a low discrepancy around
empty origin delimiters; the parser now rejects them and regression tests cover
the cases. Round 3 returned a bounded PROVISIONAL PASS. Reports are in
`docs/reviews/GR-039/`. Scope is only the dynamic `/open/` host page: static
editor HTML, browser-enforced bundle compatibility, reverse-proxy behavior and
deployment security remain NOT VERIFIED. This does not change the project-level
INCOMPLETE verdict or unlock upstream publication.

## GR-040 — synthetic ONLYOFFICE preservation regression

An actual ONLYOFFICE 8.0.1-31 browser editor opened a synthetic Seafile DOCX,
committed two edits through Seahub callbacks (HTTP 200), advanced file history
from 3 to 5, and reopened both edits from a fresh Seahub library-list click.
The isolated stack and exact readback evidence are in
`docs/reviews/GR-040/`. This closes matrix row 6.3 for the tested synthetic
stack only. Independent evidence review returned bounded PROVISIONAL ACCEPT,
no blocker/major and three minor limitations (active test container, no
callback-body hash, test-specific loopback workaround); see
`docs/reviews/GR-040/INDEPENDENT-REVIEW-R1.md`. Production/deployed ONLYOFFICE,
other document types and versions, deployment security, and callback-byte
identity remain NOT VERIFIED. Overall GPT REVIEW stays INCOMPLETE and upstream
publication stays locked.

## Historical first-pass result — 2026-10-25 (95d8983)

```text
Candidate: 95d89835b2b1d06fd098c586469ed03b8fd0549e
Reviewer: GPT-6.1 Sol (low)
Verdict: INCOMPLETE — GPT REVIEW PASS not granted
Report: docs/reviews/GPT-FIRST-PASS-95D8983.md
Synthetic DOCX MVP: demonstrated on isolated patched Seafile C-fileserver stack
Open gates at review time: ONLYOFFICE regression, security/authorization cases, server compatibility,
            pinned editor assets/protocol check, distribution/licensing decision
Upstream publication: LOCKED
```

GR-040 subsequently closes the isolated synthetic ONLYOFFICE gate above;
production/deployment and other types/versions remain NOT VERIFIED. GR-054
identifies the current source snapshot and unresolved operational asset identity.

This historical result supersedes the old “no Seafile E2E” objection for the candidate's
remediation evidence; it does not erase the historical FAIL on `0edbe52` or
establish production readiness. The current test matrix corrects the stale
GridCraft formula-recalculation entries based on the later GR-016 runtime report.

## Historical candidate result — 2026-10-23

```text
Candidate: 0edbe524b4fa321b0f73f8601afef390e7f785e6
Reviewer: GPT-6.1 Sol
Verdict: FAIL
Report: docs/reviews/GPT-SOL-REREVIEW-0EDBE52.md
Prototype at review time: operator-only investigation; local DOCX E2E remediation is recorded below and awaits review
Public deployment: NOT READY
Upstream RFC/patch: NOT READY
Upstream publication: LOCKED
```

The failed candidate remains immutable. At review time, Sol found a defect in
the conditional route name: it did not satisfy Seafile's existing `op=update`
prefix check. Commit `0da898f` renames the route. Later isolated runtime work
verified the header hook and DOCX E2E; that work is recorded below and does not
change the reviewed candidate's verdict. Earlier failures remain in their
separate reports. The current worktree is not yet frozen or reviewed.

## Remediation evidence — 2026-10-23

An independent Nemotron review of exact SHA
`a4ecc8e1d0da44a12f7bd9c4e529ed4accdb4a0e` returned **FAIL for candidate
readiness**. It accepted the isolated DOCX click/edit/save/reopen and route-token
runtime evidence, but found ONLYOFFICE regression still unverified and retained
major findings for production origins, authorization edge cases, editor-level
concurrency, other Crafts, security controls and licensing. The two-real-editor
concurrency result below was reproduced after this review and has not itself
been independently reviewed. Full report:
`docs/reviews/REVIEW-NEMOTRON-A4ECC8E.md`.

After the reviewed `0edbe52` SHA, the exact pinned GR-015 Seahub and C server
patches were applied and run in a synthetic rootless Podman environment. Django
checks/migrations and the patched fileserver startup passed. The real synthetic
Seahub file-list click opened WordCraft Web/WASM; a text edit was saved, the
fileserver committed a new head/file ID, WordCraft confirmed success, and a
fresh Seafile click reopened the edit. A simultaneous pair of conditional
Seahub save requests produced one HTTP 200 and one HTTP 409; a fresh WordCraft
open showed the winning paragraph only. A further race used two actual
WordCraft editors: both made different edits and sent Ctrl+S concurrently. One
created a new version; the other remained dirty with HTTP 409. A fresh Seahub
click/reopen rendered only the winner. Detailed evidence and limits are in
`docs/reviews/GR-015/ISOLATED-RUNTIME-E2E-20261023.md`.

This is remediation evidence on the current local tip, not a new frozen GPT
candidate and not a Sol PASS. The initial browser test used a same-origin
loopback proxy; a follow-up on separate Seahub and gateway/Craft loopback origins
verified a WordCraft edit, durable save, and persisted content after a fresh
route load. Production TLS/proxy/CSP/CSRF, adversarial-frame isolation,
ONLYOFFICE regression, live read-only/revocation propagation, unsupported stock/Go
fileserver behavior, and the other Craft apps remain unverified. Public
deployment and upstream publication remain locked.

Nemotron independently reviewed the separate-origin evidence at exact SHA
`36c0bc0f2b534b34c52193519fbb422ac5c22948` and returned **FAIL for candidate
readiness**. It accepted the separate-origin browser handoff and durable-save
evidence but retained findings for ONLYOFFICE preservation, authorization edge
cases, production security topology, unsupported fileserver behavior, other
Crafts, concurrency windows, and licensing. After that review, a fresh gateway
session exposed `Saved — new version` with `confirmedSave=true`; the next fresh
Seafile-backed WordCraft load read a DOCX containing the edit. This is added
prototype evidence, not a new immutable candidate or independent review. Full
report: `docs/reviews/REVIEW-NEMOTRON-36C0BC0.md`.
The exact patched Seahub handler was also exercised with synthetic storage and
an ONLYOFFICE response double: allow-listed DOCX selected ArtCraft, while a
non-allow-listed DOCX selected Seahub's existing ONLYOFFICE template. This is
a routing guard only; Document Server edit/save/version/reopen remains untested.

A further isolated Django runtime check posts a valid synthetic DOCX through the
actual patched `thirdparty-editor/file-save` URL. A read-only permission and an
edit capability whose current permission changed from `rw` to `r` both returned
403 before update-token minting or fileserver transport. The test uses synthetic
Seafile RPC/cache/user dependencies; live revocation propagation and persisted
state remain NOT VERIFIED. See `tests/test_gr015_save_authorization_runtime.py`
and the GR-015 isolated runtime evidence.

## Queue

### GR-038 — Safe Craft Web asset ingestion

```text
Status:      Luna High bounded re-review: provisional ACCEPT; no material finding remains
Change:      exact tag + SHA-256 required; ZIP paths validated; candidate staged without replacing active build
Evidence:    docs/GR-038-CRAFT-ASSET-INGESTION.md
Limit:       host-protocol compatibility check and deployment promotion are not implemented
Upstream:    no upstream artifact or production state changed
```

### GR-001 — Seafile online-editor integration contract

```text
Status:     GPT REVIEW FAIL (Sol); remediation pending re-review
Owner:      artcraft-owner
Reviewer:   artcraft-reviewer (free pass) -> GPT (final)

Branch:     main
SHA:        (filled at freeze time)

Requirements:  Document the real, current Seafile <-> ONLYOFFICE online-editor
               integration and extract the abstract contract Seafile expects from
               an external web editor. Every claim evidenced by Seafile source
               code (file:line) or public documentation.
Decision:       The contract is documented from the DEPLOYED instance (12.0.14 Pro),
               not only from upstream: the doc key, the three tokens, the callback
               statuses, the update call, the lock, and the fact that the save is
               UNCONDITIONAL. A generic, configuration-only third-party-editor hook
               exists upstream AND in Pro.
Files:          docs/reviews/GR-001/DEPLOYED-INSTANCE-CONTRACT.md
Tests:          Documentation review + citation spot-check; no runtime code.
Free review:    FAIL -> remediated (REVIEW-01 F1, F6, F8)
Evidence:       the deployed files, read over SSH, read-only
Known risks:    The ONLYOFFICE path is hardcoded per suite id; the generic hook
                is read-only by design.
```

### GR-002 — Seafile integration point

```text
Status:     GPT REVIEW PENDING
Owner:      artcraft-owner
Reviewer:   artcraft-reviewer (free pass) -> GPT (final)

Branch/SHA: (filled at freeze time)

Requirements:  Choose and justify the best insertion point for a third-party
               web editor (extension/plugin, custom online editor registration,
               external editing service, iframe host page, small integration
               gateway, or upstream patch). Answer the 10 questions of the
               mission, including "can we avoid a permanent fork of Seafile?"
Decision:       (filled at freeze time)
Files:          docs/SEAFILE-INTEGRATION-POINTS.md
Tests:          (filled at freeze time)
Free review:    FAIL -> remediated (REVIEW-01 F2, F5, F7)
Evidence:       docs/SEAFILE-INTEGRATION-POINTS.md; the deployed instance; the
                upstream seahub tree
Known risks:    The hook SHADOWS ONLYOFFICE per extension; the write is
                attributed to the service account, not the user; share links are
                not covered.
```

### GR-003 — ArtCraft Web capability matrix

```text
Status:     GPT REVIEW PENDING
Owner:      artcraft-owner
Reviewer:   artcraft-reviewer (free pass) -> GPT (final)

Branch/SHA: (filled at freeze time)

Requirements:  A verified verdict, per Craft app, on: web build, WASM, host
               bridge, programmatic open, programmatic save, iframe safety, origin
               requirements, browser limitations, maturity. The 13 apps must NOT
               be assumed equivalent.
Decision:       (filled at freeze time)
Files:          docs/ARTCRAFT-WEB-CAPABILITIES.md
Tests:          (filled at freeze time)
Free review:    FAIL -> remediated (REVIEW-01 F4)
Evidence:       docs/ARTCRAFT-WEB-CAPABILITIES.md, docs/reviews/GR-003/WEB-BUILD-SURVEY.md
Known risks:    All 13 apps HAVE a browser build; only 3 have a host bridge; the
                13 are NOT equivalent in their services seam. The baseline audit
                was about the desktop packages and was silent about the web ones.
```

### GR-004 — Common Craft Web Host Contract

```text
Status:     GPT REVIEW PENDING
Branch/SHA: (filled at freeze time)

Requirements:  A reusable, storage-agnostic host contract for embedding Craft
               web editors, reusing existing ArtCraft conventions where they
               exist. Must not embed Seafile concepts in the Craft side.
Decision/Files/Tests/Free review/Evidence/Known risks: (filled at freeze time)
```

### GR-005 — First host-integration technical proof

```text
Status:     GPT REVIEW FAIL (Sol); gateway simulation is not Seafile E2E
Branch/SHA: (filled at freeze time)

Requirements:  Smallest end-to-end proof: Seafile host -> Craft Web -> open ->
               edit -> save -> new Seafile version. Mocks allowed as intermediate
               steps, never as final evidence.
Decision:       GridCraft + .xlsx: .xlsx is in no other library and is not claimed
               by the deployed ONLYOFFICE configuration, so claiming it has ZERO
               blast radius; and GridCraft already ships the bridge, so no
               application had to be changed.
Files:          integration/gateway/, docs/reviews/GR-005/
Tests:          tests/test_integration.py (20 checks) + tests/test_browser.py
Free review:    FAIL -> remediated (REVIEW-02 G1, G4, G5, G6, G8, G9, G10)
Evidence:       docs/reviews/GR-005/ (with browser-proof.png)
Known risks:    The original service-account write path is closed; stock
                Seafile lacks user-bound authorization and atomic CAS, so the
                gateway is read-only until the upstream endpoint exists.
```

### GR-006 — WordCraft Seafile MVP

```text
Status:     GPT REVIEW FAIL (Sol); remediation pending re-review
Branch/SHA: (filled at freeze time)

Requirements:  The 12-step MVP checklist of ROADMAP.md, VERIFIED END-TO-END on
               synthetic DOCX files. Must cover: simple DOCX, text edit, simple
               formatting, save, reopen, Seafile version, read-only, save
               failure, editor close, concurrent modification.
Decision:       The WordCraft `?host=parent` bridge (the GR-014 patch) makes the
               DOCX MVP technically possible. The required synthetic local
               Seafile Web → WordCraft edit → durable version → editor
               acknowledgement → close/reopen flow is now REPRODUCED against
               patched isolated Seahub/C fileserver. It has not been accepted by
               Sol on a new candidate; production ONLYOFFICE regression and
               separate-origin security remain unverified.
Files:          docs/reviews/GR-006/, docs/reviews/GR-014/
Tests:          See `docs/reviews/GR-015/ISOLATED-RUNTIME-E2E-20261023.md`;
               isolated real browser/Seafile E2E reproduced, broader security
               and regression cases remain open
Free review:    historical review-03 PASS is provisional and superseded by Sol FAIL
Evidence:       docs/reviews/GR-006/ and docs/reviews/GPT-SOL-REREVIEW-D9EF476.md
Known risks:    Test used a local same-origin proxy; production origins,
               ONLYOFFICE preservation, permission revocation/read-only, public
               security controls and live deployment remain NOT VERIFIED.
```

### GR-007 — Save protocol

```text
Status:     GPT REVIEW FAIL (Sol); overlapping saves produced a false clean state
Branch/SHA: (filled at freeze time)

Requirements:  Exact save semantics: dirty state -> serialization -> host
               delivery -> authorization/conflict check -> upload -> version
               committed -> acknowledgement -> clean. On failure the Craft
               stays dirty and the UI must not claim success.
Decision:       A save is successful when Seafile has committed a new version. The
               editor holds a ticket and stays dirty until the host answers.
Files:          docs/SAVE-PROTOCOL.md
Tests:          the ticket loop is closed by the application's own log line
Free review:    pending
Evidence:       docs/reviews/GR-006/, docs/reviews/GR-005/
Known risks:    Upstream GridCraft still has optimistic save semantics. The
                local GR-010 patch adds ticketed save results and now has an
                isolated synthetic Seafile save/reopen proof; formula
                recalculation, conflict testing and upstream adoption remain.
```

### GR-008 — Data integrity and conflicts

```text
Status:     GPT REVIEW FAIL (Sol); remediation pending re-review
Branch/SHA: (filled at freeze time)

Requirements:  Concurrent edit, deleted file, renamed file, revoked permission,
               expired session, network loss, interrupted upload, double save,
               browser reload. Must use a mechanism Seafile really provides.
Decision:       Seafile has NO compare-and-swap. The gateway requires an
               upstream atomic save and fails closed instead of using a
               read-then-unconditional-write sequence.
Files:          docs/CONFLICTS.md, docs/reviews/GR-008/
Tests:          tests/test_integration.py (conflict, file-gone, same content)
Free review:    FAIL -> remediated (REVIEW-02 G2: the TOCTOU window is documented)
Evidence:       the Go file server's source, read directly
Known risks:    External-writer concurrency is NOT VERIFIED until an upstream
                atomic CAS/lock endpoint is implemented and exercised.
```

### GR-009 — Web integration security

```text
Status:     GPT REVIEW FAIL (Sol); capability scope, origin isolation and resource controls
Branch/SHA: (filled at freeze time)

Requirements:  XSS, CSRF, CSP, iframe sandbox, postMessage origin validation,
               same-origin/cross-origin isolation, token leakage, replay, session
               fixation, SSRF, malicious/oversized document, ZIP bomb, path
               traversal, save forgery, cross-user access, read-only bypass,
               share-link permissions, expired sessions. `targetOrigin = "*"` is
               forbidden for sensitive messages without a very strong argument.
Decision:       The gateway is the trust boundary and the ONLY defence: an
               op=update file-server token is library-wide, so no Seafile-native
               token is safe in a browser. The browser holds one opaque session id.
Files:          docs/SECURITY.md
Tests:          symlink escape, unknown session, read-only, cross-session
Free review:    FAIL -> remediated (REVIEW-02 G1, G4)
Evidence:       the Go file server's source; the two reviews
Known risks:    CSP, a CSRF check on the state-changing endpoints, and a rate
                limit are still open (S-1, S-2, S-3).
```

### GR-010 — GridCraft Seafile integration

Status: **GPT REVIEW FAIL** on the earlier candidate; the pinned-source bridge
patch now has a reproduced GridCraft Web → isolated synthetic Seafile
save/version acknowledgement → fresh editor reopen path. The narrow bridge
patch received an independent Nemotron PASS with three minor follow-ups; the
runtime evidence does not complete GR-010 or the all-Craft/multi-platform
scope. See `docs/reviews/GR-010/README.md` and
`docs/reviews/GR-010/GRIDCRAFT-SEAFILE-E2E-20261023.md`.

```text
Status:     GPT REVIEW FAIL (Sol on 0edbe52); GridCraft runtime save/reopen now reproduced in synthetic Seafile, but formula recalculation, conflicts and broader app/platform coverage remain open
Branch/SHA: (filled at freeze time)

Requirements:  .xlsx open/edit/save/reopen/conflict via GridCraft Web; all Craft apps remain in the overall product scope.
Decision/Files/Tests/Free review/Evidence/Known risks: (filled at freeze time)
```

### GR-011 — DeckCraft Seafile integration

```text
Status:     NOT IMPLEMENTED — deferred for the upstream DeckCraft host-bridge capability gap
Branch/SHA: (filled at freeze time)

Requirements:  .pptx open/edit slide/save/reopen via DeckCraft Web.
Decision/Files/Tests/Free review/Evidence/Known risks: (filled at freeze time)
```

### GR-012 — Non-office Craft integration

Status: **GPT REVIEW FAIL on 0edbe52**; later local evidence reproduces a
VectorCraft SVG click/edit/save/version/history/reopen in synthetic Seafile.
This does not prove the common host contract or other Craft apps. See
`docs/reviews/GR-012/VECTORCRAFT-SEAFILE-E2E-20261023.md`.

```text
Status:     GPT REVIEW FAIL (Sol); VectorCraft SVG runtime reproduced, common contract/general Craft coverage remain unverified
Branch/SHA: (filled at freeze time)

Requirements:  .pdf via PdfCraft Web and .svg via VectorCraft Web, proving the
               integration is not reserved to Office formats.
Decision/Files/Tests/Free review/Evidence/Known risks: (filled at freeze time)
```

### GR-013 — ArtCraft upstream RFC

```text
Status:     GPT REVIEW FAIL (Sol); stale E2E and credential claims must be corrected
Branch/SHA: (filled at freeze time)

Requirements:  A reusable ArtCraft Web host-integration RFC with the mission's
               required sections. Do not claim Seafile end-to-end validation
               until the required live acceptance flow is proven. NOT PUBLISHED.
Decision:       One shared crate in craft-libs; the message vocabulary three apps
               already use; the ticket and the saveResult answer added; a
               four-step rollout that changes nothing for a person using the app.
Files:          docs/RFC-DRAFT.md
Tests:          (n/a - a document)
Free review:    pending
Evidence:       the three upstream bridges, the reference integration, the patch
Known risks:    The maintainers may prefer a different home than craft-libs.
```

### GR-014 — First ArtCraft upstream patch

```text
Status:     GPT REVIEW FAIL (Sol); packaging/provenance and runtime evidence incomplete
Branch/SHA: (filled at freeze time)

Requirements:  The smallest justified upstream contribution (e.g. a common host
               API primitive). Prepared only; NOT PUBLISHED.
Decision:       One new file in apps/wordcraft-web/ (the bridge) plus three small
               edits; it reuses the async_saves machinery instead of inventing
               anything, so the document is saved only once the host stored it.
Files:          docs/reviews/GR-014/ (README.md + DIFF.patch)
Tests:          it COMPILES for wasm32; it was BUILT and run in a real browser
Free review:    pending (review 03 in flight)
Evidence:       docs/reviews/GR-006/
Known risks:    NOT PUBLISHED. The upstream hard gate holds until GPT REVIEW PASS.
```

### GR-016 — All-app seams and shared Rust transport

```text
Status:      PROTOTYPE IN PROGRESS; not a candidate; bounded Sol low review PASS with minor notes
Branch/SHA:  main / `bdbea5faa7e8b1cdd4c1e526cd3b212e712a0789` (gateway compatibility update pushed); source changes remain in scratch clones
Scope:       inventory all 13 ArtCraft Web app seams; standardize transport; adapt WordCraft and GridCraft first
Evidence:    docs/reviews/GR-016/APP-SEAM-AUDITS-20261024.md, README.md, REVIEW-PORTABLE-CRAFT-PLATFORM-20261024.md
Tests:       standalone craft-platform metadata, 6 native tests and WASM check pass; WordCraft/GridCraft/PdfCraft/CADCraft clean-checkout Rust 1.95 WASM checks pass with --locked against immutable transport revision 90c261de22ef75c4c7c5c5cd1c712d483be0bbc8
Open:        remaining app-specific seams and acknowledgement gaps; security/deployment coverage; single-file Open boundary; runtime/optimized-bundle evidence for the newly pinned PdfCraft/CADCraft builds
GPT review:  NOT REQUESTED; existing project verdict remains GPT REVIEW FAIL on 0edbe524
Publication: LOCKED; no upstream issue, PR, RFC or patch was published

Update 2026-10-24: WordCraft and GridCraft now each have synthetic Seahub/Seafile
edit → durable save → new version → readback → fresh editor reopen evidence after
the shared-transport refactor. The WordCraft run used an actual Seahub file-list
open; GridCraft used the Seahub file route. A GridCraft `SUM(B2:B2)` formula was
also recalculated after B2 changed to 1337 and verified after durable save and
fresh reopen. Exact editor-to-gateway payload hashing and optimized bundle
performance remain unverified. The bounded Nemotron re-review accepted the
updated evidence with minor qualifications; see
`docs/reviews/GR-016/REVIEW-NEMOTRON-GRIDCRAFT-E2E-R2-20261024.md`. Reports:
`docs/reviews/GR-016/SEAFILE-WORDCRAFT-SHARED-TRANSPORT-E2E-20261024.md` and
`docs/reviews/GR-016/SEAFILE-GRIDCRAFT-SHARED-TRANSPORT-E2E-20261024.md`.

Follow-up 2026-10-24: packaged transport revision
`90c261de22ef75c4c7c5c5cd1c712d483be0bbc8` is pinned by the WordCraft,
GridCraft, PdfCraft, and CADCraft patches. All four patches were applied to
clean upstream-source checkouts and pass locked Rust 1.95 WASM checks. This is
build-reproducibility evidence only; other Craft integrations, app runtime
behavior for PdfCraft/CADCraft, and project-level GPT readiness remain open.
See `docs/reviews/GR-016/PORTABLE-APP-PATCHES-20261024.md`.
The bounded independent Sol review returned PASS after two minor documentation/
patch-scope findings were corrected; details and round history are in
`docs/reviews/GR-016/REVIEW-PORTABLE-APP-PATCHES-SOL-LOW-20261024.md`.
```

### GR-017 — PdfCraft durable host-save acknowledgement

```text
Status:      BOUNDED PROTOTYPE REVIEW PASS (Sol low round 4); synthetic Seafile E2E accepted with minor qualifications by Nemotron Free; project GPT remains FAIL
Base:        storytold/pdfcraft `57e531ccca0047597809748b5cb4276336d6051a`
Transport:   storytold/craft-libs `f180fc0d35d521c5d18e118c881d3efde1ec1eee` scratch prototype
Scope:       reuse ticketed shared transport for PdfCraft's existing same-origin host bridge; preserve dirty state until durable result
Evidence:    docs/reviews/GR-017/README.md, SEAFILE-PDFCRAFT-E2E-20261024.md, and patches/pdfcraft-durable-host-ack.patch
Tests:       7 focused native acknowledgement tests, Rust 1.95 WASM check, formatting/diff checks, exact-revision release build, Chromium synthetic-host ACK/reopen smoke, and isolated synthetic Seafile save/version/readback/fresh-reopen reproduction
Open:        lifecycle test gaps remain MINOR for this bounded prototype; file-list click, exact editor-to-gateway payload hash, browser timeout/response loss, deployment security and optimized bundle are NOT VERIFIED
GPT review:  NOT REQUESTED; project remains GPT REVIEW FAIL on 0edbe524
Publication: LOCKED; no upstream issue, PR, RFC or patch was published

Update 2026-10-24: `craft-platform` is packaged with preserved MIT/Apache
notices and pinned at revision
`90c261de22ef75c4c7c5c5cd1c712d483be0bbc8`. PdfCraft's patch now uses that
revision and its clean-checkout locked WASM build passes; details are in the
GR-016 portable app report.
```

### GR-018 — CADCraft durable host-save acknowledgement

```text
Status:      BOUNDED LOCAL PROTOTYPE REVIEW PASS (GPT-6.1 Sol low round 4); no project-level GPT change
Base:        storytold/cadcraft `7bf5905ac97316a7896de8cbc12d243f57b09bd8`
Transport:   `craft-platform` pinned at `56c5e16d79b77751106173c13111ef4fe0a2c0ec`; repin exact review found no blocker/major
Scope:       ticketed save/saveResult adapter; dirty state follows host durable acknowledgement
Evidence:    docs/reviews/GR-018/README.md, cadcraft-host-save.patch, REVIEW-SOL-LOW-R2.md through REVIEW-SOL-LOW-R4.md, REVIEW-TRANSPORT-REPIN-R1.md, CADCRAFT-BROWSER-ACK-SMOKE-20261024.md, CADCRAFT-SEAFILE-E2E-20261024.md
Tests:       Rust 1.95 WASM check; 8 focused acknowledgement tests; 344 engine library tests; fmt/diff checks; local Chromium synthetic-host and isolated synthetic-Seafile edit/save/history/fresh-reopen runs
Open:        Synthetic CADCraft Seafile version/reopen is reproduced; browser failure/timeout/security paths remain NOT VERIFIED; exact editor-to-gateway byte hash and optimized bundle remain open
GPT review:  NOT REQUESTED as a project candidate; project remains GPT REVIEW FAIL on 0edbe524
Publication: LOCKED; no upstream issue, PR, RFC or patch was published
```

### GR-019 — FigCraft shared host-save adapter prototype

```text
Status:      local prototype; focused tests and WASM compile pass; not Seafile E2E
Base:        storytold/figcraft 8d790607ff1ad40e32343ca2116d8fdcf3244c8d
Transport:   craft-platform pinned at 56c5e16d79b77751106173c13111ef4fe0a2c0ec; exact repin review found no new blocker/major
Scope:       one pathless .figcraft file per iframe; ticketed snapshot save ACK; no host Save As
Evidence:    docs/reviews/GR-019/README.md and figcraft-shared-host-save.patch
Tests:       3 engine tests, 1 synthetic-host UI test, Rust 1.95 locked WASM check, patch apply check, fmt/diff checks
Open:        GR-048 verifies actual-WASM browser host-only runtime; durable Seafile dispatch/version/reopen, timeout runtime, and deployment security NOT VERIFIED
Independent: Sol low rounds 1 and 2 returned FAIL; round 3 returned bounded PASS for the original implementation; transport repin R1 scope objection was closed in R2 after comparison against the accepted patch. Full-patch SHA `954850ba5aff7362e776b2331a5a5ff54bf9d71374d7b29bc856c2b7a47c4798`; one MINOR remains for retrying failed dirty-state reports; no project GPT PASS, Seafile E2E, or upstream authorization
GPT review:  NOT REQUESTED as a project candidate; project remains GPT REVIEW FAIL on 0edbe524
Publication: LOCKED; no upstream issue, PR, RFC, or patch published
```

### GR-020 — DeckCraft host-save acknowledgement prototype

```text
Status:      bounded local prototype review PASS (GPT-6 Luna high round 2 on exact current patch); no project-level GPT change
Base:        storytold/deckcraft `0f4fffcf6c71ffa16029d07ac23752fedd783547`
Transport:   `craft-platform` pinned to `56c5e16d79b77751106173c13111ef4fe0a2c0ec`
Patch SHA:   `8d7f98468ce446add5357e10ed8e10e729eb3306fee359d320f09805acc3ee4a`
Scope:       one host-bound presentation; ticketed serialized snapshot save; clean only after matching durable ACK; no host Save As
Evidence:    docs/GR-020-DECKCRAFT-HOST-SAVE.md and docs/reviews/GR-020/
Tests:       2 engine tests, 4 UI lifecycle tests, locked WASM check on 56c5e16, fmt, assets and layers checks pass; full workspace tests did not complete
Open:        browser messaging and Seafile dispatch/version/fresh-reopen NOT VERIFIED; no Seafile route added
CI:          `xtask ci` stops at pre-existing workspace Clippy finding in untouched `crates/matroska/src/demux.rs:726`; `assets`, `layers`, `wasm` and non-strict targeted Clippy pass; workspace test suite remains incomplete
GPT review:  NOT REQUESTED as a project candidate; project remains GPT REVIEW FAIL on 0edbe524
Publication: LOCKED; no upstream issue, PR, RFC, or patch was published
```

### GR-021 — DesignCraft host-save acknowledgement prototype

```text
Status:      bounded local prototype; GR-045 verifies actual-WASM browser host flow; project GPT verdict remains FAIL on 0edbe524
Base:        storytold/designcraft 80d13911b2d20fbb5cd9398696627bb3a715417b
Transport:   craft-platform `56c5e16d79b77751106173c13111ef4fe0a2c0ec`
Patch:       `519c03180b17f035ef8fbfcd08a85bda312f6f0721bfbdf9dc1d9d5992fdf972`
Scope:       one pathless native .designcraft document; serialized snapshot save with durable ticket ACK; no Save As
Tests:       five focused Rust 1.95 tests, locked WASM check, formatting and diff checks PASS
Independent: Luna high R1 found pre-copy transport gap; package fixed/reviewed. Luna high R3 PROVISIONAL: no code blocker/major; R2 P3 peak-serialization-memory qualification is documented
Open:        Seafile version/reopen and production security NOT VERIFIED; GR-045 actual-WASM synthetic open/edit/save/ACK/fresh-reopen evidence does not establish durable persistence; 64 MiB serialized payload cap is after allocation
GPT review:  not a project candidate; project remains GPT REVIEW FAIL on 0edbe524
Publication: LOCKED; no upstream issue, PR, RFC, or patch published
```

### GR-021 — shared transport Open admission

```text
Status:      bounded local transport remediation; project GPT verdict remains FAIL on 0edbe524
Base:        craft-platform package revision d59c3ace80140fa20672131c5ae7c4e6392f8da6
Change:      incoming Open bytes share a cumulative 256 MiB and 64-message budget across same-origin/app transports in one WASM runtime; repeat Open remains supported
Review:      Luna high R2 found one-open compatibility and per-listener state defects; latest bounded review R4 found no functional findings, one wording nit corrected
Tests:       7 native package tests, WASM `--tests` compile, 19 checksums, formatting and diff checks pass; browser tests were not run
Open:        DesignCraft/EffectCraft/FilmCraft app patches need this new transport pin and exact-patch reviews; browser and Seafile runtime remain NOT VERIFIED
Publication: no upstream publication; project and public deployment readiness unchanged
Evidence:    `docs/reviews/GR-021/TRANSPORT-OPEN-ADMISSION-REVIEW.md`
```

### GR-024 — ignore malformed host save acknowledgements

```text
Status:      bounded shared-transport parser fix, pushed at `56c5e16`; project GPT verdict remains FAIL on 0edbe524
Base:        local main `ee140f37be49517e2e35a542fec0fa9453cba27b`
Change:      ignore `saveResult` with missing/non-boolean `ok`; keep valid true/false behavior and public API unchanged
Review:      independent read-only review verified exact diff/hash; no functional issue; test-coverage follow-up for valid true was closed
Tests:       7 native tests, WASM `--tests` compile, all 19 checksums, formatting and diff checks pass; browser tests not run
Open:        active app patches must pin immutable revision `56c5e16d79b77751106173c13111ef4fe0a2c0ec`; browser and Seafile runtime remain NOT VERIFIED
GPT review:  not a project candidate; project remains GPT REVIEW FAIL on 0edbe524
Publication: LOCKED; no upstream issue, PR, RFC or patch published
Evidence:    `docs/reviews/GR-024/`
```

### GR-022 — EffectCraft host-save acknowledgement prototype

```text
Status:      bounded local prototype; project GPT verdict remains FAIL on 0edbe524
Base:        storytold/effectcraft `049070d65c66a73f322b496b22521816e0018f14`
Transport:   craft-platform `56c5e16d79b77751106173c13111ef4fe0a2c0ec`
Patch SHA:   `4e0a1799e36209e1234a1b3ff504ab5ed647cf3bd066af6dec90dacd46ab7407`
Review:      independent exact review found no blocker/major; tests/builds not rerun by reviewer
Tests:       engine 2/2; UI 4/4; Rust 1.95 locked WASM, fmt and diff checks pass per implementer
Open:        browser messaging, host authorization, Seafile version creation and fresh reopen NOT VERIFIED; not in dispatch
GPT review:  not a project candidate; project remains GPT REVIEW FAIL on 0edbe524
Publication: LOCKED; no upstream issue, PR, RFC or patch published
Evidence:    `docs/reviews/GR-022/`
```

### GR-023 — FilmCraft host-save acknowledgement prototype

```text
Status:      bounded local prototype; project GPT verdict remains FAIL on 0edbe524
Base:        storytold/filmcraft `fa550ce2d07bdfee6b1d7b6835e8abc8c6913d00`
Transport:   craft-platform `56c5e16d79b77751106173c13111ef4fe0a2c0ec`
Patch SHA:   `16158f500b2ec12f93c8fcb14867e0b452030dbb338b2d4d7fa8612850a694d4`
Review:      independent bounded R2 source review found no blocker/major; tests/builds were not rerun by reviewer
Tests:       engine 4/4; UI 3/3; Rust 1.95 locked WASM; fmt/diff checks pass per implementer
Open:        GR-047 verifies actual-WASM browser messaging and fresh in-memory iframe reopen; authorization and durable Seafile version/reopen remain NOT VERIFIED; not in dispatch
GPT review:  not a project candidate; project remains GPT REVIEW FAIL on 0edbe524
Publication: LOCKED; no upstream issue, PR, RFC or patch published
Evidence:    `docs/reviews/GR-023/`
```

### GR-025 — SoundCraft host-save acknowledgement prototype

```text
Status:      PROVISIONAL source review; R1 local-open bypass fixed; WASM blocked by pinned-base API mismatch
Base:        storytold/soundcraft `d47abe484d4f9ef0cc9f8e872e0b3880a61a4588`
Transport:   `craft-platform` `56c5e16d79b77751106173c13111ef4fe0a2c0ec`
Patch SHA:   `f8f9da024b80b3292cca1a60ee69eaf4e19c450d7582fac582596fd11aebc331`
Review:      R1 found local picker/drop replacement bypass; R2 confirms guard closes it, no new blocker/major by inspection
Tests:       2 host-save ledger tests and the focused UI regression pass; full WASM passes with GR-027/028/029 overlays (unpatched-base failures are historical)
Open:        GR-027 ports Symphonia, GR-028 addresses CPAL; full WASM passes with GR-029 overlays; browser/Seafile version/reopen NOT VERIFIED; output cap after allocation
GPT review:  not a project candidate; overall project remains GPT REVIEW FAIL on 0edbe524
Publication: LOCKED; no upstream issue, PR, RFC or patch published
Evidence:    `docs/GR-025-SOUNDCRAFT-HOST-SAVE.md`, `docs/reviews/GR-025/`
```

### GR-027 — SoundCraft Symphonia 0.6.1 compatibility

```text
Status:      PROVISIONAL PASS, bounded audio-crate patch; exact independent R5 review found no findings
Base:        storytold/soundcraft `d47abe484d4f9ef0cc9f8e872e0b3880a61a4588`
Patch SHA:   `e4a63489cfdfc0fd3cfc347a1998347bd92bb0b682ac9a25d1051f887e357e6b`
Tests:       57 soundcraft-audio-io tests; locked native/WASM crate checks pass
Open:        full SoundCraft Web WASM now passes with local GR-029 compatibility overlays; browser/Seafile NOT VERIFIED
Publication: LOCKED; no upstream changes
Evidence:    `docs/reviews/GR-027/`
```

### GR-028 — SoundCraft CPAL 0.18.2 playback compatibility

```text
Status:      local patch candidate; independent R1 incomplete (no semantic API finding; exact base/builds not verified)
Base:        storytold/soundcraft `d47abe484d4f9ef0cc9f8e872e0b3880a61a4588`
Patch SHA:   `ff1ced58251397b8077f92ee9b92c7cae1ada25a8a7fe9068c50ba7cdad5901c`
Tests:       implementer reports 36 soundcraft-playback tests and locked native/WASM checks pass; independent reproduction unavailable
Open:        full SoundCraft Web WASM now passes with local GR-029 overlays; browser/Seafile NOT VERIFIED
Publication: LOCKED; no upstream changes
Evidence:    `docs/reviews/GR-028/`
```

### GR-029 — SoundCraft egui 0.37 compatibility

```text
Status:      local compatibility patches; Sol low R3 bounded PROVISIONAL PASS, no findings; GPT REVIEW PENDING
Bases:       SoundCraft `d47abe484d4f9ef0cc9f8e872e0b3880a61a4588`; craft-libs `5c874d51eeb3de70e735c8ce87a59a7dedd47675`
Patch SHA:   craft-ui `5cf2728d20ed74d9fe0521543280d77ce9ef1a5efd3b6f3db3862b6363b06292`; SoundCraft `af31ccc5d69ea1e9577e0a7f989077ccafd9e40cfe3643a2e8c8f934cc6fa098`; lock `d86d74198de55f7f98a4a381d1d18183013f9195c046dd0f56667cbc305f0743`
Checks:      exact GR-025→027→028→029 sequence replays; locked full SoundCraft Web WASM check passes; focused host-save UI test 1/1 passes
Open:        browser screenshot/gutter-scroll runtime and Seafile version/reopen NOT VERIFIED
Publication: LOCKED; no upstream changes
Evidence:    `docs/GR-029-SOUNDCRAFT-EGUI-WASM.md`, `docs/reviews/GR-029/`
```

### GR-030 — SoundCraft browser host-save smoke

```text
Status:      browser protocol smoke reproduced; bounded evidence, GPT REVIEW PENDING
Base:        SoundCraft `d47abe484d4f9ef0cc9f8e872e0b3880a61a4588` with local GR-025/027/028/029 overlays
Transport:   craft-platform `56c5e16d79b77751106173c13111ef4fe0a2c0ec`
Evidence:    Chromium Open → UI edit → ticketed save/ACK → clean → fresh iframe reopen; 66,203,163-byte payload SHA-256 recorded
Open:        in-memory parent only; Seafile version/reopen NOT VERIFIED; payload exceeds gateway's default 50 MiB cap; wasm-opt=0 build is not optimized
Dispatch:    SoundCraft remains excluded
Evidence:    `docs/GR-030-SOUNDCRAFT-BROWSER-SMOKE.md`, `docs/reviews/GR-030/`
```

### GR-031 — SoundCraft Seafile save/version/reopen evidence

```text
Status:      reproduced on isolated synthetic Seafile; Luna High R1/R2 bounded PROVISIONAL PASS; project GPT review pending
Base:        SoundCraft `d47abe484d4f9ef0cc9f8e872e0b3880a61a4588` with local GR-025/027/028/029 overlays
Transport:   craft-platform `56c5e16d79b77751106173c13111ef4fe0a2c0ec`
Evidence:    Seahub file-list click → add Audio 2 → host save ACK → new Seafile file ID/head → 6,877-byte user-bound readback → fresh Seahub reopen showing all three tracks
Readback:    SHA-256 `895bce8fa565730ded872bbf1dd1746ddddc0345e72d9485279e3d987a5a3aff`; exact outgoing message bytes were not separately hashed
Limits:      `wasm-opt=0`; loopback synthetic stack; ONLYOFFICE regression, deployment security and optimized bundle NOT VERIFIED
Dispatch:    SoundCraft remains excluded until review and remaining readiness gaps are addressed
Evidence:    `docs/GR-031-SOUNDCRAFT-SEAFILE-E2E.md`, `docs/reviews/GR-031/`
```

### GR-026 — PhotoCraft host integration assessment

```text
Status:      bounded pathless-open/snapshot-ACK core PROVISIONAL PASS; no browser adapter yet
Base:        storytold/photocraft `a02f2ee41059d3312e7ff24a5af5edcac7b6435a`
Transport:   future app dependency must pin `56c5e16d79b77751106173c13111ef4fe0a2c0ec`
Finding:     `open_file(path, bytes)` binds the name as a local path; browser download uses `write_unconfirmed: true`; pathless binding and revision ACK require app-layer seams and route guards
Tests:       4 engine tests, 1 pathless-open UI test, Rust 1.95 locked PhotoCraft Web WASM check pass
Open:        browser messaging, async UI save lifecycle, Seafile version creation and fresh reopen NOT VERIFIED
GPT review:  not a project candidate; overall project verdict unchanged
Publication: LOCKED; no upstream issue, PR, RFC or patch published
Evidence:    `docs/GR-026-PHOTOCRAFT-HOST-SAVE.md`, `docs/reviews/GR-026/`
```

### GR-032 — PhotoCraft host-save adapter

```text
Status:      GPT REVIEW PENDING — bounded source prototype; R1 findings remediated; R2/R3 independent PROVISIONAL PASS
Base:        storytold/photocraft `a02f2ee41059d3312e7ff24a5af5edcac7b6435a` plus GR-026 core patch
Patch:       `docs/reviews/GR-032/photocraft-host-save.patch`; SHA-256 `487935d8f6db33cf82c85f8d9c8aa0686016612510f15cf34f6b3f05a2c53fe7`
Transport:   `craft-platform` exact rev `56c5e16d79b77751106173c13111ef4fe0a2c0ec`, locked in Cargo.lock
Review:      R1 found unbounded SaveResult enqueue and a swallowed listener-registration error. R2 verified the included fixed-slot inbox and listener failure handling; R3 verified documentation of the 50 MiB/serialization limit. Both are bounded provisional reviews, not project GPT PASS.
Tests:       UI lifecycle test 1/1, inbox/listener tests 2/2, Rust 1.95 locked Web WASM check, clean-base patch apply and diff checks pass
Open:        browser message execution, Seafile durable version/readback/fresh reopen, ONLYOFFICE regression NOT VERIFIED; gateway default is 50 MiB and serialization occurs before rejection, so oversized payload peak memory/compatibility is NOT VERIFIED
Publication: LOCKED; no upstream issue/PR/RFC, commit or push
Evidence:    `docs/GR-032-PHOTOCRAFT-HOST-SAVE.md`, `docs/reviews/GR-032/`
```

### GR-033 — PhotoCraft browser host-protocol smoke

```text
Status:      browser Open/edit/save/ACK/fresh iframe reopen reproduced; bounded independent evidence review PROVISIONAL ACCEPT
Scope:       same-origin Chromium; parent retains bytes in JavaScript memory
Save bytes:  4,995; SHA-256 cbaa7b458588780210d1da7a267d2d5223d6808e0b15ea9e80e84d23ea980f34
Evidence:    screenshot, static host harness and synthetic fixture in docs/reviews/GR-033/runtime/
Limits:      no Seafile write/version/readback, optimized bundle, deployment security or ONLYOFFICE regression
Dispatch:    PhotoCraft remains excluded; no project GPT PASS or upstream publication approval
Review:      Nemotron 3 Ultra PROVISIONAL ACCEPT; no blocker/major; reviewer did not rerun browser or builds
```

### GR-034 — PhotoCraft gateway payload validation

```text
Status:      gateway-only validation; Nemotron 3 Ultra R2 bounded PROVISIONAL PASS
Base:        repository main at 39b6944; native format source storytold/photocraft a02f2ee41059d3312e7ff24a5af5edcac7b6435a
Change:      `.pcraft` validation requires exactly one nonempty exact root `manifest.json` in ZIP central-directory metadata; no decompression
Tests:       `python3 tests/test_gateway_unit.py` passes; malformed ZIP, missing/nested/duplicate/empty manifest, native fixture acceptance and invalid save-before-write are covered
Limits:      shape check only; no manifest JSON/CRC/semantic validation; Seafile runtime unavailable and NOT VERIFIED
Dispatch:    unchanged; `.pcraft` intentionally not added to integration/config/dispatch.json
Review:      R1 MINOR test gap (duplicate/empty manifest) fixed; R2 confirmed coverage by source inspection, no tests rerun
Publication: no upstream action, service/config change or Seafile access
Evidence:    `docs/GR-034-PHOTOCRAFT-GATEWAY-VALIDATION.md`
```

### GR-035 — PhotoCraft optimized Web host smoke

```text
Status:      bounded optimized-bundle browser smoke; Nemotron PROVISIONAL ACCEPT, no blocker/major
Base:        PhotoCraft a02f2ee41059d3312e7ff24a5af5edcac7b6435a + GR-032 host adapter patch
Build:       Trunk 0.22.0 `trunk build --release`; `wasm-opt -Oz` completed; WASM 26,342,447 bytes
Flow:        real PhotoCraft WASM opens a 4,000-byte synthetic fixture in the GR-033 same-origin harness; UI edit; 4,984-byte ticketed save; exact ticket ACK; fresh iframe reopen shows Layer 1 and dirty=false
Save hash:   `92e93c2b993b7de073a2c870aba522d7f9112647d9d1181d2b8592df665936b3`
Limits:      parent retains bytes in JS memory; no gateway/Seafile call, version, or storage-backed reopen; `.pcraft` remains out of dispatch
Review:      PROVISIONAL ACCEPT; screenshot does not identify loaded WASM resource hash
Evidence:    `docs/GR-035-PHOTOCRAFT-OPTIMIZED-BROWSER-SMOKE.md` and `docs/reviews/GR-035/`
```

### GR-037 — PhotoCraft exact save-byte provenance and Seafile reopen

```text
Status:      synthetic Seafile E2E; exact bytes match at editor message, gateway body and Seafile readback; independent review PROVISIONAL ACCEPT, final wording MINOR corrected but not re-reviewed
Base:        PhotoCraft GR-032 adapter + GR-036 repaint fix; no app source patch in this follow-up
Flow:        Seahub open → PhotoCraft edit → Ctrl+S → version 2→3 → byte-identical Seafile readback → fresh Seahub route/new editor session
Bytes:       8,555 at all three boundaries; SHA-256 ea0121c1e465c753947005e1ff4452cc031f734baed3345400bcd3a96218c4ca
Limits:      synthetic loopback; wasm-opt=0; deployment/security and ONLYOFFICE regression NOT VERIFIED; PhotoCraft remains out of dispatch
Evidence:    `docs/reviews/GR-037/`
```

### GR-036 — PhotoCraft synthetic Seafile save/version/reopen

```text
Status:      bounded synthetic Seafile E2E; independent R2 PROVISIONAL ACCEPT, no blocker/major; GPT REVIEW PENDING
Base:        PhotoCraft a02f2ee41059d3312e7ff24a5af5edcac7b6435a + GR-032 adapter + GR-036 repaint fix
Build:       `trunk build --release`, wasm-opt=0; loaded WASM 35,820,040 bytes, SHA-256 d4f339df6312429fa15de653a37b3ef156cee84a3c58eee1358caee34523324c
Flow:        Seahub open → PhotoCraft host Open → add Layer 1 → Ctrl+S → host confirmation → Seafile history 1→2 → fresh Seahub route/session reopens Layer 1
Readback:    4,984 bytes, SHA-256 92e93c2b993b7de073a2c870aba522d7f9112647d9d1181d2b8592df665936b3
Limits:      synthetic loopback only; temporary `.pcraft` route not committed; exact browser-message bytes not independently hashed; security, ONLYOFFICE and optimized production bundle NOT VERIFIED; see independent R1/R2 evidence review
Dispatch:    committed `integration/config/dispatch.json` unchanged; PhotoCraft remains excluded
Evidence:    `docs/GR-036-PHOTOCRAFT-SEAFILE-E2E.md`, `docs/reviews/GR-036/`
```

## GPT review instruction (for the future session)

```text
Do not trust previous free-model PASS verdicts.

Independently inspect and verify:

- Seafile integration assumptions
- OnlyOffice reference analysis
- ArtCraft Web capability matrix
- Host Contract
- browser messaging
- authentication
- authorization
- Save protocol
- version creation
- concurrency handling
- data integrity
- security
- licensing
- deployment
- source code
- diffs
- tests
- upstream RFC
- proposed ArtCraft patches

Return:

BLOCKER
MAJOR
MINOR

Only GPT REVIEW PASS may unlock upstream publication.
```
