# Independent review — GR-042 browser-enforced dynamic host CSP

**Verdict: PROVISIONAL PASS (bounded).** No finding in the reviewed scope.

The reviewer confirmed that the Chromium test exercises the real
`Handler.do_POST` → `Handler._open` path. Only `do_GET` is overridden to serve
a tiny synthetic editor endpoint; POST routing and CSP generation are inherited
from the production gateway handler.

Verified claims:

- The configured synthetic Seafile origin can frame the `/open/` response.
- The nonce-bound host script runs, fetches the synthetic document and updates
  the host status.
- The nonce-bound stylesheet applies, and the allowed page records no
  `securitypolicyviolation` events.
- A foreign `localhost` outer ancestor is blocked even though the inner
  synthetic Seafile-origin page submits the form.
- Loopback servers and a synthetic adapter/token/document are used; server
  threads are shut down and joined.

The independent reviewer inspected the test, evidence, gateway handler,
host-page template and existing gateway unit tests. No services were started by
that review. This is not a project-level GPT verdict.

**Not verified:** a real Craft bundle under CSP, production Seafile, TLS or
reverse-proxy behavior, deployment security, and browsers other than the
recorded Chromium build.
