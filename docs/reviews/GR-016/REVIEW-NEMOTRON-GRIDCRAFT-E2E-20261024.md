# Bounded independent review — GR-016 Seafile E2E evidence

Date: 2026-10-24
Reviewer task: `artcraft-gr016-seafile-e2e-free-review-20261024-r1`
Reviewer model: `opencode/nemotron-3-ultra-free`
Scope: WordCraft and GridCraft synthetic Seafile runtime evidence; not the project GPT gate

## Initial verdict

**PROVISIONAL FAIL.** The reviewer accepted that both apps had real-browser
runtime flows against isolated synthetic Seafile, but identified three major
evidence gaps:

1. The exact editor-to-gateway save payload was not separately hashed and
   compared with Seafile readback.
2. GridCraft formula recalculation had not been exercised; the original test
   only checked formula XML and cached value preservation.
3. Both scratch release builds used `data-wasm-opt="0"`, so optimized bundle
   performance and production packaging were unverified.

It also listed non-blocking gaps: external-writer concurrency, ONLYOFFICE
regression, Seafile-backed file picker for GridCraft Open, visible handling of
some transport errors, and security/deployment tests.

## Owner follow-up

The formula finding was reproduced in a fresh isolated Seahub session after a
stale session correctly received HTTP 403 without committing a write:

- GridCraft Web/WASM changed B2 from 42 to 1337.
- The editor recalculated B3's `SUM(B2:B2)` result to 1337.
- Ctrl+S created Seafile head
  `fbdcec44f48ef805d89d142203a405b0108bcbc7` and a new file/history revision.
- Seafile API readback returned a valid 4,145-byte XLSX, SHA-256
  `ec33a69193d3acf2efea9d2e61f8722cd96ef275be55941d0046f49582d2ac72`.
- Readback contained B2=1337, the B3 formula, and cached result 1337. A fresh
  GridCraft route load displayed B2=1337 and B3=1337. See the detailed runtime
  report and [`runtime/gridcraft-seafile-reopen-20261024.png`](runtime/gridcraft-seafile-reopen-20261024.png).

The other two findings are not represented as fixed. The outbound message bytes
were not separately captured and hashed before the gateway, and the optional
`wasm-opt -Oz` pass remains unrun. The test reports disclose both limits. These
are not evidence for an optimized production deployment.

## Related checks reproduced by the owner

At lab repo base `38b2631e1a01ec5a843295fca318254d1a5f6a97` (documentation and
evidence were uncommitted during these checks):

| Command | Result |
|---|---|
| `python3 tests/test_gateway_unit.py` | Exit 0; all checks passed, including conditional save conflict, read-only/revoked access, concurrent writes, and response bounds |
| `python3 tests/test_xlsx_fixture.py` | Exit 0; fixture formula and style structure passed |
| `python3 tests/test_gr012_svg_assertions.py` | Exit 0; three negative/semantic assertions passed |
| `python3 tests/test_hostpage_protocol.py` | Not run: environment lacks Python `playwright` (`ModuleNotFoundError`) |

These local checks supplement, but do not replace, the described GridCraft
runtime save/reopen run. The synthetic Seafile container was stopped after the
run; its repo static bundle and XLSX allowlist were restored. Production was not
accessed.

## Disposition

The independent second round accepted this bounded evidence update with minor
qualifications. It closed the formula-recalculation finding and downgraded the
payload-hash and optimized-bundle gaps to minor because they limit byte provenance
and production-readiness claims, not the synthetic functional workflow. The
re-review is preserved in
[`REVIEW-NEMOTRON-GRIDCRAFT-E2E-R2-20261024.md`](REVIEW-NEMOTRON-GRIDCRAFT-E2E-R2-20261024.md).

This bounded acceptance does not establish all-app support and does not change
the project-level GPT-6.1 Sol FAIL on
`0edbe524b4fa321b0f73f8601afef390e7f785e6`. Public deployment readiness remains
NOT ESTABLISHED; upstream publication remains locked.
