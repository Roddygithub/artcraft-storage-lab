# Re-Foundation Report — ArtCraft Storage Lab

Date: 2026-10-31. Mandate: `Claude.md` (commit `f30d39c`). Status of this document: **draft for owner review**. Nothing in this report has been published, and no production system was touched while producing it.

```text
REFOUNDATION_STATE=DECISION_REACHED, BRIDGE_PROTOTYPE_BUILT, REAL_SEAFILE_SLICE_PASSED (stock Seafile CE 13.0.28 + ONLYOFFICE 9.4 + 4 upstream ArtCraft bundles, HTTP 45/45 + browser 17/17)
DECISION=CHANGE_PRODUCT_FORM (+ REDUCE_SCOPE, + PAUSE_UNTIL_UPSTREAM_MATURITY for ArtCraft office apps)
PRODUCTION_STATUS=UNTOUCHED (by this audit; but see §3.4 — the live instance already carries GR-015 patches)
UPSTREAM_STATUS=LOCKED
```

Labels used throughout: **FACT** (verified in code or primary source), **EVIDENCE** (recorded by the project, not independently replayed), **ASSUMPTION**, **INFERENCE**, **DECISION**.

---

## 1. What problem are we actually solving?

Problem statement with no ArtCraft assumption:

> A self-hosting Seafile user clicks a supported file in Seafile Web. A good open-source web editor opens it in place. Save writes the new bytes back as a normal Seafile version, attributed to that user, honouring that user's permission. Reopening shows the edit. No SeaDrive, no download/upload, no desktop app.

Requirement classification:

| Requirement | Class | Note |
| --- | --- | --- |
| Click in Seafile Web opens the editor | essential | this is the whole UX |
| Save → new Seafile version, user-attributed, permission-checked | essential | Sol blockers 1–2 were about this, correctly |
| Reopen shows the edit; history works | essential | |
| Self-hostable, open source, survives Seafile upgrades | essential | "no permanent fork" was a phase-2 exit criterion from day one (`ROADMAP.md` phase 2) |
| Editor confirms save only after durable storage | desirable | correct engineering, but Seafile's own ONLYOFFICE/WOPI paths do not offer it either (FACT, §3.2) |
| Server-side compare-and-swap on save | **historical** | introduced to answer Sol FAIL #1 ("silent overwrite"); Seafile applies no such check to ONLYOFFICE, Collabora, SeaDoc or Excalidraw (FACT, §3.2). A client-side `Version` check before write gives the same protection as Nextcloud's WOPI host |
| DOCX/XLSX/PPTX editing | essential for the user | **already solved** on the owner's instance by ONLYOFFICE (FACT) |
| SVG / raster / CAD / native project formats | desirable → accidental | SVG/raster are real gaps in Seafile; `.pcraft/.figcraft/.designcraft/.fcproj/.ecproj/.scraftz` have zero interoperability value in a document platform (INFERENCE) |
| Use ArtCraft | **accidental** | implementation choice; the repository name is not a requirement |
| Support 5 / 13 apps | accidental | scope expansion of 10-23 and 10-26 (`HISTORY.md`) |
| Gateway, Host Contract, Rust transport, Seahub + C patches | accidental | consequences of the two choices above |
| Nextcloud/ownCloud adapters | unnecessary | both platforms already have their own editor-slot APIs and WOPI; nobody asked |

---

## 2. Current reality (reconstructed from code, not from reports)

