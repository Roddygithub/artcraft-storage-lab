# GR-085 retained evidence

HTTP **48/48**, followed by focused WordCraft Chromium **28/28**, on a fresh
synthetic Seafile CE 13.0.28 rootless lab, 2026-11-08. Runtime code is exact
candidate `8a6f07bbe1ddecfd44852ea8adc85777901e1788`.

| Artifact | Meaning |
| --- | --- |
| `http-results.json`, `browser-results.json` | Check names/status only, with hashes of private raw records |
| `candidate-provenance.json` | Ten matching source/config hashes, 26 served official asset hashes, fixture and screenshot hashes, private runner/compose hashes, failed-attempt boundary |
| Five `wordcraft-*.png` files | Initial rendered content, typed edit, first save, fresh open, second save |
| `SOURCE-REVIEW-R1.md` | Independent bounded GPT source review |
| `SHA256SUMS` | Exact inventory of retained bundle artifacts |

No raw WOPI URLs, capabilities, account/library identifiers or logs are retained
here. The five original PNGs passed CRC/framing checks and contain no text/EXIF
metadata; the parent visually inspected them. All test project containers and
its network were removed; its ports were free and user Podman socket/service
were inactive after cleanup. Those lifecycle facts are parent-observed.

To reproduce the browser scenario in a disposable lab, import the pinned
WordCraft ZIP through `scripts/craft_web_zip.py` and compare every served asset
with `candidate-provenance.json` before starting. Set the two environment entries
in the browser service:

```text
BROWSER_ONLY_EDITOR=wordcraft
BROWSER_WORDCRAFT_FIXTURE=fidelity-layout.docx
```

Run the configured lab's HTTP `slice`, then `browser`, with fresh synthetic
storage. The repository's Lima entry points are `lab/real-seafile/up.sh slice`
and `lab/real-seafile/up.sh browser`; this run used equivalent private Compose
services on rootless Podman. Private runner/compose contents and secrets are
not distributed in this bundle. Runtime prerequisites are documented in
`lab/real-seafile/README.md`.

Offline check: `python3 tests/test_wordcraft_browser_fixture.py`.
This is main-text retention, not complete DOCX fidelity. The report lists the
remaining limits. Project GPT **INCOMPLETE**; upstream **LOCKED**; direct parent
work, not Aptarchy completion.
