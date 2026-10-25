# GR-042 — browser enforcement of dynamic host-page CSP

## Scope

This check drives the real `Handler.do_POST` → `Handler._open` route with a
synthetic Seafile adapter and a browser form handoff. It verifies the generated
response policy in Chromium. It does not start Seafile or ONLYOFFICE and does
not modify production state.

## Result

`python3 tests/test_gr042_hostpage_csp_browser.py` passed using the installed
Chromium 1248 and Playwright Python package supplied to the run with `uv`:

```sh
uv run --with playwright --python 3.14 -- python tests/test_gr042_hostpage_csp_browser.py
```

Recorded output is in `docs/reviews/GR-042/README.md`. The test checks:

| Browser condition | Result |
| --- | --- |
| Synthetic Seafile origin submits a form to actual `POST /open/` and frames its response | PASS |
| Host inline script runs and its nonce stylesheet applies (`#bar` is absolutely positioned) | PASS |
| No `securitypolicyviolation` event fires on the allowed host page | PASS |
| A foreign outer ancestor wraps an allowed Seafile-origin form page | PASS — the `/open/` document does not commit in Chromium |

The foreign-ancestor case uses a nested page: its innermost Seafile-origin page
submits the form, satisfying the gateway's separate `/open/` Origin check, while
an outer `localhost` document is an additional disallowed CSP ancestor.

## Limits

The configured app URL points to a tiny synthetic same-origin endpoint that
sends `wordcraft:ready`; it does not load a Craft bundle. Static editor CSP,
production Seafile, proxy/header behavior, browser compatibility beyond the
recorded Chromium, and deployment security remain **NOT VERIFIED**. This does
not change the project GPT review status or unlock upstream publication.

Work-item state: **GPT REVIEW PENDING**. The project-level verdict remains
**INCOMPLETE**.
