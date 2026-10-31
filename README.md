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
45/45, browser slice 21/21 (`lab/real-seafile/results/`). Not yet deployed anywhere real. Nothing
published upstream.

## What works today

| File | Editor | How |
| --- | --- | --- |
| `.docx` | WordCraft 0.13.2 | upstream bundle, its own `host.rs` |
| `.xlsx` | GridCraft 0.14.2 | upstream bundle, its own `host.rs` |
| `.pdf` (`?edit_pdf=true`) | PdfCraft 0.16.1 | upstream bundle, its own bridge |
| `.dxf` | CADCraft 0.15.1 | upstream bundle, its own `host.rs` |
| `.svg` | VectorCraft 0.19.0 | upstream bundle + a one-line page-API shim (`lab/real-seafile/static/host-shim.js`) |
| `.pptx`, the rest of Office | ONLYOFFICE | unchanged; Seahub picks per extension |

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
