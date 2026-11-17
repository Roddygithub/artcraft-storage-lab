# ArtCraft Storage Lab

# ArtCraft Storage Lab

> **2026-11-17:** project **REMEDIATION COMPLETE**, stabilised on `main` at `f7b9358`.
> The validated candidate is the stateless WOPI bridge at `123d2a0` (bridge
> code unchanged since; later commits are evidence, documentation, and remediation only).
> Current proof: Seafile CE 12.0.14 isolated 66/66 browser replay with
> byte-level relay==readback artifacts for DOCX, XLSX and PPTX, version
> history and fresh-context details retained
> ([validation state](docs/VALIDATION-STATE.md)); CE 13.0.28 DOCX/replay
> evidence plus four read-only rendered formats (ODT, ODS, CSV, PPSX).
> A host write boundary is documented: Seahub PutFile ignores the WOPI
> token's `can_edit`, so read-only view routes are not safe for untrusted
> viewers zero-patch ([security analysis](docs/security/HOST_PERMISSION_BOUNDARY.md)).
> DOC, XLS, FODS, FODT, FODP, PPT, ODP and PPS remain unrouted. Production is
> untouched and upstream remains LOCKED. Hardware acceptance (17/22 PASS),
> session expiry TTL limitation documented, and restore test completed.
> GPT_FINAL_GATE=PENDING, UPSTREAM_STATUS=LOCKED. See
> [the closure ledger](docs/PROJECT-CLOSURE.md) and
> [the validation checkpoint](docs/VALIDATION-STATE.md).


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

Status: **validated lab candidate at bridge SHA `123d2a0`** (bridge code
unchanged since `123d2a0`; commits on top are evidence and documentation
only). Current bridge evidence covers
WordCraft DOCX, GridCraft XLSX, PdfCraft AcroForm and CADCraft DXF. VectorCraft
and FigCraft semantic edit/reopen slices passed the combined six-editor replay.
An opt-in official DeckCraft v0.16.0 candidate also passed a real PPTX title
edit/save/new-version/fresh-reopen slice; broad presentation fidelity is unverified. The exact closure criteria and remaining checks are in
[`PROJECT-CLOSURE.md`](docs/PROJECT-CLOSURE.md); the current validation
checkpoint is [`VALIDATION-STATE.md`](docs/VALIDATION-STATE.md). The earlier
`864fc77` freeze is a historical ledger entry, superseded by the 2026-11-15/16
replay chain.

## Zero-patch candidate

| File | Editor | Adapter |
| --- | --- | --- |
| `.docx` | WordCraft 0.13.2 | unmodified upstream bundle, merged parent bridge |
| `.xlsx` | GridCraft 0.14.2 | unmodified upstream bundle, merged parent bridge |
| `.pdf` (`?edit_pdf=true`) | PdfCraft 0.16.1 | unmodified upstream bundle |
| `.dxf` | CADCraft 0.15.1 | unmodified upstream bundle |
| `.svg` | VectorCraft 0.19.0 | upstream bundle plus declared lab page-API shim |
| `.figcraft` | FigCraft 0.13.1 | upstream bundle plus declared lab page-API shim |
| `.pptx` (lab `--pptx`) | DeckCraft 0.16.0 | unmodified upstream bundle; focused same-format edit/save/reopen verified |
| ODF / legacy office (lab `--viewing`) | ODT → WordCraft, ODS/CSV → GridCraft, PPSX → DeckCraft | these four routes have exact-payload and synthetic-render evidence; DOC/XLS standalone bundle import works but Seafile-host behavior is not verified and they remain unrouted; FODS shows raw XML; 8 formats unrouted |

The deployment example routes DXF by default; office extensions are operator
opt-ins. The synthetic lab routes DOCX/XLSX/PDF to Craft for testing and leaves
unverified office formats without an editor route. No production deployment is claimed.

DeckCraft, SoundCraft, PhotoCraft and DesignCraft Rust host ports are
experimental drafts outside this candidate's no-editor-patch requirement.
Their retained runs and configurations remain available for research.
GR-078 describes the retired `integration/` architecture and is not current
bridge evidence. Media applications and the draw.io stub are not supported by
this candidate. Broad document fidelity remains unverified.

## Save and host limitations

The bridge checks the user's permission, file name, content signature and
expected version, then verifies persisted bytes by readback. A version already
changed before the write is rejected. Seahub's unconditional PutFile does not
provide an atomic conditional write: an intervening external writer can still
be overwritten. The owner explicitly accepted this documented host limitation
for the zero-patch MVP; see the closure ledger and `bridge/README.md`.

Seahub also accepts direct writes using an extracted read-only WOPI token.
The bridge enforces read-only permission on its own path, not on that separate
host endpoint. Editor bundles share the host origin and are trusted code.
Upstream publication remains locked pending the project gate and owner approval.

## Repository layout

```text
bridge/               the WOPI editor bridge (stdlib Python WSGI + host page JS); 33 fake-host tests in tests/bridge/
deploy/bridge/        Dockerfile, compose, Seahub settings, nginx snippet, bundle fetcher — run it next to your Seafile
lab/real-seafile/     the validation lab: Seafile CE 13 + bridge + editor bundles in a Lima VM, HTTP and browser slices
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

Not an official ArtCraft or Seafile project. Not a SeaDrive or WebDAV client. Full office replacement remains unverified. Not a re-implementation of Seafile.

## License

Dual licensed: [MIT](LICENSE-MIT) or [Apache-2.0](LICENSE-APACHE), at your option. The Craft
web bundles fetched into the lab keep their own licenses (MIT OR Apache-2.0) and are not
versioned here.
