# GR-076 responses to independent R1

R1 is a source-only **PROVISIONAL PASS**, not an independently executed test result.

| Finding | Response |
|---|---|
| 1, export payload bound | Added a 50 MiB cap in host-mode Web write callback; standalone remains unchanged. Exports are explicit browser downloads, not messages delivered to the parent host (R1 misdescribes their destination). Live export behavior NOT VERIFIED. |
| 2, pre-serialization allocation | Explicit source comment and report limitation. Existing exporter returns a complete Vec; handoff size is bounded, peak serialization memory is NOT BOUNDED. Streaming encoder deferred outside this adapter slice. |
| 3, fallback RNG | Removed predictable fallback. Host startup now requires successful browser Crypto.getRandomValues; standalone startup does not request a namespace. Browser failure UI NOT VERIFIED. |
| 4, beforeunload | Report already states best-effort browser confirmation; no impossible-to-close guarantee. Browser can abandon any iframe/document. |
| 5, authorizer interaction | Existing nonempty Session.authorize prevents installing automation_authorize. Browser has no control-channel listener. Focused tests exercise direct engine dispatch; no bypass established by R1. |
| 6, clipboard rule | Generic file-prefix prohibition intentionally includes file.newFromClipboard. Tests cover it; waiting authorizer separately rejects paste-before-open. |
| 7, retained unknown ticket | Intentional requirement. Late matching positive/negative result resolves the unknown outcome; no timeout auto-retry. Tests cover unknown lockout and late resolution. |

Additional final delta since the reviewed patch: explicit existing workspace
photocraft-format dependency for bounded decoder (lockfile adds only this local
edge); dedicated standalone confirmed-write vs unconfirmed-download regression.
The retained lock's external versions/Git pins remain unchanged.

R1's phrase "50 MiB transport cap" is imprecise: the existing shared transport
permits up to 256 MiB cumulative Open copying; the adapter caps document input
and host-save output at 50 MiB. Limits are separate in the report. R1's whole
browser/Seafile/security-runtime claims and "browser will prompt" language are
not demonstrated here; browser confirmation is best effort only. Licensing of
the full transitive graph was not audited by this implementation session.
