# Licensing

The rule for this repository: **this repository contains only original work and
permissively licensed material. Anything derived from a copyleft or proprietary
upstream must be clearly separated, attributed, and carry its own licence.**

This document is a live record, not a legal opinion. Where a conclusion needs the
owner's decision, it is marked `OWNER DECISION REQUIRED`.

## 1. Components and their licences

| Component | Licence | Evidence | Consequence for us |
| --- | --- | --- | --- |
| Seafile Server — **Professional** edition (the deployed instance) | proprietary (Seafile Ltd.) | the deployed tree ships `pro-data/` and Pro-only modules (`IsProVersion` permission class, `repo_office_suite` endpoint) | **We must not copy its code.** Reading it and documenting its interfaces is fine. |
| Seafile / Seahub — inspected upstream revisions | **Apache-2.0** (Seahub `c01d46bc`) / **AGPLv3 with OpenSSL exception** (Seafile Server `a652460e`) | [Seahub LICENSE](https://raw.githubusercontent.com/haiwen/seahub/c01d46bcaa0b2ce24c71561c6c61d15fea808d1a/LICENSE.txt), [Seafile Server LICENSE](https://raw.githubusercontent.com/haiwen/seafile-server/a652460e9d4314d5e67c82e0ebe9aa48e8ea1212/LICENSE.txt) | Do not copy code; re-verify the exact target revision before deriving or contributing. |
| GR-015 Seafile Server 12.0.14 patch context | **AGPLv3 with OpenSSL exception** at source SHA `32ed9c69594c9faa5cea28024403fcde362589ec` | [`seafile-server-12.0.14.patch`](reviews/GR-015/seafile-server-12.0.14.patch); [source LICENSE](https://raw.githubusercontent.com/haiwen/seafile-server/32ed9c69594c9faa5cea28024403fcde362589ec/LICENSE) | The diff contains upstream context lines. Preserve provenance and applicable notices; compatibility/distribution treatment is **NOT LEGALLY REVIEWED**. |
| GR-015 Seahub 12.0.14 patch context | **Apache-2.0** at source SHA `1e9bde801b4360c14d784d9681d4261abc233a8b` | [`seahub-12.0.14.patch`](reviews/GR-015/seahub-12.0.14.patch); [source LICENSE](https://raw.githubusercontent.com/haiwen/seahub/1e9bde801b4360c14d784d9681d4261abc233a8b/LICENSE.txt) | The diff contains upstream context lines. Preserve provenance and applicable notices; compatibility/distribution treatment is **NOT LEGALLY REVIEWED**. |
| ONLYOFFICE Document Server | proprietary (Ascensio System SIA) | `local.json`, container labels, `api.js` copyright header ("Copyright (C) Ascensio System SIA, 2009-2026") | We study its **behaviour**, never its code. |
| ArtCraft apps (`storytold/*`) | to be confirmed per repo — **NOT VERIFIED yet** | each repo's licence file | must be checked before any ArtCraft code is vendored or derived from |
| `storytold/craft-libs` | **MIT OR Apache-2.0** | `LICENSE-MIT` + `LICENSE-APACHE` in the repository root | compatible |
| `storytold/craftrules` | not accessible from outside | HTTP 404 | no constraint we can observe |

**Verified on 2026-10-22: all 13 `storytold/*` applications AND `storytold/craft-libs`
ship both `LICENSE-MIT` and `LICENSE-APACHE`** — i.e. they are dual MIT / Apache-2.0,
which is exactly this repository's licence. The table's "to be confirmed" entries for
the applications are therefore **closed**; the only remaining licence question is
whether the *upstream maintainers* accept a contribution under those terms (L-3).

## 2. Upstream licensing and the network boundary

* The inspected Seafile Server revision is AGPLv3 with an OpenSSL exception;
  the inspected Seahub revision is Apache-2.0. The deployed Professional build
  and the exact revision intended for any contribution still require separate
  verification.
* This repository is dual-licensed MIT / Apache-2.0.

The gateway itself remains separate and talks to Seafile over HTTP. However,
the GR-015 patch artifacts do contain context copied from the exact Seahub and
Seafile Server revisions listed above. They are review/patch material, not
vendored runtime components, but they still require explicit upstream
provenance, notices and a legal compatibility check before redistribution or
submission. Do not describe this repository as containing no upstream source
context.

### Architectural consequence

The ArtCraft connector must reach Seafile **over its HTTP API** — a network
boundary, not a link. Consequences:

* The connector does not import Seahub modules.
* The connector does not vendor Seahub code.
* The connector speaks Seafile's documented HTTP API (Account API v2, Repo API
  v2.1, seafhttp upload/update) with a short-lived, narrowly scoped credential.

This is also simply better design: it keeps the Craft side free of Seafile
concepts (repository ids, tokens, internal URLs), which is a hard requirement of
the project.

### Status

> **PROVISIONAL — FREE REVIEW PENDING.** The licences are now **verified** for
> every `storytold/*` repository (see the table). What is *not* verified is the
> upstream contribution's acceptance (L-3).

## 3. What we will never do

* Copy ONLYOFFICE source, templates, or assets.
* Vendor Seahub (Professional or Community) source into this repository.
* Copy ArtCraft source into this repository without a licence determination and
  the upstream owner's agreement.
* Ship a file whose header claims a licence the content does not have.
* Use the ArtCraft logos or other trademarks as if they were ours — they are
  marks, not open-source assets (per the ArtCraft contribution rules).

## 4. Clean-room discipline for ArtCraft contributions

The ArtCraft repositories impose strict clean-room rules: no code, shader, icon,
ICC profile or asset copied from a commercial product; behaviour may only be
implemented from public specifications and documentation.

Any ArtCraft-facing patch we prepare (GR-014) must follow the same discipline,
and must be written against public specifications only.

## 5. Attribution obligations

If we ever quote Seafile or ONLYOFFICE code or identifiers in this repository
(documentation, minimal illustrative snippets), we must:

* name the source and the version,
* state the upstream licence,
* keep the quotation short enough to be a reference, not a substitute for the
  original.

The GR-015 patch files are additional source-context material. Their source
repositories, exact revisions and license files are listed in §1. The patches
must retain enough provenance for reviewers to identify the upstream context;
this document does not decide whether the proposed combined distribution is
legally compatible.

## 6. Decisions to confirm

| # | Question | Status |
| --- | --- | --- |
| L-1 | Exact licence of each of the 13 `storytold/*` repos | **CLOSED** — all dual MIT / Apache-2.0 (2026-10-22) |
| L-2 | Licence of `storytold/craft-libs` | **CLOSED** — dual MIT / Apache-2.0 |
| L-3 | Does the ArtCraft upstream accept a contribution under its own licence terms? | **NOT VERIFIED** — GR-013 |
| L-4 | Should this repository stay dual MIT/Apache? | **OWNER DECISION REQUIRED** (recommended: keep dual, and keep the network boundary) |
| L-5 | Does the selected Seafile upstream revision accept the patch shape we intend? | **NOT VERIFIED** — GR-002 / GR-014 |
