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
| Seafile / Seahub — open-source upstream (`haiwen/seahub`, `haiwen/seafile`) | **GPLv2** (Seahub) / LGPL-ish mix for the C server components | upstream repository licence files | Any code we take from it must be GPLv2. |
| ONLYOFFICE Document Server | proprietary (Ascensio System SIA) | `local.json`, container labels, `api.js` copyright header ("Copyright (C) Ascensio System SIA, 2009-2026") | We study its **behaviour**, never its code. |
| ArtCraft apps (`storytold/*`) | to be confirmed per repo — **NOT VERIFIED yet** | each repo's licence file | must be checked before any ArtCraft code is vendored or derived from |
| `storytold/craft-libs` | to be confirmed — **NOT VERIFIED yet** | ditto | same |
| `storytold/craftrules` | not accessible from outside | HTTP 404 | no constraint we can observe |

## 2. The GPLv2 / Apache-2.0 incompatibility — the decisive constraint

* Apache-2.0 is compatible with **GPLv3**, and **not** with GPLv2.
* MIT is compatible with GPLv2.
* This repository is dual-licensed MIT / Apache-2.0.

Therefore, **any ArtCraft or Seafile code that is GPLv2 must not be linked into
or vendored into this repository** if we want to keep the Apache-2.0 option.

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

> **PROVISIONAL — FREE REVIEW PENDING.** The exact licence of every
> `storytold/*` repository is **NOT VERIFIED** in this document yet. GR-003 and
> the GR-014 patch phase must fill the table above with the real licence file
> contents before any ArtCraft code is vendored, derived from, or contributed to.

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

Currently the only such material is in
`docs/reviews/GR-001/DEPLOYED-INSTANCE-CONTRACT.md` and
`docs/DEPLOYMENT.md`: it documents **interfaces, parameter names and behaviour**,
not code. Where a short snippet is quoted for clarity, it is attributed and is
from GPLv2/proprietary upstream — it is documentation, not a derived work of the
kind that would infect this repository.

## 6. Decisions to confirm

| # | Question | Status |
| --- | --- | --- |
| L-1 | Exact licence of each of the 13 `storytold/*` repos | **NOT VERIFIED** — GR-003 |
| L-2 | Licence of `storytold/craft-libs` | **NOT VERIFIED** — GR-003 |
| L-3 | Does the ArtCraft upstream accept a contribution under its own licence terms? | **NOT VERIFIED** — GR-013 |
| L-4 | Should this repository stay dual MIT/Apache, or move to MIT only to keep GPLv2 compatibility? | **OWNER DECISION REQUIRED** (recommended: keep dual, and keep the network boundary) |
| L-5 | Does the Seafile upstream (GPLv2) accept the patch shape we intend? | **NOT VERIFIED** — GR-002 / GR-014 |