| Field | Value |
| --- | --- |
| LOCAL_HEAD | not observable from this audit (the mandate's `~/Projects/artcraft-storage-lab` is on the owner's machine) |
| REMOTE_HEAD | `f30d39cfbc72f93b8cb52285436cc4a1cac83485` (`main`, 2026-10-29, "add Claude project re-foundation mandate") |
| WORKTREE_STATE | fresh clone, clean |
| RECENT_HISTORY | 158 commits, 157 of them between 2026-10-22 and 2026-10-26; ~80 GRs in five days; docs churn 50.7k lines vs code 10.1k |
| CURRENT_ARCHITECTURE | browser → patched Seahub `view_lib_file` mints capability → form POST to **separate-origin** Python gateway (`integration/gateway/`, 1,557 LOC, hand-rolled on `BaseHTTPRequestHandler`) → host page + same-origin Craft WASM iframe → `postMessage` ticket/ACK protocol → gateway → patched Seahub `thirdparty-editor/file-save/` → patched **C** fileserver `update-conditional-api` |
| CURRENT_DISPATCH | `integration/config/dispatch.json`: docx→WordCraft, xlsx→GridCraft, pdf→PdfCraft, svg→VectorCraft (polling adapter, not the contract), pcraft→PhotoCraft. A second, hand-synchronised allowlist lives in Seahub settings. `scripts/verify-dispatched-candidates.sh` still expects four routes (stale) |
| CURRENT_PATCHES | `docs/reviews/GR-015/seahub-12.0.14.patch` (283 lines) + `seafile-server-12.0.14.patch` (103 lines, C). Go fileserver: unsupported. Stock Seafile: read-only, save returns a misleading "file no longer exists" |
| CURRENT_APP_ADAPTERS | 13 patches, 350–700 added lines each, all touching upstream `crates/engine` / `crates/ui-egui`, pinned to a git dependency on **this lab repo**, several bumping upstream MSRV; SoundCraft needs three extra dependency patches just to build |
| CURRENT_SHARED_TRANSPORT | `integration/rust/craft-platform/` = divergent fork of upstream `craft-libs/crates/platform`; ~490 of 1,781 LOC are host-protocol; generic, not Seafile-specific |
| CURRENT_SEAFILE_MODIFICATIONS | **The owner's live Seafile 12.0.14 Pro carries the patched Seahub and a patched `seaf-server` binary** (`docs/GR-059-*.md`, rollback archive recorded). `docs/SECURITY.md`, `docs/SEAFILE-INTEGRATION-POINTS.md`, `integration/README.md` still say the opposite — stale |
| CURRENT_SECURITY_MODEL | capability in gateway RAM, 30-min absolute TTL plus 15-min idle TTL, 256-session LRU, all state lost on restart; per-save permission recheck against Seahub (a real strength); capability sent to Seahub in query strings; nonce CSP on host page, none on static editor HTML; rate limit keyed on TCP peer (one bucket behind the proxy) |
| CURRENT_SAVE_MODEL | durable-before-ACK holds **only with the patches**; CAS precondition includes the **library head**, so any commit to any other file in the library between open and save yields 409 (acknowledged "deliberately conservative"); the C patch disables Seafile's identical-content no-op, so unchanged saves create versions, contradicting `docs/CONFLICTS.md:118` |
| CURRENT_TEST_MODEL | 95 solid gateway unit checks (`tests/test_gateway_unit.py`); Playwright tests against a synthetic iframe; three tests need a patched Seahub checkout; live tests need the patched instance. No runner, no CI. `TEST-MATRIX.md` has 90 "NOT VERIFIED" cells |
| CURRENT_DEPLOYMENT_MODEL | gateway runs on the developer desktop via Tailscale Serve; dedicated LXC provisioned then paused; editor bundles are 19–74 MB because every lab build used `wasm-opt=0` |
| CURRENT_REVIEW_MODEL | per-GR free-model R1…R5 → "PROVISIONAL PASS" on nearly every GR; six final GPT/Sol reviews → **5 FAIL, 1 INCOMPLETE, 0 PASS**; last reviewed SHA `95d8983`; 4 of the last 10 GRs are documentation reconciliation |
| CURRENT_UPSTREAM_MODEL | RFC drafted, nothing published; the drafted Seafile patch targets a Pro-tagged, proprietary C server and excludes Go — weak upstreamability |

### 2.1 Assumptions the project held that are now invalidated

