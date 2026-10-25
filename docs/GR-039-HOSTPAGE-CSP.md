# GR-039 — CSP for the dynamic capability host page

## Scope

The gateway-generated `/open/` HTML contains the browser-side session capability
and the parent half of the editor `postMessage` protocol. This change adds a
response-specific CSP to that page only. It does not add a policy to static Craft
editor HTML, JSON/API responses, or reverse-proxy configuration.

## Implementation

`Handler._open` generates an 18-byte cryptographic nonce for each host page and
places it on the page's inline `<script>` and `<style>`. The response policy:

* defaults to `default-src 'none'` and denies base URLs, objects, and form
  submission;
* permits the host page to load same-origin editor frames, call same-origin
  gateway endpoints, and display same-origin/data/blob images;
* permits only the nonce-bearing inline script and style; and
* sets `frame-ancestors` to the normalized `ARTCRAFT_SEAFILE_ORIGIN`, or
  `'none'` if the setting is missing or malformed.

This retains the intended Seahub → host-page iframe embedding when the configured
origin is valid. The shared origin parser now accepts only HTTP(S) origins with
a valid DNS hostname, IPv4/IPv6 literal and port; it rejects control and
percent-encoded characters, CSP separators, credentials, paths, queries,
fragments, and invalid ports before using the value for CSRF admission or a
response header. Explicit default ports are normalized away so the configured
origin matches the browser's serialized `Origin` value.

## Verification

`python3 tests/test_gateway_unit.py` passed. Its HTTP checks verify that the
host page returns both nonce attributes matching the CSP nonce, that a second
response gets a different nonce, that the configured Seahub origin is the sole
`frame-ancestors` source, and that CR/LF, CSP-separator, and percent-encoded
newline inputs, empty user-info and empty query/fragment delimiters fail closed
without injecting a response header. An explicit HTTPS `:443` setting also
accepts the browser's default-port-less Origin. Python bytecode compilation and
`git diff --check` passed as well.

## Limits

This is a unit-tested response-header change; no browser CSP enforcement test was
run. In particular, compatibility with each editor bundle's scripts, WASM,
fonts, image/blob workers and network behavior is **NOT VERIFIED**. The static
editor documents do not yet receive a separate CSP, and proxy/CDN header behavior
has not been tested. Rate limiting, ONLYOFFICE save/version/reopen regression,
production topology, and project-level GPT review remain **NOT VERIFIED**.
Upstream publication remains locked.
