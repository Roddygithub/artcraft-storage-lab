# Craft-only WordCraft replay

Fresh rootless Podman lab at source `2fb30cd`, using stock Seafile CE 13,
the bridge and the previously verified WordCraft v0.13.2 asset snapshot.
ONLYOFFICE is absent from the Compose services and disabled in Seahub.
The HTTP count deliberately excludes six retired ONLYOFFICE checks; it is
not directly comparable to historical mixed-suite totals.

Results: **HTTP 40/40; Chromium 28/28; launcher exit 0**. Offline checks:
11 launcher tests and 32 bridge tests passed. Parent inspection after exit found
no running Podman containers. No ONLYOFFICE service was started.

Two typed edits produced two user-attributed versions. Between them the old
page was closed and a fresh authenticated Seafile file-list click opened the
first saved bytes. No final reopen after save two is claimed. The first relay
and Seafile readback are byte-identical; the bounded verifier also checks
referenced header/footer text, PAGE instructions, table-cell text, page breaks,
page geometry and paragraph style references across both saves. This is one
synthetic fixture, not complete document fidelity.

The parent inspected all three retained screenshots: original header/body,
first saved marker, and both markers on the second page with the table and
preceding page-number footer visible. Synthetic DOCX package contents and
retained bytes were scanned against this run's generated credentials before
retention; none matched. The PNGs show no private origins or account details.

Run `python3 lab/real-seafile/results/2026-11-08-craft-only-wordcraft/verify.py`
to verify hashes, browser assertions and the bounded document invariants.

The requested browser case is `wordcraft` with `fidelity-layout.docx`.
Raw URLs, tokens, accounts and version IDs are omitted from the retained JSON.
Source hashes and the static-manifest identity are recorded in `provenance.json`.
Assets were reused byte-for-byte from the prior structure-recovery run; their
original ingestion and limitations are documented in that retained evidence.
No new editor bundle was introduced.

The first launch was interrupted before testing to correct the requested
fixture name from `layout` to `fidelity-layout.docx`; it cleaned up its lab.
This evidence belongs to the second launch.

Reproduce with the verified static assets and their independently checked manifest:

```sh
python3 tests/lab/test_local.py
python3 tests/bridge/test_bridge.py
python3 lab/real-seafile/local.py --run-dir /absolute/new/private-run \
  --static /absolute/verified-static --manifest /absolute/verified-manifest.json \
  --editor wordcraft --wordcraft-fixture fidelity-layout.docx
```

This is internal HTTP and automated Chromium evidence. HTTPS desktop acceptance,
arbitrary DOCX fidelity, missing office-format coverage and independent project
review remain open. No production changes or upstream publication were made.
