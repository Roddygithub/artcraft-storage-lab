# GR-042 browser evidence

Date: 2026-10-25

Command:

```sh
uv run --with playwright --python 3.14 -- python tests/test_gr042_hostpage_csp_browser.py
```

Environment: cached Playwright Chromium 1248; Playwright Python provided by
`uv` for this run. Synthetic adapter, synthetic token and document bytes, and
loopback-only HTTP servers. No Seafile or ONLYOFFICE service was started.

Output:

```text
PASS: actual POST /open/ response framed by configured Seafile origin
PASS: nonce inline script fetched/opened the synthetic document; nonce style applied; no CSP violations
PASS: actual POST /open/ response refused a disallowed outer ancestor
```

The test goes through `Handler.do_POST` and `Handler._open`; a small test-only
`Handler` subclass serves the synthetic editor endpoint, which sends
`wordcraft:ready`. The allowed case verifies the host script fetched the
synthetic document and reported it opened, the nonce style applied (`#bar`
computed position is `absolute`), and the host document collected no
`securitypolicyviolation` events. For the negative case, an outer
`localhost` page embeds a synthetic Seafile-origin page that submits the form;
Chromium never commits the gateway `/open/` frame because the outer ancestor is
not allowed by `frame-ancestors`.

Limits: the synthetic editor endpoint does not load a Craft bundle. Static
editor CSP, proxy behavior and other browsers are not covered.

Independent review: `INDEPENDENT-REVIEW-R1.md` returned a bounded provisional
PASS with no findings. This does not alter the project-level GPT status.
