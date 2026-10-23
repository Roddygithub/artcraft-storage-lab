# Luna follow-up to Sol re-review

Date: 2026-10-23
Sol candidate: `d9ef476e6fbcb04c9a9e23cfe235812167d1f27c`

This note supplements, and does not alter, Sol's independent report. The following checks were read-only against the existing Proxmox LXC 108 over SSH:

| Check | Result |
| --- | --- |
| `pct status 108` | `status: running` |
| `systemctl is-active seahub` | `active` |
| `systemctl is-active seafile` | `active` |
| `ss -lntp` | `seaf-server` listens on `0.0.0.0:8082`; Seahub workers listen on `0.0.0.0:8000` |
| Nginx effective configuration | `/seafhttp` is rewritten and proxied to `127.0.0.1:8082`; `/` is proxied to `127.0.0.1:8000` |
| `GET http://127.0.0.1:8000/healthz` inside LXC 108 | Seafile/Gunicorn 404 page, not the ArtCraft gateway's health response |

This verifies that the installed HTTP fileserver route goes to the C `seaf-server` listener, rather than a Go fileserver listener. It does **not** verify that the proposed patch is installed, that the save endpoint is active, or that a conditional save works. The ArtCraft gateway is not installed at the checked port. No files, configuration, services, or Seafile data were changed.

The Go fileserver finding remains relevant to an upstream patch unless that route is explicitly unsupported/refused. The real DOCX MVP, current read authorization, conditional-save race behavior, and ONLYOFFICE regression remain unverified.

## Recovery after Sol's round-2 FAIL

Sol's report is preserved at [`GPT-SOL-REREVIEW-D9EF476.md`](GPT-SOL-REREVIEW-D9EF476.md).
It reviewed the clean candidate SHA above. The current root worktree contains
additional **uncommitted** local remediation and must not be treated as that
candidate or as Sol-approved.

### Reproduced locally after the report

| Command | Result | Scope |
| --- | --- | --- |
| `python3 tests/test_gateway_unit.py` | PASS | synthetic HTTP/upstream harness |
| `/tmp/opencode/pwvenv/bin/python tests/test_hostpage_protocol.py` | PASS | synthetic bridge/save-state protocol |
| `ARTCRAFT_SEAHUB_SOURCE=/tmp/artcraft-seahub-review python3 tests/test_gr015_authorization.py` | PASS | executes patched permission/type helper with synthetic Django/Seafile dependencies; not a Django runtime test |
| `/tmp/opencode/pwvenv/bin/python tests/test_wordcraft_host_roundtrip.py` | PASS | real local WordCraft Web bundle performs an edit, serializes DOCX, receives a host acknowledgement and reopens from in-memory storage |
| `python3 -m py_compile integration/gateway/*.py tests/*.py` | PASS | local syntax check |
| `cargo fmt --check --all` in `.work/wordcraft-patch` | PASS | local WordCraft source patch |
| `git apply --check` on GR-015 patches against exact clean base SHAs | PASS | patch applicability only; C build/Django runtime not tested |

`tests/test_browser.py` and `tests/test_gr012_svg.py` were invoked without the
Seahub-issued `ARTCRAFT_SEAFILE_ACCESS_TOKEN`; both printed usage and exited 2,
so neither was run. The current T3 browser profile lands on Seafile's login
screen. The previously observed synthetic DOCX click still routed to
ONLYOFFICE; no document was edited in that observation. No credentials were
read or exposed.

### Remaining blockers and limits

The local WordCraft browser test closes the host's premature-clean/confirmation
false positive for the tested protocol, but its storage is in-memory. It does
not satisfy the required Seafile Web → WordCraft → durable version → close and
reopen acceptance. The Seafile C patch is still unbuilt/uninstalled; the Seahub
patch is still unimported in a Django runtime. Current-read authorization has
only source-harness evidence. ONLYOFFICE open/edit/save regression, live
conditional-save races, GridCraft semantics, and VectorCraft semantic reopen
remain unverified. CSP and rate limiting remain open for any public deployment.

The synthetic file on live Seafile remains untouched by this recovery. No
Seafile configuration/service was changed, and no upstream issue, PR, or RFC was
published.
