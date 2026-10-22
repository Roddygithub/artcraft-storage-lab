# GPT Handoff

A single document that lets a future GPT session take over this project **without
trusting the summaries produced by the free models**.

It is filled in progressively. When it is complete, GPT should be able to verify
every claim from the repository itself.

## Repository

| Item | Value |
| --- | --- |
| Local path | `~/Projects/artcraft-storage-lab` |
| GitHub | `artcraft-storage-lab` (public) |
| Default branch | `main` |
| HEAD SHA | _(filled at freeze time)_ |

## Architecture

_(filled at freeze time — the concrete integration architecture, with a diagram)_

## GR list

| GR | Title | Artifact | Free review | GPT review |
| --- | --- | --- | --- | --- |
| GR-001 | Seafile online-editor contract | `docs/SEAFILE-ONLYOFFICE-RESEARCH.md` | | PENDING |
| GR-002 | Seafile integration point | `docs/SEAFILE-INTEGRATION-POINTS.md` | | PENDING |
| GR-003 | ArtCraft Web capability matrix | `docs/ARTCRAFT-WEB-CAPABILITIES.md` | | PENDING |
| GR-004 | Common Craft Web Host Contract | `docs/HOST-CONTRACT.md` | | PENDING |
| GR-005 | First technical proof | `integration/`, `prototypes/` | | PENDING |
| GR-006 | WordCraft Seafile MVP | `docs/reviews/GR-006/` | | PENDING |
| GR-007 | Save protocol | `docs/SAVE-PROTOCOL.md` | | PENDING |
| GR-008 | Data integrity and conflicts | `docs/CONFLICTS.md` | | PENDING |
| GR-009 | Web integration security | `docs/SECURITY.md` | | PENDING |
| GR-010 | GridCraft | `docs/reviews/GR-010/` | | PENDING |
| GR-011 | DeckCraft | `docs/reviews/GR-011/` | | PENDING |
| GR-012 | Non-office Craft integration | `docs/reviews/GR-012/` | | PENDING |
| GR-013 | ArtCraft upstream RFC | `docs/RFC-DRAFT.md` | | PENDING |
| GR-014 | First upstream patch | `docs/reviews/GR-014/` | | PENDING |

## Relevant upstream repositories and SHAs

_(filled at freeze time — every repo inspected, with the exact commit SHA and
the date of inspection)_

## Test environment

_(filled at freeze time — how to reproduce the test setup, which services are
needed, which synthetic fixtures are used)_

## Commands

_(filled at freeze time — the exact commands to run the test suite)_

## Integration flow

_(filled at freeze time)_

## Seafile configuration changes

_(filled at freeze time — every key added to `seahub_settings.py` / `local_settings.py`,
with the exact value shape and how to roll it back)_

## ArtCraft changes

_(filled at freeze time)_

## Security assumptions

_(filled at freeze time — the trust boundaries, token lifetimes, origin checks,
and anything still assumed-but-unverified)_

## Known limitations

_(filled at freeze time)_

## Prepared upstream patches

_(filled at freeze time — location of each prepared diff, and the explicit
statement that none of them has been published)_
