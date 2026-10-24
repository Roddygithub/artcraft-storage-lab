# GR-016 — WordCraft shared transport against isolated Seafile

Date: 2026-10-24
Lab repository commit before evidence update: `38b2631e1a01ec5a843295fca318254d1a5f6a97`
Result: **REPRODUCED in an isolated synthetic stack; not a project GPT verdict**

## Scope and environment

This run checks the GR-016 WordCraft adapter using the shared Rust browser
transport through the existing Seafile gateway. It does not test public
deployment, production Seafile, or other ArtCraft applications.

| Component | Exact setup |
|---|---|
| WordCraft | `storytold/wordcraft` base `00bc6a4b028013b2dfb0e85e8b326aeed3ecff6d`, with the recorded GR-014 and GR-016 patches in `/tmp/artcraft-gr016-wordcraft` |
| Shared Rust transport | `storytold/craft-libs` `f180fc0d35d521c5d18e118c881d3efde1ec1eee`, local path dependency in the scratch checkout |
| Seafile server | `haiwen/seafile-server` `32ed9c69594c9faa5cea28024403fcde362589ec`, with the recorded GR-015 patch, built and run in isolated rootless Podman |
| Seahub | `haiwen/seahub` `1e9bde801b4360c14d784d9681d4261abc233a8b`, with the recorded GR-015 patch |
| Synthetic library | `ArtCraft Synthetic`, repo `a1a2768f-a6ea-4e18-858f-b09e3f64a11d`; synthetic fixtures only |
| Origins | Seahub `http://127.0.0.1:18000`; gateway and Craft `http://127.0.0.1:8777`; loopback only |
| Browser | Collaborative Chromium; actual Seahub routes, WordCraft Web/WASM and synthetic account |

No credentials, access tokens, production documents, production services or
upstream repositories are included in this evidence. The synthetic Seahub
allowlist was temporarily set to `docx` and `xlsx`; its action URL pointed to
the local gateway. ONLYOFFICE settings and the production Seafile instance
were not changed.

## Build

The WordCraft scratch checkout was built with `trunk build --release`. The
optional `wasm-opt -Oz` optimization was stopped after several minutes on the
59 MB intermediate. For this functional run only, the scratch `index.html`
used `data-wasm-opt="0"`; the Rust release profile and source patches were
unchanged. The built JS and WASM assets returned HTTP 200 in Chromium. This is
functional release-profile evidence, not an optimized production bundle.

## Reproduction

1. Opened `synthetic.docx` from its actual row in the Seahub library list. The
   patched Seahub route posted its scoped capability to gateway `/open/`; the
   browser loaded the WordCraft host frame and the gateway delivered the DOCX.
2. Edited the document in WordCraft. The app reported `Unsaved changes`; Ctrl+S
   returned `Saved — new version` with head `25e7d1684b57ac03ccfe896fe4417dce7635e759`.
3. Seafile API history and download readback showed a new file ID, history
   growth, valid DOCX, and `gr016hostsave` in `word/document.xml`.
4. Added the separate synthetic XLSX fixture to the library for the GridCraft
   run, changing the library head while a second WordCraft session was open. That
   stale session's save returned HTTP 409 and did not overwrite the DOCX.
5. Reopened the DOCX from the Seahub list, edited it again, and saved. The
   editor reported `Saved — new version` with head
   `f7c006db6b699f8aae3f9a76e785d0bbead01da4`. A fresh route load opened the saved
   document in WordCraft and rendered both `gr016hostsave` and `seafilelistclick`.

Screenshots: the Seahub synthetic library list is in
[`runtime/seafile-synthetic-library-20261024.png`](runtime/seafile-synthetic-library-20261024.png);
the fresh WordCraft reopen is in
[`runtime/wordcraft-seafile-reopen-20261024.png`](runtime/wordcraft-seafile-reopen-20261024.png).

## Seafile data evidence

The successful second save was based on the library head after the XLSX fixture
was added. The before/after file data and latest history entry were read from
Seafile after the save.

| | Before second save | After WordCraft host save |
|---|---:|---:|
| Repository head | `767905ced33b21afaf45a232fa7955bdce086657` | `f7c006db6b699f8aae3f9a76e785d0bbead01da4` |
| File ID | `03e65c7ba73e5f1d6433a1a23c2ca02ef496a01e` | `4013284e8809fc29b350714340e05ba4dd24ee0d` |
| Length | 5,286 bytes | 5,305 bytes |
| SHA-256 from API download | `535364836796548fff67b728806df7f423735e99db6de8712b37ecbd37fd3fc5` | `b36c1f1d1a43e5bdd083c91ebff599c1f1d4437a4b8d856d85e896d1a7f59212` |
| DOCX history entries | 2 | 3 |
| Semantic check | contains `gr016hostsave` | valid DOCX; both edits present in XML and in fresh WordCraft render |

The post-save bytes were downloaded from Seafile. The exact bytes in the
`wordcraft:save` browser message were not separately hashed, so this report
does not claim byte-for-byte identity across that boundary. The visible editor
save acknowledgement followed the host's durable Seafile result.

## Commands and outcomes

| Command/action | Result |
|---|---|
| `trunk build --release` in the pinned WordCraft scratch app, with scratch `data-wasm-opt="0"` | Exit 0; release-profile bundle loaded |
| Seahub DOCX route and gateway `/open/` capability handoff | HTTP 200; WordCraft assets/document loaded |
| WordCraft Ctrl+S, first edit | New Seafile history entry; editor showed saved state |
| Stale WordCraft session save after fixture changed library head | HTTP 409; stale write rejected |
| WordCraft Ctrl+S after reopening current head | HTTP 200; new Seafile head/file ID; editor showed `Saved — new version` |
| Seafile API detail/history/content readback | HTTP 200; history 2→3; valid DOCX with both markers |
| Fresh editor reopen | WordCraft rendered both persisted edits |

## Independent bounded review

The independent GR-016 evidence review returned **ACCEPT with MINOR
qualifications**, not a project verdict. Its supplied summary contained
metadata values that do not match this runtime record; those values were
discarded and the file IDs, revisions, sizes and hashes above were queried
again from the isolated Seafile instance. The review's useful qualifications
are retained: the exact editor-to-gateway save payload was not independently
hashed, and the functional bundle used `data-wasm-opt="0"`.

## Limits

- This verifies the WordCraft shared transport through the synthetic Seafile
  stack only. It does not establish production readiness or deployment
  security.
- The run used a loopback test stack. TLS/proxy/CSP/CSRF controls, permission
  revocation, response loss, public deployment, and concurrent external writers
  remain unverified.
- ONLYOFFICE was left untouched; no regression test of its separate Seafile
  integration was run here.
- Other ArtCraft applications remain separate work. Overall GPT status remains
  **FAIL on `0edbe524b4fa321b0f73f8601afef390e7f785e6`**. This report does not
  freeze a new candidate or authorize upstream publication.