1. **"Seafile has no generic external-editor write channel, so we must patch."** FALSE on Seahub ≥ 13.0, PARTIALLY TRUE on 12.0. Seahub ships a complete **WOPI host** (`seahub/wopi/`): CheckFileInfo, GetFile, PutFile, LOCK/UNLOCK/REFRESH/GET_LOCK (PUT_RELATIVE on master only), in **CE and Pro**, configured by a discovery XML whose `<action ext= name= urlsrc=>` elements are read verbatim with no `<app>` or proof-key check; PutFile writes through `update-api` as the token's user. (FACT: `seahub/wopi/utils.py`, `seahub/wopi/views.py`.) **Routing caveat (FACT, independently re-verified):** in `view_lib_file`, the WOPI branch sits inside `elif filetype in (DOCUMENT, SPREADSHEET, PDF)`. On the **12.0** branch, SVG, IMAGE, TEXT and unknown types return earlier in the chain, so on the owner's 12.0.14 the WOPI slot can only serve office/PDF files. On **13.0 and master** the office `elif` precedes SVG/IMAGE/TEXT, so any extension listed in the discovery XML routes to the WOPI editor; `.pdf` is still captured first by the built-in PDF viewer unless the edit query flag is set. The project evaluated the read-only `thirdparty_editor` hook and ONLYOFFICE's bespoke callback, and never evaluated the WOPI slot as a generic editor slot.
2. **"Self-hosted office editing needs ArtCraft because ONLYOFFICE CE is limited."** FALSE: ONLYOFFICE Docs 9.4.0 "Removed the limitation of 20 simultaneously opened documents" (FACT, upstream CHANGELOG; release date not verified). Collabora's CODE page says "not recommended for production" and states no connection limit either way (EVIDENCE only). The owner already runs ONLYOFFICE 9.4.0.
3. **"The ACK protocol needs our fork."** PARTIALLY FALSE: upstream has since merged a same-origin `?host=parent` postMessage bridge in WordCraft (#3822, 2026-10-24), GridCraft, PdfCraft and CADCraft, with `ready/open/save/dirty/failed`. Still missing upstream: a save acknowledgement. That one primitive is the lab's genuinely novel contribution.
4. **"ArtCraft is a mature editor ecosystem."** NOT ESTABLISHED: every Craft app repo was created between 2026-09-30 and 2026-10-16; upstream self-reports WordCraft "~60% ready", GridCraft "~50%", fidelity on real-world OOXML as the main unmet beta goal; several minor releases per week (FACT from READMEs/releases). A report of a broken PhotoCraft web package in v0.17.0 could not be confirmed by the independent reviewer (v0.17.0 and v0.18.0 both ship a web ZIP) — UNVERIFIED, dropped from the argument.
5. **"Server-side CAS is required."** NOT REQUIRED to match the field: Seahub's ONLYOFFICE callback, its WOPI PutFile, SeaDoc and Excalidraw all write unconditionally; the fileserver's `head` parameter is a merge base, not a guard; Nextcloud's WOPI host protects with a timestamp check before write, i.e. client-side optimistic check with a TOCTOU window. (FACT.)
6. **"Cheap review layers predict the gate."** FALSE: near-100 % PROVISIONAL PASS at the GR layer vs 0 % at the GPT layer.

### 2.2 Things the project got right (preserve)

- Separate origins for Seahub and the editor (Sol `afec19e`) — still correct for any design that embeds third-party WASM.
- User-bound writes; capability must never be an account token; preview capability must never become write authority.
- "Clean only after durable ack" and the ticket/`saveResult` idea; overlap and stale-ack rejection; `beforeunload` guard.
- The Seafile API knowledge in `docs/reviews/GR-008/` (`last_modify` is mtime only, `head` is not a guard, update tokens are library-wide, identical content creates no commit).
- Byte-identity capture at the message boundary; "never dirty → silent no-op" as a test smell; realistic XLSX fixtures.
- Bounded ZIP extraction and SHA-pinned bundles.

---

## 3. Challenges

### 3.1 Is ArtCraft the right editor ecosystem? → **B/C: partially, not yet**

| App | Format value in a DMS | Upstream state (2026-10-31) | Verdict |
| --- | --- | --- | --- |
| WordCraft / GridCraft / DeckCraft | high, but **already served by ONLYOFFICE** on the owner's instance with better fidelity and co-editing | alpha, ~50–60 % self-reported, bridge merged (no ack) | **PAUSE**. Re-evaluate when upstream declares OOXML fidelity beta and merges a save-ack |
| PdfCraft | medium (ONLYOFFICE 9+ edits PDF text/forms; Seafile 13 opens PDFs in ONLYOFFICE; Seahub's built-in PDF viewer takes `.pdf` before the WOPI branch unless the edit flag is set) | alpha, bridge merged | optional adapter, low priority |
| VectorCraft | medium (SVG is a real Seafile gap) | alpha, **no host bridge**; only an automation API; `.vectorcraft` native | wait for an upstream bridge; do not ship the polling adapter |
| PhotoCraft | medium (raster is a gap) but `.pcraft` is useless in Seafile; PSD/PNG round-trip would be the value | early alpha, no bridge, web package currently broken upstream | wait |
| CADCraft | low for this owner | pre-alpha, bridge merged | no |
| FigCraft, DesignCraft, FilmCraft, EffectCraft, SoundCraft, LightCraft | native project formats only | pre-alpha/alpha | **drop** |

DECISION: ArtCraft is not a justification for an integration project today. It is a *candidate editor family* that a generic editor slot could host later.

### 3.2 Is the gateway justified? → **not in its current form**

The gateway exists because (a) Seahub cannot write back without a patch via the hook the project chose, and (b) the WASM bundle must be same-origin with the host page. (a) disappears with the WOPI slot **on Seahub ≥ 13** (on 12.0 the slot only reaches office/PDF files, §2.1). (b) remains, but it only requires a **static file server plus a stateless WOPI relay**: the browser cannot call Seahub's WOPI endpoints directly (no CORS, FACT), so a tiny server component must forward CheckFileInfo/GetFile/PutFile with the access token Seahub already posted into the iframe. No session store, no capability minting, no rate limiter, no retry receipts: PutFile of identical bytes is a natural no-op at the fileserver, so retry is idempotent for free.

### 3.3 Are the Seafile patches acceptable? → **no**

- They target a **proprietary** Pro build's C server (`docs/LICENSING.md` §1): unsupportable through any upgrade.
- The Go fileserver is excluded; Seafile's changelogs show active Go fileserver work in 13.x.
- The library-wide head precondition breaks shared libraries by design.
- They impose a stricter write semantic than Seafile uses for its own editors, for a guarantee the client can approximate.
- An equivalent "PutFile" already exists upstream in `seahub/wopi/views.py`.

### 3.4 Production status (owner attention required)

EVIDENCE: `docs/GR-059-*.md` records patched Seahub source **and a patched `seaf-server` binary installed on the owner-managed live Seafile LXC 108** (rollback archive created), and EVIDENCE: since GR-076 (2026-10-26) the ONLYOFFICE client `api.js` URL returns **404** on that instance while Document Server probes return 200; nobody diagnosed it (`STATUS.md`, GR-080). Two owner-only actions follow (§7).

### 3.5 Is the Host Contract the right abstraction? → **half**

The transport (`postMessage`, origin + source check, `open/save/dirty/failed`) is real and upstream now ships it. The lifecycle (durable ack, snapshot identity) is real too but lives in each app's engine — GR-016's own finding: "the applications do not share one interchangeable save hook". The smallest correct abstraction is therefore **not** a shared Rust crate owned by the lab; it is a **documented message protocol with one added message (`saveResult{ticket, ok, version}`)** proposed upstream, implemented per app by upstream. The lab should own the *host side* only.

### 3.6 Save model → client-side optimistic check, WOPI locks, no server patch

Required property: a user-visible successful save corresponds to durable storage of the intended generation. Achievable without patches:

1. On open: CheckFileInfo → remember `Version` (= `obj_id`); take a WOPI LOCK (Seahub stores it, Pro also sets the Seafile file lock, visible in Seafile Web).
2. On save: CheckFileInfo again; if `Version` ≠ remembered → surface conflict (offer "save as copy" via PUT_RELATIVE if `UserCanNotWriteRelative` is false). Else PutFile; on 200, CheckFileInfo once more → new `Version` becomes the remembered one; only then answer the editor's ticket.
3. Lost response: CheckFileInfo + GetFile hash compare (the project's GR-052 reconciliation logic, reused as-is).

Residual race: milliseconds between check and PutFile, same class as Nextcloud; strictly better than Seahub's own ONLYOFFICE/WOPI behaviour. "Save as copy" via PUT_RELATIVE exists on Seahub master only, not on 12.0.

**Permission gap (FACT from source, not exercised at runtime, UPSTREAM LOCKED):** Seahub's WOPI PutFile never reads the token's `can_edit`; the `access_token_check` decorator does not either; the token caches `can_edit` at mint time for `WOPI_ACCESS_TOKEN_EXPIRATION` (default 12 h). Downstream, `seaf_web_at_manager_get_access_token` and both fileservers' `update-api` paths validate only the token/op pair, not repo permission. Consequences for the bridge, which the design must absorb: (a) the bridge **must refuse PutFile itself when `UserCanWrite` is false**, because Seahub will not; (b) permission revocation mid-session is not honoured until the token expires — the current gateway rechecks permission on every save and expires sessions after 30 min/15 min idle, so this is a **guarantee lost** unless the deployment sets `WOPI_ACCESS_TOKEN_EXPIRATION` short (the manual's own example is 30 min) and the bridge re-runs CheckFileInfo before each PutFile. Any disclosure to Seafile is the owner's decision.

---

## 4. Architecture families compared

| | A. Current (gateway + Seahub/C patches + per-app ticket patches) | B. Seafile-native editors only (ONLYOFFICE/Collabora; no ArtCraft) | C. Generic **WOPI editor bridge**: stateless relay + static bundles, plugs any non-WOPI web editor into Seahub's existing WOPI slot | D. ArtCraft-centric storage provider (WebDAV/Seafile backend inside the apps) | E. `thirdparty_editor` hook + minimal Seahub-only PR adding `file-save` | F. Upstream-only (ack protocol to ArtCraft, PutFile fixes to Seafile), no lab runtime |
| --- | --- | --- | --- | --- | --- | --- |
| UX (click → edit → version) | yes | yes for office/PDF, nothing for SVG/raster | yes, any extension **on Seahub ≥ 13**; office/PDF only on 12.0 | **no**: no click-to-open from Seafile Web; requires in-app login | yes, any extension, any Seahub version (hook runs first) | n/a |
| Seafile patches | Seahub + C fileserver, Pro binary | none | **none** | none (WebDAV) | one Seahub PR, must be accepted | none |
| Works on CE, Pro, Go, C | C-only, Pro-tainted | yes | **yes** | yes | after upstream merge | — |
| Engineering effort remaining | large, open-ended | ~0 (fix the api.js 404) | small: ~400–600 LOC relay + ~300 LOC host page + discovery XML | large, upstream-owned, in flight (#518, #4886) | small but blocked on Seahub acceptance | zero runtime |
| Editor patches | 13 forks, engine-level | none | **none** (uses upstream bridges; degraded "optimistic" mode until ack lands) | none | none | — |
| Security surface | sessions, capability minting, custom HTTP, CSP, rate limit; per-save permission recheck | Seafile's own | token relay only; token already in browser by Seahub design; separate origin kept; **bridge must enforce `UserCanWrite` and re-CheckFileInfo per save** because Seahub's PutFile does not; token TTL is Seahub's (12 h default, set it to 30 min) | app holds user credentials | moderate | — |
| Conflict correctness | CAS incl. library head (over-strict) | none (last writer / merge) | optimistic `Version` check + WOPI locks (Nextcloud parity) | WebDAV If-Match | CAS on file id | — |
| Seafile upgrade resilience | **fork forever** | native | config-only (WOPI is public, documented) | native | depends on upstream | — |
| ArtCraft upgrade resilience | re-base 13 patches per release (several per week) | n/a | pin release ZIP + SHA; protocol drift only | n/a | same as C | — |
| Self-hoster complexity | gateway + patched server + proxy | already running | one container + five `seahub_settings.py` keys (`ENABLE_OFFICE_WEB_APP`, `OFFICE_WEB_APP_BASE_URL`, `OFFICE_WEB_APP_FILE_EXTENSION`, `ENABLE_OFFICE_WEB_APP_EDIT`, `OFFICE_WEB_APP_EDIT_FILE_EXTENSION`) + one proxy route; discovery XML must list both `view` and `edit` actions per extension | per-app config | patched Seahub | — |
| Upstreamability | poor (Pro C patch, Go excluded) | n/a | high: a generic bridge is useful to draw.io/SVG-edit/embedPDF users too; the ack message is a small ArtCraft RFC | depends on upstream | medium | high |
| Co-editing / locks | none | ONLYOFFICE yes | WOPI locks + Pro file locks for free; no co-editing | none | none | — |
| Long-term cost | highest | lowest | low | not ours | low-medium | lowest |

Scoring was not biased toward A; A loses on the two hard constraints the project itself set (no permanent fork, upgrade resilience). Two variants considered and set aside: emulating the ONLYOFFICE Document Server protocol instead of WOPI (also any-extension on CE/Pro, but it would displace the real ONLYOFFICE slot the owner uses); and the Pro/13 `ENABLE_MULTIPLE_OFFICE_SUITE` mechanism, which selects a suite per library and is a cleaner answer than an aggregated discovery XML if the owner wants Collabora alongside the bridge (see U3).

---

## 5. Decision

```text
DECISION = CHANGE_PRODUCT_FORM
  + REDUCE_SCOPE   (office formats stay on ONLYOFFICE; drop native-format apps; drop Nextcloud/ownCloud adapters)
  + PAUSE_UNTIL_UPSTREAM_MATURITY (ArtCraft office apps; VectorCraft/PhotoCraft until they ship a host bridge)
```

Leading architecture: **C**, with **B as the immediate answer for DOCX/XLSX/PPTX/PDF**.

**Precondition for C on this owner's instance: Seafile ≥ 13.** On 12.0.14 the WOPI slot cannot reach non-office files (§2.1). Until the upgrade, the honest answer for this owner is B alone: there is no zero-patch path for SVG/raster on 12.0, and E (a Seahub patch, even a small one) is exactly what this report rejects. Seafile 13.0 has been GA since January 2026, so this is an ordinary upgrade, not a blocker, but it is the owner's call.

**Guarantees dropped relative to A, and their mitigations:**

| Dropped | Why acceptable / mitigation |
| --- | --- |
| Server-side CAS on file id + library head | replaced by client-side `Version` check before PutFile (Nextcloud parity); the library-head part was over-strict anyway |
| Per-save permission recheck by the gateway | the bridge re-runs CheckFileInfo before each PutFile and refuses when `UserCanWrite` is false; set `WOPI_ACCESS_TOKEN_EXPIRATION` to 30 min; revocation inside that window is not honoured (same as Collabora users today) |
| Content-signature / export-name guard (gateway refused non-OOXML bytes under a `.docx` name) | reimplement in the bridge host page before PutFile; cheap |
| 30-min capability held server-side only | WOPI token reaches the browser by Seahub design (as for Collabora); the bridge holds nothing server-side |
| Retry receipts | identical bytes are a fileserver no-op, so retry is idempotent without receipts; lost-response reconciliation (GR-052 logic) is kept |

WHY: C satisfies every hard constraint with zero Seafile patches and zero editor patches, reuses a public, documented, CE-available Seafile protocol, reduces the runtime to a stateless relay and static files, keeps the lab's two real contributions (host-side save discipline, the `saveResult` proposal), and lets ArtCraft be adopted editor-by-editor only when it beats what Seafile already has. A does not survive its own phase-2 exit criterion. B alone leaves the SVG/raster/diagram gap and discards the lab's knowledge. D does not meet the click-to-open requirement. E is dominated by C (E needs an upstream merge, C needs none). F is where C's protocol contribution should eventually go, but gives the owner nothing to use.

The repository becomes: **a generic Seafile external-web-editor bridge + a compatibility lab** (fixtures, protocol tests, editor adapters, regression evidence). ArtCraft is one adapter family among several (draw.io embed mode and SVG-edit are cheaper first proofs of the gap).

Minimum useful product: discovery XML + relay + host page + **one** adapter that proves the thesis end-to-end against an **isolated Seafile CE** container: WordCraft **upstream release bundle, unpatched** (uses its merged bridge; proves "no patch on either side"), compared against ONLYOFFICE on the same file. Success = 12-step MVP checklist of `ROADMAP.md` passes, with the editor in degraded-ack mode documented honestly.

### Components to keep

- Knowledge: `docs/reviews/GR-008/`, GR-001 deployed contract, GR-016 seam audits, the GPT review findings (as a checklist), `docs/SECURITY.md` lessons (separate origins, capability ≠ account token).
- Host-page logic as a JS reference: origin+source checks, overlap refusal, dirty/save revision counters, `beforeunload`.
- GR-052 lost-response reconciliation logic; GR-049 idempotent-retry tests (re-targeted at WOPI PutFile).
- `scripts/craft_web_zip.py` bounded extraction; SHA-pinned bundle fetch (simplified to upstream release ZIPs).
- Fixtures (`tests/fixtures/`) and the "reopen in editor or it didn't happen" test discipline.
- The `saveResult{ticket, ok, version}` proposal, rewritten as a short upstream RFC to ArtCraft (prepared locally, **not published**).

### Components to remove (sunk cost)

- `integration/gateway/` session store, capability minting, rate limiter, body framing/deadline code, `/open/` flow.
- `docs/reviews/GR-015/*.patch` and **their live deployment** (owner rollback, §7).
- `integration/rust/craft-platform/` fork and all 13 per-app patches, SoundCraft dependency patches, candidate-manifest machinery (GR-054–058, 071).
- The VectorCraft polling adapter.
- Nextcloud/ownCloud target scope in `README.md`/`ROADMAP.md`.
- The GR numbering, the five-round free-model review loop, and the reconciliation documents whose only purpose was keeping earlier claims consistent.

### Review process going forward

Keep "implementation ≠ independent review". Replace the GR loop with: unit/protocol tests on every change; one independent bounded review per merged change (cheap model); one strong forensic review at each milestone (slice working / candidate frozen); GPT/Sol only on a frozen candidate the team believes in.

---

## 6. Major uncertainties

| # | Uncertainty | How to resolve |
| --- | --- | --- |
| U1 | Seahub's WOPI `lang_dict[language_code]` raises `KeyError` for unsupported UI languages (FACT from code) — affects Collabora users too; may need an upstream fix or a documented workaround | reproduce in the isolated CE container |
| U2 | ~~Whether WOPI PutFile with a view-only token is rejected by the fileserver token layer~~ **Resolved from source by the independent reviewer: it is not rejected anywhere** (Seahub, `web-accesstoken-mgr.c`, Go and C `update-api`). Runtime exercise still pending; Pro binary unverifiable but shares this code | isolated test; owner decides on disclosure |
| U3 | WOPI slot is single: if the owner later wants Collabora, either the bridge serves an **aggregated** discovery XML (Seahub reads all `<action>` elements regardless of `<app>`, FACT) or, on Pro/13, `ENABLE_MULTIPLE_OFFICE_SUITE` selects the suite per library | slice step |
| U8 | Owner's willingness to upgrade 12.0.14 Pro → 13.x (precondition for C's non-office value) | owner |
| U4 | `OFFICE_SERVER_TYPE` other than `CollaboraOffice`: behaviour verified for the empty default only | slice step |
| U5 | ArtCraft upstream bridge stability (unversioned, lives in PR text) | pin releases; write a protocol contract test |
| U6 | Whether the official Seafile 12/13 Docker images enable the Go fileserver by default | irrelevant to C; relevant only to A |
| U7 | Current state of ONLYOFFICE on the owner's instance | owner |

---

## 7. Next executable steps

Owner-only (production; this audit will not do them):

1. Diagnose/restore the ONLYOFFICE `api.js` 404 on the live instance (likely `ONLYOFFICE_APIJS_URL` or Nginx Proxy Manager routing after the 10-26 Seahub restart). Office editing for the user depends on this, not on ArtCraft.
2. Decide whether to roll back the GR-015 Seahub/`seaf-server` patches on LXC 108 using the recorded rollback archive. Recommendation: **roll back** — the architecture that needed them is abandoned, and a patched proprietary binary is unsupportable.

Lab (safe, isolated, no production, no upstream):

3. **Done** (`lab/real-seafile/`, run in a dedicated Lima VM with Docker on the audit machine): stock Seafile CE **13.0.28** + ONLYOFFICE Docs **9.4.0** + the bridge, the five WOPI keys pointing at the bridge's discovery XML. `run_slice.py` passes **45/45** (`results/slice.json`). Measured on the real Seahub, not assumed:
   - `.docx/.xlsx/.pdf/.dxf/.svg` route to the bridge; `.pptx` stays on ONLYOFFICE on the same instance (`OFFICE_WEB_APP_*` is checked before `ONLYOFFICE_*` per extension in `view_lib_file`). `.pdf` reaches the office branch only with `?edit_pdf=true` (U3/U4 resolved for 13.0).
   - Seahub's WOPI `PutFile` **accepts a read-only token** and attributes the commit to that user — the gap the fake host reproduces is real (U2 resolved at runtime). The bridge refuses the same save with 403.
   - Save → new Seafile version attributed to the editing user; stale/external-writer saves → 409 and no overwrite; identical bytes → no new commit; WOPI lock/unlock/conflict through Seahub; revoked/expired token → 401.
   - Seahub 12/13 render the WOPI page as React JS literals (`actionURL`, `accessToken`) posting into `<iframe name="office_frame">`, not a server-side `<form>`; the bridge is unaffected (it only sees the POST).
   - ONLYOFFICE Docs CE 9.4 refuses to fetch from private/compose IPs unless `ALLOW_PRIVATE_IP_ADDRESS=true`; with it, JWT command + docx→pdf conversion round-trip through Seahub pass. Relevant to the owner's `api.js` 404 investigation only as a reminder that Docs has its own network policy.
4. **Done**: the four upstream web bundles that already ship the parent-host protocol — WordCraft v0.13.2, GridCraft v0.14.2, PdfCraft v0.16.1, CADCraft v0.15.1, fetched by SHA-256 (`static/*-PROVENANCE.txt`), **unpatched** — open from a real Seahub page in headless Chromium through the bridge host page, load the document from Seafile, and Ctrl+S produces a new Seafile version attributed to the user (`run_browser.py`, **17/17**, screenshots in `results/`). VectorCraft v0.19.0 and PhotoCraft v0.18.0 bundles carry no host protocol (grep of the wasm: no `<app>:ready`), confirming §3.1: they need an upstream change before they can be hosted, and that change is locked. One bridge bug was found only by the real browser and fixed: editor pages must send `frame-ancestors 'self' <seahub>` (the whole ancestor chain is checked), not `'self'` alone. Still to do: ONLYOFFICE on the same DOCX for a fidelity comparison; a non-headless pass on HTTPS (WebGPU, clipboard) by a human.
5. Re-target GR-049/052 tests at the relay; add a protocol contract test for the upstream bridge messages.
6. Rewrite `README.md`, `ROADMAP.md`, `AGENTS.md` to the new product form; archive the GR corpus under `docs/history/`.
7. Prepare (do not publish) the ArtCraft `saveResult` RFC and a note on Seahub WOPI PutFile findings.

```text
REFOUNDATION_STATE=DECISION_REACHED
CURRENT_REALITY=gateway+patches architecture, 0/6 GPT PASS, live instance patched, ONLYOFFICE state unknown since 10-26
ASSUMPTIONS_INVALIDATED=no generic write channel (WOPI exists; any extension on Seahub>=13, office/PDF only on 12.0); ONLYOFFICE CE limited (limit removed 9.4); CAS required (Seafile's own editors don't); ArtCraft mature (3–5 weeks old, alpha); cheap reviews predictive (0%)
PRECONDITIONS=Seafile>=13 for non-office formats; bridge enforces UserCanWrite itself; WOPI_ACCESS_TOKEN_EXPIRATION set to 30 min
INDEPENDENT_REVIEW=R1 FAIL (keystone over-stated for 12.0; permission gap; dropped guarantees) -> all findings incorporated in this revision; R2 not yet run; real-Seafile slice supersedes several R1 ASSUMPTION labels with FACTs (§7 step 3)
ARCHITECTURE_OPTIONS_CONSIDERED=A current, B Seafile-native only, C generic WOPI editor bridge, D ArtCraft storage provider, E hook+Seahub PR, F upstream-only
CURRENT_LEADING_ARCHITECTURE=C (+B for office formats)
WHY=zero patches either side, public CE protocol, stateless, upgrade-resilient, keeps lab's real contributions, ArtCraft adopted only where it beats incumbents
COMPONENTS_TO_KEEP=Seafile API knowledge, host-page save discipline, reconciliation/retry logic+tests, fixtures, bounded zip tooling, saveResult RFC draft
COMPONENTS_TO_REMOVE=gateway sessions/capabilities/custom HTTP, Seahub+C patches (and live deployment), craft-platform fork, 13 app patches, VectorCraft polling, Nextcloud/ownCloud scope, GR review loop
MAJOR_UNCERTAINTIES=U1–U7 above, minus U2/U3/U4 (resolved on CE 13.0.28, §7)
NEXT_EXECUTABLE_STEP=owner decisions (ONLYOFFICE api.js 404, GR-015 rollback, Seafile 13 upgrade); lab: steps 5–7, R2 independent review of this revision
PRODUCTION_STATUS=UNTOUCHED
UPSTREAM_STATUS=LOCKED
```
