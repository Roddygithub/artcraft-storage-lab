# GR-039 independent review — round 2

**Result:** PROVISIONAL PASS on the two round-1 findings, with one low
documentation/validation discrepancy. This is not a project-level GPT verdict.

## Round-2 finding and response

The reviewer found that empty delimiters (`@`, `?`, `#`) were accepted and
normalized even though the design text said credentials, queries and fragments
were rejected. No CSP injection path was identified, but the parser behavior did
not match the stated rule.

The normalizer now rejects `@` in the authority and any `?` or `#` in the
configured or request Origin. The HTTP regression set now includes empty
userinfo, query and fragment cases, alongside CR/LF, semicolon, and
percent-encoded newline. The gateway unit suite passes with all six malformed
origins failing closed. A round-3 exact re-review is pending.

The reviewer confirmed that the prior medium CSP-origin injection and low
default-port mismatch are closed. Browser CSP enforcement, static editor CSP,
reverse proxy, deployment, Seafile/ONLYOFFICE behavior and overall project
readiness remain NOT VERIFIED.
