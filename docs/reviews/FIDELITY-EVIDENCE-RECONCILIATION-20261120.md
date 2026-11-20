# Fidelity evidence reconciliation — 2026-11-20

## Scope and verdict

Read-only reconciliation of `lab/real-seafile/results/2026-11-18-clipboard-and-fidelity/fidelity/` against the retained files, the repository history, and the current semantic comparators. Historical evidence was not edited. This is not a new Seafile/browser replay.

**The archived `37/37` is a historical assertion summary, not a reproducible three-format fidelity pass.** Its exact producer scripts and source fixture bytes cannot be established from the packet. Reopen fidelity is `NOT_VERIFIED` for all three formats because the second Seafile readback binaries are absent. The current probe now gates reopen success on the fresh browser editor's own relay response and OCR of the edited marker; unavailable OCR remains `NOT_VERIFIED` and fails the check.

## Historical packet findings

| Claim | Retained evidence | Reconciliation |
| --- | --- | --- |
| `37/37 PASS` | `fidelity.json` contains 37 `ok: true` rows: 17 DOCX, 12 XLSX, 8 PPTX. It is a summary; there are no corresponding raw run logs or script hashes. The packet names source commit `23de889181bd1b002019da89f824877d123d81b3`, but that tree has no `fidelity_probe.py` or `fidelity_compare.py`. | Exact producer and executed bytes: **NOT_VERIFIED**. The `37/37` must not be used as an independently reproducible pass. |
| DOCX accents: saved `PRESERVED`, reopened `ALTERED` | The two historical JSON reports have identical `after.accents_found` (`Åéïñöü`) and identical `text_len` (326), despite different accent verdicts. The saved DOCX is retained (SHA-256 `39c9b461ab6e50b4220e6af7f0a2a07c29ea7680a8b4b0c682cb0b337fbd7d7a`); the reopened DOCX is not. Current comparator on saved bytes with the recorded marker `fiddocx031a50`: 18 feature verdicts preserved, zero regressions. | The old verdict divergence is inconsistent with its own extracted fields and cannot be reproduced without the reopened bytes or exact producer. Reopen fidelity: **NOT_VERIFIED**. |
| PPTX texts: saved `PRESERVED`, reopened `ALTERED` | Historical saved/reopen reports contain identical per-slide text arrays, including the typed marker. The reopened screenshot visibly shows `fidpptx7f3e45`. Saved PPTX SHA-256: `dea09c540c966a19553dd10331fd179a3426f6d0415b2a28ca7927c782586aa5`. Current comparator on saved bytes with that marker: all 10 semantic verdicts preserved, zero regressions. No reopened PPTX bytes are retained. | Historical text verdict is inconsistent with the retained arrays; exact cause cannot be established. Screenshot supports visible marker only, not full reopened-document fidelity. Reopen fidelity: **NOT_VERIFIED**. |
| XLSX formulas and values preserved | The report says formula checks passed, but archived saved bytes contain `Data!C2` formula `Sheet2!B1` with cached value `#REF!`. The actual workbook sheets are named `Data` and `Source`; its intended source value is `Source!B2` (`42`). Saved XLSX SHA-256: `c2929ddd4acfef66007c52b145b44212f590d681a899a4fc3d7f01564b35c34f`. | The archived result does not demonstrate formula/value fidelity; those claims are **NOT_VERIFIED**. The generated fixture has been corrected for future campaigns to use `Source!B2`. The old binary/report remain unchanged. |

All files in the historical packet's `SHA256SUMS` were checked before this reconciliation. The manifest establishes the integrity of retained artifacts, not which unrecorded scripts produced them.

## Probe change and proof boundary

`fidelity_probe.py` now records its own source commit and SHA-256 for the probe, comparator, and corpus scripts in each new report. For each format it separately records:

- fixture and first Seafile readback hashes;
- first WOPI save payload hash and byte equality with the Seafile readback;
- Seafile history change after the save;
- fresh-login and editor-ready checks;
- the body and SHA-256 actually returned to the reopened editor by `/relay/file`, compared byte-for-byte with the first readback;
- whether the edited marker is visible in the reopened editor screenshot (Tesseract OCR);
- a structural comparison of the editor-relayed bytes;
- a later Seafile API readback hash, labeled as storage integrity only.

New runs also retain the original fixture, first save payload, first readback,
fresh-editor relay bytes, and post-reopen API readback as separate files beside
the screenshots and JSON record.

An API download cannot satisfy the editor-reopen gate. Missing login, render/OCR, relay bytes, or a changed Seafile version prevents a positive end-to-end result. No positive runtime result is claimed by this source change alone.

## Runtime replay availability

No new Proxmox/lab replay was run. This checkout has no `limactl`, no ArtCraft editor bundles under `lab/real-seafile/static/`, and no active isolated CE12 stack. Read-only `podman --remote=false ps -a` showed only stopped containers, including a local CE13 development stack; it is not the pinned CE12 target. Production LXC 108 was not accessed. A fresh tri-format browser campaign remains **NOT_VERIFIED** until the isolated CE12 lab and pinned editor bundles are available.

## Reproduction of current offline checks

```sh
python3 tests/test_fidelity_probe_save_gate.py
python3 tests/test_fidelity_probe_reopen.py
python3 tests/test_xlsx_fixture.py
python3 tests/test_xlsx_fidelity_mutations.py
python3 tests/test_xlsx_fidelity_json.py
python3 tests/test_docx_fidelity_mutations.py
python3 tests/test_pptx_fidelity_mutations.py
```

The full candidate validator completed **28/28 command groups** after the final
probe change using:

```sh
uv run --with playwright --with pillow python3 scripts/validate-candidate.py \
  --output /home/roddy/.cache/artcraft-fidelity-validation-20261120-final
```

Its private `summary.json` and logs remain outside the repository. The
historical packet manifest verified all **23/23** retained files. These offline
checks do not validate browser rendering or a new real Seafile save; that
replay is still NOT_VERIFIED.
