# ArtCraft Storage Lab

> Open a file in Seafile Web, edit it in a Craft web editor, save, and get a normal Seafile
> version — with **no patch to Seafile, no patch to the editors, no SeaDrive, no download/upload,
> no desktop app**.

The lab's answer, after a first-principles re-foundation (`docs/REFOUNDATION-REPORT.md`,
2026-10-31): Seahub already speaks **WOPI** to external editors (that is how ONLYOFFICE and
Collabora plug in). The missing piece is a small, stateless **WOPI editor bridge** that turns a
Seahub WOPI session into the `?host=parent` message protocol the Craft web apps already ship.

```text
Seafile Web ──(WOPI form POST, access token)──▶ bridge (host page, same origin as the editor)
                                                  │  iframe: upstream Craft web bundle, unpatched
Seahub WOPI host ◀──(CheckFileInfo/GetFile/PutFile/Lock, token in headers)── bridge /relay/*
```

Status: **prototype, validated on a stock Seafile CE 13.0.28** in an isolated VM — HTTP slice
48/48, browser slice 50/50 (`lab/real-seafile/results/`); independent review R2 of the bridge
incorporated (30 fake-host tests). Not yet deployed anywhere real. Nothing
published upstream.

ROADMAP step 3 has current-bridge Seafile evidence for WordCraft DOCX and GridCraft
XLSX, the five-route GR-078 replay (WordCraft, GridCraft, PdfCraft, VectorCraft and
PhotoCraft), native DeckCraft `.deckcraft`, and CADCraft DXF. The DeckCraft and
CADCraft runs are direct parent work, not Aptarchy completion. See
[`GR-078`](docs/GR-078-COMBINED-SEAFILE-ROUTE-REPLAY.md),
[`GR-081`](docs/GR-081-DECKCRAFT-REAL-SEAFILE-ROUNDTRIP.md), and
[`GR-082`](docs/GR-082-CADCRAFT-REAL-SEAFILE-ROUNDTRIP.md). Remaining dispatched
scenarios, foreign `.pptx` editing, broad CADCraft fidelity and production
behavior still require separate validation.

The bounded synthetic WordCraft/ONLYOFFICE DOCX comparison is recorded in
[`GR-083`](docs/GR-083-WORDCRAFT-ONLYOFFICE-DOCX-COMPARISON.md). After R1's
OOXML-order finding was fixed and passed source review R2, a fresh run opened
three corrected fixtures in each editor with unchanged readback hashes and no
downloads. It did not edit or save. Independent review of the fresh evidence R3
is pending. The initial pre-remediation artifacts remain archived; earlier
ONLYOFFICE manifest 502s did not recur, but their cause is unverified. This
comparison does not replace the owner’s live ONLYOFFICE repair.

## What works today

| File | Editor | How |
| --- | --- | --- |
| `.docx` | WordCraft 0.13.2 | upstream bundle, its own `host.rs` |
| `.xlsx` | GridCraft 0.14.2 | upstream bundle, its own `host.rs` |
| `.pdf` (`?edit_pdf=true`) | PdfCraft 0.16.1 | upstream bundle, its own bridge |
| `.dxf` | CADCraft 0.15.1 | upstream bundle, its own `host.rs` |
| `.svg` | VectorCraft 0.19.0 | upstream bundle + a one-line page-API shim (`lab/real-seafile/static/host-shim.js`) |
| `.figcraft` | FigCraft 0.13.1 | upstream bundle + the same shim (`?control` enables its page API) |
| `.pptx` / `.deckcraft` | DeckCraft 0.13.1 | upstream source + the lab's `host.rs` port (`docs/upstream-drafts/`), built in the lab |
| `.png` / `.psd` / `.pcraft` | PhotoCraft 0.18.0 | same, with a dirty signal |
| `.designcraft` | DesignCraft 0.15.2 | same |
| `.scraft` / `.scraftz` | SoundCraft 0.15.0 | same |
| ODF and the rest of Office | ONLYOFFICE | unchanged; Seahub picks per extension |

A foreign format opened in a Craft app (a `.pptx` in DeckCraft, a `.png` in PhotoCraft) is saved by
the app in its own format; the host page hands that over as a download and leaves the Seafile
file untouched. In-place saves are verified by reading the file back from Seafile.

Per-app coverage of all 13 Craft apps: report §7, step 4. Ports for the others:
`docs/upstream-drafts/host-bridge-ports.md`.

## What the bridge enforces that Seahub does not

`UserCanWrite` on save (Seahub's `PutFile` accepts a read-only token — measured), an optimistic
version precondition (409 on a concurrent change, nothing overwritten), file name and content
signature, reconciliation after a lost response, WOPI locks. Details: `bridge/README.md`.

## Repository layout

```text
bridge/               the WOPI editor bridge (stdlib Python WSGI + host page JS); 21 unit tests in tests/bridge/
deploy/bridge/        Dockerfile, compose, Seahub settings, nginx snippet, bundle fetcher — run it next to your Seafile
lab/real-seafile/     the validation lab: Seafile CE 13 + ONLYOFFICE + bridge + editor bundles in a Lima VM, HTTP and browser slices
docs/REFOUNDATION-REPORT.md   the decision and its evidence
docs/upstream-drafts/ what we would propose to Seahub and storytold — prepared, NOT published
docs/                 earlier research (host contract, capabilities audit, Seafile integration points) and the GR review corpus
integration/          LEGACY: the previous gateway + Seahub/fileserver patch architecture, superseded by the report; kept for evidence
scripts/              bundle download/extraction helpers
```

## Try it

```bash
python3 tests/bridge/test_bridge.py        # bridge against a fake Seahub WOPI host, no Seafile needed
```

```bash
lab/real-seafile/up.sh up && lab/real-seafile/up.sh configure && lab/real-seafile/up.sh slice   # needs Lima (macOS) with Docker
```

Deploy next to a real Seafile: `deploy/bridge/README.md`.

## Rules that still apply

* Production Seafile is never touched without the owner's explicit authorization.
* Upstream is locked: no issue, RFC, PR or discussion before the project-level review gate passes
  **and** the owner approves. Drafts live in `docs/upstream-drafts/`.
* No secrets in Git.

## What this project is not

Not an official ArtCraft or Seafile project. Not a SeaDrive or WebDAV client. Not a replacement
for ONLYOFFICE. Not a re-implementation of Seafile.

## License

Dual licensed: [MIT](LICENSE-MIT) or [Apache-2.0](LICENSE-APACHE), at your option. The Craft
web bundles fetched into the lab keep their own licenses (MIT OR Apache-2.0) and are not
versioned here.
