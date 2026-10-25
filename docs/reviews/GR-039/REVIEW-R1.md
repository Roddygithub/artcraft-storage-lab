# GR-039 independent review — round 1

**Result:** PROVISIONAL, remediation requested. This bounded review does not
change the project-level GPT verdict.

## Findings and remediation

1. **Medium — CSP-origin injection.** The initial validator accepted a
   semicolon-bearing hostname and a percent-encoded newline. Since the value was
   inserted into `frame-ancestors`, it could add a CSP directive or produce a
   non-origin source. Remediation: validate DNS names/IP literals/ports and
   reject percent and control characters before serializing the origin.
   Regression cases now cover semicolon and `%0a` inputs, alongside CR/LF.
2. **Low — explicit HTTPS default port mismatch.** The initial canonicalizer
   retained `:443`, while browsers serialize the corresponding Origin without
   the default port. Remediation: normalize default ports away and exercise the
   configured `:443` handoff using the browser-normalized Origin.

The independent reviewer also noted that browser CSP enforcement, proxy
behavior, editor bundle compatibility, Seafile and ONLYOFFICE runtime behavior
were not tested. Those limits remain open.

## Follow-up checks

After remediation, `python3 -m py_compile` and
`python3 tests/test_gateway_unit.py` pass. The unit suite checks the three
malformed origin inputs fail closed, that no injected response header appears,
and that default-port normalization permits the expected origin. A second
independent review is pending.
