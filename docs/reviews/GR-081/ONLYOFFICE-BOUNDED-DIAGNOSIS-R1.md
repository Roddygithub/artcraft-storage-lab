# GR-081 bounded ONLYOFFICE 404 diagnosis R1

**PROVISIONAL — INCONCLUSIVE / NOT VERIFIED.** This is read-only research. No
files, tests, browser, or runtime services were used or changed.

## Retained observations

GR-080 records the configured `/onlyoffice/web-apps/apps/api/documents/api.js`
request returning HTML 404, undefined ONLYOFFICE globals/editor, and zero
frames. Its probe did not repeat direct Document Server requests. GR-076 had
recorded direct API-script and healthcheck HTTP 200s earlier. Those earlier
responses show service availability at that time, but do not prove the
browser-facing proxy URL reached that same upstream. Earlier GR-072 synthetic
edit/save/history/later-load evidence predates the later routing changes and
does not close this preservation gate.

## Bounded causal tree (hypotheses only)

1. **Configured or rendered URL mismatch:** wrong origin/port, stale setting,
   or external prefix mismatch. GR-080 retained the path but not the full
   rendered URL, origin, redirect chain, or final host.
2. **Reverse-proxy mapping:** wrong virtual host/upstream, prefix fallthrough,
   or prefix strip/preserve mismatch. The tracked deployment assigns
   `/onlyoffice/` to Document Server while Seahub also has an
   `/onlyoffice/editor-callback/` endpoint; inspect actual location precedence
   rather than changing either route. No collision has been established.
3. **Policy interference:** CSP might block script execution but does not itself
   explain an HTTP 404. Frame policy is a weaker explanation because the API
   global was absent before any editor frame. A proxy rule could intentionally
   return 404. The target's non-allow-listed scope reduces, but does not rule
   out, dispatcher interference.

The recorded direct-service 200s and GR-080 browser-facing 404 are separated in
time and path. No causal link to ArtCraft has been established.

## Safe next investigation

Use only existing archived artifacts: compare the effective configured API URL
with the rendered URL for GR-072/076/080; trace the exact URL through saved proxy
configuration and location precedence; inspect retained proxy access/error logs
or HAR redirect/status metadata; compare archived CSP and dispatch settings.
Identify which component generated the 404 before assigning cause. Redact
credentials, JWTs and capability URLs. If these artifacts are unavailable,
record the missing evidence. Do not change ONLYOFFICE or proxy configuration as
part of this diagnosis.

## Authoritative references

- [Seafile 12 ONLYOFFICE setup](https://manual.seafile.com/12.0/extension/only_office/)
- [Seafile 11 ONLYOFFICE subfolder note](https://manual.seafile.com/11.0/deploy/only_office/)
- [ONLYOFFICE Document Server proxy virtual-path example](https://github.com/ONLYOFFICE/document-server-proxy/blob/master/nginx/proxy-to-virtual-path.conf)

These documents support the configuration concepts, not the cause of this
instance's 404.
